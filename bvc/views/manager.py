from itertools import chain

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.contrib.admin.views.decorators import staff_member_required

from .. import models


@require_http_methods(["POST"])
@staff_member_required
def place_grouped_command(request):
    # Check if any grouped command was already placed
    placed_grouped_cmd = models.command.GroupedCommand.objects.filter(
        state=models.command.PLACED_STATE
    )
    if placed_grouped_cmd.count():
        messages.error(
            request,
            'Une commande groupée est déjà en cours. Opération annulée.'
        )

        return redirect('admin:index')

    models.command.IndividualCommand.cancel_old_commands()
    command = models.command.GroupedCommand()
    command.next(models.command.GroupedCommand.get_amount_to_place())

    messages.success(request, 'Votre command a bien été passée.')

    return redirect('admin:index')
