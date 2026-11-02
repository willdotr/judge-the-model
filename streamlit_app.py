"""Starter app for Streamlit Community Cloud: three plain sections that read results/ and show correct numbers.

Run locally:  bash run_app.sh  (your agent writes it; it runs streamlit run streamlit_app.py)
Build each section up to its required minimum (see the activity website). Keep every number
coming from m11.py, and label every table and plot "Training" or "Test".
"""

import altair as alt
import pandas as pd
import streamlit as st

import m11

TRAIN = "Training"
TEST = "Test"
SECTIONS = ["1. Beyond Accuracy", "2. A Threshold for the Job", "3. Training vs. Test"]

st.set_page_config(page_title="Judge the Model", layout="wide")


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
    st.altair_chart(bars + values + chance, width="stretch")

    rows = [{"Model": m11.MODEL_LABEL[m], f"{TRAIN} AUROC": m11.fmt_num(v["train"]), f"{TEST} AUROC": m11.fmt_num(v["test"]),
             f"Gap ({TRAIN.lower()} − {TEST.lower()})": m11.fmt_num(v["gap"])} for m, v in s.items()]
    st.caption(f"{TRAIN} and {TEST} · the same AUROCs in a table, with the gap between them")
    st.table(pd.DataFrame(rows).set_index("Model"))
    st.caption("A large positive gap means the model did much better on the patients it learned from than on patients it "
               "never saw, a sign it memorised its training patients. The training AUROC flatters every model, so only the "
               "test AUROC is what to expect on new patients.")


RENDER = dict(zip(SECTIONS, [beyond_accuracy, threshold, train_vs_test]))

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
