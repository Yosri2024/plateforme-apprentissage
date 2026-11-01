from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Utilisateur, Cours

class FormulaireInscription(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Requis. Fournissez un email valide.')
    telephone = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': '+1234567890'}))
    date_naissance = forms.DateField(required=False, widget=forms.SelectDateWidget(years=range(1900, 2026)))
    bio = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Un peu à propos de vous...'}))
    photo_profil = forms.ImageField(required=False)
    is_enseignant = forms.BooleanField(required=False, label='Je souhaite enseigner cette matière', help_text='Cochez si vous voulez créer et gérer des cours')
    
    class Meta:
        model = Utilisateur
        fields = ('email', 'telephone', 'date_naissance', 'bio', 'photo_profil', 'is_enseignant')
    
    def save(self, commit=True):
        utilisateur = super().save(commit=False)
        utilisateur.set_password(self.cleaned_data['mot_de_passe'])
        if commit:
            utilisateur.save()
        return utilisateur

class FormulaireConnexion(forms.Form):
    email = forms.EmailField(label='Adresse e-mail')
    mot_de_passe = forms.CharField(label='Mot de passe', widget=forms.PasswordInput)
    
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        mot_de_passe = cleaned_data.get('mot_de_passe')
        
        if email and mot_de_passe:
            try:
                utilisateur = Utilisateur.objects.get(email=email)
                if not utilisateur.check_password(mot_de_passe):
                    raise forms.ValidationError('Email ou mot de passe invalide.')
            except Utilisateur.DoesNotExist:
                raise forms.ValidationError('Email ou mot de passe invalide.')
        
        return cleaned_data

class FormulaireProfil(forms.ModelForm):
    class Meta:
        model = Utilisateur
        fields = ('telephone', 'date_naissance', 'bio', 'photo_profil')

class FormulaireCours(forms.ModelForm):
    class Meta:
        model = Cours
        fields = ('titre', 'description', 'niveau', 'est_publie', 'image_couverture')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6}),
        }