import feedparser
from datetime import datetime, timedelta
import time

class Scraper:
    def __init__(self):
        pass

    def fetch_feeds(self, urls):
        all_news = []
        now = datetime.now()
        three_days_ago = now - timedelta(days=3)

        for url in urls:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                # 발행 시간 파싱
                published_struct = entry.get("published_parsed") or entry.get("updated_parsed")
                if published_struct:
                    dt = datetime.fromtimestamp(time.mktime(published_struct))
                    if dt >= three_days_ago:
                        if len(all_news) < 10:
                            all_news.append({
                                "title": entry.title,
                                "link": entry.link,
                                "summary": entry.get("summary", ""),
                                "published": dt.strftime("%Y-%m-%d %H:%M:%S")
                            })
                        else:
                            break # 특정 피드에서 10개를 채웠으면 해당 피드 순회 종료
            if len(all_news) >= 10:
                break # 전체 URL 중 10개를 채웠으면 전체 수집 중단
        return all_news
