from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import BaseUserCreationForm, UserChangeForm
from .models import Utilisateur, Cours, Module, Lecon, ProgressEtudiant, ListeLecture

class FormulaireCreationUtilisateur(BaseUserCreationForm):
    """Formulaire de création d'utilisateur dans l'admin (sans username)"""
    class Meta(BaseUserCreationForm.Meta):
        model = Utilisateur
        fields = ('email',)

class FormulaireModificationUtilisateur(UserChangeForm):
    """Formulaire de modification d'utilisateur dans l'admin"""
    class Meta:
        model = Utilisateur
        fields = '__all__'

@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    add_form = FormulaireCreationUtilisateur
    form = FormulaireModificationUtilisateur
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informations personnelles', {'fields': ('first_name', 'last_name', 'telephone', 'date_naissance', 'bio', 'photo_profil')}),
        ('Profil plateforme', {'fields': ('is_enseignant', 'est_approuve')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates importantes', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_enseignant', 'est_approuve'),
        }),
    )
    list_display = ('email', 'telephone', 'is_enseignant', 'est_approuve', 'is_staff')
    search_fields = ('email', 'telephone')
    ordering = ('email',)

@admin.register(Cours)
class CoursAdmin(admin.ModelAdmin):
    list_display = ('titre', 'enseignant', 'est_publie', 'niveau')
    list_filter = ('est_publie', 'niveau', 'enseignant')
    search_fields = ('titre', 'description')
    prepopulated_fields = {'slug': ('titre',)}
    raw_id_fields = ('enseignant',)

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('titre', 'cours', 'ordre')
    list_filter = ('cours',)
    ordering = ('cours', 'ordre')

@admin.register(Lecon)
class LeconAdmin(admin.ModelAdmin):
    list_display = ('titre', 'module', 'ordre')
    list_filter = ('module__cours', 'module')
    ordering = ('module__cours', 'module', 'ordre')

@admin.register(ProgressEtudiant)
class ProgressEtudiantAdmin(admin.ModelAdmin):
    list_display = ('etudiant', 'lecon', 'est_terminee', 'date_terminee')
    list_filter = ('est_terminee', 'lecon__module__cours')
    raw_id_fields = ('etudiant', 'lecon')

@admin.register(ListeLecture)
class ListeLectureAdmin(admin.ModelAdmin):
    list_display = ('titre', 'etudiant', 'est_publique')
    list_filter = ('est_publique',)
    filter_horizontal = ('cours',)