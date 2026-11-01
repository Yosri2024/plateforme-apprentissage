from django.contrib.auth.backends import ModelBackend

from .models import Utilisateur


class BackendEmailTelephone(ModelBackend):
    """Connexion par e-mail OU par numéro de téléphone (mobile tunisien).

    Ancré avant ModelBackend : l'identifiant peut être un e-mail
    (casse indifférente, espaces ignorés) ou un téléphone à 8 chiffres.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # Compat : identifiant / email / téléphone passés directement,
        # y compris par django.test Client.login(...)
        identifiant = (
            username
            or kwargs.get('identifiant')
            or kwargs.get('email')
            or kwargs.get('telephone')
        )
        if not identifiant or not password:
            return None

        identifiant = str(identifiant).strip().lower().replace(' ', '')

        utilisateur = (
            Utilisateur.objects.filter(email__iexact=identifiant).first()
            or Utilisateur.objects.filter(telephone=identifiant).first()
        )
        if utilisateur and utilisateur.check_password(password) and self.user_can_authenticate(utilisateur):
            return utilisateur
        return None
