from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        return redirect('home')
    return render(request, 'registration/register.html')