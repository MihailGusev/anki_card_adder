import json
from typing import Any, Dict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.generic import TemplateView, View
from django.urls import reverse_lazy

from anki_word_adder.apps.accounts.models import Language, Learner, Settings, Word, Translation, Request, Feedback
from apis.collins import CollinsData
from apis.google import GoogleData


class MainPageView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('accounts:login')
    template_name = 'main.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        settings: Settings = self.request.user.settings
        learner_settings = {
            'note_id': settings.note_id,
            'deck_id': settings.deck_id,
            'translate_to': settings.language.code,
            'translation_filter': settings.translation_filter,
            'add_google_definitions': settings.add_google_definitions,
            'add_collins_definitions': settings.add_collins_definitions,
            'show_message_on_card_addition': settings.show_message_on_card_addition,
        }
        context['learner_settings'] = learner_settings
        return context


class GuidePageView(TemplateView):
    template_name = 'guide.html'


class VersionsPageView(TemplateView):
    template_name = 'versions.html'


class FeedbackView(LoginRequiredMixin, View):
    def post(self, request):
        text = json.loads(request.body)['feedback'].strip()
        feedback = Feedback(learner=request.user, text=text)
        feedback.save()
        return HttpResponse(status=204)


class GetWordDataView(LoginRequiredMixin, View):
    login_url = reverse_lazy('accounts:login')

    def get(self, request: HttpRequest, word: str):
        """Try to find word and its translation in the DB. If cannot find - fetch it"""
        word = word.lower()

        learner: Learner = request.user
        lang_code = learner.settings.language.code

        # At some point there will be a lot of words in a the DB,
        # so EAFP will be better than LBYL
        try:
            translation_model = Translation.objects.get(word__name=word, language__code=lang_code)
        except Translation.DoesNotExist:
            google_data = GoogleData.get(word, lang_code)
            if google_data is None:
                return JsonResponse({
                    'errors': ['The word not found. Check if you typed it correctly and try again']
                })
            translation_model = self.create_translation(word, lang_code, google_data)

        word_model = translation_model.word
        Request(learner=learner, word=word_model).save()

        return JsonResponse({
            'word': word,
            'translations': translation_model.translation['translations'],
            'google': word_model.google,
            'collins': word_model.collins,
        })

    def create_translation(self, word: str, lang_code: str, google_data: GoogleData):
        try:
            word_model = Word.objects.get(name=word)
        except Word.DoesNotExist:
            word_model = self.create_word(word, google_data)

        translation_model = Translation(word=word_model)
        translation_model.language = Language.get_by_code(lang_code)
        translation_model.translation = {
            'main_translation': google_data.main_translation,
            'translations': google_data.translations,
        }
        translation_model.save()
        return translation_model

    def create_word(self, word: str, google_data: GoogleData) -> Word:
        word_model = Word(name=word)

        collins_data = CollinsData.get(word)

        if collins_data is not None:
            word_model.collins = {
                "audio_url": collins_data.audio_url,
                "frequency": collins_data.frequency,
                "transcription": collins_data.transcription,
                "definitions": collins_data.definitions,
            }

        word_model.google = {
            "transcription": google_data.transcription,
            "examples": google_data.examples,
            "definitions": google_data.definitions,
        }

        word_model.save()
        return word_model
