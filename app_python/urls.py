from django.urls import path
from . import views

app_name = 'app_python'

urlpatterns = [
    # Pages publiques
    path('', views.page_accueil_python, name='accueil'),
    
    # Pages des exercices
    path('exercices/', views.ListeExercicesView.as_view(), name='liste_exercices'),
    path('exercices/<int:pk>/', views.DetailExerciceView.as_view(), name='detail_exercice'),
    
    # Pages de résolution
    path('exercices/<int:pk>/resoudre/', views.page_resoudre_exercice, name='resoudre_exercice'),
    
    # Pages des collections
    path('collections/', views.page_mes_collections, name='liste_collections'),
    path('collections/nouvelle/', views.page_creer_collection, name='creer_collection'),
    path('collections/<int:pk>/', views.page_detail_collection, name='detail_collection'),
]