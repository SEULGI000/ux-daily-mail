# ===== 설정 파일 =====
# 여기서 당신의 정보를 입력하면 자동화 도구가 작동합니다!

import os

# ==================== 네이버 메일 설정 ====================
# 민감 정보(이메일/비밀번호)는 코드에 절대 적지 않고,
# 오직 환경변수(GitHub Secrets)에서만 읽는다. → 저장소를 공개해도 안전.
# 로컬에서 직접 돌릴 땐 실행 전에 환경변수를 설정해야 한다.
NAVER_EMAIL = os.environ.get("NAVER_EMAIL", "")
NAVER_APP_PASSWORD = os.environ.get("NAVER_APP_PASSWORD", "")
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL", "")

# ==================== 아티클 수집 설정 ====================
# UX/UI 관련 아티클 소스들 (RSS 피드)
# 국내 소스 위주
RSS_FEEDS = [
    # 국내 UX/UI 디자인 소스
    "https://brunch.co.kr/rss/collections/323",  # 브런치 - 디자인
    "https://brunch.co.kr/rss/collections/328",  # 브런치 - 기술
    "https://brunch.co.kr/rss/collections/361",  # 브런치 - UX
    "https://www.designnighter.com/feed",  # 디자인나이트

    # 국내 아티클 큐레이션 / 디자인 블로그 (추가)
    "https://yozm.wishket.com/magazine/feed/",  # 요즘IT - IT/디자인 아티클 (글 풍부)
    "https://story.pxd.co.kr/feed",             # pxd - UX 컨설팅펌 디자인 스토리
    "https://medium.com/feed/29cm",             # 29CM - 커머스/브랜드 디자인
    "https://medium.com/feed/daangn",           # 당근마켓 - 프로덕트/디자인
    # 참고: 서핏(Surfit)은 공개 RSS를 제공하지 않아 제외함
]

# 추천할 아티클 개수
NUM_ARTICLES = 5

# ==================== 아티클 선별 기준 설정 ====================
# 추천 아티클이 갖춰야 할 조건을 키워드로 표현합니다.
#  조건1) UX/UI 디자인에 가까울 것      → CORE_KEYWORDS (최소 1개 필수, 우선순위 순)
#  조건2) 신입에게 어렵지 않을 것       → BEGINNER 가점 / ADVANCED 감점
#  조건3) 사용자 심리·UX/UI 트렌드 관련 → TOPIC_KEYWORDS 가점

# [조건1] UX/UI 디자인 핵심 키워드 — 이 중 하나도 없으면 추천에서 제외 (우선순위 순)
CORE_KEYWORDS = [
    "UX",
    "UI",
    "사용자 경험",
    "사용성",
    "인터페이스",
    "디자인",
    "사용자",
    "화면",
    "프로덕트",
]

# [조건3] 사용자 심리 · UX/UI 트렌드 주제 — 포함되면 가점
TOPIC_KEYWORDS = [
    "심리",
    "행동",
    "인지",
    "멘탈 모델",
    "사용자 조사",
    "트렌드",
    "동향",
    "사례",
    "패턴",
    "접근성",
]

# [조건2-가점] 신입에게 친절한 입문/가이드성 글 — 포함되면 가점
BEGINNER_KEYWORDS = [
    "입문",
    "기초",
    "기본",
    "신입",
    "주니어",
    "가이드",
    "쉽게",
    "알아보기",
    "정리",
    "이해하기",
    "처음",
]

# [조건2-감점] 신입에게 어려운 고난도/기술 심화 글 — 포함되면 감점
ADVANCED_KEYWORDS = [
    "심화",
    "아키텍처",
    "엔지니어링",
    "알고리즘",
    "딥다이브",
    "논문",
    "백엔드",
    "서버",
    "쿠버네티스",
    "리팩터링",
    "최적화 전략",
]

# 추천에서 무조건 제외 (스팸/비아티클)
EXCLUDE_KEYWORDS = [
    "광고",
    "판매",
    "채용",
    "모집",
    "행사 안내",
    "이벤트 당첨",
]

# 최소 콘텐츠 길이 (글자 수)
MIN_CONTENT_LENGTH = 50

# ==================== 실행 시간 설정 ====================
# 매일 아침 몇 시에 실행할지 설정 (0-23)
SCHEDULE_HOUR = 8  # 8시에 실행
SCHEDULE_MINUTE = 0  # 0분
