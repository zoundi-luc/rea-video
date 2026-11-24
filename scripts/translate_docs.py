#!/usr/bin/env python3
"""Translate Markdown docs (skill, references) in place with an OpenAI-compatible LLM, section by section.

  python scripts/translate_docs.py skills/rea-video/SKILL.md skills/rea-video/references/*.md --env-file ~/.rea-video/openrouter.env

Commands, flags, file paths, JSON keys, field names and enum values stay as they are, so the agent instructions keep
matching the CLI. Reads REA_VLM_BASE_URL / REA_VLM_API_KEY / REA_VLM_MODEL (or REA_TRANSLATE_MODEL).
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from translate_catalog import GLOSSARY, load_env  # noqa: E402

PROMPT = """Translate this part of a Markdown document from Chinese (and any English prose) into natural, concise French.
It is an instruction file read by an AI agent that drives the `rea-video` command-line tool, and by French-speaking users.
Rules:
- Output ONLY the translated Markdown, no comments, no code fences around the whole answer.
- Keep the Markdown structure exactly: headings, lists, tables (same number of columns and rows), links, line breaks.
- Do NOT change: shell commands and their flags (rea-video ..., --vlm, --lang zh|en|fr), file names and paths, environment
  variables, JSON/YAML keys and field names (label_probs, image_source, narrative, role, performance, aspects, ...),
  enum values written in Latin letters (live_action, ai_video, avatar, cg_3d, code_render, ...), model and product names,
  URLs, numbers. Inside code blocks translate only comments and Chinese prose; keep the code.
- Chinese words quoted as values the tool prints (for example a status shown in the output) may be translated, but keep
  their meaning clear.
- When the text says the report/answers are in Chinese by default, keep that fact, and note that French is available with
  `--lang fr` only where the original talks about choosing the language.
- Address the reader with "vous". Glossary:
{glossary}

Markdown to translate:
<<<
{text}
>>>"""


def ask(text: str) -> str:
    base = os.environ["REA_VLM_BASE_URL"].rstrip("/")
    model = os.getenv("REA_TRANSLATE_MODEL") or os.environ["REA_VLM_MODEL"].split(",")[0].strip()
    body = {"model": model, "temperature": 0.1,
            "messages": [{"role": "user", "content": PROMPT.format(glossary=GLOSSARY, text=text)}]}
    req = urllib.request.Request(base + "/chat/completions", data=json.dumps(body).encode(), method="POST",
                                 headers={"Content-Type": "application/json", "User-Agent": "rea-video-translate",
                                          "Authorization": f"Bearer {os.environ['REA_VLM_API_KEY']}"})
    err = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                out = json.loads(r.read().decode())["choices"][0]["message"]["content"]
            out = re.sub(r"^\s*<<<\s*\n|\n\s*>>>\s*$", "", out.strip("\n"))
            if out.startswith("```markdown") or out.startswith("```md"):
                out = re.sub(r"^```\w*\n|\n```$", "", out)
            return out
        except Exception as e:
            err = e
            time.sleep(2 + 3 * attempt)
    raise RuntimeError(f"translation failed: {err}")


def chunks(md: str, limit: int = 5000) -> list[str]:
    """Split on level-2/3 headings outside code blocks, then pack sections up to `limit` characters."""
    parts, cur, fence = [], [], False
    for line in md.splitlines(keepends=True):
        if line.lstrip().startswith("```"):
            fence = not fence
        if not fence and re.match(r"#{2,3} ", line) and cur:
            parts.append("".join(cur)); cur = []
        cur.append(line)
    if cur:
        parts.append("".join(cur))
    packed, buf = [], ""
    for p in parts:
        if buf and len(buf) + len(p) > limit:
            packed.append(buf); buf = ""
        buf += p
    if buf:
        packed.append(buf)
    return packed


def translate_file(path: Path) -> None:
    md = path.read_text(encoding="utf-8")
    front = ""
    m = re.match(r"---\n.*?\n---\n", md, re.S)
    if m:
        front, md = m.group(0), md[m.end():]
    pieces = chunks(md)
    with ThreadPoolExecutor(4) as ex:
        out = list(ex.map(ask, pieces))
    body = "".join(o if o.endswith("\n") else o + "\n" for o in out)
    if front:
        name = re.search(r"^name:.*$", front, re.M)
        desc = re.search(r"^description:\s*(.*)$", front, re.M)
        if desc:
            fr = ask("Translate this one-line skill description; keep it on ONE line, keep the trailing English "
                     "'Use when ...' sentence translated as well:\n" + desc.group(1)).strip().replace("\n", " ")
            front = front.replace(desc.group(0), "description: " + fr)
        _ = name
    path.write_text(front + body, encoding="utf-8", newline="\n")
    print(f"{path}: {len(pieces)} part(s)", file=sys.stderr)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--env-file")
    a = ap.parse_args()
    load_env(a.env_file)
    for f in a.files:
        translate_file(Path(f))
    return 0


if __name__ == "__main__":
    sys.exit(main())
