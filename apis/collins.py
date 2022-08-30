# Downloads data from collins dictionary API
from __future__ import annotations
import os
from urllib.error import HTTPError

import bs4

from .utils import get_json_data

collins_key = os.environ.get('COLLINS_KEY')


class CollinsData:
    def __init__(self, frequency: int, audio_url: str, transcription: str, definitions) -> None:
        self.frequency = frequency
        self.audio_url = audio_url
        self.transcription = transcription
        self.definitions = definitions

    @staticmethod
    def get(word) -> CollinsData:
        try:
            html = CollinsData._download_american_learner(word)
            return CollinsData._parse(html['entryContent'])
        except (HTTPError, KeyError):
            return None

    @staticmethod
    def _download_american_learner(word):
        # There are other dictionaries, like 'english', but 'american-learner' usually describes words better
        url = f'https://api.collinsdictionary.com/api/v1/dictionaries/american-learner/search/first/?q={word}&format=html'
        headers = {
            'Accept': 'application/json',
            'accessKey': collins_key,
        }
        return get_json_data(url, headers=headers)

    @staticmethod
    def _parse(html_markup) -> CollinsData:
        soup = bs4.BeautifulSoup(html_markup, 'html.parser')
        # Top level div that contains all word information
        entry = soup.div.div
        # The word itself, frequency, transcription and forms
        top_info = entry.span

        # Frequency data is represented by three dots and looks like this: '●○○'
        # the more dots filled - the more dots, the more common the word (min frequency is 1, max is 3)
        try:
            frequency = top_info.find('span', {'class': 'lbfreq'}).text.count('●')
        except BaseException:
            frequency = None

        transcription_span = top_info.find('span', {'class': 'pron'})

        try:
            audio = transcription_span.audio
            # I'm not sure if audio sample is there for every word
            audio_url = audio.source.get('src', '')
            # Remove audio, so we can get transcription without additional symbols
            audio.decompose()
        except BaseException:
            audio_url = None

        try:
            transcription = transcription_span.text
        except BaseException:
            transcription = None

        # Gram groups contain definitions (part of speech, definition, tags if any and examples)
        homonyms = entry.find_all('div', {'class': 'hom'})
        definitions = []
        for hom in homonyms:
            sense = hom.find('div', {'class': 'sense'})
            try:
                tags = sense.find_all('span', {'class': 'lbl'})
                tag_texts = ([list(tag.children)[1].text for tag in tags])
                definitions.append({
                    'part_of_speech': hom.find('span', {'class': 'gramGrp'}).text,
                    'definition': sense.find('span', {'class': 'def'}).text,
                    'examples': [s.text for s in sense.find_all('span', {'class': 'quote'})],
                    'tags': tag_texts
                })
            except BaseException:
                continue

        return CollinsData(frequency, audio_url, transcription, definitions)


