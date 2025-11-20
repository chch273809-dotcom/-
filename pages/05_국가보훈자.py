# app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re
import calendar
from pathlib import Path
from io import StringIO, BytesIO

st.set_page_config(page_title="독립유공자 — 생월/사망월 분석 (견고 버전)", layout="wide")
st.title("🇰🇷 독립유공자 — 생월 & 사망월 분석 (인코딩 오류 방어 포함)")

DEFAULT_CSV = "The.korean.goat.csv"

# ---------------------
# 파일 읽기: 여러 인코딩 시도 + 안전한 대체 방법
# ---------------------
@st.cache_data
def read_csv_robust(path_or_buffer):
    """
    path_or_buffer: str path or streamlit UploadedFile
    Tries several encodings; if all fail, reads binary and decodes with 'replace'.
    Returns a pandas.DataFrame.
    """
    encodings_to_try = ["utf-8", "utf-8-sig", "cp949", "euc-kr", "latin1"]
    read_kwargs = dict(dtype=str, low_memory=False)
    # If path is a path string or Path
    try_paths = []
    if isinstance(path_or_buffer, (str, Path)):
        try_paths = [str(path_or_buffer)]
    else:
        # UploadedFile-like object (has read()/seek())
        # We'll handle separately below
        pass

    # 1) If it's path-like, try pandas.read_csv with different encodings
    if try_paths:
        p = try_paths[0]
        for enc in encodings_to_try:
            try:
                df = pd.read_csv(p, encoding=enc, **read_kwargs)
                return df
            except Exception:
                continue
        # last resort: open binary and decode with replace
        with open(p, "rb") as f:
            raw = f.read()
        text = raw.decode("utf-8", errors="replace")
        return pd.read_csv(StringIO(text), **read_kwargs)

    # 2) If it's a buffer (UploadedFile), try reading same way but with seek resets
    else:
        buf = path_or_buffer
        for enc in encodings_to_try:
            try:
                buf.seek(0)
                df = pd.read_csv(buf, encoding=enc, **read_kwargs)
                return df
            except Exception:
                continue
        # fallback: read binary and decode with replace
        buf.seek(0)
        raw = buf.read()
        if isinstance(raw, bytes):
            text = raw.decode("utf-8", errors="replace")
        else:
            # sometimes UploadedFile.read() returns str
            text = str(raw)
        return pd.read_csv(StringIO(text), **read_kwargs)

# ---------------------
# Load data: repo file preferred, else upload
# ---------------------
def load_data_with_ui():
    repo_path = Path(DEFAULT_CSV)
    df = None
    if repo_path.exists():
        try:
            df = read_csv_robust(repo_path)
            st.sidebar.success(f"로컬 파일 '{DEFAULT_CSV}' 로드 성공")
        except Exception as e:
            st.sidebar.error(f"로컬 파일 로드 실패: {e}")
            df = None

    st.sidebar.markdown("---")
    st.sidebar.write("원본 CSV가 없다면 업로드하세요 (UTF-8/CP949 지원).")
    uploaded = st.sidebar.file_uploader("CSV 업로드 (대체)", type=["csv"])
    if uploaded is not None:
        try:
            df = read_csv_robust(uploaded)
            st.sidebar.success("업로드 파일 로드 성공")
        except Exception as e:
            st.sidebar.error(f"업로드 파일 읽기 실패: {e}")
            st.stop()

    if df is None:
        st.error(f"'{DEFAULT_CSV}' 파일을 찾을 수 없고 업로드도 되지 않았습니다. 파일을 추가해주세요.")
        st.stop()

    # normalize column names
    df.columns = [c.strip() for c in df.columns]
    return df

df = load_data_with_ui()

# ---------------------
# 날짜 파싱 유틸 (여러 포맷 허용)
# ---------------------
def parse_date_flexible(x):
    if pd.isna(x):
        return pd.NaT
    s = str(x).strip()
    if s == "" or s.lower() in {"nan", "none", "-", "미상", "불명"}:
        return pd.NaT
    # common replacements
    s = re.sub(r"년|월|일|\s+", "-", s)
    s = re.sub(r"[^0-9\-\./]", "", s)
    s = s.replace(".", "-").replace("/", "-")
    s = re.sub(r"-+", "-", s).strip("-")
    # direct patterns
    if re.fullmatch(r"\d{8}", s):
        return pd.to_datetime(s, format="%Y%m%d", errors="coerce")
    if re.fullmatch(r"\d{6}", s):
        yy = int(s[:2])
        year = 2000 + yy if yy <= 25 else 1900 + yy
        try:
            return pd.to_datetime(f"{year}{s[2:]}", format="%Y%m%d", errors="coerce")
        except:
            pass
    try:
        return pd.to_datetime(s, errors="coerce")
    except:
        return pd.NaT

# ---------------------
# 자동 컬럼 감지 (생년월일 / 사망년월일)
# ---------------------
possible_birth_cols = [c for c in df.columns if "생" in c or "birth" in c.lower() or "출생" in c]
possible_death_cols = [c for c in df.columns if "사망" in c or "death" in c.lower() or "별세" in c]

birth_col = possible_birth_cols[0] if possible_birth_cols else None
death_col = possible_death_cols[0] if possible_death_cols else None

st.sidebar.markdown("**감지된 날짜 컬럼**")
st.sidebar.write("생년월일:", birth_col)
st.sidebar.write("사망년월일:", death_col or "없음")

if not birth_col:
    st.error("CSV에서 생년월일(또는 출생 관련) 컬럼을 찾을 수 없습니다. 컬럼명을 확인해 주세요.")
    st.stop()

