from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
from django.utils.timezone import now

from .. import forms
from .. import utils
from .. import models

def list_grouped_commands(request):
    # TODO: use model formset
    
    context = {
        'placed_commands': models.command.GroupedCommand.objects.filter(
            state=models.command.PLACED_STATE,
        ),
        'received_commands': models.command.GroupedCommand.objects.filter(
            state=models.command.GroupedCommand.RECEIVED_STATE,
        ),
        'prepared_commands': models.command.GroupedCommand.objects.filter(
            state=models.command.PREPARED_STATE,
        ),
        'receive_form': forms.command.ReceiveGroupedCommand(),
        'prepare_form': forms.command.PrepareGroupedCommand(),
    }

    return render(request, 'bvc/list_grouped_commands.html', context)

@require_http_methods(["POST"])
def receive_grouped_command(request, pk):
    command = get_object_or_404(models.command.GroupedCommand, pk=pk)
    form = forms.command.ReceiveGroupedCommand(request.POST, instance=command)

    if form.is_valid():
        form.save()
        command.datetime_received = now()
        command.state = models.command.GroupedCommand.RECEIVED_STATE
        command.save()

        send_mail(
            utils.format_mail_subject('Commande groupée reçue'),
            render_to_string(
                'bvc/mails/receive_grouped_command.txt',
                {'pk': pk}
            ),
            settings.TREASURER_MAIL,
            [settings.BVC_MANAGER_MAIL],
            fail_silently=False,
        )

    return redirect('bvc:list_grouped_commands')

@require_http_methods(["POST"])
def prepare_grouped_command(request, pk):
    return redirect('bvc:list_grouped_commands')

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
        form = forms.command.PlaceGroupedCommand(request.POST) 

    context['form'] = form

    return render(request, 'bvc/place_grouped_command.html', context)
