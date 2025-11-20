import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="독립유공자 - 생월 & 사망월 목록", layout="wide")

# -----------------------
# 🎌 페이지 제목 + 태극기
# -----------------------
st.markdown(
    """
    <div style='text-align: center;'>
        <img src='https://upload.wikimedia.org/wikipedia/commons/0/09/Flag_of_South_Korea.svg' 
             width='120'>
        <h1>독립유공자 - 생월 & 사망월 목록</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------
# 📌 CSV 로드 (인코딩 자동 감지)
# -----------------------
@st.cache_data
def load_data():
    encodings = ["utf-8-sig", "euc-kr", "cp949", "utf-8"]

    for enc in encodings:
        try:
            return pd.read_csv("The.korean.goat.csv", dtype=str, encoding=enc)
        except:
            pass

    st.error("❌ CSV 파일 인코딩을 읽을 수 없습니다. 인코딩을 UTF-8 또는 CP949로 저장해 주세요.")
    return None


df = load_data()
if df is None:
    st.stop()

# -----------------------
# 📌 날짜 컬럼 정제
# -----------------------
def extract_month(series):
    return (
        series.astype(str)
        .str.replace(r"[^0-9]", "", regex=True)
        .str.zfill(8)
        .str[4:6]
    )

df["birth_month"] = extract_month(df["생년월일"])
df["death_month"] = extract_month(df["사망년월일"])

df["birth_month"] = df["birth_month"].replace("00", None)
df["death_month"] = df["death_month"].replace("00", None)

# ------------------------------------
# 🎨 그래프 색상 (1등: 한국 느낌 = 남색)
# ------------------------------------
KOREA_COLOR = "#003478"  # 한국 태극기 청색 계열
GRADIENT = px.colors.sequential.Blues[::-1][1:]  # 나머지 그라데이션

# ------------------------------------------------------
# 📈 월별 출생자 그래프 (제목 옆의 ‘인터랙티브?’ 제거)
# ------------------------------------------------------
birth_counts = df["birth_month"].value_counts().sort_index()
birth_fig = px.bar(
    x=birth_counts.index,
    y=birth_counts.values,
)
birth_fig.update_traces(marker_color=[KOREA_COLOR] + GRADIENT[:len(birth_counts)-1])

birth_fig.update_layout(
    title="",  # 제목 제거 → 옆에 뜨는 "인터랙티브?" 문구도 함께 제거됨
    xaxis_title="월",
    yaxis_title="출생자 수",
)

# ------------------------------------------------------
# 📈 월별 사망자 그래프
# ------------------------------------------------------
death_counts = df["death_month"].value_counts().sort_index()
death_fig = px.bar(
    x=death_counts.index,
    y=death_counts.values,
)
death_fig.update_traces(marker_color=[KOREA_COLOR] + GRADIENT[:len(death_counts)-1])

death_fig.update_layout(
    title="",
    xaxis_title="월",
    yaxis_title="사망자 수",
)

# -----------------------
# 📌 월 선택 UI
# -----------------------
st.subheader("🔎 특정 월의 독립유공자 목록 보기")

month_options = sorted(df["birth_month"].dropna().unique())
selected_month = st.selectbox("출생월 선택", month_options)

filtered = df[df["birth_month"] == selected_month]

st.write(f"### 📋 {selected_month}월 출생 독립유공자 목록")
st.dataframe(filtered)

# -----------------------
# 📊 그래프 표시
# -----------------------
st.markdown("## 📈 월별 출생자 수")
st.plotly_chart(birth_fig, use_container_width=True)

st.markdown("## 📈 월별 사망자 수")
st.plotly_chart(death_fig, use_container_width=True)
