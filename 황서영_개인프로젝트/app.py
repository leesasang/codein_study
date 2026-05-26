import streamlit as st
import pandas as pd
import os
import datetime

# 1. 페이지 설정
st.set_page_config(page_title="Today I...", layout="wide")

# 2. 미니멀리즘 블랙앤화이트 CSS
st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-size: 14px;
        font-family: 'Inter', sans-serif;
    }
    .main-title {
        font-size: 32px;
        font-weight: 700;       
        letter-spacing: -0.5px;
        margin-bottom: 2px;
    }
    div[data-testid="stSliderTickBar"] {
        display: none !important;
    }
    div[data-testid="stSlider"] [data-testid="styled-secondary-text"] {
        display: none !important;
    }
    div[data-baseweb="slider"] > div > div {
        background: #e0e0e0 !important;
    }
    div[role="slider"] {
        background-color: white !important;
        border: 1px solid #000 !important;
    }
    div[data-testid="stHorizontalBlock"] > div {
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .stButton > button {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        padding: 8px 0px !important;
        line-height: 1 !important;
    }
    </style>
    """, unsafe_allow_html=True)

side_space_left, center_content, side_space_right = st.columns([1, 10, 1])

with center_content:
    st.markdown('<div class="main-title">Today I...</div>', unsafe_allow_html=True)
    st.write("---")

    FILE_PATH = "diary_data.csv"

    left_col, right_col = st.columns(2)

    with left_col:
        st.write("### ✍️ Record")
        
        with st.container(border=True):
            date = st.date_input("Date", datetime.date.today())
            st.write("How Are You Feeling?")
            
            emo_cols = st.columns(6)
            emojis = ["☀️", "🙂", "☁️", "🥱", "🌑", "🌪️"]
            
            if "selected_mood" not in st.session_state:
                st.session_state.selected_mood = "☀️"
                
            for i, emo in enumerate(emojis):
                with emo_cols[i]:
                    if st.button(emo, key=f"emo_{i}", use_container_width=True):
                        st.session_state.selected_mood = emo
            
            st.write(f"Selected Mood: **{st.session_state.selected_mood}**")
            st.write("")
            
            st.write("Sleep Duration")
            sleep_hours = st.slider(
                "Sleep Select",
                min_value=0.0,
                max_value=12.0,
                value=7.0,
                step=0.5,
                label_visibility="collapsed"
            )
            
            if sleep_hours >= 12.0:
                display_sleep = "12h+"
            else:
                display_sleep = f"{sleep_hours}h"
                
            st.write(f"Selected Sleep: **{display_sleep}**")
            st.write("")
            
            st.write("What Did You Eat?")
            meal = st.text_input("Meal Input", placeholder="e.g. salad and coffee", label_visibility="collapsed")
            st.write("")

            st.write("How Was Today?")
            note = st.text_input("Note Input", placeholder="e.g.a peaceful day.", label_visibility="collapsed")
            
            st.write("")
            save_btn = st.button("Save Record", use_container_width=True)

    with right_col:
        st.write("### 📊 Overview")
        
        with st.container(border=True):
            st.write(f"**{date.strftime('%B %d, %Y')}**")
            current_mood = st.session_state.selected_mood
            
            if save_btn:
                new_data = {
                    "Date": [date.strftime("%Y-%m-%d")],
                    "Mood": [current_mood],
                    "Sleep": [display_sleep],
                    "Meal": [meal],
                    "Note": [note]
                }
                new_df = pd.DataFrame(new_data)
                
                # 안전한 저장 장치: 파일이 없거나 구버전이라 컬럼 개수가 안 맞으면 새로 생성
                if not os.path.exists(FILE_PATH):
                    new_df.to_csv(FILE_PATH, index=False, encoding="utf-8-sig")
                else:
                    try:
                        old_df = pd.read_csv(FILE_PATH)
                        # 컬럼 수가 안 맞으면(구버전) 강제로 리셋 후 저장하도록 방어 코드 추가
                        if len(old_df.columns) != len(new_df.columns):
                            new_df.to_csv(FILE_PATH, index=False, encoding="utf-8-sig")
                        else:
                            new_df.to_csv(FILE_PATH, mode='a', header=False, index=False, encoding="utf-8-sig")
                    except:
                        new_df.to_csv(FILE_PATH, index=False, encoding="utf-8-sig")
                    
                st.toast("Saved Successfully", icon="✅")
                
            st.write(f"Mood : {current_mood}")
            st.write(f"Sleep : {display_sleep}")
            st.write(f"Meal : {meal if meal else '...'}")
            st.write(f"Note : {note if note else '...'}")
            
            st.write("---")
            st.write("**Mood & Sleep Summary**")
            
            # 구버전 파일 검사 예외처리 로직으로 에러 원천 차단
            if os.path.exists(FILE_PATH):
                try:
                    df_summary = pd.read_csv(FILE_PATH)
                    # 파일에 진짜 해당 컬럼들이 다 들어있는지 체크 후 노출
                    if all(col in df_summary.columns for col in ["Date", "Mood", "Sleep"]):
                        summary_view = df_summary[["Date", "Mood", "Sleep"]].tail(5)
                        st.dataframe(summary_view, use_container_width=True, hide_index=True)
                    else:
                        st.warning("구버전 데이터 데이터 구조를 갱신 중입니다. 다시 한 번 저장해 주세요!")
                except Exception as e:
                    st.info("No records found yet.")
            else:
                st.info("No records found yet. Save a record first!")

    if os.path.exists(FILE_PATH):
        st.write("")
        with st.expander("Past Logs (All Details)", expanded=False):
            try:
                df = pd.read_csv(FILE_PATH)
                st.dataframe(df.tail(5), use_container_width=True, hide_index=True)
            except:
                st.write("기록을 불러오는 중 오류가 발생했습니다.")