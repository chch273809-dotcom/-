# pages/top10_oct2025.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="2025-10 일별 역별 이용자 Top10", layout="wide")

st.title("2025년 10월 — 일자 & 호선별 역 이용자 Top10")
st.markdown(
    """
    **사용법**
    1. 좌측에서 2025년 10월의 날짜를 선택하세요.  
    2. 호선을 선택하세요. (해당 날짜/호선의 역들을 합산하여 상위 10개 역을 보여드립니다.)  
    """
)

@st.cache_data(show_spinner=False)
def load_data(path="gusalgu.csv"):
    # 다양한 인코딩 시도(현업에서 CP949로 저장된 경우가 많음)
    encodings = ["utf-8-sig", "cp949", "euc-kr", "latin1"]
    for enc in encodings:
        try:
            df = pd.read_csv(path, encoding=enc)
            df.columns = df.columns.str.strip()
            # 날짜 컬럼 처리: 정수형 YYYYMMDD -> datetime
            if "사용일자" in df.columns:
                df["사용일자_str"] = df["사용일자"].astype(str)
                df["date"] = pd.to_datetime(df["사용일자_str"], format="%Y%m%d", errors="coerce")
            else:
                df["date"] = pd.NaT
            # 합계 컬럼 추가
            if {"승차총승객수", "하차총승객수"}.issubset(df.columns):
                df["total"] = pd.to_numeric(df["승차총승객수"], errors="coerce").fillna(0) + \
                              pd.to_numeric(df["하차총승객수"], errors="coerce").fillna(0)
            else:
                df["total"] = 0
            return df
        except Exception:
            continue
    raise FileNotFoundError("gusalgu.csv 파일을 루트에 두고 다시 시도하세요. (지원 인코딩: utf-8-sig, cp949, euc-kr, latin1)")

# 로드
with st.spinner("데이터 로드 중..."):
    df = load_data("gusalgu.csv")

# --- 필터: 2025-10의 날짜 목록 생성 ---
oct_mask = (df["date"].notna()) & (df["date"].dt.year == 2025) & (df["date"].dt.month == 10)
available_dates = df.loc[oct_mask, "date"].dropna().dt.date.unique()
available_dates = np.sort(available_dates)

if len(available_dates) == 0:
    st.error("데이터에서 2025년 10월의 날짜를 찾을 수 없습니다. CSV가 올바른지 확인하세요.")
    st.stop()

# 사이드바 컨트롤
st.sidebar.header("필터")
selected_date = st.sidebar.selectbox("날짜 선택 (2025년 10월)", available_dates, index=0)
# 노선 목록 (해당 날짜에 존재하는 노선만)
lines_on_date = df.loc[df["date"].dt.date == selected_date, "노선명"].dropna().unique()
lines_on_date = np.sort(lines_on_date)
selected_line = st.sidebar.selectbox("호선 선택", lines_on_date)

top_n = st.sidebar.number_input("상위 N개 (막대그래프)", min_value=1, max_value=50, value=10, step=1)

# 필터 적용
mask = (df["date"].dt.date == selected_date) & (df["노선명"] == selected_line)
df_f = df.loc[mask].copy()

if df_f.shape[0] == 0:
    st.warning("선택한 날짜와 호선에 해당하는 데이터가 없습니다.")
    st.stop()

# 그룹화: 역명별 total 합계 (하지만 보통 데이터는 이미 일별/역별이므로 sum이 안전)
grouped = df_f.groupby("역명", dropna=False, as_index=False)["total"].sum()
grouped = grouped.sort_values("total", ascending=False)
topk = grouped.head(int(top_n)).copy()

# 색 만들기: 1등 빨강, 나머지 파란색 그라데이션 (연한 -> 진한)
def make_colors(n):
    if n <= 0:
        return []
    colors = []
    # 첫 색: 빨강 계열
    colors.append("#ff4d4d")  # 1등
    if n == 1:
        return colors
    # 나머지: 파란색 그라데이션 (light -> dark)
    rest = n - 1
    # linear interpolation between light blue and dark blue in hex
    start_rgb = np.array([210, 230, 250]) / 255.0  # 연한파랑
    end_rgb = np.array([10, 60, 130]) / 255.0      # 진한파랑
    for i in range(rest):
        t = i / max(1, rest - 1)  # 0..1
        rgb = (1 - t) * start_rgb + t * end_rgb
        hexc = '#' + ''.join(f'{int(x*255):02x}' for x in rgb)
        colors.append(hexc)
    return colors

colors = make_colors(len(topk))

# Plotly 막대그래프 (가로 막대가 보기 좋음)
fig = px.bar(
    topk[::-1],  # 막대가 큰 값이 위로 오도록 역순
    x="total",
    y="역명",
    orientation="h",
    text="total",
    labels={"total": "승차+하차 합계", "역명": "역명"},
    title=f"{selected_date} — {selected_line} 상위 {len(topk)} 역 (승차+하차 합계)"
)

# 색 지정
fig.update_traces(marker_color=colors[::-1], textposition="outside", marker_line_width=0)
fig.update_layout(yaxis=dict(autorange="reversed"), 
                  margin=dict(l=200, r=30, t=80, b=40),
                  hovermode="y")

st.plotly_chart(fig, use_container_width=True)

# 표로도 보여주기
with st.expander("Top 결과표 보기"):
    st.dataframe(topk.reset_index(drop=True))

st.markdown("----")
st.caption("Note: CSV 파일의 `사용일자`가 YYYYMMDD 형식(정수)으로 저장되어 있어야 정상 동작합니다.")
