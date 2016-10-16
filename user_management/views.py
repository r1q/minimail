from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.models import User
from user_management.forms import UserForm, UserExtendForm, RegisterForm, LoginForm
from user_management.models import UserExtend
from django.contrib.auth import authenticate, login


class UserUpdateView(View):
    """
    Update View for user info data.
    """

    @method_decorator(login_required)
    def get(self, request):
        user = User.objects.get(pk=request.user.id)
        user_extend = None
        try:
            user_extend = UserExtend.objects.get(user=user)
        except:
            user_extend = UserExtend(user=user)
            user_extend.save()
        form_user = UserForm(instance=user)
        form_user_extend = UserExtendForm(instance=user_extend)
        return render(request, "user_management/user_update.html", locals())

    @method_decorator(login_required)
    def post(self, request):
        user = User.objects.get(pk=request.user.id)
        user_extend = None
        try:
            user_extend = UserExtend.objects.get(user=user)
        except:
            user_extend = UserExtend(user=user)
            user_extend.save()
        form_user = UserForm(request.POST, instance=user)
        form_user_extend = UserExtendForm(request.POST, instance=user_extend)
        if form_user.is_valid() and form_user_extend.is_valid():
            form_user.save()
            form_user_extend.save()
        return render(request, "user_management/user_update.html", locals())

class Register(View):

    def get(self, request):
        form = RegisterForm()
        return render(request, "user_management/user_register.html", locals())

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            pwd = form.cleaned_data.get('password')
            User.objects.create_user(email, email, pwd)
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
                return redirect('/')
        return render(request, "user_management/user_login.html", locals())
