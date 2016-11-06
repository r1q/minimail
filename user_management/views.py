from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
#from django.contrib.auth.models import User
from user_management.forms import UserForm, RegisterForm, LoginForm
from user_management.models import MyUser
from django.contrib.auth import authenticate, login


class UserUpdateView(View):
    """
    Update View for user info data.
    """

    @method_decorator(login_required)
    def get(self, request):
        user = MyUser.objects.get(pk=request.user.id)
        form_user = UserForm(instance=user)
        return render(request, "user_management/user_update.html", locals())

    @method_decorator(login_required)
    def post(self, request):
        user = MyUser.objects.get(pk=request.user.id)
        form_user = UserForm(request.POST, instance=user)
        if form_user.is_valid():
            form_user.save()
        return render(request, "user_management/user_update.html", locals())

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
