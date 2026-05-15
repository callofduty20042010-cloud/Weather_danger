from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash, get_user_model
from .forms import *
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib.auth.models import Group

User = get_user_model()

@login_required
def home(request):
    return render(request, 'base_layout.html')

def sign_up(request):
   form = SignUpForm(request.POST or None)
   if request.method == "POST" and form.is_valid():
       form.save()
       return redirect('users:sign_in')
   return render(request, 'sign_up.html', {'form': form})


def sign_in(request):
    form = SignInForm(data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect('index')
    return render(request, 'sign_in.html', {'form': form})
    
def sign_out(request):
   logout(request)
   return redirect('index')
