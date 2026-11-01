from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.http import Http404
from django.db.models import Q
from django import forms
from .models import Cours, Lecon, ProgressEtudiant, Utilisateur

# ==============================
# Pages publiques (non connectées)
# ==============================

def page_accueil(request):
    """Page d'accueil publique"""
    cours_publies = Cours.objects.filter(est_publie=True).select_related('enseignant')[:6]
    return render(request, 'web/accueil.html', {'cours': cours_publies})

# ==============================
# Authentification et profil
# ==============================

def page_connexion(request):
    """Page de connexion : par e-mail OU par téléphone"""
    if request.user.is_authenticated:
        return redirect('app_web:accueil')

    if request.method == 'POST':
        identifiant = (request.POST.get('identifiant') or '').strip()
        mot_de_passe = request.POST.get('mot_de_passe') or ''
        utilisateur = authenticate(request, identifiant=identifiant, password=mot_de_passe)
        if utilisateur is not None:
            login(request, utilisateur)
            messages.success(request, 'Connexion réussie !')
            return redirect('app_web:accueil')
        messages.error(request, 'E-mail/téléphone ou mot de passe incorrect.')

    return render(request, 'web/connexion.html')

@login_required
def page_deconnexion(request):
    """Déconnexion"""
    logout(request)
    messages.info(request, 'Vous avez été déconnecté')
    return redirect('app_web:accueil')

def page_inscription(request):
    """Page d'inscription"""
    if request.user.is_authenticated:
        return redirect('app_web:accueil')
    
    if request.method == 'POST':
        form = FormulaireInscription(request.POST, request.FILES)
        if form.is_valid():
            utilisateur = form.save()
            # Connecter directement l'utilisateur après son inscription
            login(request, utilisateur, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, 'Inscription réussie ! Bienvenue sur la plateforme.')
            return redirect('app_web:accueil')
        else:
            messages.error(request, 'Veuillez corriger les erreurs du formulaire')
    else:
        form = FormulaireInscription()
    
    return render(request, 'web/inscription.html', {'form': form})

@login_required
def page_profil(request):
    """Page de profil de l'utilisateur connecté"""
    # Progressions de l'étudiant sur ses leçons
    progressions = ProgressEtudiant.objects.filter(
        etudiant=request.user
    ).select_related('lecon__module__cours').order_by('-est_terminee', '-lecon__ordre')[:10]
    
    # Pourcentage complété approximatif pour chaque progression récente
    for progression in progressions:
        progression.lecon.num_points_de_passage = min(100, round(progression.temps_passe / 60))
    
    # Cours en cours (distincts) à partir des progressions
    cours_en_cours = list({progression.lecon.module.cours for progression in progressions})
    
    return render(request, 'web/profil.html', {
        'etudiant': request.user,
        'progressions': progressions,
        'cours_en_cours': cours_en_cours,
    })

