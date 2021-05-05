from django.shortcuts import render, redirect, reverse
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model, authenticate, login
from django.utils.translation import gettext as _
from django.contrib import messages

from .forms import RegistrationForm, PersonalInfoForm

import logging

logger = logging.getLogger('general')

UserModel = get_user_model()

class RegistrationView(View):

    def get(self, request):
        form = RegistrationForm()

        context = {
            'form': form
        }
        return render(request, 'registration/registration.html', context)

    def post(self, request):
        logger.debug(f'request.POST: {request.POST}')
        form = RegistrationForm(request.POST)

        if form.is_valid():
            logger.debug(f'Form is valid, form.cleaned_data: {form.cleaned_data}')

            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = UserModel(email=email)
            user.set_password(password)
            user.save()
            logger.debug('User is created')

            user = authenticate(request, email=email, password=password)
            logger.debug(f'User: {user}')
            if user is not None:
                logger.debug('User is authenticated')
                login(request, user)
                logger.debug('User is logged in')
            else:
                logger.debug('User is not authenticated')

            return redirect(reverse('home'))
        else:
            logger.debug(f'Form is not valid, form.errors: {form.errors}')
            context = {
                'form': form,
            }
            return render(request, 'registration/registration.html', context)

class UserAccountView(LoginRequiredMixin, View):

    def get(self, request):
        user = request.user
        form = PersonalInfoForm(initial={'email': user.email})
        context = {
            'form': form
        }
        return render(request, 'user_account.html', context)

    def post(self, request):
        logger.debug(f'request.POST: {request.POST}')
        logger.debug(f'request.FILES: {request.FILES}')
        logger.debug(f'request.FILES["account_image"]: {request.FILES.get("account_image", None)}')

        user = request.user

        if request.FILES:
            account_image = request.FILES["account_image"]
            user.profile_photo = account_image
            user.save()
            logger.debug('User profile photo uploaded successfully ')
            messages.success(request, _('Фото для аватара, загружено успешно'))
        if request.POST.get('email', None):
            user.email = request.POST['email']
            user.save()
            logger.debug('User profile information changed successfully')
            messages.success(request, _('Информация пользователя изменена успешно'))

        form = PersonalInfoForm(initial={'email': user.email})
        context = {
            'form': form
        }
        return render(request, 'user_account.html', context)
