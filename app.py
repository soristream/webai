import streamlit as st
import pandas as pd
from datetime import datetime
from utils.file_manager import FileManager
from utils.scraper import Scraper
from utils.ai_analyst import AIAnalyst

# 페이지 설정
st.set_page_config(page_title="AI IT 뉴스룸", layout="wide")

# 모듈 초기화
fm = FileManager()
scraper = Scraper()
try:
    analyst = AIAnalyst()
except Exception as e:
    st.error(f"AI 모델 초기화 실패: {e}")
    analyst = None

# 세션 상태 초기화
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

# 사이드바 메뉴
st.sidebar.title("🚀 IT 뉴스룸")
menu = st.sidebar.radio("메뉴", ["최신 리포트", "과거 리포트", "관리자 대시보드"])

# 관리자 로그인 체크
def admin_login():
    if not st.session_state.admin_logged_in:
        with st.sidebar.expander("🔑 관리자 로그인"):
            pwd = st.text_input("비밀번호", type="password")
            if st.button("로그인"):
                if pwd == st.secrets.get("ADMIN_PASSWORD"):
                    st.session_state.admin_logged_in = True
                    st.rerun()
                else:
                    st.error("관리자 비밀번호가 틀렸습니다.")
    else:
        if st.sidebar.button("로그아웃"):
            st.session_state.admin_logged_in = False
            st.rerun()

admin_login()

# 데이터 로드
news_data = fm.get_news_data()
feeds = fm.get_feeds()

if menu == "최신 리포트":
    st.header("📅 최신 IT 토픽 리포트")
    if news_data:
        latest_date = list(news_data.keys())[0]
        st.subheader(f"기준일: {latest_date}")
        
        for item in news_data[latest_date]:
            with st.expander(f"📌 {item['topic']}", expanded=True):
                st.write(item['summary'])
                st.markdown("**참고 뉴스:**")
                for source in item['sources']:
                    st.markdown(f"- [{source['title']}]({source['url']})")
    else:
        st.info("아직 분석된 데이터가 없습니다. 관리자 대시보드에서 분석을 실행해 주세요.")

elif menu == "과거 리포트":
    st.header("📂 과거 기록 조회")
    if news_data:
        dates = list(news_data.keys())
        selected_date = st.select_slider("날짜 선택", options=dates)
        
        if selected_date:
            st.subheader(f"리포트 날짜: {selected_date}")
            for item in news_data[selected_date]:
                with st.expander(f"📌 {item['topic']}"):
                    st.write(item['summary'])
                    st.markdown("**참고 뉴스:**")
                    for source in item['sources']:
                        st.markdown(f"- [{source['title']}]({source['url']})")
    else:
        st.info("데이터가 없습니다.")

elif menu == "관리자 대시보드":
    st.header("🛠 관리자 대시보드")
    if not st.session_state.admin_logged_in:
        st.warning("관리자 로그인이 필요합니다.")
    else:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("🔗 RSS 피드 관리")
            new_feed = st.text_input("새 RSS URL 추가")
            if st.button("추가"):
                if new_feed and new_feed not in feeds:
                    feeds.append(new_feed)
                    fm.save_feeds(feeds)
                    st.success("추가되었습니다.")
                    st.rerun()
            
            st.write("등록된 피드 목록:")
            for i, f in enumerate(feeds):
                col_f1, col_f2 = st.columns([4, 1])
                col_f1.text(f)
                if col_f2.button("삭제", key=f"del_{i}"):
                    feeds.pop(i)
                    fm.save_feeds(feeds)
                    st.rerun()

        with col2:
            st.subheader("🤖 수집 및 분석 실행")
            if st.button("지금 분석 시작", type="primary"):
                if not feeds:
                    st.error("등록된 RSS 피드가 없습니다.")
                elif not analyst:
                    st.error("AI 모델이 설정되지 않았습니다.")
                else:
                    with st.spinner("뉴스를 수집하고 있습니다..."):
                        raw_news = scraper.fetch_feeds(feeds)
                        st.write(f"{len(raw_news)}개의 뉴스를 찾았습니다.")
                    
                    if raw_news:
                        with st.spinner("Gemini 3 Flash가 분석 중입니다..."):
                            analysis_result = analyst.analyze_news(raw_news)
                            
                            if analysis_result:
                                today = datetime.now().strftime("%Y-%m-%d")
                                # 기존 데이터의 맨 앞에 최신 결과 추가
                                new_entry = {today: analysis_result}
                                updated_data = {**new_entry, **news_data}
                                fm.save_news_data(updated_data)
                                st.success(f"{today} 리포트 생성 완료!")
                                st.rerun()
                    else:
                        st.warning("최근 3일 이내의 뉴스가 없습니다.")
