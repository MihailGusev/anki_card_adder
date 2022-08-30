import json
from typing import Any, Dict

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.views.generic import CreateView, TemplateView
from ipware import get_client_ip

from .forms import LearnerCreationForm, LearnerAuthenticationForm
from .models import Learner, Settings, Language
from apis.ip_registry import get_language_code_by_ip


class RegisterView(CreateView):
    template_name = 'register.html'
    form_class = LearnerCreationForm

    # Without this line there's "RegisterView has no attribute 'object'" exception
    object = None

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('main')
        return super(RegisterView, self).get(request, *args, **kwargs)

    def post(self, request):
        """Create new user, his settings and redirect to main"""
        form: LearnerCreationForm = self.get_form()
        if form.is_valid():
            learner: Learner = form.save()
            language = self.get_language(request)
            settings = Settings(learner=learner, language=language)
            settings.save()
            learner = authenticate(request,
                                   username=form.cleaned_data['username'],
                                   password=form.cleaned_data['password1'])
            login(request, learner)
            return redirect('main')
        else:
            return super(RegisterView, self).form_invalid(form)

    def get_language(self, request):
        """Try to identify language by request or return default"""
        user_ip, is_routable = get_client_ip(request)

        if user_ip is not None and is_routable:
            language_code = get_language_code_by_ip(user_ip)
            language = Language.get_by_code(language_code)
            message = f'The translation language was identified as {language.name}'
        else:
            language_code = Language.default_code
            language = Language.get_by_code(language_code)
            message = f'Unable to identify translation language. {language.name} was selected by default'

        settings_url = reverse_lazy('accounts:settings')
        message = f'{message}. You can change it in the <a href="{settings_url}">settings</a>'
        messages.info(request, mark_safe(message))
        return language


class LoginLearnerView(LoginView):
    form_class = LearnerAuthenticationForm
    template_name = 'login.html'
    redirect_authenticated_user = True
    next_page = reverse_lazy('main')


class LogoutView(LogoutView):
    next_page = reverse_lazy('accounts:login')


class GuideView(TemplateView):
    template_name = 'guide.html'


class SettingsView(LoginRequiredMixin, TemplateView):
    """Main view also has UI for some settings.
    This one is for settings that won't be changed often (language, deck, etc.)"""

    login_url = reverse_lazy('accounts:login')
    template_name = 'settings.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        settings: Settings = self.request.user.settings
        settings = {
            'current_language_code': settings.language.code,
            'language_list': [{'code': l.code, 'name': l.name} for l in Language.objects.all()],
            'deck_id': settings.deck_id,
            'show_message_on_card_addition': settings.show_message_on_card_addition,
        }
        context['settings'] = settings
        return context

    def post(self, request):
        """Accept JSON data and set it's key-value pairs as settings' fields"""
        settings: Settings = request.user.settings
        new_settings: dict = json.loads(request.body)

        # Settings are posted from 'main' and from 'accounts:settings', and language is not there in 'main'
        language_code = new_settings.pop('language', None)
        if language_code:
            language = Language.get_by_code(language_code)
            settings.language = language

        for key in new_settings:
            setattr(settings, key, new_settings[key])
        settings.save()
        return HttpResponse(status=204)
