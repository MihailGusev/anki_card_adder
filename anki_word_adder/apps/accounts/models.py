import googletrans
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager
from django.db import models


class Language(models.Model):
    """Different languages that a user may have as native"""
    code = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=30)

    default_code = next(iter(googletrans.LANGUAGES))

    @staticmethod
    def get_by_code(code: str):
        try:
            return Language.objects.get(code=code.lower())
        except Language.DoesNotExist:
            if Language.objects.all().count() > 0:
                return Language._get_default()

            Language._fill_table()
            try:
                return Language.objects.get(code=code.lower())
            except Language.DoesNotExist:
                return Language._get_default()

    @staticmethod
    def _fill_table():
        Language.objects.bulk_create([Language(code=code, name=name.title())
                                      for code, name in googletrans.LANGUAGES.items()])

    @staticmethod
    def _get_default():
        return Language.objects.all().first()


class Learner(AbstractUser):
    """User of the application"""
    objects = UserManager()


class Settings(models.Model):

    class TranslationFilter(models.IntegerChoices):
        NO = 1,  # do not filter
        RARE = 2,  # filter rare translations
        UNCOMMON = 3,  # filter rare and uncommon (only common left)

    learner = models.OneToOneField(Learner, on_delete=models.DO_NOTHING, primary_key=True)
    language = models.ForeignKey(Language, on_delete=models.DO_NOTHING)

    deck_id = models.BigIntegerField(null=True)  # anki deck id
    note_id = models.BigIntegerField(null=True)  # anki note id

    translation_filter = models.IntegerField(choices=TranslationFilter.choices, default=TranslationFilter.NO)

    add_collins_definitions = models.BooleanField(default=True)  # add collins definitions to card if true
    add_google_definitions = models.BooleanField(default=True)  # add google definitions to card if true

    show_message_on_card_addition = models.BooleanField(default=True)  # show success message when card is added if true


class Word(models.Model):
    """Cache already searched words"""

    name = models.CharField(max_length=50, unique=True)
    google = models.JSONField(null=True)  # data from google translate (definitions and examples)
    collins = models.JSONField(null=True)  # data from collins american-learner dictionary

    @staticmethod
    def get_by_name(name: str):
        try:
            return Word.objects.get(name=name.lower())
        except Word.DoesNotExist:
            return None


class Translation(models.Model):
    """Another caching model. One word can have more than 1 translation"""
    word = models.ForeignKey(Word, on_delete=models.DO_NOTHING)
    language = models.ForeignKey(Language, on_delete=models.DO_NOTHING)
    translation = models.JSONField()


class Feedback(models.Model):
    """Feedback sent by users"""

    class Priotity(models.IntegerChoices):
        CRITICAL = 1,
        HIGH = 2,
        MEDIUM = 3,
        LOW = 4,
        NEW = 5,

    learner = models.ForeignKey(Learner, on_delete=models.DO_NOTHING)
    text = models.TextField()
    priority = models.IntegerField(choices=Priotity.choices, default=Priotity.NEW)


class Request(models.Model):
    learner = models.ForeignKey(Learner, on_delete=models.DO_NOTHING)
    word = models.ForeignKey(Word, on_delete=models.DO_NOTHING)
    date = models.DateTimeField(auto_now_add=True)
