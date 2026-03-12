import json
import os
import requests
import base64
import streamlit as st

class FileManager:
    def __init__(self, repo_path="news_data.json", feeds_path="feeds.json"):
        self.data_dir = "data"
        self.repo_path = os.path.join(self.data_dir, repo_path)
        self.feeds_path = os.path.join(self.data_dir, feeds_path)
        self.github_token = st.secrets.get("GITHUB_TOKEN")
        self.github_repo = st.secrets.get("GITHUB_REPO")  # 예: "username/repo"

    def load_json(self, file_path):
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {} if "news_data" in file_path else []

    def save_json(self, file_path, data):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # GitHub Sync (토큰과 리포지토리 정보가 있을 때만 실행)
        if self.github_token and self.github_repo:
            self._sync_to_github(file_path)

    def _sync_to_github(self, file_path):
        rel_path = os.path.relpath(file_path, os.getcwd()).replace("\\", "/")
        url = f"https://api.github.com/repos/{self.github_repo}/contents/{rel_path}"
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }

        # 파일 존재 확인 및 SHA 가져오기
        response = requests.get(url, headers=headers)
        sha = None
        if response.status_code == 200:
            sha = response.json().get("sha")

        with open(file_path, "rb") as f:
            content = base64.b64encode(f.read()).decode("utf-8")

        payload = {
            "message": f"Update {rel_path} via Newsroom App",
            "content": content,
            "branch": "main"
        }
        if sha:
            payload["sha"] = sha

        res = requests.put(url, headers=headers, json=payload)
        if res.status_code in [200, 201]:
            st.success(f"GitHub 동기화 완료: {rel_path}")
        else:
            st.error(f"GitHub 동기화 실패: {res.text}")

    def get_news_data(self):
        return self.load_json(self.repo_path)

    def save_news_data(self, data):
        self.save_json(self.repo_path, data)

    def get_feeds(self):
        return self.load_json(self.feeds_path)

    def save_feeds(self, feeds):
        self.save_json(self.feeds_path, feeds)
