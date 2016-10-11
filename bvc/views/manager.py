from itertools import chain

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
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
    command = get_object_or_404(models.command.GroupedCommand, pk=pk)
    form = forms.command.PrepareGroupedCommand(request.POST, instance=command)

    if form.is_valid():
        form.save()
        command.datetime_prepared = now()
        command.state = models.command.PREPARED_STATE
        command.save()
        
        # Fill stock
        try:
            stock = models.voucher.Operation.objects.latest('id').stock
        except ObjectDoesNotExist:
            stock = 0

        stock += command.prepared_amount

        operation = models.voucher.Operation(
            command_type=models.voucher.Operation.GROUPED_COMMAND,
            command_id=command.id, 
            stock=stock,
        )
        operation.save()

        # Prepare individual commands
        commission_commands = models.command.CommissionCommand.objects.filter(
            state=models.command.PLACED_STATE,
        ).order_by('datetime_placed')
        member_commands = models.command.MemberCommand.objects.filter(
            state=models.command.PLACED_STATE,
        ).order_by('datetime_placed')

        for cmd in chain(commission_commands, member_commands):
            email = utils.get_cmd_email(cmd)

            # Not enough vouchers to prepare current command
            if stock - cmd.amount < settings.VOUCHER_STOCK_MIN:
                send_mail(
                    utils.format_mail_subject('Commande indisponible'),
                    render_to_string(
                        'bvc/mails/command_unprepared.txt',
                        {'amount': cmd.amount,}
                    ),
                    settings.BVC_MANAGER_MAIL,
                    [email],
                    fail_silently=False,
                )

                # Try to prepare smaller commands
                continue

            # Prepare command
            cmd.state = models.command.PREPARED_STATE
            cmd.datetime_prepared = now()
            cmd.save()

            send_mail(
                utils.format_mail_subject('Commande reçue'),
                render_to_string(
                    'bvc/mails/command_prepared.txt',
                    {
                        'amount': cmd.amount,
                        'price': utils.get_cmd_price(cmd),
                    }
                ),
                settings.BVC_MANAGER_MAIL,
                [email],
                fail_silently=False,
            )

            # Update stock
            stock -= cmd.amount

            if isinstance(cmd, models.command.CommissionCommand):
                command_type = models.voucher.Operation.COMMISSION_COMMAND
            elif isinstance(cmd, models.command.MemberCommand):
                command_type = models.voucher.Operation.MEMBER_COMMAND

            operation = models.voucher.Operation(
                command_type=command_type,
                command_id=cmd.id, 
                stock=stock,
            )
            operation.save()

    return redirect('bvc:list_grouped_commands')

def place_grouped_command(request):
    # TODO: no form + determine cancelled commands
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
