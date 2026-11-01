from django.contrib import admin
from .models import Probleme, Solution, SousProbleme, ProgressSolution, CollectionProblemes

@admin.register(Probleme)
class ProblemeAdmin(admin.ModelAdmin):
    list_display = ('titre', 'difficulte', 'auteur', 'date_creation')
    list_filter = ('difficulte', 'auteur')
    search_fields = ('titre', 'description')
    raw_id_fields = ('auteur',)

@admin.register(Solution)
class SolutionAdmin(admin.ModelAdmin):
    list_display = ('probleme', 'langage', 'auteur', 'date_publication')
    list_filter = ('langage', 'auteur')
    search_fields = ('probleme__titre', 'code')
    raw_id_fields = ('probleme', 'auteur')

@admin.register(SousProbleme)
class SousProblemeAdmin(admin.ModelAdmin):
    list_display = ('titre', 'probleme', 'ordre')
    list_filter = ('probleme',)
    ordering = ('probleme', 'ordre')

@admin.register(ProgressSolution)
class ProgressSolutionAdmin(admin.ModelAdmin):
    list_display = ('etudiant', 'probleme', 'est_resolu', 'note_obtenue')
    list_filter = ('est_resolu', 'probleme')
    raw_id_fields = ('etudiant', 'probleme')

@admin.register(CollectionProblemes)
class CollectionProblemesAdmin(admin.ModelAdmin):
    list_display = ('titre', 'etudiant', 'est_publique')
    list_filter = ('est_publique',)
    filter_horizontal = ('probleme',)