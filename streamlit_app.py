"""Starter app for Streamlit Community Cloud: three plain sections that read results/ and show correct numbers.

Run locally:  bash run_app.sh  (your agent writes it; it runs streamlit run streamlit_app.py)
Build each section up to its required minimum (see the activity website). Keep every number
coming from m11.py, and label every table and plot "Training" or "Test".
"""

from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

import m11

TRAIN = "Training"
TEST = "Test"
SECTIONS = ["1. Beyond Accuracy", "2. A Threshold for the Job", "3. Training vs. Test"]

st.set_page_config(page_title="Judge the Model", layout="wide")

# Space theme: a drifting, twinkling starfield and a floating planet behind the page. Decoration only:
# content sits on a semi-transparent dark panel so text and tables stay readable, and the motion stops
# for people who ask their system for reduced motion. (The dark theme itself is set in .streamlit/config.toml.)
SPACE_CSS = """
<style>
.stApp { background: radial-gradient(ellipse at bottom, #1b2447 0%, #0a0c1c 55%, #05060d 100%); }
.stApp::before, .stApp::after { content: ""; position: fixed; inset: 0; pointer-events: none; z-index: 0;
  filter: drop-shadow(0 0 2px rgba(255, 255, 255, 0.9)); }
.stApp::before {
  background-image:
    radial-gradient(1.8px 1.8px at 20px 30px, #fff, transparent),
    radial-gradient(2.4px 2.4px at 90px 140px, #cfd8ff, transparent),
    radial-gradient(1.8px 1.8px at 160px 70px, #fff, transparent),
    radial-gradient(1.8px 1.8px at 230px 210px, #ffe9c4, transparent),
    radial-gradient(2.4px 2.4px at 300px 120px, #fff, transparent),
    radial-gradient(1.8px 1.8px at 60px 260px, #cfd8ff, transparent),
    radial-gradient(1.8px 1.8px at 340px 300px, #fff, transparent);
  background-size: 360px 340px;
  animation: space-drift 110s linear infinite;
}
.stApp::after {
  background-image:
    radial-gradient(3px 3px at 50px 80px, #fff, transparent),
    radial-gradient(3px 3px at 210px 40px, #bcd0ff, transparent),
    radial-gradient(3.6px 3.6px at 400px 260px, #fff, transparent),
    radial-gradient(3px 3px at 120px 330px, #ffe9c4, transparent);
  background-size: 520px 420px;
  animation: space-drift 60s linear infinite, space-twinkle 4s ease-in-out infinite alternate;
}
.space-planet {
  position: fixed; right: 4vw; bottom: 8vh; width: 110px; height: 110px; border-radius: 50%;
  pointer-events: none; z-index: 0; opacity: 0.55;
  background: radial-gradient(circle at 30% 30%, #ffd6a5, #c9743a 55%, #5a2a14 100%);
  box-shadow: 0 0 40px rgba(255, 170, 90, 0.35);
  animation: space-float 12s ease-in-out infinite alternate;
}
.space-planet::after {
  content: ""; position: absolute; left: -35%; top: 42%; width: 170%; height: 16%;
  border: 2px solid rgba(255, 220, 170, 0.55); border-radius: 50%; transform: rotate(-18deg);
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stVegaLiteChart"], [data-testid="stVegaLiteChart"] canvas, [data-testid="stVegaLiteChart"] svg { background: transparent !important; }
[data-testid="stAppDeployButton"], .stAppDeployButton { display: none; }
[data-testid="stMainBlockContainer"] {
  position: relative; z-index: 1;
  background: rgba(9, 10, 25, 0.62); border-radius: 16px; padding: 2rem 2.5rem 6rem; margin-top: 1rem; margin-bottom: 1rem;
}
@keyframes space-drift { from { background-position: 0 0; } to { background-position: -360px 340px; } }
@keyframes space-twinkle { from { opacity: 0.75; } to { opacity: 1; } }
@keyframes space-float { from { transform: translateY(0); } to { transform: translateY(-18px); } }
@media (prefers-reduced-motion: reduce) {
  .stApp::before, .stApp::after, .space-planet { animation: none; }
}
</style>
<div class="space-planet" aria-hidden="true"></div>
"""
SPACE_THEME = True  # set to False to switch the space background off
if SPACE_THEME:
    st.markdown(SPACE_CSS, unsafe_allow_html=True)

