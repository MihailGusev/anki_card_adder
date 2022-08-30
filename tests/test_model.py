from django.test import TestCase

from anki_word_adder.apps.accounts.models import Language, Word


class LanguageModelTests(TestCase):
    def test_get_language_by_code(self):
        name, code = 'Russian', 'ru'
        Language(name=name, code=code).save()
        lang = Language.get_by_code(code)
        self.assertEqual(lang.name, name)


class WordModelTests(TestCase):
    def test_get_by_name(self):
        word_name = 'new'
        Word(name=word_name).save()
        word = Word.get_by_name(word_name)
        self.assertEqual(word.name, word_name)
