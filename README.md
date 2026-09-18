# 사부작(SABUZAK) | K-전통스낵 해외 박람회 운영 자동화 대시보드

김부각·약과 등 K-전통스낵 수출기업 '사부작' 의 해외 박람회 운영 업무를 자동화하는 내부용 대시보드입니다. 해외 시장 조사, 박람회 일정 수집, 부스 컨셉 기획, 기안서 작성까지 하나의 화면에서 처리합니다.

## 제품군
사부작이 수출하는 5종 K-전통스낵입니다. 국가별 세부 HS코드·관세율은 박람회 상세 페이지의 HS코드 탭에서 확인합니다.

| 품목 | HS코드 |
|---|---|
| 김부각 | 1905.90 |
| 유과 | 1905.90 |
| 약과 | 1905.90 |
| 누룽지칩 | 1904.90 |
| 고구마스틱 | 2005.99 |

## 화면 흐름
```
로그인 → 대시보드(세계 지도) → [대륙 핀 클릭] → 대륙별 박람회 목록 → 박람회 상세
        → 부스 컨셉 기획 → 기안서 작성
        └ 작성 중인 박람회 (진행 상황 관리)
```

① **대시보드** — 세계 지도에서 대륙 핀(박람회 개수 표시)을 클릭하면 해당 대륙의 박람회 목록 페이지로 이동

② **대륙별 박람회 목록** — 선택한 대륙의 박람회를 목록으로 표시, 클릭 시 상세로 이동

③ **박람회 상세** — 4개 탭으로 구성
- 박람회 개요 — 개최지·장소·규모·카테고리·실시간 환율, 공식 소개
- 시장·트렌드 — YoY 성장률 등 시장 인사이트
- HS코드 — 품목별 HS코드·관세율·필요 인증(HACCP 등)
- 수출 주의사항 — 필수/정보/주의 등급별 규제 카드

④ **부스 컨셉 기획** — 상세 데이터를 기반으로 AI가 부스 테마·슬로건, 핵심 셀링포인트, 이벤트 기획안 자동 생성 → 내용 수정 및 초안 저장

⑤ **기안서 작성** — 컨셉을 바탕으로 참가 기안서 자동 생성 → 내용 수정 및 초안 저장, PDF·Word 출력

⑥ **작성 중인 박람회** — 컨셉/기안서 진행 상태 관리 및 이어서 작성

## 로그인
사부작 내부 시스템으로, 임직원 계정으로만 접근합니다 (아이디/비밀번호 기반 세션 로그인).

## 기술 스택
- Backend — Python + Flask, Flask-Login(로그인), Flask-SQLAlchemy(DB)
- 데이터 처리 — pandas
- Frontend — Jinja2 템플릿 + HTML/CSS + 바닐라 JS (탭 전환, AI 생성 버튼, 초안 저장 등 AJAX)
- Database — SQLite (`instance/sabuzak.db`)
- 외부 연동 — 환율 API(실시간 환율), OpenAI API(부스 컨셉·기안서 생성, 박람회 자동 분류)

## 설치
한 번에 설치하려면:
```bash
./setup.sh
```
가상환경(.venv) 생성 → `requirements.txt` 설치 → `.env` 생성(`.env.example` 복사) → DB 테이블 초기화까지 자동으로 처리합니다. 완료 후 `.env`에 `SECRET_KEY`, `OPENAI_API_KEY`를 채워주세요.

수동으로 하려면:
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # 값 채우기
export FLASK_APP=run.py && flask init-db
```

## 실행
```bash
source .venv/bin/activate
python run.py          # 기본 포트 5000
```

## 데이터 파이프라인 (앱과 분리된 배치 스크립트)
웹 요청-응답과 무관한 주기적 배치 작업은 `scripts/`에 따로 둡니다. 실행 순서는 아래와 같습니다.

```bash
# 1. tradefairdates.com에서 박람회 크롤링 → raw_exhibitions 테이블에 증분 동기화
python scripts/crawl/sync_to_db.py --db instance/sabuzak.db --details

