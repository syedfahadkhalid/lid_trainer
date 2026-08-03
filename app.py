"""
Leben in Deutschland / Einbürgerungstest Trainer
================================================
Official BAMF question catalogue (Stand 07.05.2025):
300 general questions + 10 Bayern questions.

Run with:  streamlit run app.py
"""

import json
import random
from pathlib import Path

import streamlit as st

APP_DIR = Path(__file__).parent
DATA_FILE = APP_DIR / "data" / "questions.json"
PROGRESS_FILE = APP_DIR / "progress.json"
PER_PAGE = 10
LETTERS = ["A", "B", "C", "D"]

st.set_page_config(page_title="LiD Trainer", page_icon="🇩🇪", layout="centered")


# --------------------------------------------------------------------------
# Data
# --------------------------------------------------------------------------
@st.cache_data
def load_questions():
    with open(DATA_FILE, encoding="utf-8") as fh:
        return json.load(fh)


def load_progress():
    if PROGRESS_FILE.exists():
        try:
            with open(PROGRESS_FILE, encoding="utf-8") as fh:
                data = json.load(fh)
                if isinstance(data.get("answers"), dict):
                    return data
        except (json.JSONDecodeError, OSError):
            pass
    return {"answers": {}}


def save_progress(progress):
    tmp = PROGRESS_FILE.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(progress, fh, ensure_ascii=False, indent=1)
    tmp.replace(PROGRESS_FILE)


QUESTIONS = load_questions()
BY_ID = {q["id"]: q for q in QUESTIONS}

if "progress" not in st.session_state:
    st.session_state.progress = load_progress()
if "page" not in st.session_state:
    st.session_state.page = 0
if "exam_ids" not in st.session_state:
    st.session_state.exam_ids = None

progress = st.session_state.progress
answers = progress["answers"]


def record(qid, status, selected=None):
    entry = answers.get(qid, {})
    entry["status"] = status
    if selected is not None:
        entry["selected"] = selected
    answers[qid] = entry
    save_progress(progress)


def stats():
    correct = sum(1 for a in answers.values() if a.get("status") == "correct")
    wrong = sum(1 for a in answers.values() if a.get("status") == "wrong")
    revealed = sum(1 for a in answers.values() if a.get("status") == "revealed")
    return correct, wrong, revealed


# --------------------------------------------------------------------------
# Sidebar
# --------------------------------------------------------------------------
correct, wrong, revealed = stats()
answered = correct + wrong

