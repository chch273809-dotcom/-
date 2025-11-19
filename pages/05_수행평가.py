# pages/1_분석_페이지.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# --- 설정 및 데이터 로드 ---
st.set_page_config(layout="wide")

# 데이터 로드 (Streamlit 캐싱을 사용하여 성능 최적화)
@st.cache_data
def load_and_preprocess_data():
    
    # 6. 파이썬 코드는 pages 폴더 밑에, csv 파일은 루트 폴더에 있으므로 pathlib로 경로 설정
    try:
        # 현재 파일(1_분석_페이지.py) -> pages 폴더 -> 루트 폴더 (경로: ../)
        base_dir = Path(__file__).resolve().parent.parent 
        file_path = base_dir / "police.crime..csv"
        
        if not file_path.exists():
            # 파일 경로 오류 시 메시지 출력
            st.error(f"🚨 파일을 찾을 수 없습니다. 경로를 확인해주세요: {file_path}")
            return pd.DataFrame()

        # CSV 파일 로드
        df = pd.read_csv(file_path)

    except Exception as e:
        st.error(f"데이터 로드 중 오류 발생: {e}")
        return pd.DataFrame() 

    # 1. '경찰서' 컬럼에서 '지역(시/도)명' 추출 (Pandas 분석 및 전처리)
    crime_cols = ['살인', '강도', '절도', '폭력']
    
    # 경찰서 이름의 앞 2글자(지역명) 추출
    # '서울중부서' -> '서울', '전남영광서' -> '전남'
    df['지역'] = df['경찰서'].apply(
        lambda x: x[:2] if len(x) > 2 and x[1] in '울산광주대전대구부산인천세종경기강원충북충남전북전남경북경남제주' else x
    )
    
    # 지역별 범죄 총합 계산
    df_grouped = df.groupby('지역')[crime_cols].sum().reset_index()
    
    return df_grouped

df_crime_by_region = load_and_preprocess_data()

# 데이터 로드 실패 시 앱 종료
if df_crime_by_region.empty:
    st.stop()
    
# --- Streamlit UI 구성 ---
st.title("📊 지역별 4대 강력범죄 발생 현황 (2024년)")
st.markdown("---")

# 3. 국가(지역) 선택 필터 (요청에 따라 '국가' 대신 '지역'을 사용)
regions = sorted(df_crime_by_region['지역'].unique())
selected_region = st.selectbox(
    "📍 **분석할 지역(시/도)을 선택하세요:**", 
    regions,
    index=regions.index('서울') if '서울' in regions else 0
)

if selected_region:
    # 선택된 지역의 데이터 추출 및 피벗
    region_data = df_crime_by_region[df_crime_by_region['지역'] == selected_region]
    
    # 그래프를 그리기 위해 데이터 변환
    df_plot = region_data.melt(
        id_vars='지역', 
        value_vars=['살인', '강도', '절도', '폭력'], 
        var_name='범죄 유형', 
        value_name='발생 건수'
    )
    
    # 최다 발생 범죄 유형 찾기
    max_crime_row = df_plot.loc[df_plot['발생 건수'].idxmax()]
    max_crime_type = max_crime_row['범죄 유형']
    
    # 4. 그래프 색상 설정: 1등은 빨간색, 나머지는 그라데이션 느낌
    
    # 기본 색상 (그라데이션 느낌의 붉은 계열)
    # 살인, 강도, 절도, 폭력 순서로 심각성이 높다고 가정하고 짙은 색을 배정
    color_map = {
        '살인': '#CC0000', '강도': '#FF6666', 
        '절도': '#FF9999', '폭력': '#FFCCCC' 
    }
    
    # 최고값의 색상을 가장 진한 빨간색 (#FF0000)으로 지정
    color_map_final = {k: v for k, v in color_map.items()}
    color_map_final[max_crime_type] = '#FF0000' # 1등은 빨간색

    # Plotly 막대 그래프 생성
    fig = go.Figure()
    
    for crime_type in ['살인', '강도', '절도', '폭력']:
        count = df_plot[df_plot['범죄 유형'] == crime_type]['발생 건수'].iloc[0]
        
        fig.add_trace(go.Bar(
            x=[crime_type],
            y=[count],
            name=crime_type,
            marker_color=color_map_final[crime_type], # 설정된 색상 적용
            text=f"{count:,} 건", # 천 단위 구분 기호 적용
            textposition='outside'
        ))

    # 2. plotly로 깔끔하고 인터랙티브한 데이터 출력
    fig.update_layout(
        title=f"**{selected_region}** 지역 4대 강력범죄 발생 건수 비교",
        xaxis_title="범죄 유형",
        yaxis_title="발생 건수 (건)",
        hovermode="x unified",
        showlegend=False, 
        template="plotly_white",
    )

    st.plotly_chart(fig, use_container_width=True)
    
    # 분석 요약 정보
    st.markdown("---")
    st.subheader(f"📌 {selected_region} 지역 범죄 현황 요약")
    st.info(f"""
    선택하신 **{selected_region}** 지역의 4대 강력범죄 중 **'{max_crime_type}'** 발생 건수가 **{max_crime_row['발생 건수']:,} 건**으로 가장 높습니다.
    """)
    
    # 원본 데이터 테이블 표시
    st.markdown("### 🔍 데이터 테이블")
    # 원본 데이터 (지역별 합계)를 보기 좋게 표시
    st.dataframe(region_data.set_index('지역'), use_container_width=True)

else:
    st.warning("분석할 지역을 선택해주세요.")