# Music player: a black-hole button fixed at the top right. Click it to play or pause; it spins while the
# music plays. Put your song at static/music.mp3 (served by enableStaticServing in .streamlit/config.toml).
# The player is created once and kept in the page, so the music keeps playing when you change section.
MUSIC_PLAYER = True  # set to False to remove the player
MUSIC_FILE = Path(__file__).resolve().parent / "static" / "music.mp3"
PLAYER_HTML = """
<script>
(function () {
  // The player adds its own stylesheet from script, because the page's HTML cleaner removes style blocks.
  try {
  var style = document.getElementById("bh-style");
  if (!style) {
    style = document.createElement("style");
    style.id = "bh-style";
    document.head.appendChild(style);
  }
  style.textContent = [
    "#bh-player { position: fixed; top: 8px; left: 50%; margin-left: -28px; z-index: 1000000; width: 56px; height: 56px; padding: 0;",
    "  border: 0; border-radius: 50%; background: transparent; cursor: pointer; }",
    "#bh-player.missing { opacity: 0.4; cursor: not-allowed; }",
    "#bh-player .bh { position: relative; width: 100%; height: 100%; transform: rotate(32deg); }",
    "#bh-player .pl-ring { position: absolute; left: 0; top: 0; width: 100%; height: 100%; border-radius: 50%;",
    "  box-sizing: border-box; border: 3px solid rgba(214, 240, 244, 0.8);",
    "  box-shadow: inset 0 0 0 2px rgba(150, 200, 210, 0.35); transform: rotate(-78deg) scaleY(0.26); }",
    "#bh-player .pl-ring-front { clip-path: inset(50% 0 0 0); }",
    "#bh-player .pl-body { position: absolute; left: 22%; top: 22%; width: 56%; height: 56%; border-radius: 50%;",
    "  overflow: hidden; background: #8fdde6; box-shadow: 0 0 10px 1px rgba(130, 225, 238, 0.55); }",
    "#bh-player .pl-bands { position: absolute; left: 0; top: 0; width: 100%; height: 100%;",
    "  background: repeating-linear-gradient(90deg, #b9f3f6 0, #b9f3f6 5px, #79d3de 5px, #79d3de 7px, #a3ebf0 7px, #a3ebf0 12px);",
    "  background-size: 12px 100%; }",
    "#bh-player .pl-shade { position: absolute; left: 0; top: 0; width: 100%; height: 100%; border-radius: 50%;",
    "  background: radial-gradient(circle at 32% 30%, rgba(255, 255, 255, 0.55), rgba(255, 255, 255, 0) 38%, rgba(8, 40, 60, 0.55) 100%); }",
    "#bh-player.playing .pl-bands { animation: pl-spin 1.6s linear infinite; }",
    "#bh-player.playing .pl-body { box-shadow: 0 0 16px 3px rgba(150, 235, 245, 0.85); }",
    "#bh-player:focus-visible { outline: 2px solid #7c9cff; outline-offset: 3px; }",
    "@keyframes pl-spin { from { background-position: 0 0; } to { background-position: 12px 0; } }",
    "@media (prefers-reduced-motion: reduce) { #bh-player.playing .pl-bands { animation: none; } }"
  ].join("\\n");
  if (document.getElementById("bh-player")) return;
  var hasFile = "__HAS_FILE__" === "yes";
  var btn = document.createElement("button");
  btn.id = "bh-player"; btn.type = "button";
  function part(parent, cls) {
    var el = document.createElement("div");
    el.className = cls;
    parent.appendChild(el);
    return el;
  }
  var bh = part(btn, "bh");
  part(bh, "pl-ring pl-ring-back");
  var body = part(bh, "pl-body");
  part(body, "pl-bands");
  part(body, "pl-shade");
  part(bh, "pl-ring pl-ring-front");
  // Try the app's own static folder first; if the host does not serve it, fall back to the same file on GitHub.
  var sources = [
    "/app/static/music.mp3",
    "https://raw.githubusercontent.com/willdotr/judge-the-model/main/static/music.mp3"
  ];
  var which = 0;
  var failed = false;
  var audio = new Audio(sources[0]);
  audio.loop = true; audio.volume = 0.5;
  audio.addEventListener("error", function () {
    console.error("black-hole player: could not load " + sources[which]);
    if (which + 1 === sources.length) {
      failed = true;
      sync();
      return;
    }
    which += 1;
    audio.src = sources[which];
    audio.load();
    audio.play().catch(function () {});
  });
  function sync() {
    var on = !audio.paused;
    btn.classList.toggle("playing", on);
    btn.setAttribute("aria-pressed", on ? "true" : "false");
    var label = !hasFile ? "Music file not added yet" : (failed ? "Music could not be loaded" : (on ? "Pause music" : "Play music"));
    btn.title = label; btn.setAttribute("aria-label", label);
  }
  if (!hasFile) btn.classList.add("missing");
  btn.addEventListener("click", function () {
    if (!hasFile) return;
    if (audio.paused) {
      audio.play().catch(function (e) { console.error("black-hole player: play() was refused:", e); });
    } else { audio.pause(); }
  });
  audio.addEventListener("play", sync); audio.addEventListener("pause", sync);
  sync();
  document.body.appendChild(btn);
  } catch (e) { console.error("black-hole player failed:", e); }
})();
</script>
"""
if MUSIC_PLAYER:
    st.html(PLAYER_HTML.replace("__HAS_FILE__", "yes" if MUSIC_FILE.exists() else "no"), unsafe_allow_javascript=True)


