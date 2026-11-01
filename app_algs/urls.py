from django.urls import path
from . import views

app_name = 'app_algs'

urlpatterns = [
    # Pages publiques
    path('', views.page_accueil_algos, name='accueil'),
    path('cours/lycee/', views.page_cours_public, kwargs={'public': 'lycee'}, name='cours_lycee'),
    path('cours/fac/', views.page_cours_public, kwargs={'public': 'fac'}, name='cours_fac'),
    
    # Pages des problèmes
    path('problemes/', views.ListeProblemesView.as_view(), name='liste_problemes'),
    path('problemes/<int:pk>/', views.DetailProblemeView.as_view(), name='detail_probleme'),
    
    # Pages de résolution
    path('problemes/<int:pk>/resoudre/', views.page_resoudre_probleme, name='resoudre_probleme'),
    
    # Pages des collections
    path('collections/', views.page_mes_collections, name='liste_collections'),
    path('collections/nouvelle/', views.page_creer_collection, name='creer_collection'),
    path('collections/<int:pk>/', views.page_detail_collection, name='detail_collection'),
]