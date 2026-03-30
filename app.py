import streamlit as st
import pandas as pd
import joblib
import plotly.express as px
import plotly.graph_objects as go
import time
import sqlite3
from datetime import datetime

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Churn Intelligence", page_icon="📡", layout="wide")

# ── PALETTE ───────────────────────────────────────────────────────────────────
TEAL_LIGHT  = "#78B9B5"
TEAL_MID    = "#0F828C"
BLUE_DEEP   = "#065084"
PURPLE_DEEP = "#320A6B"

# ── THEME STATE ───────────────────────────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

dark = st.session_state.dark_mode

if dark:
    BG       = "#060d1a"
    SURFACE  = "#0b1628"
    SURFACE2 = "#101e35"
    TEXT     = "#e8f4f4"
    MUTED    = "rgba(120,185,181,0.55)"
    CARD_BG  = "linear-gradient(135deg, rgba(15,130,140,0.12), rgba(6,80,132,0.10))"
    CARD_BOR = "rgba(120,185,181,0.18)"
    PLY_TPL  = "plotly_dark"
    PLY_BG   = "rgba(11,22,40,0.6)"
    SIDEBAR  = f"linear-gradient(180deg, {PURPLE_DEEP} 0%, #1a0740 60%, #0a0520 100%)"
    TITLE_C  = f"{TEAL_LIGHT}, {TEAL_MID}, {BLUE_DEEP}"
    INPUT_BG = "#101e35"
    HR_COL   = "rgba(120,185,181,0.12)"
    BODY_TXT = "#c4dedd"
else:
    BG       = "#f0f7f8"
    SURFACE  = "#ffffff"
    SURFACE2 = "#e8f4f5"
    TEXT     = "#0d2b30"
    MUTED    = "rgba(6,80,132,0.6)"
    CARD_BG  = "linear-gradient(135deg, rgba(15,130,140,0.08), rgba(6,80,132,0.05))"
    CARD_BOR = "rgba(6,80,132,0.2)"
    PLY_TPL  = "plotly_white"
    PLY_BG   = "rgba(240,247,248,0.8)"
    SIDEBAR  = f"linear-gradient(180deg, {BLUE_DEEP} 0%, {TEAL_MID} 60%, {TEAL_LIGHT} 100%)"
    TITLE_C  = f"{BLUE_DEEP}, {TEAL_MID}, {TEAL_MID}"
    INPUT_BG = "#ffffff"
    HR_COL   = "rgba(6,80,132,0.12)"
    BODY_TXT = "#065084"

# ── GLOBAL CSS ────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;600;800&family=Space+Mono&display=swap');

:root {{
  --teal-light:  {TEAL_LIGHT};
  --teal-mid:    {TEAL_MID};
  --blue-deep:   {BLUE_DEEP};
  --purple-deep: {PURPLE_DEEP};
}}

html, body, .stApp {{
  background: {BG} !important;
  color: {TEXT} !important;
  font-family: 'DM Sans', sans-serif !important;
  transition: background 0.3s ease, color 0.3s ease;
}}

section[data-testid="stSidebar"] {{
  background: {SIDEBAR} !important;
  border-right: 1px solid {CARD_BOR} !important;
}}
section[data-testid="stSidebar"] * {{
  color: {'#d4eae9' if dark else '#ffffff'} !important;
  font-family: 'DM Sans', sans-serif !important;
}}
section[data-testid="stSidebar"] .stSlider > div > div > div > div {{
  background: {TEAL_MID} !important;
}}
section[data-testid="stSidebar"] [data-baseweb="slider"] [role="slider"] {{
  background: {TEAL_LIGHT} !important;
  border: 2px solid {TEAL_MID} !important;
  box-shadow: 0 0 10px {TEAL_MID}80 !important;
}}

h1, h2, h3, h4 {{
  font-family: 'DM Sans', sans-serif !important;
  color: {TEAL_LIGHT} !important;
}}

.churn-card {{
  background: {CARD_BG};
  border: 1px solid {CARD_BOR};
  border-radius: 16px;
  padding: 28px 32px;
  margin-bottom: 20px;
  backdrop-filter: blur(12px);
  box-shadow: 0 4px 32px rgba(50,10,107,0.15);
}}

.hero-title {{
  font-size: 52px;
  font-weight: 800;
  text-align: center;
  background: linear-gradient(135deg, {TITLE_C});
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -1px;
  line-height: 1.1;
  margin-bottom: 8px;
}}

.hero-sub {{
  text-align: center;
  color: {MUTED};
  font-size: 17px;
  letter-spacing: 0.5px;
  margin-bottom: 36px;
}}

.section-label {{
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 2.5px;
  text-transform: uppercase;
  color: {TEAL_MID};
  margin-bottom: 4px;
}}

