from django.forms import ModelForm
from django.contrib.auth.models import User
from django import forms
from user_management.models import UserExtend, TIMEZONES

class UserForm(ModelForm):
    class Meta:
        model = User
        localized_fields = ('email','first_name', 'last_name',)
        fields = ('email','first_name', 'last_name',)

    email = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), disabled=True)
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))


class UserExtendForm(ModelForm):
    class Meta:
        model = UserExtend
        localized_fields = ('timezone',)
        fields = ('timezone',)
    timezone = forms.ChoiceField(choices = TIMEZONES, widget=forms.Select(attrs={'class':'form-control'}), required=True)
