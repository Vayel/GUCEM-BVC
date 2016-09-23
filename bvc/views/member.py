from django.shortcuts import render

def home(request):
    return render(request, 'bvc/home.html')

def command_commission(request):
    return render(request, 'bvc/command_commission.html')

def command_member(request):
    return render(request, 'bvc/command_member.html')
