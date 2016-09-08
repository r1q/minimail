from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.models import User
from user_management.forms import UserForm, UserExtendForm
from user_management.models import UserExtend


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
