from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse


class RestreindreAdminMiddleware:
    """
    Réserve l'administration (/admin/) au super-utilisateur uniquement.
    Les utilisateurs connectés ne pouvant pas être administrateurs (étudiants,
    enseignants simples) sont renvoyés vers l'accueil avec un message.
    Les visiteurs non connectés passent : la page de connexion administrative
    doit rester consultable.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        chemin = request.path
        if chemin.startswith('/admin/'):
            if chemin.startswith('/admin/login') or chemin.startswith('/admin/logout'):
                return self.get_response(request)
            utilisateur = request.user
            if utilisateur.is_authenticated and not utilisateur.is_superuser:
                messages.error(request, "L'administration est réservée à l'administrateur de la plateforme.")
                return redirect('app_web:accueil')
        return self.get_response(request)
