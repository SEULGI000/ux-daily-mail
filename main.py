# ===== 자동화 메인 스크립트 (추천 링크 메일 버전) =====
# UX/UI 디자인 아티클 3개를 선별해 "제목: 링크" 형식으로 메일 발송
# (PDF/첨부 없음, 본문에 추천 링크만)

import sys
# Windows 콘솔(cp949)에서 이모지/한글 출력 시 깨지거나 죽는 것을 방지
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import smtplib
import feedparser
import datetime
import re
import html
from email.mime.text import MIMEText
from email.utils import formatdate
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

# 링크에서 제거할 추적용 쿼리 파라미터(이 외에 utm_* 전부 제거)
TRACKING_PARAMS = {"source", "ref", "fbclid", "gi", "gclid", "igshid", "spm"}

# config.py에서 설정값 불러오기
from config import (
    NAVER_EMAIL, NAVER_APP_PASSWORD, RECIPIENT_EMAIL,
    RSS_FEEDS, NUM_ARTICLES,
    CORE_KEYWORDS, TOPIC_KEYWORDS, BEGINNER_KEYWORDS,
    ADVANCED_KEYWORDS, EXCLUDE_KEYWORDS, MIN_CONTENT_LENGTH,
)


# ==================== 유틸리티 ====================
def clean_text(text):
    """RSS가 준 HTML 기호(&quot; 등)를 실제 문자로 되돌리고 공백 정리"""
    if not text:
        return ""
    text = html.unescape(str(text))
    text = re.sub(r"<[^>]+>", "", text)      # 혹시 섞인 HTML 태그 제거
    text = re.sub(r"\s+", " ", text).strip()
    return text


def clean_link(url):
    """링크에서 추적용 쿼리 파라미터(?source=, utm_*, ref 등)를 제거해 깔끔하게."""
    if not url:
        return url
    try:
        parts = urlsplit(url)
        kept = [
            (k, v) for k, v in parse_qsl(parts.query)
            if k.lower() not in TRACKING_PARAMS and not k.lower().startswith("utm_")
        ]
        return urlunsplit((parts.scheme, parts.netloc, parts.path,
                           urlencode(kept), ""))
    except Exception:
        return url


# ==================== 1단계: 아티클 수집 ====================
def collect_articles():
    """RSS 피드에서 아티클을 모은다."""
    print("[1단계] 아티클 수집 중...")
    all_articles = []
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            print(f"  📡 {feed_url[:50]}... 수집")
            for entry in feed.entries[:20]:
                all_articles.append({
                    "title": clean_text(entry.get("title", "제목 없음")),
                    "link": clean_link(entry.get("link", "")),
                    "summary": clean_text(entry.get("summary", ""))[:500],
                    "published": entry.get("published", ""),
                })
        except Exception:
            print(f"  ⚠️ 피드 읽기 실패: {feed_url}")
    print(f"  → 총 {len(all_articles)}개 수집")
    return all_articles


# ==================== 2단계: 조건에 맞는 글 선별 ====================
def score_article(article):
    """선별 기준에 따라 점수를 매긴다. 조건에 안 맞으면 None.

    조건1) UX/UI 디자인에 가까울 것      → CORE 키워드 최소 1개 (없으면 제외)
    조건2) 신입에게 어렵지 않을 것       → BEGINNER 가점 / ADVANCED 감점
    조건3) 사용자 심리·UX/UI 트렌드 관련 → TOPIC 가점
    """
    text = (article["title"] + " " + article["summary"]).lower()

    # 스팸/비아티클 제외
    for kw in EXCLUDE_KEYWORDS:
        if kw.lower() in text:
            return None

    # [조건1] UX/UI 디자인 핵심 키워드가 하나도 없으면 추천 대상 아님
    core_hits = 0
    score = 0
    for idx, kw in enumerate(CORE_KEYWORDS):
        if kw.lower() in text:
            core_hits += 1
            score += (len(CORE_KEYWORDS) - idx) * 8   # 우선순위 가중치
    if core_hits == 0:
        return None

    # 콘텐츠 길이 (너무 짧은 글 감점)
    if len(article["summary"]) < MIN_CONTENT_LENGTH:
        score -= 20

    # [조건3] 사용자 심리 · 트렌드 주제 가점
    for kw in TOPIC_KEYWORDS:
        if kw.lower() in text:
            score += 25

    # [조건2] 신입 친화 가점 / 고난도 감점
    for kw in BEGINNER_KEYWORDS:
        if kw.lower() in text:
            score += 15
    for kw in ADVANCED_KEYWORDS:
        if kw.lower() in text:
            score -= 30

    return score


