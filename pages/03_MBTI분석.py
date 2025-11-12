# streamlit_mbti_app.py
# Streamlit app that loads a CSV of country MBTI percentages and shows an interactive Plotly bar chart.
# Behavior:
# - Tries to load 'countriesMBTI_16types.csv' from the app's working directory.
# - If the file isn't present, shows a file uploader so you can upload the CSV in the browser.
# - Sidebar: select a country (or "-- Select or upload a file --")
# - Main: shows Plotly bar chart of MBTI type percentages for the chosen country.
#   - Highest value colored red; others colored as a blue gradient.
# - Compatible with Streamlit Cloud (no local-only dependencies).

from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Country MBTI Explorer", layout="wide")

st.title("🌐 Country MBTI Explorer — Interactive Plotly Visuals")
st.markdown(
    "Upload a CSV or place `countriesMBTI_16types.csv` in the app folder. The CSV must have a `Country` column and 16 MBTI-type columns (INFJ, ISFJ, INTP, ... , ESFJ) with numerical percentages or proportions."
)

# --- Load data (try local first, then uploader) ---
DEFAULT_CSV = Path("countriesMBTI_16types.csv")

@st.cache_data
def load_csv_from_path(path: Path):
    return pd.read_csv(path)

@st.cache_data
def load_csv_from_buffer(buffer):
    return pd.read_csv(buffer)

# Try to load local file
df = None
if DEFAULT_CSV.exists():
    try:
        df = load_csv_from_path(DEFAULT_CSV)
    except Exception as e:
        st.error(f"로컬 파일을 불러오는 중 오류가 발생했습니다: {e}")

# If not present, let user upload
if df is None:
    uploaded = st.file_uploader("Upload countriesMBTI_16types.csv", type=["csv"]) 
    if uploaded is not None:
        try:
            df = load_csv_from_buffer(uploaded)
        except Exception as e:
            st.error(f"업로드된 파일을 읽는 중 오류: {e}")

# If still None, show instructions and stop
if df is None:
    st.info("CSV 파일이 필요합니다. 로컬에 `countriesMBTI_16types.csv`를 두거나 업로더에 파일을 올려주세요.")
    st.stop()

# Basic validation
if "Country" not in df.columns:
    st.error("CSV에 'Country' 열이 없습니다. 파일 형식을 확인해주세요.")
    st.stop()

# Identify MBTI columns (everything except Country)
mbti_cols = [c for c in df.columns if c != "Country"]
if len(mbti_cols) != 16:
    st.warning(f"발견된 MBTI 열의 수: {len(mbti_cols)}. 일반적으로 16개여야 합니다. 지금은 발견된 열로 진행합니다.")

# Sidebar controls
st.sidebar.header("Controls")
country = st.sidebar.selectbox("Select a country:", options=sorted(df["Country"].unique()))
show_table = st.sidebar.checkbox("Show raw row table", value=False)

# Filter row
row = df.loc[df["Country"] == country]
if row.empty:
    st.error("선택한 국가의 데이터가 없습니다.")
    st.stop()

# Prepare data for plotting
row_vals = row[mbti_cols].iloc[0].astype(float)
plot_df = pd.DataFrame({"MBTI": mbti_cols, "Value": row_vals.values})
plot_df = plot_df.sort_values("Value", ascending=False).reset_index(drop=True)

