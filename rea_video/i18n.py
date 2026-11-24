"""Report language.

Chinese is the source language of every user-facing string; English sits next to it. Two helpers:

  T("中文", "English")          pick the string for the current report language (optional .format kwargs)
  LangDict(zh={...}, en={...})  a code -> text mapping that resolves per language, so existing `X_ZH[code]`
                                lookups (and the `*_zh` fields they fill in breakdown.json) follow the language

French ("fr") is a third language built on the English one: every English string is looked up in
`locales/fr.json` (English text -> French text); a string missing there stays in English. Set REA_I18N_MISSES to a
file path to append each missing string to it (used to complete the catalogue).

The language is set once per run (`set_lang`), from `--lang` / prefs, and stored in breakdown["lang"] so
`finalize` / `summary` / `apply-review` render later in the same language. Default: zh.
"""
from __future__ import annotations

import contextvars
import json
import os
import re
from pathlib import Path
from collections.abc import Mapping
from typing import Iterator

LANGS = ("zh", "en", "fr")
LANG_NAMES = {"zh": "中文", "en": "English", "fr": "Français"}
LATIN = ("en", "fr")  # languages written from the English strings (punctuation, separators, word order)
_CATALOGS: dict[str, dict[str, str]] = {}
_lang: contextvars.ContextVar[str] = contextvars.ContextVar("rea_video_lang", default="zh")
_ui_lang: contextvars.ContextVar[str] = contextvars.ContextVar("rea_video_ui_lang", default="zh")


def _norm_lang(lang: str | None) -> str | None:
    if not lang:
        return None
    low = lang.strip().lower()
    if low in LANGS:
        return low
    prefix = re.split(r"[-_.]", low, maxsplit=1)[0]
    return prefix if prefix in LANGS else low


def set_lang(lang: str | None) -> str:
    norm = _norm_lang(lang) or "zh"
    if norm not in LANGS:
        raise ValueError(f"unsupported report language {lang!r} (choose from {', '.join(LANGS)})")
    _lang.set(norm)
    return norm


def lang() -> str:
    return _lang.get()


def latin(code: str | None = None) -> bool:
    """True for the languages built on the English strings (en, fr): English-style punctuation and separators."""
    return (code or _lang.get()) in LATIN


def _catalog(code: str) -> dict[str, str]:
    if code not in _CATALOGS:
        path = Path(__file__).with_name("locales") / f"{code}.json"
        try:
            _CATALOGS[code] = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            _CATALOGS[code] = {}
    return _CATALOGS[code]


def _miss(en: str) -> None:
    path = os.getenv("REA_I18N_MISSES")
    if path:
        try:
            with open(path, "a", encoding="utf-8") as f:
                f.write(json.dumps(en, ensure_ascii=False) + "\n")
        except OSError:
            pass


def from_en(en: str, code: str | None = None) -> str:
    """An English string in the given (default: current) language: unchanged for en, looked up for fr."""
    code = code or _lang.get()
    if code in ("zh", "en") or not isinstance(en, str) or not en.strip():
        return en
    out = _catalog(code).get(en)
    if out is None:
        _miss(en)
        return en
    return out


def T(zh: str, en: str | None = None, **kw) -> str:
    """Text for the current language; `en` missing falls back to zh. kwargs are applied with str.format."""
    code = _lang.get()
    s = from_en(en, code) if (en is not None and code in LATIN) else zh
    return s.format(**kw) if kw else s


def set_ui_lang(lang: str | None) -> str:
    """Language of CLI help and diagnostics. Separate from the report language, so it never changes what is written."""
    norm = _norm_lang(lang)
    chosen = norm if norm in LANGS else "zh"
    _ui_lang.set(chosen)
    return chosen


def ui_lang() -> str:
    return _ui_lang.get()


def U(zh: str, en: str, **kw) -> str:
    """CLI help / diagnostic text for the current CLI language."""
    code = _ui_lang.get()
    s = from_en(en, code) if code in LATIN else zh
    return s.format(**kw) if kw else s


def model_name(name: str | None) -> str | None:
    if not name or _lang.get() == "zh":
        return name
    return re.sub(r"\s*（([^）]*)）", lambda m: "" if re.search(r"[\u3400-\u9fff]", m[1]) else f" ({m[1]})", name)


def sep() -> str:
    """List separator: 、 in Chinese, ", " in English."""
    return "、" if _lang.get() == "zh" else ", "


def join(items) -> str:
    return sep().join(str(x) for x in items)


def shot_ids(ids) -> str:
    """Shot numbers as a short list: runs of three or more become a range, "#5、#8–#24"."""
    ids = sorted({int(i) for i in ids or []})
    if not ids:
        return "—"
    runs, out = [[ids[0], ids[0]]], []
    for i in ids[1:]:
        if i == runs[-1][1] + 1:
            runs[-1][1] = i
        else:
            runs.append([i, i])
    for a, z in runs:
        out += [f"#{a}–#{z}"] if z - a >= 2 else [f"#{i}" for i in range(a, z + 1)]
    return join(out)


def semi() -> str:
    """Clause separator: ； in Chinese, "; " in English."""
    return "；" if _lang.get() == "zh" else "; "


class LangDict(Mapping):
    """code -> display text, resolved per language. Keys and iteration follow the zh table."""

    def __init__(self, zh: dict, en: dict | None = None):
        self._zh = dict(zh)
        self._en = dict(en or {})

    def __getitem__(self, key):
        code = _lang.get()
        if code in LATIN and key in self._en:
            return from_en(self._en[key], code)
        return self._zh[key]

    def __iter__(self) -> Iterator:
        return iter(self._zh)

    def __len__(self) -> int:
        return len(self._zh)

    def __contains__(self, key) -> bool:
        return key in self._zh

    def __repr__(self) -> str:
        return f"LangDict({dict(self.items())!r})"
