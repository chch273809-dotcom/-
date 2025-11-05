import streamlit as st
st.title('나의 첫 웹 서비스 만들기!')
a=st.text_input('나마에오카이테구다사이')
if st.button('인사말 생성'):
  st.write(a+'님 안녕하세요')
