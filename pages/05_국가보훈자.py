# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
import calendar
from pathlib import Path
from io import BytesIO

st.set_page_config(page_title="독립유공자 — 생월/사망월 분석", layout="wide")
st.title("🇰🇷 독립유공자 — 생년월일 / 사망월 분석")

# -------------------------
# 도움말
# -------------------------
st.markdown(
    """앱 사용법:
- 리포지토리에 `국가보훈부_독립유공자 명단_20251117.csv` 파일이 있으면 자동으로 불러옵니다.
- 파일이 없으면 우측 사이드바에서 CSV 파일을 업로드하세요.
- CSV에 `생년월일` 및 `사망년월일` 같은 컬럼이 있으면 자동으로 파싱합니다."""
)

# -------------------------
# 파일 로드 (로컬 repo 우선, 없으면 업로드)
# -------------------------
DEFAULT_FILENAME = "국가보훈부_독립유공자 명단_20251117.csv"

@st.cache_data
def read_csv_robust(path_or_buffer):
    # path_or_buffer: Path or UploadedFile or string
    try:
        if isinstance(path_or_buffer, (str, Path)):
            return pd.read_csv(path_or_buffer, dtype=str)
        else:
            # streamlit UploadedFile
            return pd.read_csv(path_or_buffer, dtype=str)
    except Exception:
        # try cp949 / euc-kr fallback
        try:
            if isinstance(path_or_buffer, (str, Path)):
                return pd.read_csv(path_or_buffer, dtype=str, encoding="cp949")
            else:
                # buffer -> need to rewind
                path_or_buffer.seek(0)
                return pd.read_csv(path_or_buffer, dtype=str, encoding="cp949")
        except Exception as e:
            raise

# Check repo file
repo_file = Path(DEFAULT_FILENAME)
uploaded_file = None
if repo_file.exists():
    try:
        df = read_csv_robust(repo_file)
    except Exception as e:
        st.error(f"로컬 파일을 읽는 중 오류가 발생했습니다: {e}")
        df = None
else:
    df = None

# Sidebar: allow upload if not found or even if found allow override
st.sidebar.header("데이터 입력")
use_uploaded = st.sidebar.checkbox("파일 업로드로 대체", value=False)
if df is None or use_uploaded:
    uploaded_file = st.sidebar.file_uploader("CSV 파일 업로드 (UTF-8/CP949 지원)", type=["csv"])
    if uploaded_file is not None:
        try:
            df = read_csv_robust(uploaded_file)
            st.sidebar.success("업로드 파일 로드 완료")
        except Exception as e:
            st.sidebar.error(f"업로드 파일을 읽는 중 오류: {e}")
            st.stop()
    else:
        if df is None:
            st.error("CSV 파일을 찾을 수 없습니다. 리포 또는 업로드를 통해 CSV를 제공해주세요.")
            st.stop()

# Normalize column names
df.columns = [c.strip() for c in df.columns]
st.sidebar.write("감지된 컬럼 샘플:", df.columns.tolist()[:10])

# -------------------------
# 날짜 파싱 유틸
# -------------------------
def parse_date_flexible(x):
    if pd.isna(x):
        return pd.NaT
    s = str(x).strip()
    if s == "" or s.lower() in ["nan", "none", "-", "미상", "불명"]:
        return pd.NaT
    # replace common words
    s = re.sub(r"년|월|일|\s+", "-", s)
    s = re.sub(r"[^0-9\-\./]", "", s)
    s = s.replace(".", "-").replace("/", "-")
    # collapse multiple hyphens
    s = re.sub(r"-+", "-", s).strip("-")
    # Try YYYYMMDD (8 digits)
    if re.fullmatch(r"\d{8}", s):
        try:
            return pd.to_datetime(s, format="%Y%m%d", errors="coerce")
        except:
            pass
    # Try YYMMDD (6 digits)
    if re.fullmatch(r"\d{6}", s):
        yy = int(s[:2])
        if yy <= 25:
            year = 2000 + yy
        else:
            year = 1900 + yy
        try:
            return pd.to_datetime(f"{year}{s[2:]}", format="%Y%m%d", errors="coerce")
        except:
            pass
    # Try general pd.to_datetime
    try:
        return pd.to_datetime(s, errors="coerce", dayfirst=False)
    except:
        return pd.NaT

