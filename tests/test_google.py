# To add other tests just go to translate.google.com and copy-paste data from there
from unittest import TestCase
from apis.google import GoogleData


class TestGoogle(TestCase):

    def get_russian(self, word) -> GoogleData:
        return GoogleData.get(word, 'ru')

    def test_word_does_not_exist(self):
        self.assertIsNone(self.get_russian('qqqqq'))

    def test_word_tags_propagate_to_definition_tags(self):
        """Word and definition group tags must be propagated down to word tags"""
        word_data = self.get_russian('recursion')

        self.assertEqual(1, len(word_data.definitions))

        definition = word_data.definitions[0]
        self.assertEqual(['Mathematics', 'Linguistics'], definition['tags'])
        self.assertEqual('noun', definition['part_of_speech'])

        self.assertEqual([], word_data.examples)
        self.assertEqual(1, len(word_data.translations))

        translation = word_data.translations[0]
        self.assertEqual('', translation['part_of_speech'])
        self.assertEqual('рекурсия', translation['translation'])
        self.assertEqual(3, translation['frequency'])