# 2. 신규/변경된 박람회만 OpenAI로 분류 (대륙·제품적합도·규모·유형)
python scripts/classify/classify_with_openai.py --db instance/sabuzak.db
```

- `scripts/crawl/tradefairdates_scraper.py` — 단일 카테고리 페이지 크롤러 (다른 스크립트가 모듈로 불러다 씀)
- `scripts/crawl/sync_to_db.py` — 7개 카테고리 통합 크롤링 + `raw_exhibitions` 증분 동기화 (신규/변경 감지, 목록에서 사라진 항목은 삭제 대신 비활성 처리)
- `scripts/crawl/multi_crawl_gui.py` — 위 크롤링을 수동으로 실행할 때 쓰는 내부용 GUI(tkinter) 도구, CSV로도 저장 가능
- `scripts/crawl/kotra_support_crawler.py` — KOTRA 정부 지원사업 공고 크롤러
- `scripts/classify/classify_with_openai.py` — (DB 기반) 미분류/재분류 필요 박람회만 OpenAI로 분류해 `raw_exhibitions`에 저장. 분류 기준: 대륙 / 제품 적합도(김부각·유과·약과·누룽지칩·고구마스틱) / 규모 / 거래유형
- `scripts/classify/preprocess.py` — (CSV 기반) `원본.csv` → `clean.csv`. 분류 기준: 대륙 / `food_yn`(식품류 전시회 여부) / 규모(대·중·소·미상) / 거래고객 유형(B2B·B2C) / 키워드 5개(표준 키워드 풀에서 선택). 스크립트와 같은 폴더에 `원본.csv`를 두고 실행

`app/models.py`의 `Exhibition` 모델은 `classify_with_openai.py`가 채우는 `raw_exhibitions` 테이블을 그대로 매핑해서 읽습니다. `preprocess.py`는 CSV를 입출력으로 쓰는 별도 분류 파이프라인이라, DB에 반영하려면 `clean.csv`를 다시 `raw_exhibitions`에 적재하는 과정이 필요합니다.

## 코드 구조
```
sabuzak/
├── app/                         # Flask 웹앱
│   ├── __init__.py              # create_app (앱 팩토리)
│   ├── extensions.py            # db, login_manager
│   ├── models.py                # Exhibition(=raw_exhibitions), ConceptDraft, ProposalDraft, User
│   ├── routes/
│   │   ├── auth.py              # 로그인/로그아웃
│   │   ├── dashboard.py         # 대시보드(세계 지도) · 대륙별 박람회 목록
│   │   ├── exhibition.py        # 박람회 상세 (개요·시장·HS코드·주의사항 + 환율)
│   │   ├── concept.py           # 부스 컨셉 생성 · 수정 · 초안 저장
│   │   ├── proposal.py          # 기안서 생성 · 수정 · 초안 저장 · PDF/Word 출력
│   │   └── drafts.py            # 작성 중인 박람회 목록
│   ├── services/
│   │   ├── data.py              # raw_exhibitions 조회/가공 (pandas)
│   │   ├── exchange.py          # 환율 API 호출 + 캐싱
│   │   ├── llm.py               # OpenAI 컨셉·기안서 생성
│   │   └── export.py            # PDF(weasyprint)/Word(python-docx) 출력
│   ├── templates/
│   │   ├── base.html            # 공통 레이아웃 (사이드바)
│   │   ├── login.html
│   │   ├── dashboard.html       # 세계 지도 (대륙 핀 클릭)
│   │   ├── continent.html       # 대륙별 박람회 목록
│   │   ├── exhibition.html      # 상세 4탭
│   │   ├── concept.html         # 부스 컨셉 기획 (AI 생성·수정·저장)
│   │   ├── proposal.html        # 기안서 작성 (AI 생성·수정·저장·출력)
│   │   └── drafts.html          # 작성 중인 박람회
│   └── static/
│       ├── css/base.css
│       ├── js/                  # map.js(지도 핀), tabs.js(탭 전환), concept.js, proposal.js
│       └── img/
├── scripts/                     # 데이터 파이프라인 (웹앱과 분리된 배치 스크립트)
│   ├── crawl/
│   │   ├── tradefairdates_scraper.py
│   │   ├── sync_to_db.py
│   │   ├── multi_crawl_gui.py
│   │   └── kotra_support_crawler.py
│   └── classify/
│       └── classify_with_openai.py
├── legacy/
│   └── streamlit_prototype.py   # 초기 Streamlit 목업 (참고용, 배포 대상 아님)
├── data/                        # HS코드·규제 등 정적 참조 데이터 (CSV 등, 준비 중)
├── instance/
│   └── sabuzak.db                # SQLite (git 미포함)
├── config.py
├── requirements.txt
├── run.py
├── .env.example
└── README.md
```

## 구현 현황
- [x] 데이터 파이프라인: tradefairdates.com 크롤링 → DB 동기화 → OpenAI 분류
- [x] Flask 앱 스켈레톤: 로그인, 대시보드, 상세, 컨셉/기안서 라우트·템플릿
- [ ] 지도 핀 실제 좌표 배치 (현재 `map.js`는 최소 동작만 구현)
- [ ] 시장·트렌드 / HS코드 / 수출 주의사항 탭 데이터 연동 (`services/data.py`의 TODO)
- [ ] 실시간 환율 API 실제 연동 (`services/exchange.py`)
- [ ] AI 컨셉·기안서 생성 결과를 구조화된 필드로 파싱 (`services/llm.py`)
- [ ] 로그인 비밀번호 해시 검증, 계정 관리

## 데이터 소스
- 박람회 일정 — TradeFairDates
- 정부 지원금 — KATI(aT 농식품 수출정보), KOTRA 해외전시포털(gep.or.kr)
- 식품 규제 — 공공데이터포털(식품안전정보원 수출식품 부적합 사례)
