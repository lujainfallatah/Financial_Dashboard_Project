import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from pathlib import Path
import base64

st.set_page_config(page_title="SAMA · صناديق الاستثمار", layout="wide")

URL = "https://atzmtrdryjxeqgqbxrwl.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF0em10cmRyeWp4ZXFncWJ4cndsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE2MDkyMTMsImV4cCI6MjA4NzE4NTIxM30.J8wvZ0_3jC5vJfiEPePgnWglqYvtlgT2XLYvxC_tqEw"

GREEN       = "#1B4332"
DARK_GREEN  = "#2D6A4F"
MID_GREEN   = "#40916C"
LIGHT_GREEN = "#74C69D"
GOLD        = "#B8860B"
RED         = "#C0392B"

GREEN_LIST = ["#1B4332","#2D6A4F","#40916C","#52B788","#74C69D","#95D5B2","#B7E4C7","#D8F3DC","#A8DABD"]


# جلب البيانات من Supabase
def fetch(view, cols="*", order=None, desc=False, limit=None):
    headers = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}
    params  = {"select": cols}
    if order: params["order"] = f"{order}.{'desc' if desc else 'asc'}"
    if limit: params["limit"] = limit
    res  = requests.get(f"{URL}/rest/v1/{view}", headers=headers, params=params)
    data = res.json()
    return pd.DataFrame(data if isinstance(data, list) else [data])


# تحميل البيانات من الـ Views
@st.cache_data(ttl=300, show_spinner=False)
def load_latest():
    cols = "period,grand_total_assets,local_assets_total,foreign_assets_total,active_funds_count,subscribers_count"
    return fetch("sama_data", cols=cols, order="period", desc=True, limit=2)

