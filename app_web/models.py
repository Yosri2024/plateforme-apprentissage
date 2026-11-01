from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

# Téléphone mobile tunisien : exactement 8 chiffres, premier chiffre 2/4/5/9
VALIDATEUR_TELEPHONE = RegexValidator(
    regex=r'^[2459][0-9]{7}$',
    message=_('Numéro invalide : exactement 8 chiffres, mobile tunisien (commence par 2, 4, 5 ou 9 — Ooredoo, Orange, Tunisie Telecom)'),
)

# ==============================
# Gestion des utilisateurs et de l'authentification
# ==============================

class UtilisateurManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('L\'adresse e-mail est obligatoire'))
        email = self.normalize_email(email)
        utilisateur = self.model(email=email, **extra_fields)
        utilisateur.set_password(password)
        utilisateur.save(using=self._db)
        return utilisateur

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class Utilisateur(AbstractUser):
    # Utiliser l'e-mail comme identifiant principal au lieu du nom d'utilisateur
    username = None
    email = models.EmailField(_('adresse e-mail'), unique=True)
    telephone = models.CharField(
        _('numéro de téléphone'),
        max_length=15,
        blank=True,
        validators=[VALIDATEUR_TELEPHONE],
        help_text=_('8 chiffres exactement — mobile tunisien : commence par 2, 4, 5 ou 9 (Ooredoo, Orange, Tunisie Telecom)'),
    )
    date_naissance = models.DateField(_('date de naissance'), null=True, blank=True)
    bio = models.TextField(_('biographie'), blank=True)
    photo_profil = models.ImageField(_('photo de profil'), upload_to='photos_profil/', blank=True, null=True)
    is_enseignant = models.BooleanField(_('est enseignant'), default=False)
    est_approuve = models.BooleanField(_('compte approuvé'), default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UtilisateurManager()

    class Meta:
        verbose_name = _('utilisateur')
        verbose_name_plural = _('utilisateurs')

    def __str__(self):
        return self.email

# ==============================
# Section sur les cours
# ==============================

class Cours(models.Model):
    NIVEAUX_CHOICES = [
        ('debutant', _('Débutant')),
        ('intermediaire', _('Intermédiaire')),
        ('avance', _('Avancé')),
    ]

    DOMAINE_CHOICES = [
        ('web', _('Développement Web')),
        ('mobile', _('Développement mobile')),
        ('android', _('Développement Android natif')),
        ('algo', _('Algo & ASD')),
        ('bdd', _('Base de données')),
    ]

    PUBLIC_CIBLE_CHOICES = [
        ('lycee', _('Lycée')),
        ('fac', _('Fac (Faculté)')),
    ]

    titre = models.CharField(_('titre'), max_length=200)
    description = models.TextField(_('description'))
    slug = models.SlugField(_('slug'), max_length=200, unique=True)
    image_couverture = models.ImageField(_('image de couverture'), upload_to='images_couverture/', blank=True, null=True)
    image_banniere = models.ImageField(_('bannière (page de détail)'), upload_to='images_couverture/', blank=True, null=True)
    domaine = models.CharField(_('domaine'), max_length=20, choices=DOMAINE_CHOICES, default='web')
    niveau = models.CharField(_('niveau'), max_length=50, choices=NIVEAUX_CHOICES)
    public_cible = models.CharField(
        _('public cible'),
        max_length=10,
        choices=PUBLIC_CIBLE_CHOICES,
        default='fac',
        help_text=_('Utilisé pour classer les cours algo : Lycée (bac) ou Fac (ASD)'),
    )
    est_publie = models.BooleanField(_('est publié'), default=False)
    date_creation = models.DateTimeField(_('date de création'), auto_now_add=True)
    date_mise_a_jour = models.DateTimeField(_('date de mise à jour'), auto_now=True)
    enseignant = models.ForeignKey(
        Utilisateur, 
        on_delete=models.CASCADE, 
        related_name='cours_enseignes',
        limit_choices_to={'is_enseignant': True}
    )

    class Meta:
        verbose_name = _('cours')
        verbose_name_plural = _('cours')
        ordering = ['-date_creation']

    def __str__(self):
        return self.titre

class Module(models.Model):
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE, related_name='modules')
    titre = models.CharField(_('titre'), max_length=200)
    description = models.TextField(_('description'), blank=True)
    ordre = models.PositiveIntegerField(_('ordre'))

    class Meta:
        verbose_name = _('module')
        verbose_name_plural = _('modules')
        ordering = ['ordre']

    def __str__(self):
        return f"{self.cours.titre} - {self.titre}"

class Lecon(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lecons')
    titre = models.CharField(_('titre'), max_length=200)
    contenu_html = models.TextField(_('contenu HTML'))
    ordre = models.PositiveIntegerField(_('ordre'))
    fichier_video = models.FileField(_('fichier vidéo'), upload_to='videos_lecons/', blank=True, null=True)
    fichier_pdf = models.FileField(_('fichier PDF'), upload_to='pdf_lecons/', blank=True, null=True)

    class Meta:
        verbose_name = _('leçon')
        verbose_name_plural = _('leçons')
        ordering = ['ordre']

    def __str__(self):
        return f"{self.module.cours.titre} - {self.module.titre} - {self.titre}"

# ==============================
# Suivi et progressions de l'étudiant
# ==============================

class ProgressEtudiant(models.Model):
    etudiant = models.ForeignKey(
        Utilisateur, 
        on_delete=models.CASCADE, 
        related_name='progressions',
        limit_choices_to={'is_enseignant': False}
    )
    lecon = models.ForeignKey(Lecon, on_delete=models.CASCADE, related_name='progressions_etudiants')
    est_terminee = models.BooleanField(_('est terminée'), default=False)
    date_terminee = models.DateTimeField(_('date terminée'), null=True, blank=True)
    temps_passe = models.PositiveIntegerField(_('temps passé (secondes)'), default=0)

    class Meta:
        verbose_name = _('progression de l\'étudiant')
        verbose_name_plural = _('progressions des étudiants')
        unique_together = ('etudiant', 'lecon')

    def __str__(self):
        return f"{self.etudiant.email} - {self.lecon.titre}"

# ==============================
# Liste de lecture / Favoris
# ==============================

class ListeLecture(models.Model):
    etudiant = models.ForeignKey(
        Utilisateur, 
        on_delete=models.CASCADE, 
        related_name='listes_lecture',
        limit_choices_to={'is_enseignant': False}
    )
    titre = models.CharField(_('titre'), max_length=200)
    description = models.TextField(_('description'), blank=True)
    cours = models.ManyToManyField(Cours, related_name='listes_lecture')
    est_publique = models.BooleanField(_('est publique'), default=False)
    date_creation = models.DateTimeField(_('date de création'), auto_now_add=True)

    class Meta:
        verbose_name = _('liste de lecture')
        verbose_name_plural = _('listes de lecture')

    def __str__(self):
        return f"{self.etudiant.email} - {self.titre}"