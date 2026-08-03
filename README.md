# 🇩🇪 Leben in Deutschland — Trainer

A Streamlit study app built from the official **BAMF Gesamtfragenkatalog** (Stand 07.05.2025).
Contains **300 general questions + 10 Bayern questions = 310**, every one with an English
translation, beginner vocabulary hints, and a memory tip.

Your real test draws **33 questions** from this pool (30 general + 3 Bayern).
**Pass mark for the Niederlassungserlaubnis: 15 / 33.**

---

## Run it

```bash
cd lid_trainer
pip install -r requirements.txt
streamlit run app.py
```

It opens at `http://localhost:8501`. Press `Ctrl+C` in the terminal to stop.

If `streamlit` isn't found after install, use `python3 -m streamlit run app.py`.

---

## What it does

**10 questions per page**, 31 pages. For each question:

- German question + English translation (translations can be toggled off in the sidebar)
- Four options, each with its English translation
- **💡 Vokabelhilfe** — the key German words in the question, in dictionary form with articles
- **Antwort prüfen** — check your selection; scores as right or wrong
- **Lösung zeigen** — reveal the answer without guessing; logged separately, does *not* count against your score
- **💬 Tip** — one line on why the answer is correct
- Real images for all 13 picture questions (coats of arms, EU flag, occupation-zone map, ballot papers, Bavaria map, Reichstag, Bundestag plenary, Willy Brandt, Mitterrand/Kohl, GDR flag)

**Sidebar:**

| Control | What it does |
|---|---|
| Punktestand | Live count of correct / wrong / accuracy |
| Hochrechnung | Projects your accuracy onto a real 33-question test and tells you whether you'd pass |
| Fragen-Auswahl | All · General only · Bayern only · Unanswered only · **Wrong only** · **Exam simulation (33 random)** |
| Englische Übersetzung | Toggle English on/off — turn it off in the last week to test yourself properly |
| Punktestand zurücksetzen | Wipes all progress (needs the confirm checkbox) |

Each question also has its own **↺ reset** so you can redo just that one.

---

## How to actually use it

1. **First pass** — work through all 31 pages with English on. Don't worry about the score.
2. **Second pass** — switch to *Nur falsch beantwortete* and grind only your mistakes.
3. **Third pass** — turn English off, run *Prüfungssimulation* repeatedly until you clear 15/33 comfortably. Aim for 25+ so you have margin.

Don't start this before your Goethe A1 exam in mid-September — it'll dilute the language work.
Two focused weekends after the A1 is plenty.

---

## Files

```
lid_trainer/
├── app.py                 the application
├── requirements.txt       streamlit>=1.50
├── data/questions.json    all 310 questions + answers + translations + hints
├── assets/                25 extracted images for the 13 picture questions
└── progress.json          your score (created on first answer)
```

`progress.json` is the "database" — plain JSON, one entry per question:

```json
{"answers": {"G1": {"status": "correct", "selected": 3}}}
```

Delete that file and your score is gone; back it up and you can move your progress
to another machine. Nothing leaves your computer.

---

## Source & accuracy

Questions and images are extracted directly from
`gesamtfragenkatalog-lebenindeutschland.pdf` (BAMF, Stand 07.05.2025), which publishes
the questions **without** an answer key. The correct answers, translations, hints and
tips in `data/questions.json` were generated separately and cross-checked against the
published BAMF answer keys.

If you ever find an answer you believe is wrong, edit `data/questions.json` directly —
the `answer` field is the 0-based index into that question's `options` array.

Two items are time-sensitive and reflect the 07.05.2025 catalogue: **G72** (current
Chancellor) and **G73** (largest Bundestag groups). Re-check those against the version
of the catalogue in force on your test date.
