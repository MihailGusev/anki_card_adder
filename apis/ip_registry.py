import os
from urllib.error import HTTPError

from .utils import get_json_data
from anki_word_adder.apps.accounts.models import Language

IP_REGISTRY_KEY = os.environ.get('IP_REGISTRY_KEY')


def get_language_code_by_ip(ip: str) -> str:
    """Use ipregistry to identify the language code of the user or return default language code"""

    url = f'https://api.ipregistry.co/{ip}?key={IP_REGISTRY_KEY}'
    try:
        data = get_json_data(url)
    except HTTPError:
        return Language.default_code
    return data['location']['language']['code']
