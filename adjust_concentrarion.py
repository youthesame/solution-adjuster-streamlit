from datetime import datetime

import plotly.graph_objects as go
import streamlit as st

# ページ設定
st.set_page_config(page_title="濃度計算ツール", layout="centered")
st.markdown(
    """<style>
    button[kind="secondary"] span[data-testid="stIconMaterial"] {
        font-size: 1.5rem;
    }
    </style>""",
    unsafe_allow_html=True,
)
st.title("濃度計算ツール")

# 設定
with st.container(border=True):
    col_mode, col_unit = st.columns([2, 1])
    mode = col_mode.radio("求めたい値", ["wt%", "溶質量", "溶媒量"], horizontal=True)
    unit = col_unit.selectbox("質量の単位", ["μg", "mg", "g"], index=1)

# 単位換算係数 (入力単位 → mg)
factor = {"mg": 1.0, "g": 1000.0, "μg": 0.001}[unit]


# 計算関数
def calc_wt(solute_mg, solvent_mg):
    total = solute_mg + solvent_mg
    return 100.0 * solute_mg / total if total > 0 else None


def calc_solute(wt, solvent_mg):
    return (-wt * solvent_mg) / (wt - 100) if wt < 100 else None


def calc_solvent(wt, solute_mg):
    return (100.0 * solute_mg / wt) - solute_mg if wt > 0 else None


# メインUI
col_input, col_result = st.columns([3, 2])

with col_input:
    st.subheader("入力")

    if mode == "wt%":
        solute = st.number_input(f"溶質 ({unit})", min_value=0.0, value=11.0, step=0.1)
        solvent = st.number_input(
            f"溶媒 ({unit})", min_value=0.0, value=100.0, step=0.1
        )
        solute_mg = solute * factor
        solvent_mg = solvent * factor
        result = calc_wt(solute_mg, solvent_mg)
        label, val, suffix = "wt%", result, "%"

    elif mode == "溶質量":
        wt = st.number_input(
            "wt%", min_value=0.0, max_value=100.0, value=0.1, step=0.01
        )
        solvent = st.number_input(
            f"溶媒 ({unit})", min_value=0.0, value=100.0, step=0.1
        )
        solvent_mg = solvent * factor
        solute_mg_result = calc_solute(wt, solvent_mg)
        solute_mg = solute_mg_result if solute_mg_result is not None else 0
        result = solute_mg_result / factor if solute_mg_result is not None else None
        label, val, suffix = f"溶質 ({unit})", result, unit

    else:  # 溶媒量
        wt = st.number_input(
            "wt%", min_value=0.0, max_value=100.0, value=0.1, step=0.01
        )
        solute = st.number_input(f"溶質 ({unit})", min_value=0.0, value=11.0, step=0.1)
        solute_mg = solute * factor
        solvent_mg_result = calc_solvent(wt, solute_mg)
        solvent_mg = solvent_mg_result if solvent_mg_result is not None else 0
        result = solvent_mg_result / factor if solvent_mg_result is not None else None
        label, val, suffix = f"溶媒 ({unit})", result, unit

with col_result:
    st.subheader("結果")
    if val is not None:
        sep = "" if suffix == "%" else " "
        display = f"{val:.4f}{sep}{suffix}"

        # CSV データ作成
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        mode_key = {"wt%": "wt", "溶質量": "solute", "溶媒量": "solvent"}[mode]
        total_mg = solute_mg + solvent_mg
        wt_val = 100 * solute_mg / total_mg if total_mg > 0 else 0
        csv = (
            f"mode,solute ({unit}),solvent ({unit}),wt%\n"
            f"{mode},{solute_mg / factor:.4f},{solvent_mg / factor:.4f},{wt_val:.4f}\n"
        )

        col_metric, col_dl = st.columns([4, 1])
        col_metric.metric(label=label, value=display)
        col_dl.download_button(
            ":material/download:",
            csv,
            f"{timestamp}_{mode_key}_{unit}.csv",
            "text/csv",
        )
    else:
        st.warning("計算できません（値を確認してください）")

# 割合チャート & 計算式
st.divider()

if solute_mg > 0 or solvent_mg > 0:
    total = solute_mg + solvent_mg
    pct_solute = 100 * solute_mg / total if total > 0 else 0
    pct_solvent = 100 - pct_solute
    fig = go.Figure()
    for pct, name, color in [
        (pct_solute, "溶質", "#555555"),
        (pct_solvent, "溶媒", "#CCCCCC"),
    ]:
        fig.add_trace(
            go.Bar(
                x=[pct],
                y=[""],
                name=name,
                orientation="h",
                marker_color=color,
                text=f"{name} {pct:.1f}%",
                textposition="inside",
            )
        )
    fig.update_layout(
        barmode="stack",
        title_text="比率",
        showlegend=False,
        height=150,
        margin={"t": 40, "b": 30, "l": 10, "r": 10},
        xaxis={"visible": False},
        yaxis={"visible": False},
    )
    st.plotly_chart(fig, width="stretch", config={"staticPlot": True})

# 計算式
FORMULAS = {
    "wt%": r"\mathrm{wt\%} = \frac{m_{\mathrm{solute}}}{m_{\mathrm{solute}} + m_{\mathrm{solvent}}} \times 100",
    "溶質量": r"m_{\mathrm{solute}} = \frac{\mathrm{wt\%} \times m_{\mathrm{solvent}}}{100 - \mathrm{wt\%}}",
    "溶媒量": r"m_{\mathrm{solvent}} = m_{\mathrm{solute}} \times \left(\frac{100}{\mathrm{wt\%}} - 1\right)",
}
st.latex(FORMULAS[mode])