# -------------------------
# 컬럼 자동 감지 (생년월일, 사망년월일)
# -------------------------
possible_birth_cols = [c for c in df.columns if "생" in c or "birth" in c.lower() or "출생" in c]
possible_death_cols = [c for c in df.columns if "사망" in c or "죽" in c or "death" in c.lower()]

birth_col = possible_birth_cols[0] if possible_birth_cols else None
death_col = possible_death_cols[0] if possible_death_cols else None

st.sidebar.markdown("**자동 감지된 날짜 컬럼**")
st.sidebar.write("생년월일:", birth_col)
st.sidebar.write("사망년월일:", death_col)

if not birth_col:
    st.error("생년월일 컬럼을 자동으로 찾지 못했습니다. CSV의 해당 컬럼명을 알려주시거나 업로드 파일을 확인해주세요.")
    st.stop()

# Parse columns with caching
@st.cache_data
def prepare_df(df_in, birth_col_name, death_col_name=None):
    df2 = df_in.copy()
    # parse birth
    df2["_parsed_birth"] = df2[birth_col_name].apply(parse_date_flexible)
    df2["birth_month"] = df2["_parsed_birth"].dt.month
    # parse death if present
    if death_col_name and death_col_name in df2.columns:
        df2["_parsed_death"] = df2[death_col_name].apply(parse_date_flexible)
        df2["death_month"] = df2["_parsed_death"].dt.month
    else:
        df2["_parsed_death"] = pd.NaT
        df2["death_month"] = pd.NA
    return df2

df = prepare_df(df, birth_col, death_col)

# Basic stats
total_rows = len(df)
valid_birth = int(df["_parsed_birth"].notna().sum())
invalid_birth = total_rows - valid_birth
valid_death = int(df["_parsed_death"].notna().sum()) if death_col else 0

st.sidebar.markdown(f"- 총 행: **{total_rows}**")
st.sidebar.markdown(f"- 생년월일 유효: **{valid_birth}** / 없음 또는 파싱실패: **{invalid_birth}**")
if death_col:
    st.sidebar.markdown(f"- 사망년월일 유효: **{valid_death}**")

# -------------------------
# UI: 월 선택 (생월)
# -------------------------
st.header("1) 월 선택 → 그 달에 태어난 유공자 목록 보기")
col1, col2 = st.columns([2,1])
with col2:
    selected_month = st.selectbox("월 선택 (생월)", options=list(range(1,13)), index=0, format_func=lambda x: f"{x}월")
    show_columns = st.multiselect("표시할 컬럼(최대 15개)", options=list(df.columns)[:20], default=[birth_col, "성명"] if "성명" in df.columns else [birth_col])
    if len(show_columns) == 0:
        show_columns = df.columns.tolist()[:8]
    download_btn = st.checkbox("CSV 다운로드 버튼 표시", value=True)

with col1:
    filtered_birth = df[df["birth_month"] == selected_month]
    st.subheader(f"{selected_month}월에 태어난 유공자 — 총 {len(filtered_birth)}명")
    if len(filtered_birth) == 0:
        st.info("해당 월에 태어나신 분이 없습니다 (또는 생년월일 파싱이 되지 않음).")
    else:
        st.dataframe(filtered_birth[show_columns].reset_index(drop=True), use_container_width=True)
    if download_btn and len(filtered_birth) > 0:
        csv_bytes = filtered_birth.to_csv(index=False).encode("utf-8-sig")
        st.download_button("📥 선택 월 명단 다운로드 (CSV)", data=csv_bytes, file_name=f"{selected_month}월_명단.csv", mime="text/csv")

# -------------------------
# 그래프: 월별 생월 수
# -------------------------
st.header("2) 월별로 어떤 달에 가장 많이 태어났는지 (Interactive)")
birth_counts = df["birth_month"].value_counts().reindex(range(1,13), fill_value=0)
birth_df = pd.DataFrame({"month": list(range(1,13)), "count": birth_counts.values, "month_name": [calendar.month_name[m] for m in range(1,13)]})

