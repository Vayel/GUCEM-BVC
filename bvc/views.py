import os.path
import logging
from smtplib import SMTPException
from itertools import chain

import django.db.models
from django.db.models.functions import Lower
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings

import pdfkit

from . import models
from . import forms
from . import utils

logger = logging.getLogger(__name__)


# Manager

@staff_member_required
def print_prepared_commands(request):
    PDF_NAME = 'commandes.pdf'
    PDF_PATH = os.path.join(settings.BASE_DIR, PDF_NAME)

    context = {
        'member_commands': models.MemberCommand.objects.filter(
            state=models.command.PREPARED_STATE
        ).order_by(Lower('member__user__last_name'), Lower('member__user__first_name')),
        'commission_commands': models.CommissionCommand.objects.filter(
            state=models.command.PREPARED_STATE
        ).order_by(Lower('commission__user__username')),
    }

    try:
        pdfkit.from_string(render_to_string('bvc/print_prepared_commands.html', context), PDF_PATH)
        with open(PDF_PATH, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="{0}"'.format(PDF_NAME)
            return response
    except:
        pass

    return render(request, 'bvc/print_prepared_commands.html', context)


@staff_member_required
@require_http_methods(["POST"])
def contact_unsold_commands(request):
    commands = models.MemberCommand.objects.filter(
        state=models.command.PREPARED_STATE
    )

    for cmd in commands:
        cmd.warn_about_cancellation()

    messages.success(
        request,
        'Les commandes non vendues ont reçu un mail de rappel.'
    )
    return redirect('bvcadmin:index')


# Users

@require_http_methods(["POST"])
def subscribe_to_reminder(request):
    form = forms.user.GroupedCommandReminder(request.POST)

    if form.is_valid():
        try:
            user = User.objects.get(email=form.cleaned_data['email'])
        except ObjectDoesNotExist:
            user = form.save()
            user.username = user.email
            user.last_name = 'Inconnu'
            user.first_name = 'Inconnu'
            user.save()

            # If the user does not exist, it is necessary a member, not a commission
            club_user = models.Member(
                user=user,
                license='',
            )
        else:
            try:
                club_user = models.user.Member.objects.get(user=user)
            except ObjectDoesNotExist:
                try:
                    club_user = models.user.Commission.objects.get(user=user)
                except ObjectDoesNotExist:
                    # The user exists but not the club user
                    club_user = models.Member(
                        user=user,
                        license='',
                    )

        club_user.receive_reminder = not club_user.receive_reminder
        club_user.save()

        if club_user.receive_reminder:
            msg = ("Tu recevras un rappel par mail à l'approche de la date "
                   "limite de commande.")
        else:
            msg = ("Tu ne recevras plus de rappel par mail à l'approche de "
                   "la date limite de commande.")
        messages.success(request, msg)
    else:
        messages.error(request, 'Merci de fournir une adresse mail.')

    return redirect('bvc:home')


@require_http_methods(["POST"])
def send_command_summary(request):
    form = forms.user.CommandSummary(request.POST)

    if form.is_valid():
        try:
            user = User.objects.get(email=form.cleaned_data['email'])
        except ObjectDoesNotExist:
            club_user = None
        else:
            try:
                club_user = models.user.Member.objects.get(user=user)
            except ObjectDoesNotExist:
                try:
                    club_user = models.user.Commission.objects.get(user=user)
                except ObjectDoesNotExist:
                    club_user = None

        try:
            club_user.send_command_summary()
        except AttributeError:
            messages.error(request, 'Tu ne sembles pas avoir déjà passé commande.')
        except SMTPException:
            logger.exception('Cannot send command summary mail.')
            messages.error(request, "L'envoi du mail a échoué.")
        else:
            messages.success(request, 'Ta demande a bien été prise en compte, '
                                      "un mail t'a été envoyé.")
    else:
        messages.error(request, 'Merci de fournir une adresse mail.')

    return redirect('bvc:home')


def place_commission_command(request):
    context = {}

    if request.method == 'POST':
        form = forms.commission_command.PlaceCommissionCommand(request.POST)

        if form.is_valid():
            cmd = form.save()

            try:
                cmd.commission.send_command_summary()
            except SMTPException:
                logger.exception('Cannot send command summary mail after commission command.')
                messages.error(request, "Ta commande a bien été passée mais "
                                        "l'envoi du mail a provoqué une erreur.")
            else:
                messages.success(request, 'Ta commande a bien été '
                                          "passée. Un mail t'a été envoyé.")

            return redirect('bvc:place_commission_command')
    else:
        form = forms.commission_command.PlaceCommissionCommand()

    context['form'] = form

    return render(request, 'bvc/place_commission_command.html', context)


def home(request):
    context = {}

    if request.method == 'POST':
        user_form = forms.user.MemberUserCommand(request.POST)
        member_form = forms.user.MemberCommand(request.POST)
        command_form = forms.member_command.PlaceMemberCommand(request.POST)

        if user_form.is_valid():
            try:
                user = User.objects.get(email=user_form.cleaned_data['email'])
                user_form = forms.user.MemberUserCommand(request.POST, instance=user)
            except ObjectDoesNotExist:
                pass

            user = user_form.save(commit=False)
            user.username = user.email
            user.save()

            try:
                member = models.user.Member.objects.get(user=user)
                member_form = forms.user.MemberCommand(request.POST, instance=member)
            except ObjectDoesNotExist:
                pass

            if member_form.is_valid():
                member = member_form.save(commit=False)
                member.user = user
                member.save()

                if command_form.is_valid():
                    command = command_form.save(commit=False)
                    command.member = member
                    command.save()

                    try:
                        member.send_command_summary()
                    except SMTPException:
                        logger.exception('Cannot send command summary mail after member command.')
                        messages.error(request, "Ta commande a bien été passée mais "
                                                "l'envoi du mail a provoqué une erreur.")
                    else:
                        messages.success(request, 'Ta commande a bien été '
                                                  "passée. Un mail t'a été envoyé.")

                    return redirect('bvc:home')
    else:
        user_form = forms.user.MemberUserCommand()
        member_form = forms.user.MemberCommand()
        command_form = forms.member_command.PlaceMemberCommand()

    context['user_form'] = user_form
    context['member_form'] = member_form
    context['command_form'] = command_form
    context['command_summary_form'] = forms.user.CommandSummary()
    context['grouped_cmd_reminder_form'] = forms.user.GroupedCommandReminder()
    context['grouped_command_day'] = models.get_config().grouped_command_day
    context['last_day_to_command'] = models.get_config().grouped_command_day - 1
    context['esmug_discount'] = models.get_config().esmug_percentage_discount 
    context['gucem_discount'] = models.get_config().gucem_percentage_discount 
    context['bvc_manager_mail'] = models.get_config().bvc_manager_mail

    return render(request, 'bvc/home.html', context)
