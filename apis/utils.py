import requests


def get_json_data(url: str, **options):
    r = requests.get(url, timeout=3, **options)
    r.raise_for_status()
    return r.json()