@login_required
def page_modifier_profil(request):
    """Page de modification du profil de l'utilisateur connecté"""
    if request.method == 'POST':
        form = FormulaireProfil(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil mis à jour avec succès !')
            return redirect('app_web:profil')
        else:
            messages.error(request, 'Veuillez corriger les erreurs du formulaire')
    else:
        form = FormulaireProfil(instance=request.user)
    
    return render(request, 'web/modifier_profil.html', {'form': form})

# ==============================
# Inscription et profil basiques (simplifiés)
# ==============================

class FormulaireProfil(forms.ModelForm):
    """Formulaire de modification du profil utilisateur"""
    class Meta:
        model = Utilisateur
        fields = ('first_name', 'last_name', 'telephone', 'date_naissance', 'bio', 'photo_profil')

class FormulaireInscription(forms.ModelForm):
    mot_de_passe = forms.CharField(label='Mot de passe', widget=forms.PasswordInput)
    mot_de_passe_confirmation = forms.CharField(label='Confirmer le mot de passe', widget=forms.PasswordInput)

    # Fournisseurs de messagerie grand public acceptés (liste extensible)
    DOMAINES_EMAIL_AUTORISES = [
        'gmail.com',                            # Google
        'outlook.com', 'hotmail.com', 'live.com',  # Microsoft
        'yahoo.com',                            # Yahoo
        'icloud.com', 'me.com', 'mac.com',      # Apple
    ]

    class Meta:
        model = Utilisateur
        fields = ('first_name', 'last_name', 'email', 'telephone', 'date_naissance', 'photo_profil')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tous les champs obligatoires, sauf le téléphone (facultatif)
        for champ in ('first_name', 'last_name', 'email', 'date_naissance', 'photo_profil'):
            self.fields[champ].required = True

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip().lower()
        domaine = email.rsplit('@', 1)[-1]
        if domaine not in self.DOMAINES_EMAIL_AUTORISES:
            raise forms.ValidationError(
                'Adresse e-mail non autorisée. Utilisez un compte Gmail, Outlook/Hotmail/Live, Yahoo ou iCloud.'
            )
        if Utilisateur.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Un utilisateur avec cet email existe déjà.')
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        mot_de_passe = cleaned_data.get('mot_de_passe')
        mot_de_passe_confirmation = cleaned_data.get('mot_de_passe_confirmation')
        
        if mot_de_passe and mot_de_passe_confirmation:
            if mot_de_passe != mot_de_passe_confirmation:
                raise forms.ValidationError('Les mots de passe ne correspondent pas.')
        
        return cleaned_data
    
    def save(self, commit=True):
        utilisateur = super().save(commit=False)
        utilisateur.set_password(self.cleaned_data['mot_de_passe'])
        if commit:
            utilisateur.save()
        return utilisateur

# ==============================
# Pages des cours (Public et privé pour les enseignants)
# ==============================

def page_detail_lecon(request, pk):
    """Page de consultation d'une leçon (contenu + PDF + vidéo)"""
    lecon = get_object_or_404(
        Lecon.objects.select_related('module__cours'),
        pk=pk
    )
    cours = lecon.module.cours
    
    # Afficher la leçon seulement si le cours est publié ou pour son enseignant
    if not cours.est_publie and (not request.user.is_authenticated or request.user != cours.enseignant):
        raise Http404("Cette leçon n'est pas disponible")
    
    # Leçons précédente / suivante du même module
    precedente = lecon.module.lecons.filter(ordre__lt=lecon.ordre).order_by('-ordre').first()
    suivante = lecon.module.lecons.filter(ordre__gt=lecon.ordre).order_by('ordre').first()
    
    return render(request, 'web/detail_lecon.html', {
        'lecon': lecon,
        'cours': cours,
        'precedente': precedente,
        'suivante': suivante,
    })

def page_cours_web_mobile(request):
    """Page /cours/ au style d'/algorithmique/ : héros + 2 tuiles cliquables.
    Quand un sous-domaine ne contient qu'UN seul cours publié, la tuile ouvre
    DIRECTEMENT le cours (ex: /cours/developpement-web/), sinon la page du sous-domaine."""
    from django.urls import reverse

    def config_domaine(domaine):
        cours_domaine = Cours.objects.filter(domaine=domaine, est_publie=True)
        total = cours_domaine.count()
        if total == 1:
            return {
                'nb': total,
                'url': reverse('app_web:detail_cours', kwargs={'slug': cours_domaine.first().slug}),
                'direct': True,
            }
        return {
            'nb': total,
            'url': reverse('app_web:cours_' + domaine),
            'direct': False,
        }

    web = config_domaine('web')
    mobile = config_domaine('mobile')
    android = config_domaine('android')

    return render(request, 'web/liste_cours.html', {
        'nb_web': web['nb'], 'url_web': web['url'], 'web_direct': web['direct'],
        'nb_mobile': mobile['nb'], 'url_mobile': mobile['url'], 'mobile_direct': mobile['direct'],
        'nb_android': android['nb'], 'url_android': android['url'], 'android_direct': android['direct'],
    })


def page_cours_domaine(request, domaine):
    """Cours d'un sous-domaine : 'web' ou 'mobile' — l'enseignant voit aussi ses brouillons"""
    configurations = {
        'web': {
            'titre': 'Cours — Développement Web',
            'description_categorie': "HTML, CSS, Bootstrap, JavaScript et PHP : les fondations du web.",
        },
        'mobile': {
            'titre': 'Cours — Développement mobile (Cross-platform)',
            'description_categorie': "Flutter & Dart : applications multiplateformes Android/iOS/Web.",
        },
        'android': {
            'titre': 'Cours — Développement Android natif',
            'description_categorie': "Android natif avec Java et XML : activités, interfaces graphiques, Intents et bases de données SQLite.",
        },
    }
    configuration = configurations.get(domaine)
    if configuration is None:
        raise Http404('Sous-domaine introuvable')

    cours_liste = Cours.objects.filter(
        domaine=domaine,
    ).filter(
        Q(est_publie=True) | Q(enseignant=request.user if request.user.is_authenticated else None)
    ).select_related('enseignant').prefetch_related('modules')

    return render(request, 'web/liste_cours_domaine.html', {
        'titre': configuration['titre'],
        'description_categorie': configuration['description_categorie'],
        'domaine': domaine,
        'cours_liste': cours_liste,
    })


class ListeCoursView(ListView):
    """(Conservée si besoin : liste plate filtrable par niveau — plus liée aux routes)"""
    model = Cours
    template_name = 'web/liste_cours_domaine.html'
    context_object_name = 'cours_liste'

    def get_queryset(self):
        queryset = Cours.objects.filter(domaine='web').select_related('enseignant').prefetch_related('modules')
        niveau_filtre = self.request.GET.get('niveau')
        if niveau_filtre:
            queryset = queryset.filter(niveau=niveau_filtre)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['niveaux'] = dict(Cours.NIVEAUX_CHOICES)
        return context

class DetailCoursView(DetailView):
    """Détails d'un cours spécifique"""
    model = Cours
    template_name = 'web/detail_cours.html'
    context_object_name = 'cours'

    def get_queryset(self):
        return Cours.objects.select_related('enseignant').prefetch_related('modules__lecons')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cours = self.object
        
        # Afficher les cours seulement s'ils sont publiés ou si l'étudiant est l'enseignant
        if not cours.est_publie and (not self.request.user.is_authenticated or self.request.user != cours.enseignant):
            raise Http404("Ce cours n'est pas disponible")
        
        # Récupérer les modules
        modules = cours.modules.select_related('cours').prefetch_related('lecons')
        
        # Pour les étudiants connectés, récupérer les progrès
        if self.request.user.is_authenticated and not self.request.user.is_enseignant:
            progres_etudiant = ProgressEtudiant.objects.filter(
                etudiant=self.request.user,
                lecon__in=[lecon for module in modules for lecon in module.lecons.all()]
            ).select_related('lecon__module__cours')
            
            for progression in progres_etudiant:
                progression.lecon.num_points_de_passage = progression.temps_passe / 60  # Exemple simple
        
        modules = list(modules)
        # Numérotation continue des leçons d'un bout à l'autre du cours :
        # chaque module connaît le nombre de leçons passées (numéro global = total_avant + lecon.ordre)
        total_avant = 0
        for m in modules:
            m.total_avant = total_avant
            total_avant += m.lecons.count()
        context['modules'] = modules
        return context

# ==============================
# Pages liées à l'enseignant
# ==============================

@login_required
def page_creation_cours(request):
    """Page de création d'un nouveau cours (enseignants seulement)"""
    if not request.user.is_enseignant:
        messages.error(request, 'Vous devez être enseignant pour créer un cours')
        return redirect('app_web:accueil')
    
    if request.method == 'POST':
        titre = request.POST.get('titre', '')
        description = request.POST.get('description', '')
        niveau = request.POST.get('niveau', 'debutant')
        
        if titre and description:
            # Créer un slug simple
            slug = titre.lower().replace(' ', '-').replace('é', 'e').replace('à', 'a')
            
            cours = Cours.objects.create(
                titre=titre,
                description=description,
                slug=slug,
                niveau=niveau,
                enseignant=request.user
            )
            messages.success(request, f'Cours "{cours.titre}" créé avec succès !')
            return redirect('app_web:detail_cours', slug=cours.slug)
        else:
            messages.error(request, 'Veuillez fournir un titre et une description')
    
    return render(request, 'web/creation_cours.html')

@login_required
def page_modifier_cours(request, slug):
    """Page de modification d'un cours existant (enseignant seulement)"""
    cours = get_object_or_404(Cours, slug=slug)
    
    if cours.enseignant != request.user:
        messages.error(request, 'Vous n\'êtes pas autorisé à modifier ce cours')
        return redirect('app_web:detail_cours', slug=cours.slug)
    
    if request.method == 'POST':
        cours.titre = request.POST.get('titre', cours.titre)
        cours.description = request.POST.get('description', cours.description)
        cours.niveau = request.POST.get('niveau', cours.niveau)
        cours.est_publie = 'est_publie' in request.POST
        cours.save()
        messages.success(request, f'Cours "{cours.titre}" mis à jour avec succès !')
        return redirect('app_web:detail_cours', slug=cours.slug)
    
    return render(request, 'web/modifier_cours.html', {'cours': cours})

@login_required
def page_supprimer_cours(request, slug):
    """Page de suppression d'un cours (enseignant seulement)"""
    cours = get_object_or_404(Cours, slug=slug)
    
    if cours.enseignant != request.user:
        messages.error(request, 'Vous n\'êtes pas autorisé à supprimer ce cours')
        return redirect('app_web:detail_cours', slug=cours.slug)
    
    if request.method == 'POST':
        titre_cours = cours.titre
        cours.delete()
        messages.success(request, f'Cours "{titre_cours}" supprimé avec succès !')
        return redirect('app_web:liste_cours')
    
    return render(request, 'web/confirmer_suppression_cours.html', {'cours': cours})