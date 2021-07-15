from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.template import context
from .forms import SignUpForm, ProfileForm
from django.contrib.auth import login as auth_login 
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import UpdateView
from django.urls import reverse_lazy

# Create your views here.

def signup(request):
    form = SignUpForm(request.POST)
    if form.is_valid():
        user = form.save()
        auth_login(request, user)
        return redirect('home')
    return render(request, 'signup.html', {'form': form})


@login_required
def user_update_view(request):
    user = request.user
    form = ProfileForm(instance = user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('my_account')

    context = {'form':form}
    return render(request, 'my_account.html',context)
    