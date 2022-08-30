# When you translate a word at translate.google.com,
# there're several sections of information.
# This module's responsibility are the three sections below the main one:
# 1) definitions 2) examples 3)translations
from __future__ import annotations
import re
from typing import List

from googletrans import Translator
from googletrans.models import Translated


b_tag_pattern = re.compile('<b>|</b>')


@staticmethod
def flatten(l: List[List]) -> List:
    """Unpack nested lists into one list"""
    if l is None:
        return []
    return [item for sublist in l for item in sublist]


class GoogleData:
    def __init__(self, transcription, main_translation, definitions, examples, translations) -> None:
        self.transcription = transcription
        self.main_translation = main_translation
        self.definitions = definitions
        self.examples = examples
        self.translations = translations

    @staticmethod
    def get(word: str, destination_language: str) -> GoogleData:
        data = Translator().translate(word, src='en', dest=destination_language)
        return GoogleData._parse(data)

    @staticmethod
    def _parse(data: Translated):
        useful = data.extra_data['parsed']
        # definitions, examples and translations are located under 'useful[3]'
        # if 'useful' is shorter, then the word probably doesn't exist,
        # so there's no point in trying to parse it
        if len(useful) < 4:
            return None
        transcription = useful[0][0]
        main_translation = data.text.lower()
        definitions = []
        examples = []
        translations = []

        details = useful[3]

        if details[1]:
            definition_data = details[1]
            # Tags can be associated with:
            # 1) The whole word
            # 2) Definition group
            # 3) Only one definition of the group
            # Word and definition group tags are propagated down to individual definitions,
            # so it's easier to store and show to the user.
            # 'flatten' is used because each tag is placed inside it's own array
            # not sure if this behaviour changes somewhere
            word_tags = flatten(definition_data[3]) if len(definition_data) > 3 else []
            definition_groups = [GoogleData._get_definition_group(g, word_tags) for g in definition_data[0]]
            definitions = flatten(definition_groups)

        if details[2]:
            # examples are saved in the DB, but the do not get shown to the user,
            # because they are usually duplicates of definition examples
            example_data = details[2]
            # the word is highlighed with <b> tag in examples
            examples = [re.sub(b_tag_pattern, '', e[1]) for e in example_data[0]]

        if details[5]:
            translation_data = details[5]
            translation_groups = [GoogleData._get_translation_group(t) for t in translation_data[0]]
            translations = flatten(translation_groups)

        if not translations and main_translation:
            # create translation from the main one of translation block is empty
            translations = [GoogleData._get_translation_from_main(main_translation)]
        return GoogleData(transcription, main_translation, definitions, examples, translations)

    @staticmethod
    def _get_definition_group(data, word_tags):
        part_of_speech = data[0]
        group_tags = flatten(data[2]) if len(data) > 2 else []
        return [GoogleData._get_definition(part_of_speech, word_tags, group_tags, d) for d in data[1]]

    @staticmethod
    def _get_definition(part_of_speech, word_tags: List, group_tags: List, data):
        definition = {
            'part_of_speech': part_of_speech,
            'tags': word_tags + group_tags,
            'definition': data[0],
            'example': '',
            'synonyms': [],
        }

        if len(data) < 2:
            return definition
        if data[1] is not None:
            definition['example'] = data[1]

        if len(data) < 5:
            return definition
        if data[4] is not None:
            definition['tags'].extend(flatten(data[4]))

        if len(data) > 5:
            definition['synonyms'] = flatten(data[5][0][0])

        return definition

    @staticmethod
    def _get_translation_group(data):
        part_of_speech = data[0]
        return [GoogleData._get_translation(t, part_of_speech) for t in data[1]]

    @staticmethod
    def _get_translation(data, part_of_speech: str):
        frequency = data[3] if data[3] else 2  # IDK if data[3] can be None. Just a precaution
        # Frequency is a number from 1 to 3 (1 is common and 3 is rare)
        # reverse that, so 1 is rare and 3 is common
        if frequency != 2:
            frequency ^= 2

        return {
            'part_of_speech': part_of_speech,
            'translation': data[0],
            # The translations of this word from user's language back to English
            'reverse_translations': data[2] if data[2] else [],
            'frequency': frequency,
        }

    @staticmethod
    def _get_translation_from_main(translation: str):
        return {
            'part_of_speech': '',
            'translation': translation,
            'reverse_translations': [],
            'frequency': 3,
        }