# color scheme: top -> Korean color (red), others gradient (blue shades)
def make_colors_for_counts(counts, top_color="rgb(220,20,60)"):
    # counts: list-like length 12
    idx_top = int(pd.Series(counts).idxmax())
    colors = []
    # gradient from lightblue to darkblue for non-top
    for i in range(len(counts)):
        if i == idx_top:
            colors.append(top_color)
        else:
            t = i / (len(counts) - 1)
            # interpolate between light (180,210,240) and deep (10,60,130)
            r = int((1 - t) * 180 + t * 10)
            g = int((1 - t) * 210 + t * 60)
            b = int((1 - t) * 240 + t * 130)
            colors.append(f"rgb({r},{g},{b})")
    return colors

birth_colors = make_colors_for_counts(birth_df["count"].tolist())

fig_birth = go.Figure()
fig_birth.add_trace(go.Bar(
    x=birth_df["month_name"],
    y=birth_df["count"],
    marker_color=birth_colors,
    hovertemplate="%{x}: %{y}명<extra></extra>"
))
fig_birth.update_layout(title_text="월별 태어난 유공자 수", xaxis_title="월", yaxis_title="인원수", template="simple_white")
st.plotly_chart(fig_birth, use_container_width=True)

# -------------------------
# 그래프: 월별 사망월 수 (있으면)
# -------------------------
st.header("3) 월별로 어떤 달에 가장 많이 돌아가셨는지 (Interactive)")
if death_col:
    death_counts = df["death_month"].value_counts().reindex(range(1,13), fill_value=0)
    death_df = pd.DataFrame({"month": list(range(1,13)), "count": death_counts.values, "month_name": [calendar.month_name[m] for m in range(1,13)]})
    death_colors = make_colors_for_counts(death_df["count"].tolist(), top_color="rgb(0,56,168)")  # top color blue-ish for variety
    fig_death = go.Figure()
    fig_death.add_trace(go.Bar(
        x=death_df["month_name"],
        y=death_df["count"],
        marker_color=death_colors,
        hovertemplate="%{x}: %{y}명<extra></extra>"
    ))
    fig_death.update_layout(title_text="월별 사망(돌아가심) 유공자 수", xaxis_title="월", yaxis_title="인원수", template="simple_white")
    st.plotly_chart(fig_death, use_container_width=True)
else:
    st.info("사망년월일 컬럼을 찾지 못했습니다. CSV에 '사망' 관련 컬럼명이 있는지 확인해주세요.")

# -------------------------
# 추가: 상위 월(Top N) / 샘플 목록 보기
# -------------------------
st.header("4) 월별 상위(많은) 월 확인 및 샘플 보기")
col3, col4 = st.columns(2)
with col3:
    topn = st.number_input("상위 N개 월 보기 (N)", min_value=1, max_value=12, value=3)
    sorted_birth = birth_df.sort_values("count", ascending=False).reset_index(drop=True)
    st.write(sorted_birth.head(topn)[["month_name", "count"]])

with col4:
    sample_month = st.selectbox("샘플 보기 - 월 선택", options=list(range(1,13)), format_func=lambda x: f"{x}월")
    sample_rows = st.number_input("샘플 행 수", min_value=1, max_value=200, value=10)
    sample_df = df[df["birth_month"] == sample_month]
    if sample_df.empty:
        st.write("샘플이 없습니다.")
    else:
        st.dataframe(sample_df.head(sample_rows))

# -------------------------
# 끝: 요약 다운로드 (요약 JSON/CSV)
# -------------------------
st.markdown("---")
if st.button("요약 CSV 다운로드 (월별 생/사망 집계)"):
    summary = pd.DataFrame({
        "month": birth_df["month"],
        "month_name": birth_df["month_name"],
        "birth_count": birth_df["count"],
        "death_count": (death_df["count"] if death_col else [0]*12)
    })
    out = summary.to_csv(index=False).encode("utf-8-sig")
    st.download_button("📥 요약 CSV", data=out, file_name="summary_month_birth_death.csv", mime="text/csv")
    st.success("요약 CSV가 준비되었습니다.")