with st.sidebar:
    st.markdown("### 📊 Dein Punktestand")

    c1, c2 = st.columns(2)
    c1.metric("✅ Richtig", correct)
    c2.metric("❌ Falsch", wrong)

    accuracy = (correct / answered * 100) if answered else 0.0
    st.metric("Trefferquote", f"{accuracy:.0f} %")
    if revealed:
        st.caption(f"👁 {revealed} Frage(n) nur aufgedeckt (nicht gewertet)")

    st.progress(min(answered / len(QUESTIONS), 1.0))
    st.caption(f"{answered} von {len(QUESTIONS)} Fragen beantwortet")

    # Pass-mark simulation: the real test is 33 questions, 15 needed to pass
    if answered >= 10:
        projected = accuracy / 100 * 33
        if projected >= 15:
            st.success(f"Hochgerechnet auf 33 Fragen: **{projected:.0f}/33** — bestanden ✅ (15 nötig)")
        else:
            st.warning(f"Hochgerechnet auf 33 Fragen: **{projected:.0f}/33** — noch nicht bestanden (15 nötig)")

    st.divider()
    st.markdown("### ⚙️ Einstellungen")

    show_en = st.toggle("Englische Übersetzung zeigen", value=True)
    show_hints_open = st.toggle("Vokabelhilfe automatisch öffnen", value=False)

    mode = st.selectbox(
        "Fragen-Auswahl",
        [
            "Alle Fragen (310)",
            "Nur Allgemein (300)",
            "Nur Bayern (10)",
            "Nur noch nicht beantwortet",
            "Nur falsch beantwortete",
            "Prüfungssimulation (33 zufällig)",
        ],
    )

    if mode == "Prüfungssimulation (33 zufällig)":
        if st.button("🎲 Neue Prüfung würfeln", width="stretch"):
            general = [q["id"] for q in QUESTIONS if q["section"] == "Allgemein"]
            bayern = [q["id"] for q in QUESTIONS if q["section"] == "Bayern"]
            st.session_state.exam_ids = random.sample(general, 30) + random.sample(bayern, 3)
            st.session_state.page = 0
            st.rerun()

    st.divider()
    st.markdown("### 🔄 Zurücksetzen")
    confirm = st.checkbox("Ich bin sicher")
    if st.button("Punktestand zurücksetzen", disabled=not confirm,
                 type="primary", width="stretch"):
        # Clear the widget state too, otherwise the old selections stay
        # visible in the radios after the score has been wiped.
        for k in [k for k in st.session_state
                  if k.startswith("radio_") or k.startswith("show_")]:
            del st.session_state[k]
        st.session_state.progress = {"answers": {}}
        save_progress(st.session_state.progress)
        st.session_state.page = 0
        st.session_state.exam_ids = None
        st.rerun()

    st.divider()
    st.caption(
        "Quelle: BAMF Gesamtfragenkatalog „Leben in Deutschland“ / "
        "„Einbürgerungstest“, Stand 07.05.2025.\n\n"
        "**Bestehensgrenze Niederlassungserlaubnis: 15 von 33.** "
        "Für die Einbürgerung: 17 von 33."
    )


# --------------------------------------------------------------------------
# Filtering
# --------------------------------------------------------------------------
if mode == "Nur Allgemein (300)":
    pool = [q for q in QUESTIONS if q["section"] == "Allgemein"]
elif mode == "Nur Bayern (10)":
    pool = [q for q in QUESTIONS if q["section"] == "Bayern"]
elif mode == "Nur noch nicht beantwortet":
    pool = [q for q in QUESTIONS if q["id"] not in answers]
elif mode == "Nur falsch beantwortete":
    pool = [q for q in QUESTIONS if answers.get(q["id"], {}).get("status") == "wrong"]
elif mode == "Prüfungssimulation (33 zufällig)":
    if st.session_state.exam_ids is None:
        general = [q["id"] for q in QUESTIONS if q["section"] == "Allgemein"]
        bayern = [q["id"] for q in QUESTIONS if q["section"] == "Bayern"]
        st.session_state.exam_ids = random.sample(general, 30) + random.sample(bayern, 3)
    pool = [BY_ID[i] for i in st.session_state.exam_ids]
else:
    pool = QUESTIONS

st.title("🇩🇪 Leben in Deutschland — Trainer")
st.caption("BAMF Gesamtfragenkatalog · 300 allgemeine Fragen + 10 Fragen für Bayern")

if not pool:
    st.success("🎉 Nichts zu tun in dieser Auswahl — gut gemacht!")
    st.stop()

total_pages = (len(pool) + PER_PAGE - 1) // PER_PAGE
st.session_state.page = max(0, min(st.session_state.page, total_pages - 1))
page = st.session_state.page


def nav(key_prefix):
    n1, n2, n3 = st.columns([1, 2, 1])
    with n1:
        if st.button("← Zurück", disabled=page == 0,
                     key=f"{key_prefix}_prev", width="stretch"):
            st.session_state.page -= 1
            st.rerun()
    with n2:
        st.markdown(
            f"<div style='text-align:center;padding-top:6px'>"
            f"<b>Seite {page + 1} von {total_pages}</b></div>",
            unsafe_allow_html=True,
        )
    with n3:
        if st.button("Weiter →", disabled=page >= total_pages - 1,
                     key=f"{key_prefix}_next", width="stretch"):
            st.session_state.page += 1
            st.rerun()


nav("top")
st.divider()

chunk = pool[page * PER_PAGE:(page + 1) * PER_PAGE]

