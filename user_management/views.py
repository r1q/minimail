from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.core.mail import send_mail
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth import authenticate, login

from user_management.forms import UserForm, RegisterForm, LoginForm, \
        UpdatePasswordForm, ForgottenForm, RecoveryForm
from user_management.models import MyUser
from subscriber_management.forms import ListForm
from subscriber_management.models import List

import uuid as UUID


RECOVERY_EMAIL = _("""
Click this link to recover your account:
{}


— Sent with Minimail
""")


def homepage(request):
    if request.user and request.user.is_authenticated():
        create_list_form = ListForm()
        if request.user.has_a_list:
            try:
                email_list = List.objects.filter(user=request.user)\
                                         .latest('created')
            except Exception as ex:
                print(ex)
        if request.GET.get('skip-step-2'):
            request.user.has_passed_subscribers_import_step = True
            request.user.save()
            return redirect('/')
    return render(request, "index.html", locals())


def _send_recovery_email(user):
    send_mail(
        _("Minimail account recovery"), # Subject
        RECOVERY_EMAIL.format(user.recovery_link()), # Text email
        'hi@fullweb.io', # From: email
        [user.email], # To:
        fail_silently=False,
    )


def logout_view(request):
    logout(request)
    return redirect('/')


class UserUpdateView(View):
    """
    Update View for user info data.
    """

    @method_decorator(login_required)
    def get(self, request):
        user = MyUser.objects.get(pk=request.user.id)
        form_user = UserForm(instance=user)
        form_password = UpdatePasswordForm(None)
        return render(request, "user_management/user_update.html", locals())

    @method_decorator(login_required)
    def post(self, request):
        user = MyUser.objects.get(pk=request.user.id)
        form_user = UserForm(request.POST, instance=user)
        form_password = UpdatePasswordForm(None)
        if form_user.is_valid():
            form_user.save()
            messages.success(request, _("User successfully updated"))
            redirect("user_account")
        return render(request, "user_management/user_update.html", locals())


class UpdatePasswordView(View):

    @method_decorator(login_required)
    def post(self, request):
        user = request.user
        form_user = UserForm(instance=user)
        form_password = UpdatePasswordForm(user, request.POST)
        if form_password.is_valid():
            messages.success(request, _("Password successfully updated"))
            return redirect('user_account')
        return render(request, "user_management/user_update.html", locals())


class Forgotten(View):

    def get(self, request):
        form = ForgottenForm()
        return render(request, "user_management/user_forgotten_password.html", locals())

    def post(self, request):
        form = ForgottenForm(request.POST)
        if form.is_valid():
            try:
                user = MyUser.objects.get(email=form.cleaned_data['email'])
                user.recover_id = UUID.uuid4()
                _send_recovery_email(user)
                user.save()
            except Exception as err:
                print("send recovery email error", err)
                messages.error(request, _("Send recovery mail error."))
                return redirect('user_forgotten')
            else:
                messages.success(request, _("An email has been sent to {}".format(user.email)))
                return redirect('user_forgotten')
        return render(request, "user_management/user_forgotten_password.html", locals())


class Recovery(View):

    def get(self, request, uuid):
        form = RecoveryForm()
        try:
            user = MyUser.objects.get(recover_id=uuid)
        except Exception:
            messages.error(request, _("Your recovery link is invalid."))
        return render(request, "user_management/user_recovery.html", locals())

    def post(self, request, uuid):
        form = RecoveryForm(request.POST)
        try:
            user = MyUser.objects.get(recover_id=uuid)
        except:
            messages.error(request, _("Recovery token invalid"))
            return render(request, "user_management/user_recovery.html", locals())
        else:
            if form.is_valid():
                user.set_password(form.cleaned_data['password1'])
                user.recover_id = ''
                user.save()
                messages.success(request, _("Your password have been reset."))
                return redirect('user_login')
            return render(request, "user_management/user_recovery.html", locals())


class Register(View):

    def get(self, request):
        form = RegisterForm()
        return render(request, "user_management/user_register.html", locals())

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            full_name = form.cleaned_data.get('full_name')
            pwd = form.cleaned_data.get('password')
            MyUser.objects.create_user(full_name, email, pwd)
            messages.success(request, _("User successfully registered"))
            return redirect('user_login')
        return render(request, "user_management/user_register.html", locals())


class Login(View):

    def get(self, request):
        form = LoginForm()
        return render(request, "user_management/user_login.html", locals())

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            pwd = form.cleaned_data.get('password')
            user = authenticate(email=email, password=pwd)
            if user is None:
                messages.error(request, _("Email or password invalid"))
            else:
                login(request, user)
                if request.GET.get('next', '') == '':
                    return redirect('/')
                else:
                    return redirect(request.GET['next'])
        return render(request, "user_management/user_login.html", locals())
