import streamlit as st
import pandas as pd
import plotly.express as px
import re
import calendar

st.set_page_config(page_title="독립유공자 생월 분석", layout="wide")

st.title("🇰🇷 독립유공자 생월 분석 대시보드")

# -------------------------
# 데이터 불러오기
# -------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("국가보훈부_독립유공자 명단_20251117.csv", dtype=str)
    df.columns = [c.strip() for c in df.columns]
    return df

df = load_data()

# -------------------------
# 생년월일 파싱 함수
# -------------------------
def parse_birth(x):
    if pd.isna(x):
        return pd.NaT
    s = str(x).strip()

    # “YYYY년MM월DD일” → 숫자만 추출
    s = re.sub(r"년|월|일|\s", "-", s)
    s = re.sub(r"[^0-9\-\/\.]", "", s)
    s = s.replace('.', '-').replace('/', '-')

    try:
        # YYYYMMDD
        if len(s) == 8 and s.isdigit():
            return pd.to_datetime(s, format="%Y%m%d", errors="coerce")

        # YYMMDD
        if len(s) == 6 and s.isdigit():
            yy = int(s[:2])
            year = 1900 + yy if yy > 25 else 2000 + yy
            return pd.to_datetime(str(year) + s[2:], format="%Y%m%d", errors="coerce")

        # 일반 파싱
        return pd.to_datetime(s, errors="coerce")
    except:
        return pd.NaT

# -------------------------
# 생년월일 처리
# -------------------------
if "생년월일" in df.columns:
    df["parsed_birth"] = df["생년월일"].apply(parse_birth)
    df["birth_month"] = df["parsed_birth"].dt.month
else:
    st.error("❌ ‘생년월일’ 컬럼을 찾을 수 없습니다. CSV 파일을 다시 확인해주세요.")
    st.stop()

# -------------------------
# 월 선택 UI
# -------------------------
st.sidebar.header("🔍 검색 옵션")
months = list(range(1, 13))
selected_month = st.sidebar.selectbox("월 선택", months, index=0)

# -------------------------
# 선택한 월 명단 출력
# -------------------------
st.subheader(f"📋 {selected_month}월에 태어나신 유공자 목록")

filtered = df[df["birth_month"] == selected_month]

st.write(f"총 **{len(filtered)}명**")
st.dataframe(filtered)

# 다운로드 버튼
csv = filtered.to_csv(index=False).encode('utf-8-sig')
st.download_button(
    label="📥 이 월의 명단 CSV 다운로드",
    data=csv,
    file_name=f"{selected_month}월_독립유공자.csv",
    mime="text/csv"
)

# -------------------------
# 월별 전체 통계 그래프
# -------------------------
st.subheader("📊 월별 독립유공자 수")

month_counts = df["birth_month"].value_counts().sort_index()
month_df = pd.DataFrame({
    "month": month_counts.index,
    "count": month_counts.values
})

# 한국 느낌의 레드 → 블루 그라데이션 색상
colors = px.colors.sequential.Bluered[::-1]

fig = px.bar(
    month_df,
    x="month",
    y="count",
    title="월별 독립유공자 수",
    color="count",
    color_continuous_scale=colors
)

fig.update_layout(xaxis_title="월", yaxis_title="인원수")

st.plotly_chart(fig, use_container_width=True)