def select_articles(all_articles):
    """점수가 높은 상위 N개를 추천으로 선별한다. (중복 제목 제거)"""
    print("\n[2단계] 조건에 맞는 추천 아티클 선별 중...")
    scored = []
    seen_titles = set()
    for art in all_articles:
        if not art["link"] or not art["title"]:
            continue
        key = art["title"][:40]
        if key in seen_titles:
            continue
        s = score_article(art)
        if s is not None and s > 0:
            seen_titles.add(key)
            scored.append((s, art))

    scored.sort(key=lambda x: x[0], reverse=True)
    picked = [art for _, art in scored[:NUM_ARTICLES]]

    print(f"✅ 추천 {len(picked)}개 선별 완료!")
    for i, (s, art) in enumerate(scored[:NUM_ARTICLES], 1):
        print(f"   [{i}] ({s}점) {art['title'][:45]}")
    return picked


# ==================== 3단계: 메일 발송 (제목: 링크) ====================
def build_email_body(articles):
    """추천 아티클을 '제목: 링크' 형식의 메일 본문(텍스트)으로 만든다."""
    today = datetime.datetime.now().strftime("%Y년 %m월 %d일")
    lines = [
        f"안녕하세요! 오늘({today})의 UX/UI 추천 아티클 {len(articles)}개입니다.",
        "",
    ]
    for i, art in enumerate(articles, 1):
        lines.append(f"{i}. {art['title']}: {art['link']}")
        lines.append("")
    lines.append("좋은 하루 되세요! 😊")
    return "\n".join(lines)


def send_email(articles):
    """네이버 메일로 추천 링크를 발송한다 (첨부 없음)."""
    print("\n[3단계] 추천 링크 메일 발송 중...")
    body = build_email_body(articles)
    print("\n----- 메일 본문 미리보기 -----")
    print(body)
    print("------------------------------\n")

    try:
        server = smtplib.SMTP("smtp.naver.com", 587)
        server.starttls()
        server.login(NAVER_EMAIL, NAVER_APP_PASSWORD)

        msg = MIMEText(body, "plain", "utf-8")
        msg["From"] = NAVER_EMAIL
        msg["To"] = RECIPIENT_EMAIL
        msg["Date"] = formatdate(localtime=True)
        msg["Subject"] = (
            f"[UX/UI 추천] 오늘의 디자인 아티클 - "
            f"{datetime.datetime.now().strftime('%Y년 %m월 %d일')}"
        )

        server.send_message(msg)
        server.quit()
        print("✅ 메일 발송 완료!")
        return True
    except Exception as e:
        print(f"❌ 메일 발송 실패: {e}")
        return False


# ==================== 메인 ====================
def main():
    print("\n" + "=" * 50)
    print("🚀 UX/UI 추천 아티클 메일 자동화 시작!")
    print("=" * 50 + "\n")

    try:
        all_articles = collect_articles()
        picked = select_articles(all_articles)

        if not picked:
            print("⚠️ 조건에 맞는 추천 아티클이 없습니다!")
            return

        send_email(picked)

        print("\n" + "=" * 50)
        print("✅ 모든 작업 완료!")
        print("=" * 50 + "\n")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
