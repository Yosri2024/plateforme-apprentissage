from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

Utilisateur = get_user_model()

# ==============================
# Section sur les exercices et snippets Python
# ==============================

class Exercice(models.Model):
    NIVEAU_DIFFICULTE_CHOICES = [
        ('facile', _('Facile')),
        ('moyen', _('Moyen')),
        ('difficile', _('Difficile')),
    ]

    titre = models.CharField(_('titre'), max_length=200)
    description = models.TextField(_('description'))
    description_enigma = models.TextField(_('description de l\'énigme'), blank=True)
    code_skeleton = models.TextField(_('code squelette'), blank=True)
    niveau_difficulte = models.CharField(_('niveau de difficulté'), max_length=20,
                                         choices=NIVEAU_DIFFICULTE_CHOICES)
    exemple_entrée = models.TextField(_('exemple d\'entrée'), blank=True)
    exemple_sortie = models.TextField(_('exemple de sortie'), blank=True)
    tests_cachés = models.JSONField(_('tests cachés'), blank=True, null=True)
    date_creation = models.DateTimeField(_('date de création'), auto_now_add=True)
    date_mise_a_jour = models.DateTimeField(_('date de mise à jour'), auto_now=True)
    auteur = models.ForeignKey(
        Utilisateur,
        on_delete=models.CASCADE,
        related_name='exercices_crees',
        limit_choices_to={'is_enseignant': True}
    )

    class Meta:
        verbose_name = _('exercice')
        verbose_name_plural = _('exercices')
        ordering = ['-date_creation']

    def __str__(self):
        return self.titre

class Snippet(models.Model):
    titre = models.CharField(_('titre'), max_length=200)
    code = models.TextField(_('code'))
    explication = models.TextField(_('explication'))
    etiquettes = models.CharField(_('étiquettes'), max_length=200, help_text='Séparées par des virgules')
    date_ajout = models.DateTimeField(_('date d\'ajout'), auto_now_add=True)
    auteur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='snippets_crees')

    class Meta:
        verbose_name = _('snippet')
        verbose_name_plural = _('snippets')
        ordering = ['-date_ajout']

    def __str__(self):
        return self.titre

# ==============================
# Soumissions des étudiants et notes
# ==============================

class Soumission(models.Model):
    exercice = models.ForeignKey(Exercice, on_delete=models.CASCADE, related_name='soumissions')
    etudiant = models.ForeignKey(
        Utilisateur,
        on_delete=models.CASCADE,
        related_name='soumissions_effectuees',
        limit_choices_to={'is_enseignant': False}
    )
    code_soumis = models.TextField(_('code soumis'))
    date_soumission = models.DateTimeField(_('date de soumission'), auto_now_add=True)
    test_passed = models.BooleanField(_('test passé'), default=False)
    note_obtenue = models.IntegerField(_('note obtenue'), null=True, blank=True)
    max_note = models.IntegerField(_('note maximale'), default=100)
    temps_execution = models.FloatField(_('temps d\'exécution (secondes)'), null=True, blank=True)

    class Meta:
        verbose_name = _('soumission')
        verbose_name_plural = _('soumissions')
        unique_together = ('exercice', 'etudiant')
        ordering = ['-date_soumission']

    def __str__(self):
        return f"{self.etudiant.email} - {self.exercice.titre}"

# ==============================
# Favoris / Collections de snippets
# ==============================

class CollectionSnippet(models.Model):
    etudiant = models.ForeignKey(
        Utilisateur,
        on_delete=models.CASCADE,
        related_name='collections_snippets',
        limit_choices_to={'is_enseignant': False}
    )
    titre = models.CharField(_('titre'), max_length=200)
    description = models.TextField(_('description'), blank=True)
    snippet = models.ManyToManyField(Snippet, related_name='collections')
    est_publique = models.BooleanField(_('est publique'), default=False)
    date_creation = models.DateTimeField(_('date de création'), auto_now_add=True)

    class Meta:
        verbose_name = _('collection de snippets')
        verbose_name_plural = _('collections de snippets')

    def __str__(self):
        return f"{self.etudiant.email} - {self.titre}"