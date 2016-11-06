from django.forms import ModelForm, forms
from django.contrib.auth.models import User
from django import forms
from user_management.models import MyUser
from django.utils.translation import ugettext as _

class UserForm(ModelForm):
    class Meta:
        model = MyUser
        localized_fields = ('full_name','email',)
        fields = ('full_name','email',)

    email = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), disabled=True)
    full_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))

class RegisterForm(forms.Form):
    full_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    password_confirm = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()
        pwd = cleaned_data.get("password")
        pwdc = cleaned_data.get("password_confirm")
        email = cleaned_data.get("email")
        full_name = cleaned_data.get("full_name")

        if MyUser.objects.filter(email=email).count() != 0:
            self.add_error('email', _('this user already exists'))

        if pwd != pwdc:
            msg = _("Mismatch passwords")
            self.add_error('password_confirm', msg)

class LoginForm(forms.Form):
    email = forms.CharField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