@st.cache_data(ttl=300, show_spinner=False)
def load_trend():
    # SELECT * FROM v_assets_trend
    df = fetch("v_assets_trend")
    df["period"] = pd.to_datetime(df["period"])
    for col in ["grand_total_assets", "local_assets_total", "foreign_assets_total"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

@st.cache_data(ttl=300, show_spinner=False)
def load_yoy():
    # SELECT * FROM v_yoy_growth
    df = fetch("v_yoy_growth")
    df["year"]       = pd.to_numeric(df["year"],       errors="coerce")
    df["avg_assets"] = pd.to_numeric(df["avg_assets"], errors="coerce")
    df["yoy_pct"]    = df["avg_assets"].pct_change() * 100
    return df.dropna()

@st.cache_data(ttl=300, show_spinner=False)
def load_composition():
    # SELECT * FROM v_asset_composition
    return fetch("v_asset_composition")

@st.cache_data(ttl=300, show_spinner=False)
def load_funds():
    # SELECT * FROM v_funds_subscribers
    df = fetch("v_funds_subscribers")
    df["period"]             = pd.to_datetime(df["period"])
    df["active_funds_count"] = pd.to_numeric(df["active_funds_count"], errors="coerce")
    df["subscribers_count"]  = pd.to_numeric(df["subscribers_count"],  errors="coerce")
    return df

@st.cache_data(ttl=300, show_spinner=False)
def load_shares():
    # SELECT * FROM v_local_foreign_share
    df = fetch("v_local_foreign_share")
    df["year"]        = pd.to_numeric(df["year"], errors="coerce").astype(int).astype(str)
    df["local_pct"]   = pd.to_numeric(df["local_pct"],   errors="coerce")
    df["foreign_pct"] = pd.to_numeric(df["foreign_pct"], errors="coerce")
    return df


with st.spinner("جاري تحميل البيانات..."):
    df_latest      = load_latest()
    df_trend       = load_trend()
    df_yoy         = load_yoy()
    df_composition = load_composition()
    df_funds       = load_funds()
    df_shares      = load_shares()

latest = df_latest.iloc[0]
prev   = df_latest.iloc[1]


# اللوقو
def get_logo():
    f = Path("logo_sama.png")
    return base64.b64encode(f.read_bytes()).decode() if f.exists() else None


# CSS
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;600;700&family=IBM+Plex+Mono:wght@400&display=swap');
html, body, [class*="css"] {{ font-family: 'IBM Plex Sans Arabic', sans-serif; direction: rtl; background: #0B0F14; }}
div.block-container {{ padding-top: 1rem !important; padding-bottom: 1rem !important; }}
.stMarkdown, .stText, p, div {{ text-align: right !important; }}
[data-testid="column"] {{ direction: rtl !important; }}
.hero {{ background: linear-gradient(135deg, {GREEN}, {DARK_GREEN}); border-radius: 12px; padding: 1.5rem 2rem; color: white; margin-bottom: 1rem; display: flex; align-items: center; gap: 1.5rem; }}
.hero-logo {{ background: white; border-radius: 10px; padding: .5rem .8rem; }}
.hero-logo img {{ height: 48px; display: block; }}
.hero-badge {{ display: inline-block; background: {LIGHT_GREEN}; color: {GREEN}; font-weight: 700; font-size: .68rem; padding: .15rem .6rem; border-radius: 100px; margin-bottom: .3rem; }}
.hero-title {{ font-size: 1.4rem; font-weight: 700; margin: 0; }}
.hero-sub   {{ font-size: .82rem; opacity: .8; margin: 0; }}
.card {{ background: white; border-radius: 10px; padding: .9rem 1.1rem; border-top: 3px solid {MID_GREEN}; box-shadow: 0 2px 8px rgba(27,67,50,.07); }}
.card-label {{ font-size: .72rem; color: #6B7A6E; font-weight: 600; margin-bottom: .2rem; }}
.card-value {{ font-size: 1.6rem; font-weight: 700; color: #0A1F14; font-family: 'IBM Plex Mono', monospace; }}
.card-unit  {{ font-size: .72rem; color: #6B7A6E; margin-top: .2rem; }}
.up   {{ color: {MID_GREEN}; font-weight: 600; font-size: .78rem; }}
.down {{ color: {RED}; font-weight: 600; font-size: .78rem; }}
.chart-title {{ font-size: .95rem; font-weight: 700; color: #FFFFFF; margin: .6rem 0 .1rem 0; padding-right: .6rem; border-right: 3px solid {LIGHT_GREEN}; }}
.sql {{ font-family: 'IBM Plex Mono', monospace; font-size: .65rem; color: {MID_GREEN}; background: #EBF5EF; border: 1px solid {LIGHT_GREEN}; border-radius: 5px; padding: .1rem .5rem; display: inline-block; margin-bottom: .3rem; direction: ltr; }}
.insights {{ background: linear-gradient(135deg, #EBF5EF, #F4FAF6); border: 1px solid {LIGHT_GREEN}; border-radius: 10px; padding: .8rem 1.2rem; }}
.insights p {{ margin: .25rem 0; color: {GREEN}; font-size: .82rem; border-right: 3px solid {LIGHT_GREEN}; padding-right: .7rem; }}
</style>
""", unsafe_allow_html=True)


# Hero
logo      = get_logo()
logo_html = f'<div class="hero-logo"><img src="data:image/png;base64,{logo}" /></div>' if logo else ""

st.markdown(f"""
<div class="hero">
  {logo_html}
  <div>
    <div class="hero-badge">البنك المركزي السعودي · SAMA</div>
    <p class="hero-title">لوحة تحليل صناديق الاستثمار 1998 – 2025</p>
    <p class="hero-sub">المصدر: ساما</p>
  </div>
</div>
""", unsafe_allow_html=True)


# KPIs
def fmt(v, big=False):
    try:
        v = float(v)
        return f"{v/1000:.1f}" if big and v >= 1000 else f"{int(v):,}"
    except:
        return "—"

def change(now, before):
    try:
        pct = (float(now) - float(before)) / float(before) * 100
        return f'<span class="up">▲ {pct:.1f}%</span>' if pct >= 0 else f'<span class="down">▼ {abs(pct):.1f}%</span>'
    except:
        return ""

c1, c2, c3, c4 = st.columns(4)
for col, label, val, old, unit, big in [
    (c1, "إجمالي الأصول",  latest["grand_total_assets"],  prev["grand_total_assets"],  "مليار ريال", True),
    (c2, "عدد الصناديق",   latest["active_funds_count"],   prev["active_funds_count"],   "صندوق",      False),
    (c3, "عدد المشتركين",  latest["subscribers_count"],    prev["subscribers_count"],    "مشترك",      False),
    (c4, "الأصول المحلية", latest["local_assets_total"],   prev["local_assets_total"],   "مليار ريال", True),
]:
    with col:
        st.markdown(f"""
        <div class="card">
          <div class="card-label">{label}</div>
          <div class="card-value">{fmt(val, big)}</div>
          <div class="card-unit">{unit} &nbsp; {change(val, old)}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='margin-top:.5rem'></div>", unsafe_allow_html=True)

# إعدادات الشارتات
L = dict(margin=dict(t=20,b=25,l=45,r=10), paper_bgcolor="white", plot_bgcolor="white",
         font=dict(family="IBM Plex Sans Arabic"), hovermode="x unified", legend=dict(orientation="h", y=1.1, font=dict(size=11, color="#333")))


# Row 1
r1, r2 = st.columns([3, 2])

with r1:
    st.markdown('<p class="chart-title">نمو إجمالي الأصول</p>', unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_trend["period"], y=df_trend["grand_total_assets"],
        fill="tozeroy", line=dict(color=MID_GREEN, width=2), fillcolor="rgba(64,145,108,0.15)",
        hovertemplate="<b>%{x|%Y}</b><br>%{y:,.0f} م.ر<extra></extra>"))
    fig.update_layout(**L, height=240, xaxis=dict(showgrid=False, title="", tickfont=dict(size=9, color='#333')),
        yaxis=dict(showgrid=True, gridcolor="#F0F0F0", title="مليون ريال", tickfont=dict(size=9, color="#333"), title_font=dict(size=9, color="#333")))
    st.plotly_chart(fig, use_container_width=True)

with r2:
    st.markdown('<p class="chart-title">توزيع الأصول (آخر فترة)</p>', unsafe_allow_html=True)
    row        = df_composition.iloc[0]
    pie_cols   = ["local_shares","local_bonds","local_funds","local_real_estate","local_other",
                  "foreign_shares","foreign_bonds","foreign_funds","foreign_other"]
    pie_labels = ["أسهم محلية","صكوك محلية","صناديق محلية","عقار","أخرى محلية",
                  "أسهم أجنبية","سندات أجنبية","صناديق أجنبية","أخرى أجنبية"]
    pie_vals   = [float(row[c]) if pd.notna(row.get(c)) and str(row.get(c)) not in ["","nan"] else 0 for c in pie_cols]
    fig = go.Figure(go.Pie(labels=pie_labels, values=pie_vals, hole=.55, textinfo="percent", textfont=dict(size=10), insidetextorientation="radial",
        marker=dict(colors=GREEN_LIST),
        hovertemplate="<b>%{label}</b><br>%{value:,.0f}<br>%{percent}<extra></extra>"))
    fig.update_layout(**{**L, "hovermode":"closest"}, height=240, showlegend=False, uniformtext=dict(minsize=11, mode="hide"))
    st.plotly_chart(fig, use_container_width=True)


# Row 2
r3, r4 = st.columns(2)

with r3:
    st.markdown('<p class="chart-title">الأصول المحلية والأجنبية عبر الزمن</p>', unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_trend["period"], y=df_trend["local_assets_total"],
        name="محلي", stackgroup="one", line=dict(width=0), fillcolor="rgba(45,106,79,0.7)",
        hovertemplate="%{y:,.0f}<extra>محلي</extra>"))
    fig.add_trace(go.Scatter(x=df_trend["period"], y=df_trend["foreign_assets_total"],
        name="أجنبي", stackgroup="one", line=dict(width=0), fillcolor="rgba(116,198,157,0.7)",
        hovertemplate="%{y:,.0f}<extra>أجنبي</extra>"))
    fig.update_layout(**L, height=240, xaxis=dict(showgrid=False, title="", tickfont=dict(size=9, color='#333')),
        yaxis=dict(showgrid=True, gridcolor="#F0F0F0", title="مليون ريال", tickfont=dict(size=9, color="#333"), title_font=dict(size=9, color="#333")))
    st.plotly_chart(fig, use_container_width=True)

with r4:
    st.markdown('<p class="chart-title">نسبة النمو من سنة لسنة %</p>', unsafe_allow_html=True)
    colors = [MID_GREEN if v >= 0 else RED for v in df_yoy["yoy_pct"]]
    fig = go.Figure(go.Bar(x=df_yoy["year"], y=df_yoy["yoy_pct"], marker_color=colors,
        hovertemplate="<b>%{x:.0f}</b><br>%{y:.1f}%<extra></extra>"))
    fig.update_layout(**{**L, "hovermode":"closest"}, height=240,
        xaxis=dict(showgrid=False, title="", dtick=4, tickfont=dict(size=9, color='#333')),
        yaxis=dict(showgrid=True, gridcolor="#F0F0F0", title="%", zeroline=True, zerolinecolor="#ccc", tickfont=dict(size=9, color="#333"), title_font=dict(size=9, color="#333")))
    st.plotly_chart(fig, use_container_width=True)


# Row 3
r5, r6 = st.columns(2)

with r5:
    st.markdown('<p class="chart-title">المشتركين والصناديق</p>', unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df_funds["period"], y=df_funds["subscribers_count"],
        name="مشتركين", yaxis="y1", marker_color="rgba(45,106,79,0.4)",
        hovertemplate="%{y:,.0f}<extra>مشتركين</extra>"))
    fig.add_trace(go.Scatter(x=df_funds["period"], y=df_funds["active_funds_count"],
        name="صناديق", yaxis="y2", line=dict(color=GOLD, width=2),
        hovertemplate="%{y:.0f}<extra>صندوق</extra>"))
    fig.update_layout(**L, height=240, xaxis=dict(showgrid=False, title="", tickfont=dict(size=9, color='#333')),
        yaxis=dict(showgrid=True, gridcolor="#F0F0F0", title="المشتركين", title_font=dict(size=9, color='#4A5568'), tickfont=dict(size=8, color='#4A5568')),
        yaxis2=dict(overlaying="y", side="right", title="الصناديق", showgrid=False, title_font=dict(size=9, color='#4A5568'), tickfont=dict(size=8, color='#4A5568')))
    st.plotly_chart(fig, use_container_width=True)

with r6:
    st.markdown('<p class="chart-title">الحصة: محلي مقابل أجنبي %</p>', unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df_shares["year"], y=df_shares["local_pct"], name="محلي %",
        marker_color=DARK_GREEN, hovertemplate="<b>%{x:.0f}</b><br>%{y:.1f}%<extra>محلي</extra>"))
    fig.add_trace(go.Bar(x=df_shares["year"], y=df_shares["foreign_pct"], name="أجنبي %",
        marker_color=LIGHT_GREEN, hovertemplate="<b>%{x:.0f}</b><br>%{y:.1f}%<extra>أجنبي</extra>"))
    fig.update_layout(**{**L, "hovermode":"closest"}, barmode="stack", height=240,
        xaxis=dict(showgrid=False, title="", dtick=4, tickfont=dict(size=9, color='#333')),
        yaxis=dict(showgrid=True, gridcolor="#F0F0F0", title="%", range=[0,100], tickfont=dict(size=9, color="#333"), title_font=dict(size=9, color="#333")))
    st.plotly_chart(fig, use_container_width=True)


# الاستنتاجات
try:
    growth     = (df_trend["grand_total_assets"].iloc[-1] - df_trend["grand_total_assets"].iloc[0]) / df_trend["grand_total_assets"].iloc[0] * 100
    local_pct  = float(latest["local_assets_total"]) / float(latest["grand_total_assets"]) * 100
    best_year  = int(df_yoy.loc[df_yoy["yoy_pct"].idxmax(), "year"])
    worst_year = int(df_yoy.loc[df_yoy["yoy_pct"].idxmin(), "year"])
    subs_growth = (df_funds["subscribers_count"].dropna().iloc[-1] - df_funds["subscribers_count"].dropna().iloc[0]) / df_funds["subscribers_count"].dropna().iloc[0] * 100
    period_str = pd.to_datetime(latest["period"]).strftime('%Y-%m')

    st.markdown(f"""
    <div class="insights">
      <p>نمت الأصول الإجمالية <b>{growth:,.0f}%</b> منذ 1998 — من <b>{df_trend["grand_total_assets"].iloc[0]:,.0f}</b> إلى <b>{df_trend["grand_total_assets"].iloc[-1]:,.0f}</b> مليون ريال.</p>
      <p>الأصول المحلية تمثل <b>{local_pct:.1f}%</b> من المحفظة في آخر فترة ({period_str}).</p>
      <p>أعلى نمو سنوي: عام <b>{best_year}</b> · أكبر تراجع: عام <b>{worst_year}</b> (تأثير الأزمات الاقتصادية).</p>
      <p>ارتفع عدد المشتركين <b>{subs_growth:,.0f}%</b> — دليل على نمو الوعي الاستثماري في المملكة.</p>
    </div>
    """, unsafe_allow_html=True)
except Exception as e:
    st.warning(f"خطأ في الاستنتاجات: {e}")

st.markdown("""
<div style="text-align:right; color:#bbb; font-size:.75rem; margin-top:.5rem; padding:.5rem 0; border-top:1px solid #eee;">
  البيانات من البنك المركزي السعودي (ساما) · متصل بـ Supabase
</div>
""", unsafe_allow_html=True)