@st.cache_data
def load(name: str):
    return m11.load(name)


def starter_note(text: str) -> None:
    st.info(f"Starter display: {text} Build this section up to its required minimum.")


def recommendations() -> None:
    d = load("decisions")
    recs = (d or {}).get("recommendations", {})
    with st.container(border=True):
        st.subheader("Recommendations")
        if not any(recs.values()):
            st.caption("No recommendations yet: fill in `Recommendations` in DECISIONS.md, run "
                       "`python -m analysis`, then commit and push.")
        for k in m11.DATASETS:
            if any(recs.values()):
                st.markdown(f"**{m11.DATASET_LABEL[k]}:** {recs.get(k) or '_not written yet_'}")


# ---- 1. Beyond Accuracy ------------------------------------------------------
THRESHOLD = 0.5
# Words only (no numbers): how each dataset's two groups of patients are named.
GROUPS = {
    "readmission": {"pos": "Readmitted within 30 days", "neg": "Not readmitted within 30 days",
                    "pos_verb": "were readmitted within 30 days", "neg_verb": "were not readmitted within 30 days"},
    "diabetes": {"pos": "Diabetes", "neg": "No diabetes",
                 "pos_verb": "have diabetes (doctor diagnosis or HbA1c ≥ 6.5%)", "neg_verb": "do not have diabetes"},
}


def matrix_df(c: dict, g: dict) -> pd.DataFrame:
    """Confusion matrix: rows = actual, columns = predicted. 'Flagged' means predicted positive."""
    return pd.DataFrame(
        [[c["tp"], c["fn"]], [c["fp"], c["tn"]]],
        index=[f"Actual: {g['pos']}", f"Actual: {g['neg']}"],
        columns=["Predicted: flagged", "Predicted: not flagged"],
    )


