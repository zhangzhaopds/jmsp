from django.shortcuts import render

# Create your views here.

def index(request):
    return render(request, 'ipa/index.html', {'user': '大王'})

def login(request):
    return render(request, 'ipa/login.html')

def register(request):
    return render(request, 'ipa/register.html')