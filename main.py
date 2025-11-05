import streamlit as st
st.title('나의 첫 웹 서비스 만들기!')
a=st.text_input('나마에오카이테구다사이')
b=st.selectbox('스키나타베모노오골라구다사이',['오페라케이크','된장찌개','까르보나라','도토리국수','내가그린기린그림','쌉뚱땡이표조개구이','이차현표레몬타르트','미역국'])
if st.button('인사말 생성'):
  st.info(a+'님 하지메마시테')
  st.warning(b+'를 좋아하시는구나 저도 좋아해요')
  st.error('반갑습니다!')
  st.balloons()
