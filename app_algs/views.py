from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.http import Http404
from app_web.models import Cours
from .models import Probleme, Solution, ProgressSolution, CollectionProblemes

# ==============================
# Pages publiques (non connectées)
# ==============================

def page_cours_public(request, public):
    """Cours Algo & ASD d'un public cible : 'lycee' ou 'fac'"""
    configurations = {
        'lycee': {
            'titre': 'Cours Lycée — Algo & ASD',
            'description_categorie': "Préparation au baccalauréat : algorithmes classiques, récursivité, fichiers, Python et Qt.",
        },
        'fac': {
            'titre': 'Cours Fac — Algo & ASD',
            'description_categorie': "ASD & POO : structures de données avancées, complexité, graphes et programmation orientée objet (Java).",
        },
    }
    configuration = configurations.get(public)
    if configuration is None:
        raise Http404('Public cible introuvable')

    cours_liste = Cours.objects.filter(
        domaine='algo', public_cible=public, est_publie=True
    ).select_related('enseignant').prefetch_related('modules').order_by('titre')

    return render(request, 'algos/cours_public.html', {
        'titre': configuration['titre'],
        'description_categorie': configuration['description_categorie'],
        'public': public,
        'cours_liste': cours_liste,
    })


def page_accueil_algos(request):
    """Page d'accueil Algo & ASD : section Lycée + section Fac"""
    problemes_populaires = Probleme.objects.select_related('auteur').order_by('-date_creation')[:6]
    # Cours répartis entre Lycée (bac) et Fac (ASD)
    cours_lycee = Cours.objects.filter(domaine='algo', public_cible='lycee', est_publie=True).first()
    cours_fac = Cours.objects.filter(domaine='algo', public_cible='fac', est_publie=True).order_by('titre')
    return render(request, 'algos/accueil.html', {
        'problemes': problemes_populaires,
        'cours_lycee': cours_lycee,
        'cours_fac': cours_fac,
    })

# ==============================
# Pages de problèmes
# ==============================

class ListeProblemesView(ListView):
    """Liste tous les problèmes"""
    model = Probleme
    template_name = 'algos/liste_problemes.html'
    context_object_name = 'problemes_liste'
    paginate_by = 12

    def get_queryset(self):
        queryset = Probleme.objects.select_related('auteur').prefetch_related('solutions')
        
        # Filtrage par difficulte
        difficulte_filtre = self.request.GET.get('difficulte')
        if difficulte_filtre:
            queryset = queryset.filter(difficulte=difficulte_filtre)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['difficultes'] = dict(Probleme.DIFFICULTE_CHOICES)

class DetailProblemeView(DetailView):
    """Détails d'un problème spécifique"""
    model = Probleme
    template_name = 'algos/detail_probleme.html'
    context_object_name = 'probleme'

    def get_queryset(self):
        return Probleme.objects.select_related('auteur').prefetch_related('solutions', 'sous_problemes')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        probleme = self.object
        
        # Récupérer la meilleure solution pour ce problème
        meilleure_solution = probleme.solutions.order_by('date_publication').first()
        context['meilleure_solution'] = meilleure_solution
        
        # Si l'étudiant est connecté, récupérer sa progression
        if self.request.user.is_authenticated and not self.request.user.is_enseignant:
            try:
                progression = ProgressSolution.objects.get(etudiant=self.request.user, probleme=probleme)
                context['progression_etudiante'] = progression
            except ProgressSolution.DoesNotExist:
                context['progression_etudiante'] = None
        
        return context

@login_required
def page_resoudre_probleme(request, pk):
    """Page de résolution d'un problème (étudiants seulement)"""
    if request.user.is_enseignant:
        messages.error(request, 'Les enseignants ne peuvent pas résoudre des problèmes')
        return redirect('app_algs:accueil')
    
    probleme = get_object_or_404(Probleme, pk=pk)
    
    # Vérifier si une progression existe déjà
    progression, created = ProgressSolution.objects.get_or_create(
        etudiant=request.user,
        probleme=probleme
    )
    
    if request.method == 'POST':
        progression.code_envoye = request.POST.get('code', '')
        progression.est_resolu = bool(request.POST.get('est_resolu'))
        
        # Calculer une note simple (logique d'évaluation de base)
        if progression.est_resolu:
            if progression.code_envoye.strip():
                progression.note_obtenue = min(100, len(progression.code_envoye.split()) * 2)
            else:
                progression.note_obtenue = 0
        
        if progression.est_resolu:
            progression.date_resolu = timezone.now()
        
        progression.save()
        messages.success(request, 'Votre solution a été enregistrée !')
        return redirect('app_algs:detail_probleme', pk=probleme.pk)
    
    return render(request, 'algos/resoudre_probleme.html', {
        'probleme': probleme,
        'progression': progression
    })

# ==============================
# Pages de collection
# ==============================

@login_required
def page_mes_collections(request):
    """Page des collections de problèmes de l'étudiant"""
    collections = CollectionProblemes.objects.filter(etudiant=request.user).prefetch_related('probleme')
    return render(request, 'algos/mes_collections.html', {'collections': collections})

@login_required
def page_creer_collection(request):
    """Page de création d'une nouvelle collection"""
    if request.method == 'POST':
        titre = request.POST.get('titre', '')
        description = request.POST.get('description', '')
        est_publique = 'est_publique' in request.POST
        
        if titre:
            collection = CollectionProblemes.objects.create(
                etudiant=request.user,
                titre=titre,
                description=description,
                est_publique=est_publique
            )
            # Ajouter des problèmes depuis la liste sélectionnée
            problemes_ids = request.POST.getlist('problemes')
            collection.probleme.set(problemes_ids)
            
            messages.success(request, f'Collection "{collection.titre}" créée avec succès !')
            return redirect('app_algs:detail_collection', pk=collection.pk)
        else:
            messages.error(request, 'Veuillez fournir un titre pour la collection')
    
    # Récupérer tous les problèmes pour la sélection
    tous_les_problemes = Probleme.objects.all()
    return render(request, 'algos/creer_collection.html', {'problemes': tous_les_problemes})

@login_required
def page_detail_collection(request, pk):
    """Page de détail d'une collection"""
    collection = get_object_or_404(CollectionProblemes, pk=pk)
    
    # Vérifier les autorisations
    if not collection.est_publique and collection.etudiant != request.user:
        messages.error(request, 'Vous n\'êtes pas autorisé à voir cette collection')
        return redirect('app_algs:accueil')
    
    return render(request, 'algos/detail_collection.html', {'collection': collection})