# ---------------------
# 파싱 적용 (캐시)
# ---------------------
@st.cache_data
def prepare(df_in, birth_col_name, death_col_name=None):
    df2 = df_in.copy()
    df2["_parsed_birth"] = df2[birth_col_name].apply(parse_date_flexible)
    df2["birth_month"] = df2["_parsed_birth"].dt.month
    if death_col_name and death_col_name in df2.columns:
        df2["_parsed_death"] = df2[death_col_name].apply(parse_date_flexible)
        df2["death_month"] = df2["_parsed_death"].dt.month
    else:
        df2["_parsed_death"] = pd.NaT
        df2["death_month"] = pd.NA
    return df2

df = prepare(df, birth_col, death_col)

# ---------------------
# 사이드바: 옵션
# ---------------------
st.sidebar.markdown("---")
st.sidebar.header("조회 옵션")
selected_month = st.sidebar.selectbox("출생월 선택", options=list(range(1,13)), index=0, format_func=lambda x: f"{x}월")
display_cols = st.sidebar.multiselect("표시할 컬럼 (샘플)", options=list(df.columns)[:30], default=[birth_col] + ([c for c in df.columns if c.lower().strip() in ("성명","이름","name")] or []))
if not display_cols:
    display_cols = df.columns.tolist()[:8]

# ---------------------
# 1) 선택한 월의 명단 출력
# ---------------------
st.header(f"📋 {selected_month}월에 태어나신 유공자 목록")
filtered_birth = df[df["birth_month"] == selected_month]
st.write(f"총 {len(filtered_birth)}명")

if len(filtered_birth) == 0:
    st.info("해당 월에 태어나신 분이 없거나 생년월일이 파싱되지 않았습니다.")
else:
    st.dataframe(filtered_birth[display_cols].reset_index(drop=True), use_container_width=True)
    csv_bytes = filtered_birth.to_csv(index=False).encode("utf-8-sig")
    st.download_button("📥 선택 월 명단 다운로드 (CSV)", data=csv_bytes, file_name=f"{selected_month}월_명단.csv", mime="text/csv")

# ---------------------
# 2) 월별 출생 그래프 (Plotly) — 1등 한국 색, 나머지 그라데이션
# ---------------------
st.header("📊 월별 출생자 수 (인터랙티브)")

birth_counts = df["birth_month"].value_counts().reindex(range(1,13), fill_value=0)
birth_df = pd.DataFrame({"month": list(range(1,13)), "count": birth_counts.values, "month_name": [calendar.month_name[m] for m in range(1,13)]})

# color maker: top gets Korean red; others: blue gradient
def make_month_colors(counts, top_color="rgb(220,20,60)"):
    idx_top = int(pd.Series(counts).idxmax())
    colors = []
    n = len(counts)
    for i in range(n):
        if i == idx_top:
            colors.append(top_color)
        else:
            t = i / (n - 1) if n > 1 else 0
            # gradient light->dark blue
            r = int((1 - t) * 180 + t * 10)
            g = int((1 - t) * 210 + t * 60)
            b = int((1 - t) * 240 + t * 130)
            colors.append(f"rgb({r},{g},{b})")
    return colors

birth_colors = make_month_colors(birth_df["count"].tolist(), top_color="rgb(220,20,60)")

fig_b = go.Figure(go.Bar(
    x=birth_df["month_name"],
    y=birth_df["count"],
    marker_color=birth_colors,
    hovertemplate="%{x}: %{y}명<extra></extra>"
))
fig_b.update_layout(title="월별 태어난 유공자 수", xaxis_title="월", yaxis_title="인원수", template="simple_white")
st.plotly_chart(fig_b, use_container_width=True)

# ---------------------
# 3) 월별 사망 그래프 (있을 때)
# ---------------------
st.header("📊 월별 사망자 수 (인터랙티브)")
if death_col:
    death_counts = df["death_month"].value_counts().reindex(range(1,13), fill_value=0)
    death_df = pd.DataFrame({"month": list(range(1,13)), "count": death_counts.values, "month_name": [calendar.month_name[m] for m in range(1,13)]})
    # top color: Korean blue-ish to differentiate (or you can use same red)
    death_colors = make_month_colors(death_df["count"].tolist(), top_color="rgb(0,56,168)")
    fig_d = go.Figure(go.Bar(
        x=death_df["month_name"],
        y=death_df["count"],
        marker_color=death_colors,
        hovertemplate="%{x}: %{y}명<extra></extra>"
    ))
    fig_d.update_layout(title="월별 사망 유공자 수", xaxis_title="월", yaxis_title="인원수", template="simple_white")
    st.plotly_chart(fig_d, use_container_width=True)
else:
    st.info("CSV에 사망일 관련 컬럼이 감지되지 않았습니다. (사망 관련 컬럼명에 '사망'/'death'/'별세' 등이 포함되어야 자동 감지됩니다.)")

# ---------------------
# 4) 요약 다운로드: 월별 집계 CSV
# ---------------------
st.markdown("---")
if st.button("요약 CSV 생성 (월별 생/사망 집계)"):
    summary = pd.DataFrame({
        "month": birth_df["month"],
        "month_name": birth_df["month_name"],
        "birth_count": birth_df["count"],
        "death_count": (death_df["count"] if death_col else [0]*12)
    })
    out = summary.to_csv(index=False).encode("utf-8-sig")
    st.download_button("📥 요약 CSV 다운로드", data=out, file_name="summary_month_birth_death.csv", mime="text/csv")

st.caption("참고: 인코딩/파싱 문제는 로그에 기록됩니다. 문제가 계속되면 CSV 예시(몇 줄)를 보여주시면 맞춤 파싱 규칙을 추가해 드릴게요.")