class CollinsDataCached(CollinsData):
    """API calls are limited, so it's better to use cached html in tests"""
    data = {
        'leaf':
        r'<div class="entry_container"><div class="entry lang_en-gb" id="leaf_1"><span class="inline"><h1 class="hwd">leaf</h1><span class="lbfreq"><span> ●○○</span></span><span> /</span><span class="pron" type="">l<em class="hi">i</em>f<a href="#" class="playback"><img src="https://api.collinsdictionary.com/external/images/redspeaker.gif?version=2016-11-09-0913" alt="Pronunciation for leaf" class="sound" title="Pronunciation for leaf" style="cursor: pointer"/></a><audio type="pronunciation" title="leaf"><source type="audio/mpeg" src="https://api.collinsdictionary.com/media/sounds/sounds/e/en_/en_us/en_us_leaf_1.mp3"/>Your browser does not support HTML5 audio.</audio></span><span>/</span><span class="inline"><span> (</span><span class="orth">leaves</span><span>, </span><span class="orth">leafs</span><span>, </span><span class="orth">leafing</span><span>, </span><span class="orth">leafed</span><span>)</span></span></span><div class="hom" id="leaf_1.1"><span> \xa0 </span><span class="sensenum">1\xa0</span><span class="gramGrp"><span class="pos">countable noun</span><span class="lbl"><span> [</span>usu pl, also \'in/into\' <em class="hi">N</em><span>]</span></span></span><div class="sense"><span> </span><span class="def">The <em class="hi">leaves</em> of a tree or plant are the parts that are flat, thin, and usually green. Many trees and plants lose their leaves in the winter and grow new leaves in the spring.</span><span class="cit" id="leaf_1.2"><span> ■\xa0EG:\xa0</span><span class="quote">In the garden, the leaves of the horse chestnut had already fallen.</span></span></div><!-- End of DIV sense--></div><!-- End of DIV hom--><div class="hom" id="leaf_1.3"><span> <br/></span><span class="sensenum">2\xa0</span><span class="gramGrp"><span class="pos">countable noun</span></span><div class="sense"><span> </span><span class="def">A <em class="hi">leaf</em> is one of the pieces of paper of which a book is made.</span><span class="cit" id="leaf_1.4"><span> ■\xa0EG:\xa0</span><span class="quote">He flattened the wrappers and put them between the leaves of his book.</span></span></div><!-- End of DIV sense--></div><!-- End of DIV hom--><div class="hom" id="leaf_1.5"><span> <br/></span><span class="sensenum">3\xa0</span><span class="gramGrp"><span class="pos">phrase</span></span><div class="sense"><span> </span><span class="def">If you say that you are going to <em class="hi">turn over a new leaf</em>, you mean that you are going to start to behave in a better or more acceptable way.</span><span class="cit" id="leaf_1.6"><span> ■\xa0EG:\xa0</span><span class="quote">He realized he was in the wrong and promised to turn over a new leaf.</span></span></div><!-- End of DIV sense--></div><!-- End of DIV hom--><span class="re"><span class="xr"> See \n                \n        \t\t<a data-resource="american-learner" data-topic="leaf-through_1" href="">leaf through</a></span></span></div><!-- End of DIV entry lang_en-gb--></div><!-- End of DIV entry_container-->\n',
        'school':
        r'<div class="entry_container"><div class="entry lang_en-gb" id="school_1"><span class="inline"><h1 class="hwd">school</h1><span class="lbfreq"><span> ●●●</span></span><span> /</span><span class="pron" type="">sk<em class="hi">u</em>l<a href="#" class="playback"><img src="https://api.collinsdictionary.com/external/images/redspeaker.gif?version=2016-11-09-0913" alt="Pronunciation for school" class="sound" title="Pronunciation for school" style="cursor: pointer"/></a><audio type="pronunciation" title="school"><source type="audio/mpeg" src="https://api.collinsdictionary.com/media/sounds/sounds/e/en_/en_us/en_us_school_1.mp3"/>Your browser does not support HTML5 audio.</audio></span><span>/</span><span class="inline"><span> (</span><span class="orth">schools</span><span>, </span><span class="orth">schooling</span><span>, </span><span class="orth">schooled</span><span>)</span></span></span><div class="hom" id="school_1.1"><span> \xa0 </span><span class="sensenum">1\xa0</span><span class="gramGrp"><span class="pos">variable noun</span></span><div class="sense"><span> </span><span class="def">A <em class="hi">school</em> is a place where children are educated. You usually refer to this place as <em class="hi">school</em> when you are talking about the time that children spend there and the activities that they do there.</span><span class="cit" id="school_1.2"><span> ■\xa0EG:\xa0</span><span class="quote">...a boy who was in my class at school.</span></span><span class="cit" id="school_1.3"><span> ■\xa0EG:\xa0</span><span class="quote">Even the good students say homework is what they most dislike about school.</span></span><span class="cit" id="school_1.4"><span> ■\xa0EG:\xa0</span><span class="quote">...a school built in the Sixties.</span></span></div><!-- End of DIV sense--></div><!-- End of DIV hom--><div class="hom" id="school_1.5"><span> <br/></span><span class="sensenum">2\xa0</span><span class="gramGrp"><span class="pos">collective countable noun</span></span><div class="sense"><span> </span><span class="def">A <em class="hi">school</em> is the students or staff at a school.</span><span class="cit" id="school_1.6"><span> ■\xa0EG:\xa0</span><span class="quote">Deirdre, the whole school\'s going to hate you.</span></span></div><!-- End of DIV sense--></div><!-- End of DIV hom--><div class="hom" id="school_1.7"><span> <br/></span><span class="sensenum">3\xa0</span><span class="gramGrp"><span class="pos">countable noun</span><span> &amp; </span><span class="pos">"noun, in names"</span></span><div class="sense"><span> </span><span class="def">A privately-run place where a particular skill or subject is taught can be referred to as a <em class="hi">school</em>.</span><span class="cit" id="school_1.8"><span> ■\xa0EG:\xa0</span><span class="quote">...a riding school.</span></span></div><!-- End of DIV sense--></div><!-- End of DIV hom--><div class="hom" id="school_1.9"><span> <br/></span><span class="sensenum">4\xa0</span><span class="gramGrp"><span class="pos">variable noun</span><span> &amp; </span><span class="pos">"noun, in names"</span></span><div class="sense"><span> </span><span class="def">A university, college, or university department specializing in a particular type of subject can be referred to as a <em class="hi">school</em>.</span><span class="cit" id="school_1.10"><span> ■\xa0EG:\xa0</span><span class="quote">...a lecturer in the school of veterinary medicine at the University of Pennsylvania.</span></span></div><!-- End of DIV sense--></div><!-- End of DIV hom--><div class="hom" id="school_1.11"><span> <br/></span><span class="sensenum">5\xa0</span><span class="gramGrp"><span class="pos">uncount noun</span></span><div class="sense"><span> </span><span class="lbl"><span>[</span>US<span>]</span></span><span> </span><span class="def"><em class="hi">School</em> is used to refer to college.</span><span class="cit" id="school_1.12"><span> ■\xa0EG:\xa0</span><span class="quote">Jack eventually graduated from school, got married, and got his first real job.</span></span></div><!-- End of DIV sense--></div><!-- End of DIV hom--><div class="hom" id="school_1.13"><span> <br/></span><span class="sensenum">6\xa0</span><span class="gramGrp"><span class="pos">collective countable noun</span><span class="lbl"><span> [</span>usu with supp<span>]</span></span></span><div class="sense"><span> </span><span class="def">A particular <em class="hi">school</em> <em class="hi">of</em> writers, artists, or thinkers is a group of them whose work, opinions, or theories are similar.</span><span class="cit" id="school_1.14"><span> ■\xa0EG:\xa0</span><span class="quote">...the Chicago school of economists.</span></span></div><!-- End of DIV sense--></div><!-- End of DIV hom--><div class="hom" id="school_1.15"><span> <br/></span><span class="sensenum">7\xa0</span><span class="gramGrp"><span class="pos">transitive verb</span></span><div class="sense"><span> </span><span class="lbl"><span>[</span>written<span>]</span></span><span> </span><span class="def">If you <em class="hi">school</em> someone <em class="hi">in</em> something, you train or educate them to have a certain skill, type of behavior, or way of thinking.</span><span class="cit" id="school_1.16"><span> ■\xa0EG:\xa0</span><span class="quote">Many mothers schooled their daughters in the myth of female inferiority.</span></span></div><!-- End of DIV sense--></div><!-- End of DIV hom--><div class="hom" id="school_1.17"><span> <br/></span><span class="sensenum">8\xa0</span><span class="xr"><span>→\xa0</span><span class="lbl">see also</span><span> </span>\n                \n        \t\t<a data-resource="american-learner" data-topic="schooling_1" href="">schooling</a><span class="bold">, </span>\n                \n        \t\t<a data-resource="american-learner" data-topic="boarding-school_1" href="">boarding school</a><span class="bold">, </span>\n                \n        \t\t<a data-resource="american-learner" data-topic="grade-school_1" href="">grade school</a><span class="bold">, </span>\n                \n        \t\t<a data-resource="american-learner" data-topic="graduate-school_1" href="">graduate school</a><span class="bold">, </span>\n                \n        \t\t<a data-resource="american-learner" data-topic="grammar-school_1" href="">grammar school</a><span class="bold">, </span>\n                \n        \t\t<a data-resource="american-learner" data-topic="high-school_1" href="">high school</a><span class="bold">, </span>\n                \n        \t\t<a data-resource="american-learner" data-topic="nursery-school_1" href="">nursery school</a><span class="bold">, </span>\n                \n        \t\t<a data-resource="american-learner" data-topic="prep-school_1" href="">prep school</a><span class="bold">, </span>\n                \n        \t\t<a data-resource="american-learner" data-topic="primary-school_1" href="">primary school</a><span class="bold">, </span>\n                \n        \t\t<a data-resource="american-learner" data-topic="private-school_1" href="">private school</a><span class="bold">, </span>\n                \n        \t\t<a data-resource="american-learner" data-topic="public-school_1" href="">public school</a><span class="bold">, </span>\n                \n        \t\t<a data-resource="american-learner" data-topic="state-school_1" href="">state school</a></span></div><!-- End of DIV hom--></div><!-- End of DIV entry lang_en-gb--></div><!-- End of DIV entry_container-->\n',
        'acquisition':
        r'<div class="entry_container"><div class="entry lang_en-gb" id="acquisition_1"><span class="inline"><h1 class="hwd">acquisition</h1><span class="lbfreq"><span> ●○○</span></span><span> /</span><span class="pron" type=""><em class="hi">æ</em>kwɪz<em class="hi">ɪ</em>ʃ<sup class="hi">ə</sup>n<a href="#" class="playback"><img src="https://api.collinsdictionary.com/external/images/redspeaker.gif?version=2016-11-09-0913" alt="Pronunciation for acquisition" class="sound" title="Pronunciation for acquisition" style="cursor: pointer"/></a><audio type="pronunciation" title="acquisition"><source type="audio/mpeg" src="https://api.collinsdictionary.com/media/sounds/sounds/e/en_/en_us/en_us_acquisition_1.mp3"/>Your browser does not support HTML5 audio.</audio></span><span>/</span><span class="inline"><span> (</span><span class="orth">acquisitions</span><span>)</span></span></span><div class="hom" id="acquisition_1.1"><span> \xa0 </span><span class="sensenum">1\xa0</span><span class="gramGrp"><span class="pos">variable noun</span></span><div class="sense"><span> </span><span class="lbl"><span>[</span>business<span>]</span></span><span> </span><span class="def">If a company or business person makes an <em class="hi">acquisition</em>, they buy another company or part of a company.</span><span class="cit" id="acquisition_1.2"><span> ■\xa0EG:\xa0</span><span class="quote">...the acquisition of a profitable paper recycling company.</span></span></div><!-- End of DIV sense--></div><!-- End of DIV hom--><div class="hom" id="acquisition_1.3"><span> <br/></span><span class="sensenum">2\xa0</span><span class="gramGrp"><span class="pos">countable noun</span></span><div class="sense"><span> </span><span class="def">If you make an <em class="hi">acquisition</em>, you buy or obtain something, often to add to things that you already have.</span><span class="cit" id="acquisition_1.4"><span> ■\xa0EG:\xa0</span><span class="quote">How did you go about making this marvelous acquisition then?</span></span></div><!-- End of DIV sense--></div><!-- End of DIV hom--><div class="hom" id="acquisition_1.5"><span> <br/></span><span class="sensenum">3\xa0</span><span class="gramGrp"><span class="pos">uncount noun</span></span><div class="sense"><span> </span><span class="def">The <em class="hi">acquisition</em> of a skill or a particular type of knowledge is the process of learning it or developing it.</span><span class="cit" id="acquisition_1.6"><span> ■\xa0EG:\xa0</span><span class="quote">...language acquisition.</span></span></div><!-- End of DIV sense--></div><!-- End of DIV hom--></div><!-- End of DIV entry lang_en-gb--></div><!-- End of DIV entry_container-->\n', }

    @classmethod
    def get(cls, word) -> CollinsData:
        return super()._parse(cls.data[word])
