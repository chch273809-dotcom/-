# pages/1_분석_페이지.py

# ... (생략) ...

@st.cache_data
def load_and_preprocess_data():
    
    try:
        base_dir = Path(__file__).resolve().parent.parent 
        file_path = base_dir / "police.crime..csv"
        
        if not file_path.exists():
            st.error(f"🚨 파일을 찾을 수 없습니다. 경로를 확인해주세요: {file_path}")
            return pd.DataFrame()

        # 🚩 오류 해결 지점: encoding='cp949' 옵션 추가
        df = pd.read_csv(file_path, encoding='cp949') 

    except Exception as e:
        # CP949도 실패할 경우를 대비하여 오류 메시지를 출력합니다.
        st.error(f"데이터 로드 중 오류 발생 (현재 CP949 시도 중): {e}")
        
        # CP949가 실패하면 EUC-KR로 다시 시도하는 로직을 추가할 수도 있습니다.
        # 예를 들어: 
        # try:
        #     df = pd.read_csv(file_path, encoding='euc-kr')
        # except Exception:
        #     return pd.DataFrame()
        
        return pd.DataFrame() 

# ... (생략) ...
