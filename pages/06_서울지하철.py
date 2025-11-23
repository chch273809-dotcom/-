import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import zipfile
import io

st.set_page_config(page_title="서울 지하철 승차·하차 분석", layout="wide")

st.title("🚇 서울 지하철 시간대별 승차·하차 분석")
st.write("ZIP 파일을 업로드하면 자동으로 CSV를 추출하여 분석합니다.")

# ------------------------
# ZIP 파일 업로드
# ------------------------
uploaded_zip = st.file_uploader("📦 ZIP 파일 업로드", type=["zip"])

if uploaded_zip is not None:
    with zipfile.ZipFile(uploaded_zip, 'r') as z:
        # ZIP 내부에서 CSV 파일 읽기
        file_list = z.namelist()
        csv_name = [f for f in file_list if f.endswith(".csv")][0]  # 자동 탐색
        csv_file = z.open(csv_name)

        df = pd.read_csv(csv_file, encoding="cp949")

    st.success("ZIP 파일에서 CSV를 성공적으로 불러왔습니다!")

    # ------------------------
    # 사용자 선택 기능
    # ------------------------
    st.subheader("🔎 분석 옵션")

    line_options = sorted(df["호선명"].unique())
    selected_line = st.selectbox("호선 선택", line_options)

    station_options = sorted(df[df["호선명"] == selected_line]["지하철역"].unique())
    selected_station = st.selectbox("역 선택", station_options)

    data = df[(df["호선명"] == selected_line) & (df["지하철역"] == selected_station)]

    # ------------------------
    # 시간대별 승차/하차 계산
    # ------------------------
    time_columns = [col for col in df.columns if "승차인원" in col or "하차인원" in col]

    time_labels = [col.replace(" 승차인원", "").replace(" 하차인원", "") 
                   for col in time_columns[0::2]]

    board = data[[col for col in time_columns if "승차" in col]].sum().values
    alight = data[[col for col in time_columns if "하차" in col]].sum().values

    # 최대·최소 시간대 탐색
    max_board_idx = board.argmax()
    min_board_idx = board.argmin()

    max_alight_idx = alight.argmax()
    min_alight_idx = alight.argmin()

    # ------------------------
    # 결과 표시
    # ------------------------
    st.subheader("📊 시간대별 승차·하차 요약")

    col1, col2 = st.columns(2)

    with col1:
        st.write("### ⏰ 승차 인원")
        st.write(f"🚨 **최대 승차 시간대:** {time_labels[max_board_idx]} — {board[max_board_idx]:,}명")
        st.write(f"💧 **최소 승차 시간대:** {time_labels[min_board_idx]} — {board[min_board_idx]:,}명")

    with col2:
        st.write("### ⏰ 하차 인원")
        st.write(f"🚨 **최대 하차 시간대:** {time_labels[max_alight_idx]} — {alight[max_alight_idx]:,}명")
        st.write(f"💧 **최소 하차 시간대:** {time_labels[min_alight_idx]} — {alight[min_alight_idx]:,}명")

    # ------------------------
    # Plotly 그래프
    # ------------------------
    st.subheader("📈 시간대별 승차·하차 그래프")

    fig = go.Figure()

    # 승차
    fig.add_trace(go.Scatter(
        x=time_labels, y=board,
        mode="lines+markers",
        name="승차 인원",
        line=dict(width=3),
        marker=dict(size=8)
    ))

    # 하차
    fig.add_trace(go.Scatter(
        x=time_labels, y=alight,
        mode="lines+markers",
        name="하차 인원",
        line=dict(width=3),
        marker=dict(size=8)
    ))

    # 최대/최소 표시
    fig.add_trace(go.Scatter(
        x=[time_labels[max_board_idx]], y=[board[max_board_idx]],
        mode="markers",
        marker=dict(size=16, color="red"),
        name="승차 최대"
    ))

    fig.add_trace(go.Scatter(
        x=[time_labels[min_board_idx]], y=[board[min_board_idx]],
        mode="markers",
        marker=dict(size=16, color="blue"),
        name="승차 최소"
    ))

    fig.add_trace(go.Scatter(
        x=[time_labels[max_alight_idx]], y=[alight[max_alight_idx]],
        mode="markers",
        marker=dict(size=16, color="red"),
        name="하차 최대"
    ))

    fig.add_trace(go.Scatter(
        x=[time_labels[min_alight_idx]], y=[alight[min_alight_idx]],
        mode="markers",
        marker=dict(size=16, color="blue"),
        name="하차 최소"
    ))

    fig.update_layout(
        title=f"{selected_line} {selected_station} 시간대별 승하차 변화",
        template="plotly_white",
        xaxis_title="시간대",
        yaxis_title="인원",
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("ZIP 파일을 업로드하면 분석이 시작됩니다.")