.risk-badge-high {{
  background: linear-gradient(135deg, #7f1d1d, #991b1b);
  border: 1px solid #f87171;
  border-radius: 10px;
  padding: 16px 24px;
  font-size: 18px;
  font-weight: 700;
  color: #fecaca;
  text-align: center;
}}
.risk-badge-med {{
  background: linear-gradient(135deg, #78350f, #92400e);
  border: 1px solid #fbbf24;
  border-radius: 10px;
  padding: 16px 24px;
  font-size: 18px;
  font-weight: 700;
  color: #fde68a;
  text-align: center;
}}
.risk-badge-low {{
  background: linear-gradient(135deg, #064e3b, #065f46);
  border: 1px solid #34d399;
  border-radius: 10px;
  padding: 16px 24px;
  font-size: 18px;
  font-weight: 700;
  color: #a7f3d0;
  text-align: center;
}}

.kpi-card {{
  background: {CARD_BG};
  border: 1px solid {CARD_BOR};
  border-radius: 14px;
  padding: 20px 16px;
  text-align: center;
  transition: transform 0.2s ease;
}}
.kpi-card:hover {{ transform: translateY(-2px); }}
.kpi-number {{
  font-size: 32px;
  font-weight: 800;
  color: {TEAL_LIGHT};
  line-height: 1.1;
}}
.kpi-label {{
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  color: {MUTED};
  margin-top: 4px;
}}

.divider {{
  border: none;
  border-top: 1px solid {HR_COL};
  margin: 28px 0;
}}

.stButton > button {{
  background: linear-gradient(135deg, {TEAL_MID}, {BLUE_DEEP}) !important;
  color: white !important;
  border: none !important;
  border-radius: 10px !important;
  font-weight: 700 !important;
  font-size: 15px !important;
  padding: 10px 28px !important;
  letter-spacing: 0.3px !important;
  box-shadow: 0 4px 20px rgba(15,130,140,0.35) !important;
  transition: all 0.2s ease !important;
}}
.stButton > button:hover {{
  box-shadow: 0 6px 28px rgba(120,185,181,0.45) !important;
  transform: translateY(-1px) !important;
}}

[data-testid="stMetric"] {{
  background: {CARD_BG} !important;
  border: 1px solid {CARD_BOR} !important;
  border-radius: 12px !important;
  padding: 16px !important;
}}
[data-testid="stMetricLabel"] {{ color: {MUTED} !important; }}
[data-testid="stMetricValue"] {{ color: {TEAL_LIGHT} !important; font-weight: 800 !important; }}

[data-testid="stDataFrame"] {{
  border: 1px solid {CARD_BOR} !important;
  border-radius: 10px !important;
  overflow: hidden !important;
}}

[data-baseweb="select"] {{
  background: {INPUT_BG} !important;
  border-color: {CARD_BOR} !important;
}}

[data-testid="stNumberInput"] input {{
  background: {INPUT_BG} !important;
  border-color: {CARD_BOR} !important;
  color: {TEXT} !important;
  border-radius: 8px !important;
}}

div[data-testid="stTabs"] button {{
  font-family: 'DM Sans', sans-serif !important;
  font-weight: 600 !important;
  color: {MUTED} !important;
}}
div[data-testid="stTabs"] button[aria-selected="true"] {{
  color: {TEAL_LIGHT} !important;
  border-bottom: 2px solid {TEAL_MID} !important;
}}

[data-testid="stFileUploadDropzone"] {{
  background: {CARD_BG} !important;
  border: 2px dashed {CARD_BOR} !important;
  border-radius: 12px !important;
}}

.stSpinner > div {{ border-top-color: {TEAL_MID} !important; }}

/* ══════════════════════════════════════════════
   RESPONSIVE — Tablet (max 1024px)
══════════════════════════════════════════════ */
@media screen and (max-width: 1024px) {{

  .hero-title {{
    font-size: 38px !important;
    letter-spacing: -0.5px;
  }}

  .hero-sub {{
    font-size: 15px !important;
  }}

  .block-container {{
    padding: 1.2rem 1.5rem !important;
  }}

  .kpi-number {{
    font-size: 26px !important;
  }}

  .kpi-label {{
    font-size: 11px !important;
  }}

  .churn-card {{
    padding: 20px 22px !important;
  }}
}}

/* ══════════════════════════════════════════════
   RESPONSIVE — Mobile (max 768px)
══════════════════════════════════════════════ */
@media screen and (max-width: 768px) {{

  /* ── Layout ── */
  .block-container {{
    padding: 0.8rem 0.8rem !important;
  }}

  /* ── Hero ── */
  .hero-title {{
    font-size: 28px !important;
    letter-spacing: -0.3px;
    margin-bottom: 6px;
  }}

  .hero-sub {{
    font-size: 13px !important;
    margin-bottom: 20px !important;
  }}

  /* ── Cards ── */
  .churn-card {{
    padding: 16px 16px !important;
    border-radius: 12px !important;
    margin-bottom: 12px !important;
  }}

  /* ── KPI cards ── */
  .kpi-card {{
    padding: 14px 10px !important;
    border-radius: 10px !important;
  }}

  .kpi-number {{
    font-size: 22px !important;
  }}

  .kpi-label {{
    font-size: 10px !important;
    letter-spacing: 1px;
  }}

  /* ── Section label ── */
  .section-label {{
    font-size: 10px !important;
    letter-spacing: 1.5px;
  }}

  /* ── Risk badges ── */
  .risk-badge-high,
  .risk-badge-med,
  .risk-badge-low {{
    font-size: 14px !important;
    padding: 12px 14px !important;
    border-radius: 8px !important;
  }}

  /* ── Buttons ── */
  .stButton > button {{
    font-size: 13px !important;
    padding: 8px 16px !important;
    height: auto !important;
    width: 100% !important;
  }}

  /* ── Metrics ── */
  [data-testid="stMetric"] {{
    padding: 12px !important;
  }}
  [data-testid="stMetricValue"] {{
    font-size: 1.4rem !important;
  }}

  /* ── Sidebar: collapse friendly ── */
  section[data-testid="stSidebar"] {{
    min-width: 260px !important;
    max-width: 80vw !important;
  }}

  /* ── Tabs: scrollable on small screens ── */
  div[data-testid="stTabs"] {{
    overflow-x: auto !important;
    -webkit-overflow-scrolling: touch;
  }}
  div[data-testid="stTabs"] > div {{
    flex-wrap: nowrap !important;
    min-width: max-content;
  }}
  div[data-testid="stTabs"] button {{
    font-size: 12px !important;
    padding: 6px 10px !important;
    white-space: nowrap;
  }}

  /* ── Dataframe ── */
  [data-testid="stDataFrame"] {{
    font-size: 12px !important;
    overflow-x: auto !important;
  }}

  /* ── Plotly charts ── */
  div[data-testid="stPlotlyChart"] {{
    padding: 0.2rem !important;
  }}

  /* ── Number inputs ── */
  [data-testid="stNumberInput"] input {{
    font-size: 14px !important;
  }}

  /* ── Selectbox ── */
  [data-baseweb="select"] {{
    font-size: 13px !important;
  }}

  /* ── Slider labels ── */
  [data-testid="stSlider"] {{
    padding: 0 4px !important;
  }}

  /* ── Columns: stack on mobile ── */
  [data-testid="column"] {{
    min-width: 100% !important;
    flex: 1 1 100% !important;
  }}

  /* ── Divider spacing ── */
  .divider {{
    margin: 16px 0 !important;
  }}

  /* ── File uploader ── */
  [data-testid="stFileUploadDropzone"] {{
    padding: 20px 12px !important;
  }}
}}

/* ══════════════════════════════════════════════
   RESPONSIVE — Small mobile (max 480px)
══════════════════════════════════════════════ */
@media screen and (max-width: 480px) {{

  .hero-title {{
    font-size: 22px !important;
  }}

  .hero-sub {{
    font-size: 12px !important;
  }}

  .kpi-number {{
    font-size: 18px !important;
  }}

  .churn-card {{
    padding: 12px 12px !important;
  }}

  .risk-badge-high,
  .risk-badge-med,
  .risk-badge-low {{
    font-size: 13px !important;
    padding: 10px 12px !important;
  }}

  [data-testid="stMetricValue"] {{
    font-size: 1.2rem !important;
  }}

  div[data-testid="stTabs"] button {{
    font-size: 11px !important;
    padding: 5px 8px !important;
  }}
}}
</style>
""", unsafe_allow_html=True)

# ── THEME TOGGLE ──────────────────────────────────────────────────────────────
_tc1, _tc2 = st.columns([10, 1])
with _tc2:
    toggle_label = "☀️" if dark else "🌙"
    if st.button(toggle_label, help="Toggle Light / Dark Mode"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

# ── HERO ──────────────────────────────────────────────────────────────────────
# Viewport meta tag for proper mobile scaling
st.markdown('<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">', unsafe_allow_html=True)

st.markdown('<div class="hero-title">📡 Churn Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Telecom Customer Churn Prediction · Powered by Random Forest</div>',
            unsafe_allow_html=True)

# ── LOAD MODEL ────────────────────────────────────────────────────────────────
try:
    model   = joblib.load("churn_model.pkl")
    scaler  = joblib.load("scaler.pkl")
    columns = joblib.load("columns.pkl")
except Exception as e:
    st.error(f"⚠ Model files not found: {e}")
    st.stop()

# ── SQLITE HISTORY ────────────────────────────────────────────────────────────
DB_PATH = "churn_history.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp  TEXT,
            tenure     INTEGER,
            monthly    REAL,
            contract   TEXT,
            internet   TEXT,
            churn_prob REAL,
            risk_tier  TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_prediction(tenure, monthly, contract, internet, prob):
    init_db()
    tier = "High" if prob > 0.66 else ("Medium" if prob > 0.33 else "Low")
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO predictions (timestamp,tenure,monthly,contract,internet,churn_prob,risk_tier) "
        "VALUES (?,?,?,?,?,?,?)",
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), tenure, monthly,
         contract, internet, round(prob * 100, 2), tier)
    )
    conn.commit()
    conn.close()

def load_history():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM predictions ORDER BY id DESC LIMIT 100", conn)
    conn.close()
    return df

def get_kpi_stats():
    init_db()
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql("SELECT * FROM predictions", conn)
        conn.close()
        if df.empty:
            return 0, 0.0, 0, 0
        return (len(df), df["churn_prob"].mean(),
                int((df["churn_prob"] > 66).sum()),
                int((df["churn_prob"] <= 33).sum()))
    except:
        return 0, 0.0, 0, 0

# ── KPI BANNER ────────────────────────────────────────────────────────────────
total_pred, avg_risk, high_risk_count, low_risk_count = get_kpi_stats()

st.markdown('<div class="section-label">Dashboard KPIs</div>', unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-number">{total_pred}</div>'
                f'<div class="kpi-label">Total Predictions</div></div>', unsafe_allow_html=True)
with k2:
    st.markdown(f'<div class="kpi-card"><div class="kpi-number">{avg_risk:.1f}%</div>'
                f'<div class="kpi-label">Avg Churn Risk</div></div>', unsafe_allow_html=True)
with k3:
    st.markdown(f'<div class="kpi-card"><div class="kpi-number" style="color:#f87171;">'
                f'{high_risk_count}</div><div class="kpi-label">High Risk Customers</div>'
                f'</div>', unsafe_allow_html=True)
with k4:
    st.markdown(f'<div class="kpi-card"><div class="kpi-number" style="color:#34d399;">'
                f'{low_risk_count}</div><div class="kpi-label">Low Risk Customers</div>'
                f'</div>', unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── PROJECT INFO ──────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="churn-card">
  <div class="section-label">About this Dashboard</div>
  <p style="margin:10px 0 6px;font-size:15px;color:{BODY_TXT};">
    Predicts telecom customer churn probability using
    <strong>high-signal behavioral and contractual features</strong>.
    Adjust inputs in the sidebar and click <em>Predict</em>.
  </p>
  <p style="margin:0;font-size:13px;color:{MUTED};">
    Built with Scikit-Learn · Streamlit · Plotly &nbsp;|&nbsp;
    👩‍💻 Developed by <strong>Afiya Amer</strong>
  </p>
</div>
""", unsafe_allow_html=True)

# ── SIDEBAR INPUTS ────────────────────────────────────────────────────────────
st.sidebar.markdown("## 📋 Customer Profile")
st.sidebar.markdown("---")

st.sidebar.markdown("**📊 Account Metrics**")
tenure  = st.sidebar.slider("Tenure (months)", 0, 72, 12)
monthly = st.sidebar.slider("Monthly Charges ($)", 0, 150, 70)

st.sidebar.markdown("---")
st.sidebar.markdown("**📄 Contract & Billing**")
contract       = st.sidebar.selectbox("Contract Type",
                     ["Month-to-month", "One year", "Two year"])
payment_method = st.sidebar.selectbox("Payment Method",
                     ["Electronic check", "Mailed check",
                      "Bank transfer (automatic)", "Credit card (automatic)"])
paperless      = st.sidebar.selectbox("Paperless Billing", ["Yes", "No"])

st.sidebar.markdown("---")
st.sidebar.markdown("**🌐 Internet Service**")
internet         = st.sidebar.selectbox("Internet Service",  ["Fiber optic", "DSL", "No"])
tech_support     = st.sidebar.selectbox("Tech Support",      ["No", "Yes", "No internet service"])
online_security  = st.sidebar.selectbox("Online Security",   ["No", "Yes", "No internet service"])
online_backup    = st.sidebar.selectbox("Online Backup",     ["No", "Yes", "No internet service"])
device_prot      = st.sidebar.selectbox("Device Protection", ["No", "Yes", "No internet service"])
streaming_tv     = st.sidebar.selectbox("Streaming TV",      ["No", "Yes", "No internet service"])
streaming_movies = st.sidebar.selectbox("Streaming Movies",  ["No", "Yes", "No internet service"])

st.sidebar.markdown("---")
st.sidebar.markdown("**👤 Demographics**")
senior      = st.sidebar.selectbox("Senior Citizen", ["No", "Yes"])
partner     = st.sidebar.selectbox("Partner",         ["No", "Yes"])
dependents  = st.sidebar.selectbox("Dependents",      ["No", "Yes"])
phone       = st.sidebar.selectbox("Phone Service",   ["Yes", "No"])
multi_lines = st.sidebar.selectbox("Multiple Lines",  ["No", "Yes", "No phone service"])

# ── BUILD INPUT ROW ───────────────────────────────────────────────────────────
def yn(v):  return 1 if v == "Yes" else 0
def nis(v): return 1 if v == "Yes" else 0

raw = {
    "tenure":           tenure,
    "MonthlyCharges":   monthly,
    "TechSupport":      nis(tech_support),
    "OnlineSecurity":   nis(online_security),
    "PaperlessBilling": yn(paperless),
    "SeniorCitizen":    yn(senior),
    "Partner":          yn(partner),
    "Dependents":       yn(dependents),
    "MultipleLines":    nis(multi_lines),
    "StreamingTV":      nis(streaming_tv),
    "StreamingMovies":  nis(streaming_movies),
    "DeviceProtection": nis(device_prot),
    "OnlineBackup":     nis(online_backup),
    "PhoneService":     yn(phone),
    "Contract_Month-to-month":                1 if contract == "Month-to-month"               else 0,
    "Contract_One year":                      1 if contract == "One year"                     else 0,
    "Contract_Two year":                      1 if contract == "Two year"                     else 0,
    "InternetService_DSL":                    1 if internet == "DSL"                          else 0,
    "InternetService_Fiber optic":            1 if internet == "Fiber optic"                  else 0,
    "InternetService_No":                     1 if internet == "No"                           else 0,
    "PaymentMethod_Bank transfer (automatic)":1 if payment_method == "Bank transfer (automatic)" else 0,
    "PaymentMethod_Credit card (automatic)":  1 if payment_method == "Credit card (automatic)"   else 0,
    "PaymentMethod_Electronic check":         1 if payment_method == "Electronic check"          else 0,
    "PaymentMethod_Mailed check":             1 if payment_method == "Mailed check"              else 0,
}

input_df = pd.DataFrame([raw])
for col in columns:
    if col not in input_df.columns:
        input_df[col] = 0
input_df = input_df[columns]
scaled   = scaler.transform(input_df)

# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔍 Predict",
    "🧠 SHAP Explainer",
    "💰 Cost Estimator",
    "📂 Batch Analysis",
    "📋 History"
])