def beyond_accuracy(res: dict, model: str) -> None:
    g = GROUPS[res["dataset"]]
    p, y = m11.preds(res, model)
    c = m11.confusion(p, y, THRESHOLD)
    m = m11.metrics(c)
    tab_one, tab_all = st.tabs(["One model", "Compare all five"])

    with tab_one:
        common = g["pos"] if (m["prevalence"] or 0) >= 0.5 else g["neg"]
        st.markdown(
            f"**Prevalence:** {m11.fmt_pct(m['prevalence'])} of the {m['n']:,} test patients {g['pos_verb']}.  \n"
            f"**Baseline accuracy:** saying \"{common}\" for every patient (the most common group) would be right "
            f"{m11.fmt_pct(m11.majority_accuracy(y))} of the time."
        )
        st.caption(f"{TEST} · {m11.MODEL_LABEL[model]}, threshold 0.50 · rows = actual, columns = predicted "
                   "(\"flagged\" = the model predicts the positive class)")
        st.table(matrix_df(c, g))
        st.markdown(
            f"**Sensitivity: {m11.fmt_pct(m['sensitivity'])}.** Of the {m['positives']:,} test patients who {g['pos_verb']}, "
            f"the model flagged {c['tp']:,}.  \n"
            f"**Specificity: {m11.fmt_pct(m['specificity'])}.** Of the {m['negatives']:,} test patients who {g['neg_verb']}, "
            f"the model did not flag {c['tn']:,}.  \n"
            + (f"**Precision: {m11.fmt_pct(m['precision'])}.** Of the {m['flagged']:,} test patients the model flagged, "
               f"{c['tp']:,} {g['pos_verb']}."
               if m["flagged"] else
               "**Precision: undefined.** The model flagged no test patients, so there is no one to divide by (0 ÷ 0).")
        )

    with tab_all:
        shown = [k for k in m11.MODELS if k in res["models"]]
        st.caption(f"{TEST} · all models at threshold 0.50 · rows = actual, columns = predicted")
        cols = st.columns(len(shown))
        rows = []
        for col, k in zip(cols, shown):
            pk, yk = m11.preds(res, k)
            ck = m11.confusion(pk, yk, THRESHOLD)
            mk = m11.metrics(ck)
            with col:
                st.markdown(f"**{m11.MODEL_LABEL[k]}**")
                st.table(pd.DataFrame([[ck["tp"], ck["fn"]], [ck["fp"], ck["tn"]]],
                                      index=["Actual +", "Actual −"], columns=["Flagged", "Not flagged"]))
            rows.append({"Model": m11.MODEL_LABEL[k], "Accuracy": m11.fmt_pct(mk["accuracy"]),
                         "Sensitivity (recall, TPR)": m11.fmt_pct(mk["sensitivity"]),
                         "Specificity": m11.fmt_pct(mk["specificity"]), "FPR (1 − specificity)": m11.fmt_pct(mk["fpr"]),
                         "Precision": m11.fmt_pct(mk["precision"]), "F1": m11.fmt_pct(mk["f1"])})
        st.caption(f"{TEST} · metrics at threshold 0.50 · \"Actual +\" = {g['pos'].lower()}, \"Actual −\" = {g['neg'].lower()}")
        st.table(pd.DataFrame(rows).set_index("Model"))


# ---- 2. A Threshold for the Job ------------------------------------------------
def metrics_df(m: dict) -> pd.DataFrame:
    """One column of metrics; undefined values (0 ÷ 0) show as "undefined"."""
    return pd.DataFrame({"Value": {
        "Flagged per 100 patients": m11.fmt_num(m["flagged_per_100"], 1),
        "Accuracy": m11.fmt_pct(m["accuracy"]),
        "Sensitivity (recall, TPR)": m11.fmt_pct(m["sensitivity"]),
        "Specificity": m11.fmt_pct(m["specificity"]),
        "FPR (1 − specificity)": m11.fmt_pct(m["fpr"]),
        "Precision": m11.fmt_pct(m["precision"]),
        "F1": m11.fmt_pct(m["f1"]),
    }})


def threshold(res: dict, model: str) -> None:
    g = GROUPS[res["dataset"]]
    p, y = m11.preds(res, model)
    t = st.slider("Threshold: a patient is flagged when the model's probability is at least this value",
                  0.0, 1.0, 0.5, 0.01)
    left, right = st.columns(2)
    for col, thr, title in [(left, 0.5, "At 0.50"), (right, t, f"At your threshold, {t:.2f}")]:
        c = m11.confusion(p, y, thr)
        m = m11.metrics(c)
        with col:
            st.subheader(title)
            st.caption(f"{TEST} · {m11.MODEL_LABEL[model]}, threshold {thr:.2f} · rows = actual, columns = predicted")
            st.table(matrix_df(c, g))
            st.caption(f"{TEST} · metrics at threshold {thr:.2f}")
            st.table(metrics_df(m))
            st.caption(f"Flagged per 100: of every 100 test patients, how many the model flags "
                       f"({m['flagged']:,} of {m['n']:,} flagged).")


