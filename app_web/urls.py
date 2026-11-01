from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'app_web'

urlpatterns = [
    # Pages publiques
    path('', views.page_accueil, name='accueil'),
    
    # Pages d'authentification
    path('connexion/', views.page_connexion, name='connexion'),
    path('deconnexion/', views.page_deconnexion, name='deconnexion'),
    path('inscription/', views.page_inscription, name='inscription'),
    
    # Pages du profil
    path('profil/', views.page_profil, name='profil'),
    path('profil/modifier/', views.page_modifier_profil, name='modifier_profil'),
    
    # Pages du cours
    path('developpement/', views.page_cours_web_mobile, name='liste_cours'),
    path('developpement/web/', views.page_cours_domaine, kwargs={'domaine': 'web'}, name='cours_web'),
    path('developpement/mobile/', views.page_cours_domaine, kwargs={'domaine': 'mobile'}, name='cours_mobile'),
    path('developpement/android/', views.page_cours_domaine, kwargs={'domaine': 'android'}, name='cours_android'),
    # Redirections des anciennes URLs « cours » vers « developpement » (avant les routes <slug>)
    path('cours/', RedirectView.as_view(url='/developpement/', permanent=False), name='redirection_cours'),
    path('cours/web/', RedirectView.as_view(url='/developpement/web/', permanent=False), name='redirection_cours_web'),
    path('cours/mobile/', RedirectView.as_view(url='/developpement/mobile/', permanent=False), name='redirection_cours_mobile'),
    # Redirections POO1/POO2 -> cours POO fusionné
    path('cours/poo1/', RedirectView.as_view(url='/cours/poo/', permanent=False), name='redirection_poo1'),
    path('cours/poo2/', RedirectView.as_view(url='/cours/poo/', permanent=False), name='redirection_poo2'),
    path('cours/nouveau/', views.page_creation_cours, name='creation_cours'),
    path('cours/<slug:slug>/', views.DetailCoursView.as_view(), name='detail_cours'),
    path('lecons/<int:pk>/', views.page_detail_lecon, name='detail_lecon'),
    
    # Pages de gestion du cours (enseignant seulement)
    path('cours/<slug:slug>/modifier/', views.page_modifier_cours, name='modifier_cours'),
    path('cours/<slug:slug>/supprimer/', views.page_supprimer_cours, name='supprimer_cours'),
]