from unittest import TestCase
from apis.collins import CollinsDataCached


class TestCollins(TestCase):
    def test_common(self):
        collins_data = CollinsDataCached.get('school')
        self.assertEqual(
            'https://api.collinsdictionary.com/media/sounds/sounds/e/en_/en_us/en_us_school_1.mp3',
            collins_data.audio_url)
        self.assertEqual(3, collins_data.frequency)
        self.assertEqual('skul', collins_data.transcription)

    def test_rare(self):
        collins_data = CollinsDataCached.get('leaf')
        self.assertEqual(
            'https://api.collinsdictionary.com/media/sounds/sounds/e/en_/en_us/en_us_leaf_1.mp3',
            collins_data.audio_url)
        self.assertEqual(1, collins_data.frequency)
        self.assertEqual('lif', collins_data.transcription)

    def test_rare2(self):
        collins_data = CollinsDataCached.get('acquisition')
        self.assertEqual(
            'https://api.collinsdictionary.com/media/sounds/sounds/e/en_/en_us/en_us_acquisition_1.mp3',
            collins_data.audio_url)
        self.assertEqual(1, collins_data.frequency)
        self.assertEqual('ækwɪzɪʃən', collins_data.transcription)
