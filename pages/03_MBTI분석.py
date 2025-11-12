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