# Generate colors: first bar red, others blue gradient
n = len(plot_df)
red = "#ff4d4d"
# use Plotly's Blues sequential palette and sample it across n-1 steps
blues = px.colors.sequential.Blues
# If palette shorter than needed, interpolate by repeating
if len(blues) < max(1, n-1):
    # simple repeat to fill
    blues_extended = (blues * ((n // len(blues)) + 1))[: n-1]
else:
    # sample evenly from palette
    step = max(1, len(blues) // (n-1))
    blues_extended = [blues[i * step] for i in range(n-1)]

colors = [red] + blues_extended[: n-1]

# Build Plotly bar chart
fig = go.Figure(
    data=[
        go.Bar(
            x=plot_df["MBTI"],
            y=plot_df["Value"],
            marker_color=colors,
            hovertemplate="%{x}: %{y}<extra></extra>",
        )
    ]
)

fig.update_layout(
    title=f"MBTI distribution for {country}",
    xaxis_title="MBTI type",
    yaxis_title="Proportion / Percentage",
    template="plotly_white",
    uniformtext_minsize=8,
    uniformtext_mode='hide',
    margin=dict(l=40, r=40, t=80, b=40),
    hovermode="closest",
)

# Make responsive in Streamlit
st.plotly_chart(fig, use_container_width=True)

# Optionally show table
if show_table:
    st.subheader(f"Raw values — {country}")
    st.dataframe(plot_df)

# Footer / notes
st.markdown("---")
st.caption("Note: The app attempts to read a CSV from the app folder first, otherwise use the uploader. Colors: highest value = red, others = blue gradient.")

# (Optional) allow user to view top k countries for a given MBTI
with st.expander("Top countries by MBTI type"):
    mbti_choice = st.selectbox("Choose MBTI type:", options=mbti_cols, key="top_mbti")
    top_k = st.slider("Top K", min_value=3, max_value=20, value=10)
    top_df = df[["Country", mbti_choice]].sort_values(by=mbti_choice, ascending=False).head(top_k)
    fig2 = px.bar(top_df, x=mbti_choice, y="Country", orientation='h')
    st.plotly_chart(fig2, use_container_width=True)


# ===== requirements.txt content (below) =====
# Save this content into requirements.txt when deploying to Streamlit Cloud.

# requirements.txt
# streamlit
# pandas
# plotly
# numpy
# (You can pin versions if you prefer, e.g.)
# streamlit==1.24.0
# pandas==2.2.2
# plotly==5.18.0
# numpy==1.26.0
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# 예시 데이터 (사용자 데이터로 교체 가능)
data = {
    'Country': ['South Korea', 'USA', 'Japan', 'Germany', 'France', 'UK', 'Canada', 'Brazil', 'India', 'Australia', 'Italy'],
    'INTJ': [8, 6, 7, 5, 6, 7, 6, 5, 4, 6, 5],
    'ENFP': [10, 12, 9, 8, 9, 10, 11, 7, 6, 9, 8],
    'ISTP': [7, 5, 8, 6, 7, 6, 5, 4, 6, 5, 7],
    'INFJ': [9, 8, 7, 6, 5, 6, 7, 5, 4, 5, 6],
}
df = pd.DataFrame(data)

st.title("🌍 MBTI 세계 비교 대시보드")

tab1, tab2 = st.tabs(["국가별 MBTI 비율", "MBTI별 국가 순위"])

# ------------------------------
# 📊 탭 1: 국가별 MBTI 비율
# ------------------------------
with tab1:
    st.subheader("국가별 MBTI 비율 비교")

    country = st.selectbox("국가를 선택하세요:", df['Country'].unique())

    # 해당 국가 데이터 추출
    row = df[df['Country'] == country].iloc[0]
    mbti_values = row[1:]
    mbti_df = pd.DataFrame({
        'MBTI': mbti_values.index,
        'Value': mbti_values.values
    }).sort_values('Value', ascending=False)

    # 색상 설정 (1등은 빨강, 나머지는 파랑 그라데이션 역방향)
    colors = ['red'] + px.colors.sequential.Blues[::-1][:len(mbti_df)-1]

    fig = px.bar(
        mbti_df,
        x='MBTI',
        y='Value',
        text='Value',
        color=mbti_df['MBTI'],
        color_discrete_sequence=colors
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(
        showlegend=False,
        yaxis_title="비율(%)",
        xaxis_title="MBTI 유형",
        title=f"{country}의 MBTI 비율",
    )

    st.plotly_chart(fig, use_container_width=True)

# ------------------------------
# 📊 탭 2: MBTI별 국가 순위
# ------------------------------
with tab2:
    st.subheader("MBTI별 국가 비율 상위 10개")

    mbti_type = st.selectbox("MBTI 유형을 선택하세요:", df.columns[1:])

    sorted_df = df.sort_values(by=mbti_type, ascending=False)
    top10 = sorted_df.head(10)

    # South Korea 포함 확인
    if 'South Korea' not in top10['Country'].values:
        sk_row = df[df['Country'] == 'South Korea']
        top10 = pd.concat([top10, sk_row])

    # 색상 설정
    colors = []
    for country in top10['Country']:
        if country == 'South Korea':
            colors.append('rgb(180, 60, 180)')  # 보라톤 (빨+파 믹스)
        else:
            colors.append('rgb(0, 100, 255)')

    fig2 = px.bar(
        top10,
        x='Country',
        y=mbti_type,
        text=mbti_type,
        color='Country',
        color_discrete_sequence=colors
    )

    fig2.update_traces(textposition='outside')
    fig2.update_layout(
        showlegend=False,
        yaxis_title="비율(%)",
        xaxis_title="국가",
        title=f"{mbti_type} 유형 비율이 높은 국가 Top 10",
    )

    st.plotly_chart(fig2, use_container_width=True)