# ---- 3. Training vs. Test ------------------------------------------------------
def series_colors() -> list[str]:
    """Training, Test: categorical slots 1 and 2 of the validated palette, stepped for the page's light or dark theme."""
    try:
        dark = st.context.theme.type == "dark"
    except Exception:  # noqa: BLE001  (older Streamlit, or no theme info)
        dark = False
    return ["#3987e5", "#d95926"] if dark else ["#2a78d6", "#eb6834"]


def train_vs_test(res: dict, model: str) -> None:
    s = m11.auroc_summary(res)
    order = [m11.MODEL_LABEL[m] for m in s]

    st.markdown(
        f"**{TRAIN}:** {res['train']['n']:,} patients ({res['train']['n_pos']:,} positive), the rows each model learned from.  \n"
        f"**{TEST}:** {res['test']['n']:,} patients ({res['test']['n_pos']:,} positive), rows no model saw while learning."
    )
    st.caption("AUROC is about ranking: how often a patient who had the outcome gets a higher probability than one who did "
               "not. It is not accuracy, and it does not choose a threshold. Each AUROC rests on the patients counted above.")

    # Chart: one Training bar and one Test bar per model (undefined AUROCs are left out, never drawn as 0).
    long = pd.DataFrame([{"Model": m11.MODEL_LABEL[m], "Partition": part, "AUROC": v[key]}
                         for m, v in s.items() for part, key in [(TRAIN, "train"), (TEST, "test")] if v[key] is not None])
    enc = dict(
        x=alt.X("Model:N", sort=order, title=None, axis=alt.Axis(labelAngle=0, labelLimit=140)),
        xOffset=alt.XOffset("Partition:N", sort=[TRAIN, TEST]),
        y=alt.Y("AUROC:Q", scale=alt.Scale(domain=[0, 1]), title="AUROC (ranking, not accuracy)"),
        color=alt.Color("Partition:N", sort=[TRAIN, TEST], scale=alt.Scale(domain=[TRAIN, TEST], range=series_colors()),
                        legend=alt.Legend(title=None, orient="top")),
        tooltip=[alt.Tooltip("Model:N"), alt.Tooltip("Partition:N"), alt.Tooltip("AUROC:Q", format=".3f")],
    )
    base = alt.Chart(long).encode(**enc)
    bars = base.mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
    values = base.mark_text(dy=-7, fontSize=11).encode(text=alt.Text("AUROC:Q", format=".3f"))
    chance = alt.Chart(pd.DataFrame({"y": [0.5]})).mark_rule(strokeDash=[6, 4], strokeWidth=2.5, color="#d03b3b", opacity=1).encode(y="y:Q")
    st.caption(f"{TRAIN} and {TEST} AUROC for every model · red dashed line = 0.5, the same as ranking no better than chance")
    chart = (bars + values + chance).configure(background="rgba(0,0,0,0)").configure_view(fill=None, stroke=None)
    st.altair_chart(chart, width="stretch")

    rows = [{"Model": m11.MODEL_LABEL[m], f"{TRAIN} AUROC": m11.fmt_num(v["train"]), f"{TEST} AUROC": m11.fmt_num(v["test"]),
             f"Gap ({TRAIN.lower()} − {TEST.lower()})": m11.fmt_num(v["gap"])} for m, v in s.items()]
    st.caption(f"{TRAIN} and {TEST} · the same AUROCs in a table, with the gap between them")
    st.table(pd.DataFrame(rows).set_index("Model"))
    st.caption("A large positive gap means the model did much better on the patients it learned from than on patients it "
               "never saw, a sign it memorised its training patients. The training AUROC flatters every model, so only the "
               "test AUROC is what to expect on new patients.")


RENDER = dict(zip(SECTIONS, [beyond_accuracy, threshold, train_vs_test]))


# ---- Main menu: the first page anyone sees --------------------------------------
JOBS = {
    "readmission": "Predict readmission within 30 days, at discharge.",
    "diabetes": "Flag adults for follow-up testing; finding positives matters most.",
}
SECTION_INFO = {
    SECTIONS[0]: "Name the positive class, see why accuracy alone can mislead, read a confusion matrix as four groups of "
                 "patients, and compare every model at a threshold of 0.50.",
    SECTIONS[1]: "See that the threshold is a decision separate from the model, and what moving it gains and gives up "
                 "compared with 0.50.",
    SECTIONS[2]: "See why a model is judged on patients it never saw, and spot a model that memorised its training patients.",
}