# --------------------------------------------------------------------------
# Questions
# --------------------------------------------------------------------------
for idx, q in enumerate(chunk, start=page * PER_PAGE + 1):
    qid = q["id"]
    saved = answers.get(qid, {})
    status = saved.get("status")

    badge = {"correct": "✅", "wrong": "❌", "revealed": "👁"}.get(status, "⬜")
    label = "Bayern" if q["section"] == "Bayern" else "Allgemein"

    with st.container(border=True):
        st.markdown(f"**{badge} Frage {idx} — {label} Nr. {q['num']}**")
        st.markdown(f"### {q['question']}")
        if show_en:
            st.markdown(f":gray[*{q['q_en']}*]")

        # Context image (map, photo, ballot paper)
        if q.get("image"):
            img_path = APP_DIR / q["image"]
            if img_path.exists():
                st.image(str(img_path), width="stretch")

        # Four candidate images (coats of arms, flags)
        if q.get("option_images"):
            cols = st.columns(4)
            for i, rel in enumerate(q["option_images"]):
                p = APP_DIR / rel
                if p.exists():
                    with cols[i]:
                        st.image(str(p), caption=f"Bild {i + 1}", width="stretch")

        # Vocabulary hints
        if q.get("hints"):
            with st.expander("💡 Vokabelhilfe (Wörter zum Merken)", expanded=show_hints_open):
                for h in q["hints"]:
                    st.markdown(f"- **{h['de']}** — {h['en']}")

        # Options
        # NOTE: q is bound as a default argument on purpose. Streamlit may call
        # format_func after this loop iteration has ended, so a late-binding
        # closure over `q` would format every radio with the last question.
        def fmt(i, _q=q, _en=show_en):
            de = _q["options"][i]
            if _en and _q["opts_en"][i]:
                return f"**{LETTERS[i]})** {de}  ·  :gray[*{_q['opts_en'][i]}*]"
            return f"**{LETTERS[i]})** {de}"

        prev_sel = saved.get("selected")
        choice = st.radio(
            "Antwort wählen:",
            options=[0, 1, 2, 3],
            format_func=fmt,
            index=prev_sel if isinstance(prev_sel, int) else None,
            key=f"radio_{qid}",
            label_visibility="collapsed",
        )

        b1, b2, b3 = st.columns([1, 1, 2])
        checked = b1.button("Antwort prüfen", key=f"check_{qid}",
                            width="stretch", type="primary")
        reveal = b2.button("Lösung zeigen", key=f"reveal_{qid}",
                           width="stretch")

        if checked:
            if choice is None:
                st.warning("Bitte zuerst eine Antwort auswählen.")
            else:
                ok = choice == q["answer"]
                record(qid, "correct" if ok else "wrong", selected=choice)
                st.rerun()

        if reveal:
            if status is None:
                record(qid, "revealed", selected=choice)
            st.session_state[f"show_{qid}"] = True

        # Feedback
        ans = q["answer"]
        correct_txt = f"**{LETTERS[ans]})** {q['options'][ans]}"

        if status == "correct":
            st.success(f"✅ Richtig! {correct_txt}")
            if q.get("tip"):
                st.caption(f"💬 {q['tip']}")
        elif status == "wrong":
            sel = saved.get("selected")
            st.error(
                f"❌ Falsch. Du hattest **{LETTERS[sel]})**. "
                f"Richtig ist: {correct_txt}"
            )
            if q.get("tip"):
                st.caption(f"💬 {q['tip']}")
        elif st.session_state.get(f"show_{qid}"):
            st.info(f"👁 Lösung: {correct_txt}")
            if q.get("tip"):
                st.caption(f"💬 {q['tip']}")

        if status in ("correct", "wrong", "revealed"):
            if st.button("↺ Diese Frage zurücksetzen", key=f"rst_{qid}"):
                answers.pop(qid, None)
                st.session_state.pop(f"show_{qid}", None)
                st.session_state.pop(f"radio_{qid}", None)
                save_progress(progress)
                st.rerun()

st.divider()
nav("bottom")
