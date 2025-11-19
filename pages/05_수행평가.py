# pages/1_분석_페이지.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- 설정 및 데이터 로드 ---
st.set_page_config(layout="wide")

# 데이터 로드 (Streamlit 캐싱을 사용하여 성능 최적화)
@st.cache_data
def load_data():
    try:
        # csv 파일은 루트 폴더에 있다고 가정
        df = pd.read_csv("경찰청_전국 경찰서별 강력범죄 발생 현황_20241231.csv")
    except FileNotFoundError:
        st.error("🚨 '경찰청_전국 경찰서별 강력범죄 발생 현황_20241231.csv' 파일을 찾을 수 없습니다. 파일 경로를 확인해주세요.")
        return pd.DataFrame() # 빈 데이터프레임 반환

    # 1. '경찰서' 컬럼에서 '지역(시/도)명' 추출
    # '서울중부서' -> '서울', '전남영광서' -> '전남', '부산남부서' -> '부산'
    df['지역'] = df['경찰서'].apply(lambda x: x[:2] if len(x) > 2 and x[1] in '울산광주대전대구부산인천세종경기강원충북충남전북전남경북경남제주' else x)
    
    # 2. 지역별 범죄 총합 계산
    crime_cols = ['살인', '강도', '절도', '폭력']
    df_grouped = df.groupby('지역')[crime_cols].sum().reset_index()
    
    return df_grouped

df_crime_by_region = load_data()

# 데이터 로드 실패 시 종료
if df_crime_by_region.empty:
    st.stop()
    
# --- Streamlit UI 구성 ---
st.title("📊 지역별 4대 강력범죄 발생 현황 (2024년)")
st.markdown("---")

# 3. 국가(지역) 선택 필터
regions = sorted(df_crime_by_region['지역'].unique())
selected_region = st.selectbox(
    "📍 **분석할 지역(시/도)을 선택하세요:**", 
    regions,
    index=regions.index('서울') if '서울' in regions else 0 # 기본값 '서울' 설정
)

if selected_region:
    # 선택된 지역의 데이터 추출 및 피벗
    region_data = df_crime_by_region[df_crime_by_region['지역'] == selected_region]
    
    # 그래프를 그리기 위해 데이터 변환 (살인, 강도, 절도, 폭력을 하나의 컬럼으로)
    df_plot = region_data.melt(
        id_vars='지역', 
        value_vars=['살인', '강도', '절도', '폭력'], 
        var_name='범죄 유형', 
        value_name='발생 건수'
    )
    
    # 최다 발생 범죄 유형 찾기
    max_crime_row = df_plot.loc[df_plot['발생 건수'].idxmax()]
    max_crime_type = max_crime_row['범죄 유형']
    max_crime_count = max_crime_row['발생 건수']
    
    # 4. 그래프 색상 설정: 1등은 빨간색, 나머지는 그라데이션
    # 색상 맵 정의
    # 빨간색 (최고), 주황색, 노란색 계열 그라데이션
    color_map = {
        '살인': '#FF9999', '강도': '#FFCC99', 
        '절도': '#FFDDCC', '폭력': '#FFEEEE' 
    }
    
    # 최고값의 색상을 빨간색으로 재설정
    # 빨간색 계열의 가장 진한 색
    color_map[max_crime_type] = '#FF0000' 
    
    # Plotly 막대 그래프 생성
    fig = go.Figure()
    
    for crime_type in ['살인', '강도', '절도', '폭력']:
        count = df_plot[df_plot['범죄 유형'] == crime_type]['발생 건수'].iloc[0]
        
        fig.add_trace(go.Bar(
            x=[crime_type],
            y=[count],
            name=crime_type,
            marker_color=color_map[crime_type], # 설정된 색상 적용
            text=f"{count} 건",
            textposition='outside'
        ))

    # 그래프 레이아웃 설정
    fig.update_layout(
        title=f"**{selected_region}** 지역 4대 강력범죄 발생 건수 비교",
        xaxis_title="범죄 유형",
        yaxis_title="발생 건수 (건)",
        hovermode="x unified",
        showlegend=False, # 범례 숨김 (막대 그래프는 보통 숨김)
        template="plotly_white", # 깔끔한 테마
        uniformtext_minsize=8, uniformtext_mode='hide'
    )

    # 2. plotly로 깔끔하고 인터랙티브한 데이터 출력
    st.plotly_chart(fig, use_container_width=True)
    
    # 분석 요약 정보
    st.markdown("---")
    st.subheader(f"📌 {selected_region} 지역 범죄 현황 요약")
    st.info(f"""
    선택하신 **{selected_region}** 지역의 4대 강력범죄 중 **'{max_crime_type}'** 발생 건수가 **{max_crime_count:,} 건**으로 가장 높습니다.
    * **살인:** {region_data['살인'].iloc[0]:,} 건
    * **강도:** {region_data['강도'].iloc[0]:,} 건
    * **절도:** {region_data['절도'].iloc[0]:,} 건
    * **폭력:** {region_data['폭력'].iloc[0]:,} 건
    """)
    
    # 원본 데이터 테이블 표시
    st.markdown("### 🔍 데이터 테이블")
    # 보여주기 쉽게 전치 (Transpose)
    st.dataframe(df_plot.set_index('범죄 유형').T.drop('지역', axis=0), use_container_width=True)

else:
    st.warning("분석할 지역을 선택해주세요.")
