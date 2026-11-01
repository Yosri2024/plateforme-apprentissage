from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.http import Http404
from django.utils import timezone
from .models import Exercice, Snippet, Soumission, CollectionSnippet

# ==============================
# Pages publiques (non connectées)
# ==============================

def page_accueil_python(request):
    """Page d'accueil de l'application Python"""
    exercices_populaires = Exercice.objects.select_related('auteur').order_by('-date_creation')[:6]
    snippets_populaires = Snippet.objects.select_related('auteur').order_by('-date_ajout')[:6]
    return render(request, 'python/accueil.html', {
        'exercices': exercices_populaires,
        'snippets': snippets_populaires
    })

# ==============================
# Pages des exercices
# ==============================

class ListeExercicesView(ListView):
    """Liste tous les exercices"""
    model = Exercice
    template_name = 'python/liste_exercices.html'
    context_object_name = 'exercices_liste'
    paginate_by = 12

    def get_queryset(self):
        queryset = Exercice.objects.select_related('auteur').prefetch_related('soumissions')
        
        # Filtrage par niveau de difficulté
        niveau_filtre = self.request.GET.get('niveau_difficulte')
        if niveau_filtre:
            queryset = queryset.filter(niveau_difficulte=niveau_filtre)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['niveaux_difficulte'] = dict(Exercice.NIVEAU_DIFFICULTE_CHOICES)
        return context

class DetailExerciceView(DetailView):
    """Détails d'un exercice spécifique"""
    model = Exercice
    template_name = 'python/detail_exercice.html'
    context_object_name = 'exercice'

    def get_queryset(self):
        return Exercice.objects.select_related('auteur').prefetch_related('soumissions')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exercice = self.object
        
        # Si l'étudiant est connecté, récupérer sa soumission
        if self.request.user.is_authenticated and not self.request.user.is_enseignant:
            try:
                soumission = Soumission.objects.get(exercice=exercice, etudiant=self.request.user)
                context['soumission_etudiante'] = soumission
            except Soumission.DoesNotExist:
                context['soumission_etudiante'] = None
        
        return context

@login_required
def page_resoudre_exercice(request, pk):
    """Page de résolution d'un exercice (étudiants seulement)"""
    if request.user.is_enseignant:
        messages.error(request, 'Les enseignants ne peuvent pas résoudre des exercices')
        return redirect('app_python:accueil')
    
    exercice = get_object_or_404(Exercice, pk=pk)
    
    # Vérifier si une soumission existe déjà
    soumission, created = Soumission.objects.get_or_create(
        exercice=exercice,
        etudiant=request.user
    )
    
    if request.method == 'POST':
        soumission.code_soumis = request.POST.get('code', '')
        
        # Logique d'évaluation simple (à remplacer par un vrai système d'évaluation)
        if soumission.code_soumis.strip():
            soumission.test_passed = 'print("Hello World")' in soumission.code_soumis or 'def ' in soumission.code_soumis
            if soumission.test_passed:
                soumission.note_obtenue = min(100, len(soumission.code_soumis.split()) * 5)
            else:
                soumission.note_obtenue = 0
        else:
            soumission.test_passed = False
            soumission.note_obtenue = 0
        
        soumission.temps_execution = 0.5  # Exemple statique
        soumission.save()
        messages.success(request, 'Votre exercice a été soumis !')
        return redirect('app_python:detail_exercice', pk=exercice.pk)
    
    return render(request, 'python/resoudre_exercice.html', {
        'exercice': exercice,
        'soumission': soumission
    })

# ==============================
# Pages des collections
# ==============================

@login_required
def page_mes_collections(request):
    """Page des collections de snippets de l'étudiant"""
    collections = CollectionSnippet.objects.filter(etudiant=request.user).prefetch_related('snippet')
    return render(request, 'python/mes_collections.html', {'collections': collections})

@login_required
def page_creer_collection(request):
    """Page de création d'une nouvelle collection"""
    if request.method == 'POST':
        titre = request.POST.get('titre', '')
        description = request.POST.get('description', '')
        est_publique = 'est_publique' in request.POST
        
        if titre:
            collection = CollectionSnippet.objects.create(
                etudiant=request.user,
                titre=titre,
                description=description,
                est_publique=est_publique
            )
            # Ajouter des snippets depuis la liste sélectionnée
            snippets_ids = request.POST.getlist('snippets')
            collection.snippet.set(snippets_ids)
            
            messages.success(request, f'Collection "{collection.titre}" créée avec succès !')
            return redirect('app_python:detail_collection', pk=collection.pk)
        else:
            messages.error(request, 'Veuillez fournir un titre pour la collection')
    
    # Récupérer tous les snippets pour la sélection
    tous_les_snippets = Snippet.objects.all()
    return render(request, 'python/creer_collection.html', {'snippets': tous_les_snippets})

@login_required
def page_detail_collection(request, pk):
    """Page de détail d'une collection"""
    collection = get_object_or_404(CollectionSnippet, pk=pk)
    
    # Vérifier les autorisations
    if not collection.est_publique and collection.etudiant != request.user:
        messages.error(request, 'Vous n\'êtes pas autorisé à voir cette collection')
        return redirect('app_python:accueil')
    
    return render(request, 'python/detail_collection.html', {'collection': collection})