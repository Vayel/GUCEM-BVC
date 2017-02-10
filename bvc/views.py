import django.db.models
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings

from . import models
from . import forms
from . import utils


# Manager

@staff_member_required
@require_http_methods(["POST"])
def contact_unsold_commands(request):
    commands = models.MemberCommand.objects.filter(
        state=models.command.PREPARED_STATE
    )

    for cmd in commands:
        send_mail(
            utils.format_mail_subject('Commande bientôt annulée'),
            render_to_string(
                'bvc/mails/cancel_command_soon.txt',
                {'cmd': cmd,}
            ),
            models.get_config().bvc_manager_mail,
            [cmd.email],
        )

    messages.success(
        request,
        'Les commandes non vendues ont reçu un mail de rappel.'
    )
    return redirect('bvcadmin:index')


# Users

def home(request):
    return render(request, 'bvc/home.html')

def place_commission_command(request):
    context = {}

    if request.method == 'POST':
        form = forms.commission_command.PlaceCommissionCommand(request.POST) 

        if form.is_valid():
            cmd = form.save()
            cmd.commission.user.email_user(
                utils.format_mail_subject('Récapitulatif de tes commandes'),
                render_to_string(
                    'bvc/mails/command_summary.txt',
                    {'commands': cmd.commission.commands.all()}
                ),
                models.get_config().bvc_manager_mail
            )

            messages.success(request, 'Votre command a bien été passée. Un mail vous a été envoyé.')
            return redirect('bvc:place_commission_command')
    else:
        form = forms.commission_command.PlaceCommissionCommand() 

    context['form'] = form

    return render(request, 'bvc/place_commission_command.html', context)

def place_member_command(request):
    context = {}

    if request.method == 'POST':
        user_form = forms.user.MemberUserCommand(request.POST)
        member_form = forms.user.MemberCommand(request.POST)
        command_form = forms.member_command.PlaceMemberCommand(request.POST)

        try:
            user = User.objects.get(email=request.POST['email'])
            user_form = forms.user.MemberUserCommand(request.POST, instance=user)
        except ObjectDoesNotExist:
            pass

        if user_form.is_valid():
            user = user_form.save()
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

                    user.email_user(
                        utils.format_mail_subject('Récapitulatif de tes commandes'),
                        render_to_string(
                            'bvc/mails/command_summary.txt',
                            {'commands': member.commands.all()}
                        ),
                        models.get_config().bvc_manager_mail
                    )

                    messages.success(request, 'Votre command a bien été passée. Un mail vous a été envoyé.')
                    return redirect('bvc:place_member_command')
    else:
        user_form = forms.user.MemberUserCommand() 
        member_form = forms.user.MemberCommand() 
        command_form = forms.member_command.PlaceMemberCommand() 

    context['user_form'] = user_form
    context['member_form'] = member_form
    context['command_form'] = command_form

    return render(request, 'bvc/place_member_command.html', context)
