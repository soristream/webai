import google.generativeai as genai
import streamlit as st
import json
import time
from google.api_core import exceptions

class AIAnalyst:
    def __init__(self):
        api_key = st.secrets.get("GENAI_API_KEY")
        if not api_key:
            raise ValueError("GENAI_API_KEY가 secrets.toml에 설정되어 있지 않습니다.")
        genai.configure(api_key=api_key)
        # Gemini 2.0 Flash Lite 모델 사용 (무료 티어 할당량 문제 완화 및 실제 지원 모델 채택)
        self.model = genai.GenerativeModel('gemini-2.0-flash-lite') 

    def analyze_news(self, news_list):
        if not news_list:
            return []

        # 뉴스 리스트를 텍스트로 변환
        news_text = "\n".join([f"- 제목: {n['title']}\n  링크: {n['link']}\n  요약: {n['summary'][:200]}" for n in news_list])

        prompt = f"""
당신은 IT 전문 기자입니다. 다음 뉴스 목록에서 공통된 주제를 찾아 그룹화하고, 각 그룹의 핵심 내용을 전문가 수준으로 요약하세요.
결과는 반드시 아래 JSON 형식으로만 응답하세요. 다른 설명은 포함하지 마세요.

JSON 형식:
[
  {{
    "topic": "토픽 제목",
    "summary": "AI 요약 내용 (3~4문장 정도)",
    "sources": [
      {{ "title": "뉴스제목", "url": "링크" }}
    ]
  }}
]

뉴스 목록:
{news_text}
"""
        max_retries = 3
        retry_delay = 20
        response = None
        
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                break
            except exceptions.ResourceExhausted as e:
                if attempt < max_retries - 1:
                    st.warning(f"API 할당량 초과. {retry_delay}초 후 재시도합니다... (시도 {attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                else:
                    st.error("API 할당량 초과로 분석을 완료하지 못했습니다. 잠시 후 다시 시도해주세요.")
                    return []
            except Exception as e:
                st.error(f"API 호출 중 오류 발생: {e}")
                return []
                
        if not response:
            return []
        
        try:
            # JSON만 추출 (```json ... ``` 형태 대응)
            content = response.text.strip()
            if content.startswith("```json"):
                content = content[7:-3].strip()
            elif content.startswith("```"):
                content = content[3:-3].strip()
            
            return json.loads(content)
        except Exception as e:
            st.error(f"AI 분석 결과 파싱 실패: {e}")
            return []
