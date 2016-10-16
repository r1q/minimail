from django.forms import ModelForm, forms
from django.contrib.auth.models import User
from django import forms
from user_management.models import UserExtend, TIMEZONES
from django.utils.translation import ugettext as _

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

class RegisterForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    password_confirm = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()
        pwd = cleaned_data.get("password")
        pwdc = cleaned_data.get("password_confirm")
        email = cleaned_data.get("email")

        if User.objects.filter(email=email).count() != 0:
            self.add_error('email', _('this user already exists'))

        if pwd != pwdc:
            msg = _("Mismatch passwords")
            self.add_error('password_confirm', msg)

class LoginForm(forms.Form):
    email = forms.CharField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
