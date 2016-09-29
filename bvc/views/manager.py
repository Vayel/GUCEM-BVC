from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

from .. import forms
from .. import utils

def place_grouped_command(request):
    context = {}

    if request.method == 'POST':
        form = forms.command.PlaceGroupedCommand(request.POST)

        if form.is_valid():
            form.save()
            send_mail(
                utils.format_mail_subject('Commande groupée'),
                render_to_string(
                    'bvc/mails/place_grouped_command.txt',
                    {'amount': form.cleaned_data['placed_amount']}
                ),
                settings.BVC_MANAGER_MAIL,
                [settings.TREASURER_MAIL],
                fail_silently=False,
            )
            messages.success(request, 'Votre command a bien été passée.')

            return redirect('bvc:place_grouped_command')
    else:
        form = forms.command.PlaceGroupedCommand() 

    context['form'] = form

    return render(request, 'bvc/place_grouped_command.html', context)
