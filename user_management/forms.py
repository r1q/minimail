from django.forms import ModelForm, forms
from django import forms
from user_management.models import MyUser
from django.utils.translation import ugettext as _
from django.contrib.auth.password_validation import validate_password

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


class UpdatePasswordForm(forms.Form):
    old_password = forms.CharField(required=True, label=_("Current password"))
    password1 = forms.CharField(required=True, label=_("New password"))
    password2 = forms.CharField(required=True, label=_("New password confirm"))

    def __init__(self, user, *args, **kwargs):
        super(UpdatePasswordForm, self).__init__(*args, **kwargs)
        self.user = user

    def clean_old_password(self):
        password = self.cleaned_data.get('old_password', None)
        if not self.user.check_password(password):
            raise forms.ValidationError(_('Invalid password'))

    def clean_password1(self):
        password = self.cleaned_data.get('password1', None)
        validate_password(password)
        return password

    def clean_password2(self):
        password = self.cleaned_data.get('password2', None)
        validate_password(password)
        return password

    def clean(self):
        cleaned_data = super(UpdatePasswordForm, self).clean()
        pwd1 = cleaned_data.get("password1")
        pwd2 = cleaned_data.get("password2")

        if pwd2 != pwd1:
            self.add_error('password2', _("Passwords mismatch"))
            return cleaned_data

        self.user.set_password(pwd1)
        self.user.save()
        return cleaned_data
