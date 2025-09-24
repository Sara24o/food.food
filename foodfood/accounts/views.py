from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import SignupForm, CustomerProfileForm
from .models import Customer


def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            # create empty customer profile
            Customer.objects.create(user=user)
            login(request, user)
            messages.success(request, "Bienvenue ! Votre compte a été créé.")
            return redirect('/restaurants/')
    else:
        form = SignupForm()
    return render(request, 'accounts/signup.html', {"form": form})


@login_required
def profile_view(request):
    customer, _ = Customer.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = CustomerProfileForm(request.POST, instance=customer, user=request.user)
        if form.is_valid():
            customer = form.save()
            # update basic user fields
            request.user.first_name = form.cleaned_data.get('first_name')
            request.user.last_name = form.cleaned_data.get('last_name')
            email = form.cleaned_data.get('email')
            if email:
                request.user.email = email
            request.user.save()
            messages.success(request, "Profil mis à jour.")
            return redirect('/accounts/profile/')
    else:
        form = CustomerProfileForm(instance=customer, user=request.user)
    return render(request, 'accounts/profile.html', {"form": form})

# Create your views here.
