import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd

st.set_page_config(page_title="Seoul Top10 Map", layout="wide")

st.title("🌏 외국인이 사랑하는 서울 관광지 TOP 10")
st.markdown("서울의 대표 명소들을 Folium 지도로 만나보세요!")

# 관광지 데이터
data = [
    ["경복궁 (Gyeongbokgung Palace)", 37.579617, 126.977041, "조선의 대표 궁궐로 한복 체험 명소!"],
    ["남산서울타워 (N Seoul Tower)", 37.551170, 126.988228, "서울 전경을 한눈에! 야경이 특히 아름다워요."],
    ["명동 (Myeongdong)", 37.5641353, 126.9827516, "쇼핑과 길거리 음식의 천국!"],
    ["북촌한옥마을 (Bukchon Hanok Village)", 37.582600, 126.983000, "전통 한옥이 늘어선 골목길 산책 추천."],
    ["인사동 (Insadong)", 37.574353, 126.984355, "전통 찻집과 공예품 가게가 즐비한 거리."],
    ["동대문디자인플라자 (DDP)", 37.5669, 127.0094, "자하 하디드의 작품, 야경이 아름다운 디자인 랜드마크."],
    ["홍대거리 (Hongdae Street)", 37.555280, 126.923330, "젊음과 예술이 살아있는 거리."],
    ["창덕궁 (Changdeokgung Palace)", 37.579617, 126.991017, "세계문화유산으로 지정된 아름다운 궁궐."],
    ["광화문광장 (Gwanghwamun Square)", 37.575940, 126.976822, "이순신 장군 동상과 경복궁 입구의 명소."],
    ["롯데월드타워 (Lotte World Tower)", 37.513000, 127.102500, "서울에서 가장 높은 초고층 전망대!"]
]

df = pd.DataFrame(data, columns=["name", "lat", "lon", "desc"])

# 지도 설정
st.sidebar.header("🗺️ 지도 설정")
map_style = st.sidebar.selectbox("지도 스타일 선택", ["OpenStreetMap", "Stamen Toner", "Stamen Terrain"])
zoom = st.sidebar.slider("줌 레벨", 8, 16, 12)

# 지도 생성
m = folium.Map(location=[37.56, 126.98], zoom_start=zoom, tiles=map_style)

for _, row in df.iterrows():
    folium.Marker(
        [row["lat"], row["lon"]],
        popup=f"<b>{row['name']}</b><br>{row['desc']}",
        tooltip=row["name"]
    ).add_to(m)

# 지도 표시
st_folium(m, width=900, height=600)

# 장소 리스트 출력
st.subheader("📍 관광지 목록")
for _, row in df.iterrows():
    st.markdown(f"**{row['name']}** — {row['desc']}")

# requirements.txt 내용
st.sidebar.download_button(
    "📦 requirements.txt 다운로드",
    data="streamlit\nfolium\nstreamlit-folium\npandas\n",
    file_name="requirements.txt",
    mime="text/plain"
)

# 코드 보기
st.subheader("💻 앱 코드 (복사해서 사용 가능)")
with open(__file__, "r", encoding="utf-8") as f:
    st.code(f.read(), language="python")
