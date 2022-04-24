from django import forms 
from .models import Profile
from django.forms import ModelForm, TextInput, EmailInput, widgets

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = (
            "name",
            "persona",
            "appearance",
            "image"
        )
        widgets = {
            "name": widgets.TextInput(
                attrs={"class": "name-input", "placeholder": "What do I call you?"}
            ),
            "persona": widgets.Textarea(
                attrs={"class": "persona-input", "placeholder": "Describe your personality and motivation"}
            ),
            "appearance": widgets.Textarea(
                attrs={"class": "persona-input", "placeholder": "Describe your physical appearance"}
            ),
            "image": widgets.ClearableFileInput(
                attrs={"class": "avatar-input", "id":"imageUpload"})
        }