def main_menu() -> None:
    st.markdown(
        "<div style='text-align:center; padding: 1.5rem 0 0.5rem'>"
        "<h1 style='font-size:3rem; margin:0'>Classification Activity</h1>"
        "<p style='font-size:1.2rem; margin:0.4rem 0 0; opacity:0.85'>Generated by Willie Robinson</p></div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center; font-size:1.05rem'>Which classifier would you trust for this job, "
        "at what threshold, and with what limits?</p>",
        unsafe_allow_html=True,
    )
    st.write(
        "This app helps a clinical lead judge whether a prediction model is fit for a job. It compares a "
        "prevalence baseline with four classifiers (logistic regression, k-nearest neighbours, random forest and "
        "gradient boosting) on two health datasets. Every number comes from results exported by the Python analysis, "
        "and the app never retrains a model."
    )

    st.subheader("The two jobs")
    cols = st.columns(2)
    for col, k in zip(cols, m11.DATASETS):
        r = load(k)
        with col, st.container(border=True):
            st.markdown(f"**{m11.DATASET_LABEL[k]}**")
            st.write(JOBS[k])
            st.caption(f"Positive class: {GROUPS[k]['pos'].lower()}.")
            if r:
                st.caption(f"{r['train']['n']:,} {TRAIN.lower()} patients and {r['test']['n']:,} {TEST.lower()} patients.")

    st.subheader("The three sections")
    for s in SECTIONS:
        st.markdown(f"**{s}.** {SECTION_INFO[s]}")

    st.subheader("How to read it")
    st.markdown(
        f"- **{TRAIN} or {TEST}:** every table and chart says which it is. A model learns from the {TRAIN.lower()} "
        f"patients, so {TRAIN.lower()} results flatter it. Only {TEST.lower()} results, on patients the model never "
        "saw, show what to expect on new patients.\n"
        "- **AUROC** is about ranking: how often a patient who had the outcome gets a higher probability than one "
        "who did not. It is not accuracy, and it does not choose a threshold.\n"
        "- **Associations, not causes:** the app shows what the models flagged and how that compared with the "
        "actual outcomes. It does not say what causes either outcome."
    )

    # The button is fixed to the top left of the screen, so it never covers text when scrolling, with dark text on a light fill so the label is readable.
    st.markdown(
        """
<style>
.st-key-explore { position: fixed; left: 0; top: 14px; z-index: 1000000; width: auto; }
.st-key-explore button { background: #8fb0ff; border: 0; border-radius: 0 14px 14px 0; padding: 0.9rem 1.1rem;
  box-shadow: 0 0 18px rgba(124, 156, 255, 0.55); }
.st-key-explore button, .st-key-explore button p, .st-key-explore button div { color: #0b0b1a !important; font-weight: 700; }
.st-key-explore button:hover { background: #b5ccff; }
</style>
""",
        unsafe_allow_html=True,
    )
    if st.button("Click here to explore", key="explore", type="primary"):
        st.session_state.page = "app"
        st.rerun()


if st.session_state.get("page", "menu") == "menu":
    main_menu()
    st.stop()

if st.sidebar.button("← Main menu", width="stretch"):
    st.session_state.page = "menu"
    st.rerun()

st.title("Judge the Model")
st.caption("Which classifier would you trust for this job, at what threshold, and with what limits?")
recommendations()
section = st.sidebar.radio("Section", SECTIONS)
key = st.sidebar.selectbox("Dataset", m11.DATASETS, format_func=m11.DATASET_LABEL.get)
res = load(key)
model = st.sidebar.selectbox("Model", m11.MODELS,
                             format_func=lambda m: m11.MODEL_LABEL[m] + ("" if m in res["models"] else " (not trained yet)"))
st.header(section)
st.caption(f"{m11.DATASET_LABEL[key]}: {res['train']['n']:,} training rows ({res['train']['n_pos']:,} positive), "
           f"{res['test']['n']:,} test rows ({res['test']['n_pos']:,} positive).")
if model in res["models"]:
    RENDER[section](res, model)
else:
    st.warning(f"{m11.MODEL_LABEL[model]} has no results yet: run `python -m analysis`, then commit and push `results/`.")