# ═════════════════════════════════════════════════════════════════════════════
# TAB 1 — PREDICT
# ═════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("### 🔍 Run Prediction")

    if st.button("⚡ Predict Churn Risk", key="predict_main"):
        with st.spinner("Analyzing customer profile..."):
            time.sleep(1.0)

        prob = model.predict_proba(scaled)[0][1]
        pct  = prob * 100
        save_prediction(tenure, monthly, contract, internet, prob)

        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            if pct > 66:
                st.markdown(f'<div class="risk-badge-high">🚨 HIGH CHURN RISK — {pct:.1f}%</div>',
                            unsafe_allow_html=True)
                st.snow()
            elif pct > 33:
                st.markdown(f'<div class="risk-badge-med">⚠️ MODERATE RISK — {pct:.1f}%</div>',
                            unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="risk-badge-low">✅ LOW CHURN RISK — {pct:.1f}%</div>',
                            unsafe_allow_html=True)
                st.balloons()
        with col2:
            st.metric("Churn Probability", f"{pct:.1f}%")
        with col3:
            risk_label = "High 🔴" if pct > 66 else ("Medium 🟡" if pct > 33 else "Low 🟢")
            st.metric("Risk Tier", risk_label)

        # Gauge chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=pct,
            number={"suffix": "%", "font": {"size": 36, "color": TEAL_LIGHT}},
            delta={"reference": 50, "increasing": {"color": "#f87171"},
                   "decreasing": {"color": "#34d399"}},
            title={"text": "Churn Risk Score", "font": {"color": TEAL_LIGHT, "size": 18}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": TEAL_LIGHT},
                "bar":  {"color": TEAL_MID, "thickness": 0.3},
                "bgcolor": "rgba(0,0,0,0)",
                "steps": [
                    {"range": [0,  33], "color": "rgba(52,211,153,0.15)"},
                    {"range": [33, 66], "color": "rgba(251,191,36,0.15)"},
                    {"range": [66,100], "color": "rgba(248,113,113,0.15)"},
                ],
                "threshold": {"line": {"color": "#f87171", "width": 3}, "value": 50}
            }
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color=TEAL_LIGHT, height=280, margin=dict(t=40, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)

        # ── PDF Export ────────────────────────────────────────────────────────
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown("### 📄 Export Report")
        try:
            from fpdf import FPDF

            class PDF(FPDF):
                def header(self):
                    self.set_font("Helvetica", "B", 16)
                    self.set_text_color(15, 130, 140)
                    # Plain ASCII only — no em-dash, no emoji
                    self.cell(0, 12, "Churn Intelligence - Prediction Report",
                              new_x="LMARGIN", new_y="NEXT", align="C")
                    self.set_draw_color(120, 185, 181)
                    self.line(10, 22, 200, 22)
                    self.ln(6)

            pdf = PDF()
            pdf.add_page()
            pdf.set_font("Helvetica", "", 11)
            pdf.set_text_color(30, 30, 30)

            # Section: Prediction Summary
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_text_color(6, 80, 132)
            pdf.cell(0, 8, "Prediction Summary", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 11)
            pdf.set_text_color(30, 30, 30)
            pdf.cell(0, 7, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                     new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 7, f"Churn Probability: {pct:.1f}%",
                     new_x="LMARGIN", new_y="NEXT")
            tier_txt = "High" if pct > 66 else ("Medium" if pct > 33 else "Low")
            pdf.cell(0, 7, f"Risk Tier: {tier_txt}",
                     new_x="LMARGIN", new_y="NEXT")
            pdf.ln(4)

            # Section: Customer Profile
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_text_color(6, 80, 132)
            pdf.cell(0, 8, "Customer Profile", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 11)
            pdf.set_text_color(30, 30, 30)
            profile = {
                "Tenure":          f"{tenure} months",
                "Monthly Charges": f"${monthly}",
                "Contract":        contract,
                "Internet Service":internet,
                "Payment Method":  payment_method,
                "Tech Support":    tech_support,
                "Online Security": online_security,
                "Senior Citizen":  senior,
                "Partner":         partner,
                "Dependents":      dependents,
            }
            for k, v in profile.items():
                pdf.cell(0, 7, f"  {k}: {v}", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(4)

            # Section: Retention Recommendations
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_text_color(6, 80, 132)
            pdf.cell(0, 8, "Retention Recommendations", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 11)
            pdf.set_text_color(30, 30, 30)
            recs_pdf = []
            if contract == "Month-to-month":
                recs_pdf.append("Offer a discounted annual contract")
            if payment_method == "Electronic check":
                recs_pdf.append("Encourage auto-pay enrollment")
            if tech_support == "No":
                recs_pdf.append("Bundle Tech Support for free (first 3 months)")
            if online_security == "No":
                recs_pdf.append("Upsell Online Security add-on")
            if tenure < 12:
                recs_pdf.append("Apply loyalty discount in months 3-12")
            if internet == "Fiber optic" and monthly > 80:
                recs_pdf.append("Review fiber pricing for high-charge customers")
            if not recs_pdf:
                recs_pdf.append("No urgent actions - strong retention indicators")
            for r in recs_pdf:
                pdf.cell(0, 7, f"  - {r}", new_x="LMARGIN", new_y="NEXT")

            pdf_bytes = pdf.output()
            st.download_button(
                label="Download PDF Report",
                data=bytes(pdf_bytes),
                file_name=f"churn_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf"
            )
        except ImportError:
            st.info("Install fpdf2 to enable PDF export:  pip install fpdf2")
        except Exception as e:
            st.error(f"PDF generation failed: {e}")

        # ── Retention Recommendations ─────────────────────────────────────────
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown("### 💡 Retention Recommendations")
        recs = []
        if contract == "Month-to-month":
            recs.append("📄 **Offer a discounted annual contract** — MTM customers churn 3x more.")
        if payment_method == "Electronic check":
            recs.append("💳 **Encourage auto-pay enrollment** — lowest commitment signal.")
        if tech_support == "No":
            recs.append("🛠 **Bundle Tech Support** — customers without support churn significantly more.")
        if online_security == "No":
            recs.append("🔒 **Upsell Online Security** — add-ons increase switching costs.")
        if tenure < 12:
            recs.append("🎁 **Apply loyalty discount in months 3-12** — early churn window is highest risk.")
        if internet == "Fiber optic" and monthly > 80:
            recs.append("💰 **Review fiber pricing** — high-charge fiber customers are most price-sensitive.")
        if not recs:
            recs.append("✅ Strong retention indicators — no urgent actions needed.")
        for r in recs:
            st.markdown(
                f"<div class='churn-card' style='padding:14px 20px;margin-bottom:10px;'>{r}</div>",
                unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # Feature Importance
    st.markdown("### 📊 Feature Importance")
    try:
        imp_df = pd.DataFrame({
            "Feature":    columns,
            "Importance": model.feature_importances_
        }).sort_values("Importance", ascending=True).tail(15)

        fig = px.bar(
            imp_df, x="Importance", y="Feature", orientation="h",
            color="Importance",
            color_continuous_scale=[[0, BLUE_DEEP], [0.5, TEAL_MID], [1, TEAL_LIGHT]],
            template=PLY_TPL
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=PLY_BG,
            font_color=TEAL_LIGHT, coloraxis_showscale=False,
            margin=dict(l=0, r=0, t=10, b=0), height=420
        )
        fig.update_xaxes(gridcolor=HR_COL)
        fig.update_yaxes(gridcolor=HR_COL)
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.info(f"Feature importance unavailable: {e}")

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # Correlation Heatmap
    st.markdown("### 🔥 Feature Correlation Matrix")
    try:
        df_raw = pd.read_csv("WA_Fn-UseC_-Telco-Customer-Churn.csv")
        df_raw["TotalCharges"] = pd.to_numeric(df_raw["TotalCharges"], errors="coerce")
        df_raw["Churn"] = df_raw["Churn"].map({"Yes": 1, "No": 0})
        corr = df_raw.select_dtypes(include="number").corr()
        fig = px.imshow(
            corr, text_auto=".2f",
            color_continuous_scale=[[0, PURPLE_DEEP], [0.5, TEAL_MID], [1, TEAL_LIGHT]],
            template=PLY_TPL
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", font_color=TEAL_LIGHT,
            margin=dict(t=10, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)
    except:
        st.warning("Dataset CSV not found — skipping correlation heatmap.")

# ═════════════════════════════════════════════════════════════════════════════
# TAB 2 — SHAP EXPLAINER
# ═════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### 🧠 SHAP Explainability")
    st.markdown(f"""
    <div class='churn-card' style='padding:16px 24px;margin-bottom:20px;'>
        <div class='section-label'>What is SHAP?</div>
        <p style='margin:8px 0 0;font-size:14px;color:{BODY_TXT};'>
        SHAP (SHapley Additive exPlanations) shows <strong>which features pushed the
        prediction up or down</strong> for this specific customer.
        Red bars increase churn risk, green bars decrease it.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🔬 Explain This Prediction", key="shap_btn"):
        try:
            import shap
            with st.spinner("Computing SHAP values..."):
                explainer = shap.TreeExplainer(model)
                shap_vals = explainer.shap_values(scaled)

            # ── Robust SHAP extraction — handles all RandomForest output shapes ──
            # shap v0.4x returns list of arrays (one per class)
            # shap v0.4x+ may return 3D ndarray (n_samples, n_features, n_classes)
            import numpy as np
            if isinstance(shap_vals, list):
                # list[n_classes] → each element shape (n_samples, n_features)
                sv = np.array(shap_vals[1][0]).flatten()
            else:
                sv = np.array(shap_vals)
                if sv.ndim == 3:
                    # (n_samples, n_features, n_classes) → class 1, first sample
                    sv = sv[0, :, 1]
                elif sv.ndim == 2:
                    # (n_samples, n_features) → first sample
                    sv = sv[0]
                else:
                    sv = sv.flatten()

            shap_df = pd.DataFrame({
                "Feature":    list(columns),
                "SHAP Value": sv.tolist(),
                "Abs":        np.abs(sv).tolist()
            }).sort_values("Abs", ascending=True).tail(15)

            shap_df["Color"] = shap_df["SHAP Value"].apply(
                lambda x: "#f87171" if x > 0 else "#34d399"
            )

            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=shap_df["SHAP Value"],
                y=shap_df["Feature"],
                orientation="h",
                marker_color=shap_df["Color"],
                hovertemplate="<b>%{y}</b><br>SHAP: %{x:.4f}<extra></extra>"
            ))
            fig.add_vline(x=0, line_color=TEAL_LIGHT, line_width=1, line_dash="dash")
            fig.update_layout(
                title={"text": "Feature Contributions to This Prediction",
                       "font": {"color": TEAL_LIGHT, "size": 16}},
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=PLY_BG,
                font_color=TEAL_LIGHT, template=PLY_TPL,
                xaxis_title="SHAP Value (impact on churn probability)",
                margin=dict(l=0, r=0, t=50, b=0), height=460
            )
            fig.update_xaxes(gridcolor=HR_COL)
            fig.update_yaxes(gridcolor=HR_COL)
            st.plotly_chart(fig, use_container_width=True)

            top_pos = shap_df[shap_df["SHAP Value"] > 0].nlargest(3, "SHAP Value")
            top_neg = shap_df[shap_df["SHAP Value"] < 0].nsmallest(3, "SHAP Value")

            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### 🔴 Top Churn Drivers")
                for _, row in top_pos.iterrows():
                    st.markdown(
                        f"<div class='churn-card' style='padding:12px 18px;margin-bottom:8px;'>"
                        f"<strong>{row['Feature']}</strong><br>"
                        f"<span style='color:#f87171;font-size:13px;'>"
                        f"SHAP: +{row['SHAP Value']:.4f} — raises churn risk</span>"
                        f"</div>", unsafe_allow_html=True)
            with c2:
                st.markdown("#### 🟢 Top Retention Signals")
                for _, row in top_neg.iterrows():
                    st.markdown(
                        f"<div class='churn-card' style='padding:12px 18px;margin-bottom:8px;'>"
                        f"<strong>{row['Feature']}</strong><br>"
                        f"<span style='color:#34d399;font-size:13px;'>"
                        f"SHAP: {row['SHAP Value']:.4f} — lowers churn risk</span>"
                        f"</div>", unsafe_allow_html=True)

        except ImportError:
            st.error("SHAP not installed. Run:  pip install shap")
        except Exception as e:
            st.error(f"SHAP computation failed: {e}")

# ═════════════════════════════════════════════════════════════════════════════
# TAB 3 — CHURN COST ESTIMATOR
# ═════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### 💰 Churn Cost Estimator")
    st.markdown(f"""
    <div class='churn-card' style='padding:16px 24px;margin-bottom:20px;'>
        <div class='section-label'>Business ROI Calculator</div>
        <p style='margin:8px 0 0;font-size:14px;color:{BODY_TXT};'>
        Enter your business metrics to calculate <strong>expected revenue at risk</strong>
        and the <strong>ROI of a retention campaign</strong> for this customer.
        </p>
    </div>
    """, unsafe_allow_html=True)

    prob_live = model.predict_proba(scaled)[0][1]
    pct_live  = prob_live * 100

    ce1, ce2 = st.columns(2)
    with ce1:
        ltv = st.number_input(
            "Customer Lifetime Value ($)", min_value=0, value=1200, step=50,
            help="Total revenue expected from this customer over their lifetime")
        campaign_cost = st.number_input(
            "Retention Campaign Cost ($)", min_value=0, value=50, step=10,
            help="Cost to run a targeted retention offer for this customer")
    with ce2:
        retention_lift = st.number_input(
            "Expected Churn Reduction (%)", min_value=1, max_value=100, value=30, step=5,
            help="How much the campaign is expected to reduce churn probability")
        discount_rate = st.number_input(
            "Annual Discount Rate (%)", min_value=0, max_value=50, value=10, step=1,
            help="Used to calculate Net Present Value of at-risk revenue")

    if st.button("📊 Calculate ROI", key="roi_btn"):
        rev_at_risk    = ltv * prob_live
        new_prob       = max(0, prob_live - (retention_lift / 100))
        rev_saved      = ltv * (prob_live - new_prob)
        net_roi        = rev_saved - campaign_cost
        roi_pct        = ((rev_saved - campaign_cost) / campaign_cost * 100) if campaign_cost > 0 else 0
        breakeven_prob = campaign_cost / ltv if ltv > 0 else 0

        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        r1, r2, r3, r4 = st.columns(4)
        with r1:
            st.metric("Revenue at Risk",      f"${rev_at_risk:,.0f}")
        with r2:
            st.metric("Revenue Saved",        f"${rev_saved:,.0f}")
        with r3:
            st.metric("Net ROI",
                      f"+${net_roi:,.0f}" if net_roi >= 0 else f"-${abs(net_roi):,.0f}")
        with r4:
            st.metric("ROI %",                f"{roi_pct:.0f}%")

        # Waterfall chart
        fig = go.Figure(go.Waterfall(
            orientation="v",
            measure=["absolute", "relative", "relative", "total"],
            x=["Revenue at Risk", "Campaign Cost", "Revenue Saved", "Net ROI"],
            y=[rev_at_risk, -campaign_cost, rev_saved, 0],
            connector={"line": {"color": TEAL_MID}},
            increasing={"marker": {"color": "#34d399"}},
            decreasing={"marker": {"color": "#f87171"}},
            totals={"marker":    {"color": TEAL_MID}},
            text=[f"${rev_at_risk:,.0f}", f"-${campaign_cost:,.0f}",
                  f"+${rev_saved:,.0f}",  f"${net_roi:,.0f}"],
            textposition="outside"
        ))
        fig.update_layout(
            title={"text": "Retention Campaign ROI Waterfall",
                   "font": {"color": TEAL_LIGHT, "size": 16}},
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=PLY_BG,
            font_color=TEAL_LIGHT, template=PLY_TPL,
            height=380, margin=dict(t=50, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        if net_roi > 0:
            st.markdown(f"""
            <div class='risk-badge-low' style='font-size:15px;text-align:left;padding:18px 24px;'>
            <strong>Campaign is financially justified.</strong><br>
            For every $1 spent on retention, you earn back ${roi_pct/100:.1f}x.
            Break-even churn probability: {breakeven_prob*100:.1f}%.
            Current risk ({pct_live:.1f}%) {'exceeds' if prob_live > breakeven_prob else 'is below'} break-even.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='risk-badge-high' style='font-size:15px;text-align:left;padding:18px 24px;'>
            <strong>Campaign may not be cost-effective.</strong><br>
            Revenue saved (${rev_saved:,.0f}) is less than campaign cost (${campaign_cost:,.0f}).
            Consider a lower-cost retention channel or targeting higher-LTV customers.
            </div>
            """, unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# TAB 4 — BATCH ANALYSIS
# ═════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### 📂 Batch Customer Analysis")
    st.markdown(f"""
    <div class='churn-card' style='padding:16px 24px;margin-bottom:20px;'>
        <div class='section-label'>Bulk Scoring</div>
        <p style='margin:8px 0 0;font-size:14px;color:{BODY_TXT};'>
        Upload a CSV of customer records. The model scores every row and returns
        churn probabilities and risk tiers. Missing columns are auto-filled.
        </p>
    </div>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader("Upload customer CSV", type=["csv"])

    if uploaded:
        try:
            batch_df = pd.read_csv(uploaded)
            st.success(f"Loaded {len(batch_df):,} customer records")

            for col in columns:
                if col not in batch_df.columns:
                    batch_df[col] = 0
            batch_scaled = scaler.transform(batch_df[columns])
            probs = model.predict_proba(batch_scaled)[:, 1]

            batch_df["Churn_Probability_%"] = (probs * 100).round(1)
            batch_df["Risk_Tier"] = pd.cut(
                probs * 100, bins=[0, 33, 66, 100],
                labels=["Low", "Medium", "High"]
            )

            b1, b2, b3, b4 = st.columns(4)
            with b1: st.metric("Total Customers",  f"{len(batch_df):,}")
            with b2: st.metric("Avg Churn Risk",    f"{probs.mean()*100:.1f}%")
            with b3: st.metric("High Risk (>66%)",  f"{(probs > 0.66).sum():,}")
            with b4: st.metric("Low Risk (<33%)",   f"{(probs < 0.33).sum():,}")

            tier_counts = batch_df["Risk_Tier"].value_counts()
            fig = px.pie(
                values=tier_counts.values, names=tier_counts.index,
                color_discrete_map={"Low": "#34d399", "Medium": "#fbbf24", "High": "#f87171"},
                hole=0.45, template=PLY_TPL, title="Customer Risk Distribution"
            )
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                              font_color=TEAL_LIGHT, height=350)
            st.plotly_chart(fig, use_container_width=True)

            fig2 = px.histogram(
                batch_df, x="Churn_Probability_%", nbins=20,
                color_discrete_sequence=[TEAL_MID], template=PLY_TPL,
                title="Churn Probability Distribution"
            )
            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=PLY_BG,
                font_color=TEAL_LIGHT, height=300,
                xaxis_title="Churn Probability (%)",
                yaxis_title="Number of Customers"
            )
            st.plotly_chart(fig2, use_container_width=True)

            st.markdown("#### Scored Customers (sorted by risk)")
            st.dataframe(
                batch_df.sort_values("Churn_Probability_%", ascending=False),
                use_container_width=True
            )
            st.download_button(
                label="Download Scored CSV",
                data=batch_df.to_csv(index=False),
                file_name=f"churn_scored_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        except Exception as e:
            st.error(f"Could not process file: {e}")
    else:
        st.markdown(f"""
        <div class='churn-card' style='text-align:center;padding:40px 20px;'>
            <div style='font-size:40px;margin-bottom:12px;'>📋</div>
            <div style='font-size:16px;font-weight:600;color:{BODY_TXT};margin-bottom:8px;'>
                Drop a CSV file above to begin
            </div>
            <div style='font-size:13px;color:{MUTED};'>
                Any missing columns will be auto-filled with zero (baseline).
            </div>
        </div>
        """, unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# TAB 5 — HISTORY
# ═════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown("### 📋 Prediction History")
    st.markdown(f"""
    <div class='churn-card' style='padding:16px 24px;margin-bottom:20px;'>
        <div class='section-label'>Logged Predictions</div>
        <p style='margin:8px 0 0;font-size:14px;color:{BODY_TXT};'>
        Every prediction is automatically saved here.
        Track risk trends over time across different customer profiles.
        </p>
    </div>
    """, unsafe_allow_html=True)

    hist_df = load_history()

    if hist_df.empty:
        st.info("No predictions logged yet. Run a prediction in the Predict tab first.")
    else:
        h1, h2, h3 = st.columns(3)
        with h1: st.metric("Total Logged",    f"{len(hist_df):,}")
        with h2: st.metric("Avg Risk",         f"{hist_df['churn_prob'].mean():.1f}%")
        with h3: st.metric("High Risk Logged", f"{(hist_df['churn_prob'] > 66).sum():,}")

        hist_df["timestamp"] = pd.to_datetime(hist_df["timestamp"])
        fig = px.line(
            hist_df.sort_values("timestamp"),
            x="timestamp", y="churn_prob", markers=True,
            color_discrete_sequence=[TEAL_MID], template=PLY_TPL,
            title="Churn Risk Over Time"
        )
        fig.add_hline(y=66, line_dash="dash", line_color="#f87171",
                      annotation_text="High Risk Threshold",
                      annotation_font_color="#f87171")
        fig.add_hline(y=33, line_dash="dash", line_color="#fbbf24",
                      annotation_text="Medium Risk Threshold",
                      annotation_font_color="#fbbf24")
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=PLY_BG,
            font_color=TEAL_LIGHT, height=350,
            xaxis_title="Time", yaxis_title="Churn Probability (%)"
        )
        st.plotly_chart(fig, use_container_width=True)

        tier_hist = hist_df["risk_tier"].value_counts()
        fig2 = px.bar(
            x=tier_hist.index, y=tier_hist.values,
            color=tier_hist.index,
            color_discrete_map={"Low": "#34d399", "Medium": "#fbbf24", "High": "#f87171"},
            template=PLY_TPL, title="Risk Tier Distribution (all time)"
        )
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=PLY_BG,
            font_color=TEAL_LIGHT, height=300,
            showlegend=False,
            xaxis_title="Risk Tier", yaxis_title="Count"
        )
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("#### All Logged Predictions")
        display_df = hist_df.drop(columns=["id"]).rename(columns={
            "timestamp": "Time",      "tenure":     "Tenure",
            "monthly":   "Monthly($)","contract":   "Contract",
            "internet":  "Internet",  "churn_prob": "Churn %",
            "risk_tier": "Risk Tier"
        })
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        dl_col, clr_col = st.columns([3, 1])
        with dl_col:
            st.download_button(
                "Download History CSV",
                hist_df.to_csv(index=False),
                "prediction_history.csv", "text/csv"
            )
        with clr_col:
            if st.button("Clear History"):
                conn = sqlite3.connect(DB_PATH)
                conn.execute("DELETE FROM predictions")
                conn.commit()
                conn.close()
                st.success("History cleared.")
                st.rerun()

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown('<hr class="divider">', unsafe_allow_html=True)
st.markdown(f"""
<div style="text-align:center;color:{MUTED};font-size:13px;padding-bottom:20px;">
  Churn Intelligence Dashboard &nbsp;·&nbsp; Built with Streamlit &amp; Scikit-Learn
  &nbsp;·&nbsp; <strong style="color:{TEAL_LIGHT};">Developed by Afiya Amer</strong>
</div>
""", unsafe_allow_html=True)