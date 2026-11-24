#!/usr/bin/env python3
"""Build / complete a report-language catalogue (English text -> target text) with an OpenAI-compatible LLM.

  python scripts/translate_catalog.py strings.json rea_video/locales/fr.json --env-file ~/.rea-video/openrouter.env

`strings.json` is a JSON object (or list) whose keys are the English strings to translate (as passed to T(), U(),
LangDict(en=...) and the *_EN tables). Strings already in the catalogue are skipped, so the script can be rerun to
fill in what is missing (for example the strings logged by REA_I18N_MISSES=<file>, one JSON string per line).
Reads REA_VLM_BASE_URL / REA_VLM_API_KEY / REA_VLM_MODEL (or REA_TRANSLATE_MODEL) from the environment or --env-file.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

GLOSSARY = """shot = plan; cut = coupe; transition = transition; key frame = image clé; storyboard = storyboard;
live action / filmed = tournage réel / filmé; AI-generated video = vidéo générée par IA; avatar / digital human = avatar IA;
3D render = rendu 3D; 2D animation = animation 2D; stop motion = animation image par image (stop motion);
code / template render = rendu par code / modèle; screen capture = capture d'écran; still image + pan/zoom = image fixe animée (pan/zoom);
static hold / still = image fixe; film footage = extrait de film/série; overlay = incrustation; packaging = habillage;
subtitles / captions = sous-titres; styled text = texte stylisé; sticker = sticker; picture-in-picture = image dans l'image;
voice = voix; voice-over = voix off; talking head = face caméra; music = musique; sound effect = effet sonore; stems = pistes séparées;
remake = reproduction (to remake = reproduire); generation unit = unité de génération; prompt = prompt; reference image = image de référence;
real material = vrais rushes / matériel réel; verdict = verdict; confidence = confiance; open question = point à confirmer;
VLM / image reader = modèle de vision (VLM); framing = cadrage; shot size = valeur de plan; close-up = gros plan; medium shot = plan moyen;
lighting = éclairage; key light = lumière principale; fill light = lumière d'appoint; rim light = contre-jour; grade = étalonnage;
handheld = caméra à la main; tripod = trépied; gimbal = stabilisateur; hook = accroche; call to action = appel à l'action;
narrative line = fil narratif; cast = personnages; scene = décor; prop = accessoire; beat = temps fort / battement (music: temps)"""

PROMPT = """You translate user-facing strings of a video-analysis tool from English to {lang_name}.
Return ONLY a JSON object mapping each input id to its translation.
Rules:
- Keep every placeholder exactly as written: {{name}}, {{n}}, {{x:.1f}}, %s, %d, and keep doubled braces {{{{ }}}} as they are.
- Keep Markdown (**, `, |, #, -, links), HTML tags and attributes, emoji, arrows (→ ←), symbols (✓ ❌ ①), numbers, units, file names,
  paths, command lines (rea-video ..., --flags), JSON keys, code identifiers, model and product names unchanged.
- Keep leading/trailing spaces, line breaks and punctuation style of the source (a string starting with ", " still starts with ", ").
- Short fragments are pieces of larger sentences: translate them so they still fit (keep the same grammatical role).
- Natural, concise French for content creators; use "vous". Use this glossary:
{glossary}

Input (id -> English):
{items}"""

PH = re.compile(r"\{[^{}]*\}")


def load_env(path: str | None) -> None:
    if not path:
        return
    for line in Path(os.path.expanduser(path)).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def ask(items: dict[str, str], lang_name: str) -> dict[str, str]:
    base = os.environ["REA_VLM_BASE_URL"].rstrip("/")
    model = os.getenv("REA_TRANSLATE_MODEL") or os.environ["REA_VLM_MODEL"].split(",")[0].strip()
    body = {"model": model, "temperature": 0.1, "response_format": {"type": "json_object"},
            "messages": [{"role": "user", "content": PROMPT.format(lang_name=lang_name, glossary=GLOSSARY,
                                                                   items=json.dumps(items, ensure_ascii=False, indent=0))}]}
    req = urllib.request.Request(base + "/chat/completions", data=json.dumps(body).encode(), method="POST",
                                 headers={"Content-Type": "application/json", "User-Agent": "rea-video-translate",
                                          "Authorization": f"Bearer {os.environ['REA_VLM_API_KEY']}"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                text = json.loads(r.read().decode())["choices"][0]["message"]["content"]
            text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
            return json.loads(text)
        except Exception as e:  # network hiccup or malformed JSON: retry
            err = e
            time.sleep(2 + 3 * attempt)
    print(f"batch failed: {err}", file=sys.stderr)
    return {}


def valid(en: str, fr: str) -> bool:
    if not isinstance(fr, str) or not fr.strip():
        return False
    if sorted(PH.findall(en)) != sorted(PH.findall(fr)):
        return False
    return en.count("%s") == fr.count("%s") and en.count("%d") == fr.count("%d")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("strings")
    ap.add_argument("catalog")
    ap.add_argument("--env-file")
    ap.add_argument("--lang-name", default="French")
    ap.add_argument("--batch", type=int, default=60)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    load_env(a.env_file)
    src = json.loads(Path(a.strings).read_text(encoding="utf-8"))
    todo_all = list(src) if isinstance(src, (dict, list)) else []
    cat_path = Path(a.catalog)
    cat = json.loads(cat_path.read_text(encoding="utf-8")) if cat_path.exists() else {}
    for rnd in range(3):
        todo = [s for s in todo_all if s not in cat and s.strip()]
        if not todo:
            break
        size = a.batch if rnd == 0 else max(5, a.batch // 4)
        batches = [todo[i:i + size] for i in range(0, len(todo), size)]
        print(f"round {rnd + 1}: {len(todo)} strings in {len(batches)} batches", file=sys.stderr)

        def run(batch):
            ids = {str(i): s for i, s in enumerate(batch)}
            got = ask(ids, a.lang_name)
            return {ids[k]: v for k, v in got.items() if k in ids and valid(ids[k], v)}

        with ThreadPoolExecutor(a.workers) as ex:
            for res in ex.map(run, batches):
                cat.update(res)
        cat_path.parent.mkdir(parents=True, exist_ok=True)
        cat_path.write_text(json.dumps(dict(sorted(cat.items())), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    left = [s for s in todo_all if s not in cat and s.strip()]
    print(f"catalogue: {len(cat)} entries; still missing: {len(left)}", file=sys.stderr)
    for s in left[:20]:
        print("  missing:", s[:100], file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
