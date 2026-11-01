from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

Utilisateur = get_user_model()

# ==============================
# Section sur les algorithmes et les problèmes
# ==============================

class Probleme(models.Model):
    DIFFICULTE_CHOICES = [
        ('facile', _('Facile')),
        ('moyen', _('Moyen')),
        ('difficile', _('Difficile')),
    ]

    titre = models.CharField(_('titre'), max_length=200)
    description = models.TextField(_('description'))
    exemple_entrée = models.TextField(_('exemple d\'entrée'), blank=True)
    exemple_sortie = models.TextField(_('exemple de sortie'), blank=True)
    complexity_temporelle = models.CharField(_('complexité temporelle'), max_length=50, blank=True)
    complexity_spatiale = models.CharField(_('complexité spatiale'), max_length=50, blank=True)
    difficulte = models.CharField(_('difficulte'), max_length=20, choices=DIFFICULTE_CHOICES)
    date_creation = models.DateTimeField(_('date de création'), auto_now_add=True)
    date_mise_a_jour = models.DateTimeField(_('date de mise à jour'), auto_now=True)
    auteur = models.ForeignKey(
        Utilisateur,
        on_delete=models.CASCADE,
        related_name='propositions',
        limit_choices_to={'is_enseignant': True}
    )

    class Meta:
        verbose_name = _('problème')
        verbose_name_plural = _('problèmes')
        ordering = ['-date_creation']

    def __str__(self):
        return self.titre

class Solution(models.Model):
    probleme = models.ForeignKey(Probleme, on_delete=models.CASCADE, related_name='solutions')
    code = models.TextField(_('code'))
    explication = models.TextField(_('explication'))
    langage = models.CharField(_('langage'), max_length=50,
                               choices=[
                                   ('python', 'Python'),
                                   ('java', 'Java'),
                                   ('cpp', 'C++'),
                                   ('javascript', 'JavaScript'),
                                   ('php', 'PHP'),
                               ])
    date_publication = models.DateTimeField(_('date de publication'), auto_now_add=True)
    auteur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='solutions')

    class Meta:
        verbose_name = _('solution')
        verbose_name_plural = _('solutions')
        ordering = ['-date_publication']

    def __str__(self):
        return f"Solution en {self.langage} pour {self.probleme.titre}"

class SousProbleme(models.Model):
    probleme = models.ForeignKey(Probleme, on_delete=models.CASCADE, related_name='sous_problemes')
    titre = models.CharField(_('titre'), max_length=200)
    description = models.TextField(_('description'))
    ordre = models.PositiveIntegerField(_('ordre'))

    class Meta:
        verbose_name = _('sous-problème')
        verbose_name_plural = _('sous-problèmes')
        ordering = ['ordre']

    def __str__(self):
        return f"{self.probleme.titre} - {self.titre}"

# ==============================
# Suivi de l'étudiant pour les algorithmes
# ==============================

class ProgressSolution(models.Model):
    etudiant = models.ForeignKey(
        Utilisateur,
        on_delete=models.CASCADE,
        related_name='progressions_solutions',
        limit_choices_to={'is_enseignant': False}
    )
    probleme = models.ForeignKey(Probleme, on_delete=models.CASCADE, related_name='progressions_etudiants')
    est_resolu = models.BooleanField(_('est résolu'), default=False)
    date_resolu = models.DateTimeField(_('date résolu'), null=True, blank=True)
    code_envoye = models.TextField(_('code envoyé'), blank=True)
    note_obtenue = models.IntegerField(_('note obtenue'), null=True, blank=True)
    max_note = models.IntegerField(_('note maximale'), default=100)

    class Meta:
        verbose_name = _('progression de solution')
        verbose_name_plural = _('progressions de solutions')
        unique_together = ('etudiant', 'probleme')

    def __str__(self):
        return f"{self.etudiant.email} - {self.probleme.titre}"

# ==============================
# Favoris / Collections d'étudiants
# ==============================

class CollectionProblemes(models.Model):
    etudiant = models.ForeignKey(
        Utilisateur,
        on_delete=models.CASCADE,
        related_name='collections_problemes',
        limit_choices_to={'is_enseignant': False}
    )
    titre = models.CharField(_('titre'), max_length=200)
    description = models.TextField(_('description'), blank=True)
    probleme = models.ManyToManyField(Probleme, related_name='collections')
    est_publique = models.BooleanField(_('est publique'), default=False)
    date_creation = models.DateTimeField(_('date de création'), auto_now_add=True)

    class Meta:
        verbose_name = _('collection de problèmes')
        verbose_name_plural = _('collections de problèmes')

    def __str__(self):
        return f"{self.etudiant.email} - {self.titre}"