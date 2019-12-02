from django import forms


class OffForm(forms.Form):
    nom = forms.CharField(max_length=100, label='', widget=forms.TextInput(attrs={'size': '25', 'placeholder': 'Rechercher un produit'}))


class LoginForm(forms.Form):
    username = forms.CharField(label="Nom d'utilisateur", max_length=30)
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)


class RegistrationForm(forms.Form):
    pseudo = forms.CharField(label="Nom d'utilisateur", max_length=30, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput(), required=True)



