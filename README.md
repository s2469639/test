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
#    (예전 스키마의 DB라면 첫 실행 때 데이터를 보존하며 자동으로 새 스키마로 마이그레이션됨)
python scripts/crawl/sync_to_db.py --db instance/sabuzak.db --details

# 2. OpenAI로 분류 (대륙 / food_yn / 규모 / 키워드) → 같은 DB에 바로 저장
#    아직 분류 안 됐거나, 크롤링으로 내용이 갱신된 것만 골라서 처리 (재분류 비용 절감)
python scripts/classify/preprocess.py --db instance/sabuzak.db
```

- `scripts/crawl/tradefairdates_scraper.py` — 단일 카테고리 페이지 크롤러 (다른 스크립트가 모듈로 불러다 씀). 개최기간 원문을 `start_date`/`end_date`(YYYYMMDD 숫자)로도 변환하고, `p.zutritt`(참관대상 원문, 예: "professional visitors only")도 함께 수집
- `scripts/crawl/sync_to_db.py` — 7개 카테고리 통합 크롤링 + `raw_exhibitions` 증분 동기화 (이름이 같아도 날짜가 바뀌면 업데이트, 목록에서 사라진 항목은 삭제 대신 비활성 처리)
- `scripts/crawl/multi_crawl_gui.py` — 위 크롤링을 수동으로 실행할 때 쓰는 내부용 GUI(tkinter) 도구, CSV로도 저장 가능
- `scripts/crawl/kotra_support_crawler.py` — KOTRA 정부 지원사업 공고 크롤러
- `scripts/classify/preprocess.py` — `raw_exhibitions`를 직접 읽고 분류 결과를 그대로 저장(`continent`/`food_yn`/`scale`/`keywords` 컬럼 UPDATE). `classified_at` 컬럼으로 이미 분류된 건 건너뛰고, 크롤링으로 `last_updated_at`이 갱신된 것만 다시 분류함. `--force`로 전체 재분류, `--limit N`으로 연습용 소량 테스트 가능. 거래고객 유형(B2B/B2C)은 별도 분류 없이 `raw_exhibitions`의 참관대상 원문 컬럼을 그대로 보여주는 쪽으로 대체함

`legacy/classify_with_openai.py`(예전 영문 컬럼, B2B/B2C 자체 분류)와 `legacy/make_sample_csv.py`(CSV 샘플 추출용)는 `preprocess.py`가 DB를 직접 읽고 쓰게 되면서 더 이상 쓰지 않습니다.

`app/models.py`의 `Exhibition` 모델은 `sync_to_db.py`가 채우고 `preprocess.py`가 분류 결과를 더하는 `raw_exhibitions` 테이블을 그대로 매핑해서 읽습니다.

### raw_exhibitions 컬럼
DB 컬럼명은 영문으로 두고(SQL/ORM에서 매번 따옴표 처리를 안 해도 되고 다른 도구와의 호환성도 좋음), 화면에 한글로 보여주는 건 Jinja 템플릿의 라벨/필터가 담당합니다.

| 컬럼 | 화면 표시 | 설명 |
|---|---|---|
| id | 순번 | PK |
| detail_url | (비표시) | 크롤링 dedup용 내부 키 (tradefairdates.com 상세페이지 URL) |
| name | 박람회명 | |
| start_date / end_date | 시작일 / 종료일 | YYYYMMDD 숫자. 날짜 전체가 미상이면 `UNKNOWN_DATE`(99999999, 실존하는 모든 날짜보다 큰 sentinel), 연/월만 알고 일자가 미상이면 일(day)=`32`(예: 2027년 10월 중 → `20271032`)로 채움. **0을 미상 값으로 쓰면 오름차순 정렬에서 오히려 맨 앞으로 와버리므로 쓰지 않음** — 두 경우 모두 실제 날짜보다 큰 값이라 임박한 날짜 순 정렬 시 자연스럽게 맨 뒤로 감 |
| country / city / venue | 국가 / 도시 / 장소 | |
| audience_note | 참관대상 | 원문 그대로(예: "professional visitors only") |
| website | 웹사이트 | 박람회 공식 사이트 |
| intro | 상세설명 | |
| category | (비표시) | 크롤링 카테고리(내부용, 부분 크롤링 시 비활성화 범위 판단에 필요) |
| continent / food_yn / scale / keywords | 대륙 / food_yn / 규모 / 키워드 | `preprocess.py` 분류 결과 |
| classified_at | (비표시) | 마지막 분류 시각 (내부용, `preprocess.py`가 이미 분류된 건 건너뛰는 기준) |
| is_active | (비표시) | 최근 크롤링에서도 보였는지 |
| last_updated_at | 마지막 업데이트 | 박람회 상세 페이지에 표시 |

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
│       └── preprocess.py
├── legacy/
│   ├── streamlit_prototype.py   # 초기 Streamlit 목업 (참고용, 배포 대상 아님)
│   ├── classify_with_openai.py  # 예전 분류 스크립트 (preprocess.py로 대체됨)
│   └── make_sample_csv.py       # 예전 CSV 샘플 추출 스크립트 (preprocess.py --limit으로 대체됨)
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
