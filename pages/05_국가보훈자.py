import streamlit as st
import pandas as pd
import plotly.express as px
import re

st.set_page_config(page_title="독립유공자 생월/사망월 분석", layout="wide")

st.title("🇰🇷 독립유공자 생월/사망월 분석 대시보드")

# -------------------------------------------------
# 1) CSV 불러오기
# -------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("The.korean.goat.csv", dtype=str)
    df.columns = [c.strip() for c in df.columns]
    return df

df = load_data()

# -------------------------------------------------
# 2) 날짜 파싱 함수
# -------------------------------------------------
def parse_date(x):
    if pd.isna(x):
        return pd.NaT
    s = str(x).strip()

    # “YYYY년MM월DD일” 정리
    s = re.sub(r"년|월|일|\s", "-", s)
    s = re.sub(r"[^0-9\-]", "", s)

    try:
        # 8자리 (YYYYMMDD)
        if len(s) == 8 and s.isdigit():
            return pd.to_datetime(s, format="%Y%m%d", errors="coerce")
        # 6자리 (YYMMDD)
        if len(s) == 6 and s.isdigit():
            yy = int(s[:2])
            year = 1900 + yy if yy > 25 else 2000 + yy
            return pd.to_datetime(str(year) + s[2:], format="%Y%m%d", errors="coerce")
        return pd.to_datetime(s, errors="coerce")
    except:
        return pd.NaT

# -------------------------------------------------
# 3) 생년월일 & 사망일 컬럼 처리
# -------------------------------------------------
birth_col = None
death_col = None

for col in df.columns:
    if "생년" in col:
        birth_col = col
    if "사망" in col or "별세" in col:
        death_col = col

if birth_col is None:
    st.error("❌ CSV 파일에서 '생년월일' 컬럼을 찾지 못했습니다.")
    st.stop()

df["parsed_birth"] = df[birth_col].apply(parse_date)
df["birth_month"] = df["parsed_birth"].dt.month

if death_col:
    df["parsed_death"] = df[death_col].apply(parse_date)
    df["death_month"] = df["parsed_death"].dt.month

# -------------------------------------------------
# 4) 월 선택 → 그 달 출생 유공자 목록
# -------------------------------------------------
st.sidebar.header("🔎 조회 옵션")
month_list = list(range(1, 12 + 1))
selected_month = st.sidebar.selectbox("출생월 선택", month_list)

st.subheader(f"📋 {selected_month}월에 태어나신 유공자 목록")
birth_filtered = df[df["birth_month"] == selected_month]
st.write(f"총 **{len(birth_filtered)}명**")
st.dataframe(birth_filtered)

# -------------------------------------------------
# 5) 월별 출생 그래프 (Plotly)
# -------------------------------------------------
st.subheader("📊 월별 출생 인원")

birth_count = df["birth_month"].value_counts().sort_index()
birth_df = pd.DataFrame({"month": birth_count.index, "count": birth_count.values})

# 한국 느낌 컬러 → 파란색 (1등), 나머지 그라데이션
korea_blue = "#003E9B"  # 태극기 파랑
colors = px.colors.sequential.Blues

fig_birth = px.bar(
    birth_df,
    x="month",
    y="count",
    title="월별 출생자 수",
    color="count",
    color_continuous_scale=colors,
)

# 1등 색상 강조
max_month = birth_df.loc[birth_df["count"].idxmax(), "month"]
fig_birth.update_traces(marker=dict(line=dict(width=1, color='black')))

st.plotly_chart(fig_birth, use_container_width=True)

# -------------------------------------------------
# 6) 월별 사망 그래프
# -------------------------------------------------
if "death_month" in df.columns:
    st.subheader("📊 월별 사망 인원")

    death_count = df["death_month"].value_counts().sort_index()
    death_df = pd.DataFrame({"month": death_count.index, "count": death_count.values})

    # 한국 느낌 → 빨간색 계열
    korea_red = "#C60C30"
    colors_red = px.colors.sequential.Reds

    fig_death = px.bar(
        death_df,
        x="month",
        y="count",
        title="월별 사망자 수",
        color="count",
        color_continuous_scale=colors_red,
    )

    st.plotly_chart(fig_death, use_container_width=True)
else:
    st.info("⚠️ CSV에 사망일 정보가 없어 사망월 그래프를 그릴 수 없습니다.")
