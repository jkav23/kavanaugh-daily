#!/usr/bin/env python3
"""Generate an accessible, factual news headline recording with Kokoro neural TTS.

The model runs locally inside GitHub Actions (not in readers' browsers).
Based only on published headline metadata; does not invent article summaries.
"""
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf
import imageio_ffmpeg
from kokoro_onnx import Kokoro

ROOT = Path(__file__).resolve().parents[1]
NEWS = ROOT / "news.json"
AUDIO = ROOT / "briefing.mp3"
TRANSCRIPT = ROOT / "briefing.txt"
MODEL_DIR = Path(os.environ.get("KOKORO_MODEL_DIR", str(ROOT / ".voice-model")))
MODEL = MODEL_DIR / "kokoro-v1.0.onnx"
VOICES = MODEL_DIR / "voices-v1.0.bin"

SECTION_PLAN = (
    ("Cape Breton", "First, here's what's making news across Cape Breton.", 4),
    ("Nova Scotia", "Turning to the rest of Nova Scotia.", 3),
    ("Canada", "Across Canada now.", 3),
    ("World", "Here are some of the international headlines.", 3),
    ("Business", "In business and the economy.", 2),
    ("Health", "Turning to health news.", 2),
    ("Sports", "And finally, in sports, including the latest in hockey, football, and mixed martial arts.", 7),
)

def pronounce(s):
    """Expand common initials so the narrator does not say them as words."""
    s = re.sub(r"\s+", " ", str(s)).strip()
    for a, b in [
        ("CBRM", "C. B. R. M."), ("NHL", "N. H. L."),
        ("NFL", "N. F. L."), ("MLB", "M. L. B."),
        ("NBA", "N. B. A."), ("UFC", "U. F. C."),
        ("PFL", "P. F. L."), ("MMA", "M. M. A."),
    ]:
        s = re.sub(r"\b" + a + r"\b", b, s)
    return s

def script_parts(articles):
    parts = [
        "Welcome to The Kavanaugh Daily. Your news, starting close to home in Cape Breton.",
        "This is a brief roundup of selected headlines. Follow the links on the website for the full reporting.",
    ]
    for section, transition, limit in SECTION_PLAN:
        selected = [a for a in articles if a.get("category") == section][:limit]
        if not selected:
            continue
        parts.append(transition)
        for a in selected:
            title = pronounce(a.get("title", ""))[:270].strip().rstrip(" .")
            if title:
                parts.append(title + ".")
    parts.append("That's your headline roundup from The Kavanaugh Daily. Thanks for listening.")
    return parts

def main():
    articles = json.loads(NEWS.read_text(encoding="utf-8"))["articles"]
    parts = script_parts(articles)
    if len(parts) < 8:
        raise RuntimeError("Not enough articles for a meaningful audio briefing")
    TRANSCRIPT.write_text("\n\n".join(parts) + "\n", encoding="utf-8")
    print("Creating neural narration for", len(parts), "segments")
    if not MODEL.is_file() or not VOICES.is_file():
        raise FileNotFoundError("Neural speech model files are missing")
    engine = Kokoro(str(MODEL), str(VOICES))
    segments = []
    sample_rate = None
    try:
        for i, segment in enumerate(parts):
            # Each chunk is shorter than the model's text-context limit.
            audio, rate = engine.create(segment, voice="af_heart", speed=1.02, lang="en-us")
            if sample_rate is None:
                sample_rate = rate
            if rate != sample_rate:
                raise ValueError("Unexpected sample rate change")
            if len(audio):
                segments.append(np.asarray(audio, dtype=np.float32))
                segments.append(np.zeros(round(rate * (0.48 if i in [0, 1] else 0.24)), dtype=np.float32))
    finally:
        engine.voices.close()
    if not segments:
        raise RuntimeError("Speech model produced no audio")
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "briefing.wav"
        sf.write(str(wav), np.concatenate(segments), sample_rate)
        subprocess.run(
            [imageio_ffmpeg.get_ffmpeg_exe(), "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
             "-i", str(wav), "-codec:a", "libmp3lame", "-b:a", "80k", "-ac", "1",
             str(AUDIO)],
            check=True,
        )
    print("Created", AUDIO.name, "with", round(AUDIO.stat().st_size / 1024), "KB")

if __name__ == "__main__":
    main()
