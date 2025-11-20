import streamlit as st
import pandas as pd
import plotly.express as px
import re

# -------------------------------------------------------
# 페이지 설정 (숙연·경건한 분위기)
# -------------------------------------------------------
st.set_page_config(
    page_title="독립유공자 - 생월 & 사망월 목록",
    layout="wide"
)

# CSS 디자인
page_style = """
<style>
body {
    background-color: #0d0d0f;
    color: #ececec;
}

.stApp {
    background-image: url("https://i.imgur.com/NLzZbGr.png"); /* 흐릿한 태극 문양 */
    background-size: cover;
    background-attachment: fixed;
    background-repeat: no-repeat;
    backdrop-filter: blur(6px);
}

.block-container {
    padding-top: 2.2rem;
}

h1, h2, h3, h4 {
    font-family: 'Noto Sans KR', sans-serif;
    font-weight: 700;
    color: #ffffff;
}

p, label, span {
    font-family: 'Noto Sans KR', sans-serif;
}

.taegukgi {
    width: 180px;
    margin-bottom: 20px;
    opacity: 0.92;
}
</style>
"""
st.markdown(page_style, unsafe_allow_html=True)

# -------------------------------------------------------
# 상단 태극기 + 제목
# -------------------------------------------------------
st.markdown(
    """
    <div style="text-align:center;">
        <img class="taegukgi" src="https://i.imgur.com/ZC5iRdM.png">
        <h1>독립유공자 — 생월 & 사망월 목록</h1>
        <p style="font-size:18px; color:#cccccc;">숭고한 희생을 기억합니다</p>
    </div>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------------
# CSV 읽기 (인코딩 자동 처리)
# -------------------------------------------------------
@st.cache_data
def load_data():
    for enc in ["utf-8-sig", "cp949", "utf-8"]:
        try:
            return pd.read_csv("The.korean.goat.csv", dtype=str, encoding=enc)
        except:
            pass
    st.error("❌ CSV 파일을 읽을 수 없습니다.")
    return pd.DataFrame()

df = load_data()
df.columns = [c.strip() for c in df.columns]

# -------------------------------------------------------
# 날짜 파싱 함수
# -------------------------------------------------------
def parse_date(x):
    if pd.isna(x):
        return pd.NaT
    s = re.sub(r"[^0-9]", "", str(x))

    if len(s) == 8:  # YYYYMMDD
        return pd.to_datetime(s, format="%Y%m%d", errors="coerce")

    if len(s) == 6:  # YYMMDD 형태
        yy = int(s[:2])
        year = 1900 + yy if yy > 25 else 2000 + yy
        return pd.to_datetime(str(year) + s[2:], format="%Y%m%d", errors="coerce")

    return pd.NaT

# -------------------------------------------------------
# 필요한 컬럼 생성
# -------------------------------------------------------
if "생년월일" in df.columns:
    df["birth_date"] = df["생년월일"].apply(parse_date)
    df["birth_month"] = df["birth_date"].dt.month

if "사망일" in df.columns:
    df["death_date"] = df["사망일"].apply(parse_date)
    df["death_month"] = df["death_date"].dt.month

# -------------------------------------------------------
# 사이드바
# -------------------------------------------------------
st.sidebar.header("📅 달 선택")
mode = st.sidebar.radio("조회 유형", ["출생월", "사망월"])

if mode == "출생월":
    selected_month = st.sidebar.selectbox("월 선택", list(range(1, 12+1)))
    selected_df = df[df["birth_month"] == selected_month]
else:
    selected_month = st.sidebar.selectbox("월 선택", list(range(1, 12+1)))
    selected_df = df[df["death_month"] == selected_month]

# -------------------------------------------------------
# 선택한 월의 명단 출력
# -------------------------------------------------------
st.subheader(f"📋 {selected_month}월 {mode} 유공자 명단")
st.write(f"총 **{len(selected_df)}명**")
st.dataframe(selected_df)

# -------------------------------------------------------
# 출생월 / 사망월 그래프
# -------------------------------------------------------
st.subheader("📊 월별 유공자 분포")

if mode == "출생월":
    counts = df["birth_month"].value_counts().sort_index()
    title = "월별 출생 유공자 수"
else:
    counts = df["death_month"].value_counts().sort_index()
    title = "월별 사망 유공자 수"

chart_df = pd.DataFrame({"month": counts.index, "count": counts.values})

# 1등 색 = 한국 느낌(짙은 파랑), 나머지 = 점차 밝아지는 그라데이션
colors = px.colors.sequential.Blues[::-1]

fig = px.bar(
    chart_df,
    x="month",
    y="count",
    title=title,
    color="count",
    color_continuous_scale=colors
)

fig.update_layout(
    xaxis_title="월",
    yaxis_title="인원 수",
    title_x=0.5,
    coloraxis_showscale=False,  # 색상바 제거
)

st.plotly_chart(fig, use_container_width=True)
