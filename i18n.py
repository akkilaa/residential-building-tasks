import json
from pathlib import Path

_translations: dict = {}
_locale: str = "sr"
_default_dir = Path(__file__).parent / "translations"


def set_locale(locale: str) -> None:
    global _locale
    _locale = locale


def load(translations_dir: Path = None) -> None:
    global _translations
    base = translations_dir or _default_dir
    for path in sorted(Path(base).glob("*.json")):
        with open(path, encoding="utf-8") as f:
            _translations[path.stem] = json.load(f)


def t(key: str, **kwargs) -> str:
    parts = key.split(".")
    value = _translations.get(_locale, {})
    for part in parts:
        if not isinstance(value, dict):
            return key
        value = value.get(part)
        if value is None:
            return key
    if not isinstance(value, str):
        return key
    return value.format(**kwargs) if kwargs else value
