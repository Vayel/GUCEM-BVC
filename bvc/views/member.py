from django.shortcuts import render, redirect
from django.contrib import messages

from .. import forms

def home(request):
    return render(request, 'bvc/home.html')

def command_commission(request):
    return render(request, 'bvc/command_commission.html')

def command_member(request):
    context = {}

    if request.method == 'POST':
        form = forms.command.PlaceMemberCommand(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Votre command a bien été passée.')
            return redirect('bvc:command_member')
    else:
        form = forms.command.PlaceMemberCommand() 

    context['form'] = form

    return render(request, 'bvc/command_member.html', context)
