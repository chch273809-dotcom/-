import streamlit as st

# MBTI 추천 앱 (Streamlit single-file)
# 사용법: streamlit run streamlit_mbti_recommender.py
# Streamlit Cloud에 바로 올려서 동작합니다. 추가 라이브러리 불필요 (Streamlit만 필요).

st.set_page_config(page_title="MBTI 영화·책 추천 🌟", layout="centered")

st.title("MBTI별 영화·책 추천 🎬📚")
st.caption("대학 입시로 지친 너에게 — 작은 위로와 재미있는 추천을 전해요 😊")

mbti_list = [
    "ISTJ","ISFJ","INFJ","INTJ",
    "ISTP","ISFP","INFP","INTP",
    "ESTP","ESFP","ENFP","ENTP",
    "ESTJ","ESFJ","ENFJ","ENTJ"
]

# 각 MBTI별 추천 (영화 2개, 책 2권)
recommendations = {
    "ISTJ": {
        "movies": ["Bridge of Spies (2015)", "The King’s Speech (2010)"],
        "books": ["The Count of Monte Cristo - Alexandre Dumas", "Pride and Prejudice - Jane Austen"]
    },
    "ISFJ": {
        "movies": ["The Help (2011)", "Finding Nemo (2003)"],
        "books": ["Little Women - Louisa May Alcott", "The Book Thief - Markus Zusak"]
    },
    "INFJ": {
        "movies": ["Dead Poets Society (1989)", "Her (2013)"],
        "books": ["Man's Search for Meaning - Viktor E. Frankl", "The Alchemist - Paulo Coelho"]
    },
    "INTJ": {
        "movies": ["Inception (2010)", "The Social Network (2010)"],
        "books": ["Foundation - Isaac Asimov", "Dune - Frank Herbert"]
    },
    "ISTP": {
        "movies": ["Mad Max: Fury Road (2015)", "Drive (2011)"],
        "books": ["The Martian - Andy Weir", "Into Thin Air - Jon Krakauer"]
    },
    "ISFP": {
        "movies": ["Amélie (2001)", "La La Land (2016)"],
        "books": ["Eat, Pray, Love - Elizabeth Gilbert", "The Little Prince - Antoine de Saint-Exupéry"]
    },
    "INFP": {
        "movies": ["Amélie (2001)", "Big Fish (2003)"],
        "books": ["The Little Prince - Antoine de Saint-Exupéry", "The Perks of Being a Wallflower - Stephen Chbosky"]
    },
    "INTP": {
        "movies": ["A Beautiful Mind (2001)", "The Imitation Game (2014)"],
        "books": ["Gödel, Escher, Bach - Douglas Hofstadter", "Surely You're Joking, Mr. Feynman! - Richard Feynman"]
    },
    "ESTP": {
        "movies": ["Catch Me If You Can (2002)", "The Bourne Identity (2002)"],
        "books": ["Into the Wild - Jon Krakauer", "The Bourne Identity - Robert Ludlum"]
    },
    "ESFP": {
        "movies": ["Mamma Mia! (2008)", "La La Land (2016)"],
        "books": ["Crazy Rich Asians - Kevin Kwan", "The Great Gatsby - F. Scott Fitzgerald"]
    },
    "ENFP": {
        "movies": ["Almost Famous (2000)", "Good Will Hunting (1997)"],
        "books": ["The Alchemist - Paulo Coelho", "The Perks of Being a Wallflower - Stephen Chbosky"]
    },
    "ENTP": {
        "movies": ["The Social Network (2010)", "The Wolf of Wall Street (2013)"],
        "books": ["Freakonomics - Steven D. Levitt & Stephen J. Dubner", "Surely You're Joking, Mr. Feynman! - Richard Feynman"]
    },
    "ESTJ": {
        "movies": ["12 Angry Men (1957)", "Erin Brockovich (2000)"],
        "books": ["How to Win Friends and Influence People - Dale Carnegie", "The Checklist Manifesto - Atul Gawande"]
    },
    "ESFJ": {
        "movies": ["The Help (2011)", "Legally Blonde (2001)"],
        "books": ["To Kill a Mockingbird - Harper Lee", "Little Women - Louisa May Alcott"]
    },
    "ENFJ": {
        "movies": ["Dead Poets Society (1989)", "Freedom Writers (2007)"],
        "books": ["Man's Search for Meaning - Viktor E. Frankl", "The Kite Runner - Khaled Hosseini"]
    },
    "ENTJ": {
        "movies": ["The Social Network (2010)", "Wall Street (1987)"],
        "books": ["Good to Great - Jim Collins", "The Prince - Niccolò Machiavelli"]
    }
}

st.markdown("---")

col1, col2 = st.columns([1, 2])
with col1:
    chosen = st.selectbox("너의 MBTI를 골라줘 🧭", mbti_list)
    if st.button("추천 보기 ✨"):
        st.session_state['show'] = True

with col2:
    st.write("""
    #### 잠깐의 힐링 말 한마디 💌
    입시 준비로 매일 전투 중인 너, 정말 고생 많아. 작은 휴식도 성적을 올리는 한 방법이야 — 잠깐 쉬면서 아래 추천작으로 기분 전환해봐. 넌 충분히 잘 하고 있어. 🙌
    """)

if 'show' in st.session_state and st.session_state['show']:
    rec = recommendations.get(chosen, None)
    if rec:
        st.subheader(f"{chosen} 추천 목록 🎯")
        st.markdown("**영화 추천 🎬**")
        for i, m in enumerate(rec['movies'], 1):
            st.write(f"{i}. {m}")
        st.markdown("**책 추천 📚**")
        for i, b in enumerate(rec['books'], 1):
            st.write(f"{i}. {b}")

        st.markdown("---")
        st.info("더 보고 싶은 유형이 있으면 위에서 다른 MBTI를 골라서 다시 확인해봐요. 필요하면 추천 이유도 설명해줄게요! 💬")
    else:
        st.error("해당 MBTI에 대한 추천을 찾을 수 없습니다. 😢")

st.caption("만든이: 간단한 MBTI 추천 도구 — 추천은 대중적으로 알려진 작품 위주로 선정했습니다.")
