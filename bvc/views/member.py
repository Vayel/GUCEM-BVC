from django.shortcuts import render, redirect
from django.contrib import messages

from .. import forms

def home(request):
    return render(request, 'bvc/home.html')

def place_commission_command(request):
    return render(request, 'bvc/place_commission_command.html')

def place_member_command(request):
    context = {}

    if request.method == 'POST':
        form = forms.command.PlaceMemberCommand(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Votre command a bien été passée.')
            return redirect('bvc:place_member_command')
    else:
        form = forms.command.PlaceMemberCommand() 

    context['form'] = form

    return render(request, 'bvc/place_member_command.html', context)
