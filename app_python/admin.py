from django.contrib import admin
from .models import Exercice, Snippet, Soumission, CollectionSnippet

@admin.register(Exercice)
class ExerciceAdmin(admin.ModelAdmin):
    list_display = ('titre', 'niveau_difficulte', 'auteur', 'date_creation')
    list_filter = ('niveau_difficulte', 'auteur')
    search_fields = ('titre', 'description')
    raw_id_fields = ('auteur',)

@admin.register(Snippet)
class SnippetAdmin(admin.ModelAdmin):
    list_display = ('titre', 'auteur', 'date_ajout')
    list_filter = ('auteur',)
    search_fields = ('titre', 'code', 'explication')
    raw_id_fields = ('auteur',)

@admin.register(Soumission)
class SoumissionAdmin(admin.ModelAdmin):
    list_display = ('exercice', 'etudiant', 'date_soumission', 'test_passed', 'note_obtenue')
    list_filter = ('test_passed', 'exercice')
    raw_id_fields = ('exercice', 'etudiant')
    readonly_fields = ('date_soumission',)

@admin.register(CollectionSnippet)
class CollectionSnippetAdmin(admin.ModelAdmin):
    list_display = ('titre', 'etudiant', 'est_publique')
    list_filter = ('est_publique',)
    filter_horizontal = ('snippet',)