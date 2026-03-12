Project Spec: AI-Powered IT Newsroom (Antigravity & Streamlit)
1. 프로젝트 개요
목적: 국내 IT 뉴스 RSS를 수집하고 Gemini 1.5 Flash API로 분석하여 날짜별 토픽 리포트를 제공하는 개인용 뉴스룸 서비스.

핵심 기술 스택:

Language: Python 3.10+

Framework: Streamlit

AI Model: Google Gemini 3 Flash

Storage: Local JSON files (GitHub Repository sync)

Deployment: Streamlit Cloud

2. 데이터 아키텍처 (No-DB, JSON 기반)
모든 데이터는 data/ 디렉토리 내 JSON 파일로 관리합니다.

feeds.json: 사용자가 등록한 RSS URL 리스트 (["url1", "url2", ...])

news_data.json: 날짜별 분석 결과 (최신 날짜가 상단에 오도록 관리)

JSON
{
  "2026-03-11": [
    {
      "topic": "토픽 제목",
      "summary": "AI 요약 내용",
      "sources": [{"title": "뉴스제목", "url": "링크"}]
    }
  ]
}
3. 상세 기능 요구사항
A. 메인 화면 (User Interface)
최신 리포트 우선 출력: 접속 시 가장 최신 날짜의 분석 리포트를 메인에 노출.

날짜 네비게이션: st.select_slider 또는 사이드바 메뉴를 통해 과거 날짜의 리포트 조회 가능.

토픽별 카드: 각 뉴스 토픽은 st.expander 또는 카드 형태로 구성하며, 요약문과 원문 링크(Sources) 포함.

B. 관리자 대시보드 (Admin Dashboard)
접근 제어: 비밀번호 입력 후 진입 (st.secrets 활용).

RSS 관리: RSS 피드 URL 추가 및 삭제 기능.

수집 및 분석 실행:

클릭 시 등록된 모든 RSS에서 최근 3일치 게시글 수집.

수집된 텍스트를 Gemini 3 Flash에 전달.

Gemini가 뉴스들을 주제별(Topic)로 그룹화하고 요약하도록 프롬프트 설계.

결과를 news_data.json에 날짜별로 저장.

통계: 간단한 접속 로그 또는 수집된 뉴스 개수 시각화.

C. 데이터 영구 저장 (GitHub Sync)
Streamlit Cloud의 휘발성 파일 시스템 문제를 해결하기 위해, 데이터 업데이트 시 GitHub API를 사용하여 JSON 파일을 리포지토리에 자동 커밋/푸시하는 로직 포함.

4. Antigravity 작업 지침 (Step-by-Step)
Step 1: 환경 구성
requirements.txt 생성: streamlit, google-generativeai, feedparser, pandas, requests.

.streamlit/secrets.toml 구조 설계: GENAI_API_KEY, ADMIN_PASSWORD, GITHUB_TOKEN.

Step 2: 핵심 모듈 개발
Scraper: feedparser를 이용해 발행 시간을 체크하고 최근 3일 데이터만 필터링하는 로직.

AI Analyst: Gemini 3 Flash 전용 프롬프트 최적화 (JSON 출력 유도).

File Manager: JSON 읽기/쓰기 및 GitHub API 연동 함수.

Step 3: Streamlit UI 구현
app.py 작성: 사이드바 메뉴 구성 및 날짜별 데이터 렌더링 로직.

5. Gemini 분석 프롬프트 가이드
"당신은 IT 전문 기자입니다. 제공된 뉴스 목록에서 공통된 주제를 찾아 그룹화하고, 각 그룹의 핵심 내용을 전문가 수준으로 요약하세요. 결과는 반드시 날짜, 토픽명, 요약, 소스 링크가 포함된 구조화된 데이터여야 합니다."