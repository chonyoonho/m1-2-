# 3.8민주의거기념사업회 데이터 비서

대전광역시 3.8민주의거기념사업회의 **교육·행사 프로그램 참가자 수** 데이터를 분석하고, 그 요약을 바탕으로
담당자의 질문에 맞춤형으로 답변하는 AI 데이터 비서입니다. "이번 달 참가자가 어때?" 같은 질문에 실제 데이터 기반으로 답합니다.

> 3.8민주의거기념관 홈페이지([38demo.kr](https://38demo.kr/))에는 방문객·참가자 통계가 별도로 공개되어 있지 않아,
> 기념관이 실제 운영 중인 프로그램군(3.8민주아카데미, 보드게임으로 만나는 민주주의, 청소년 백일장·사생대회,
> 학교 연계 현장체험학습, 시민 해설사 양성과정 등)을 기준으로 현실적인 추정 데이터를 생성해 사용합니다.
> (`backend/seed_data.py` 참고, 2019~2025년 총 245건)

## 무엇을 해결하나요

- 담당자가 매번 엑셀을 열어보지 않아도, AI 채팅으로 참가자 추이·평균·최근 트렌드를 바로 물어볼 수 있습니다.
- 데이터(참가자 수 기록)를 웹에서 직접 추가/수정/삭제할 수 있습니다.
- AI와 나눈 대화를 저장하고 나중에 다시 불러볼 수 있습니다.

## 기술 스택

| 영역 | 기술 |
|---|---|
| 백엔드 | FastAPI, Pydantic, uvicorn |
| 데이터베이스 | Firebase Firestore |
| AI | OpenAI GPT API (Chat Completions) |
| 프론트엔드 | HTML / CSS / JavaScript (바닐라, 프레임워크 미사용) |
| 배포 | 백엔드: Render / 프론트엔드: Vercel |

## 배포 URL

| 항목 | URL |
|---|---|
| 프론트엔드 | https://frontend-blond-one-98.vercel.app |
| 백엔드 API | https://three8demo-backend.onrender.com |
| Swagger 문서 | https://three8demo-backend.onrender.com/docs |

> ⚠️ Render 무료 티어는 일정 시간 요청이 없으면 슬립 상태가 되어, 배포 후 첫 요청은 응답까지 30초~1분 정도 걸릴 수 있습니다.
> 프론트엔드 채팅 로딩 표시("답변을 생각하는 중입니다...")가 이 지연을 안내합니다.

## 프로젝트 구조

```
3.8-project/
├── backend/            # FastAPI 백엔드
│   ├── app/
│   │   ├── main.py         # 앱 초기화 + CORS + 라우터 등록
│   │   ├── config.py        # 환경 변수 설정
│   │   ├── models/          # Pydantic 요청/응답 스키마
│   │   ├── routers/         # data / conversations / chat 엔드포인트
│   │   └── services/        # firestore, openai, 데이터 분석 로직
│   ├── seed_data.py    # 샘플 참가자 수 데이터 생성/업로드 스크립트
│   ├── requirements.txt
│   ├── render.yaml     # Render 배포 설정
│   └── .env.example
└── frontend/           # 바닐라 HTML/CSS/JS 프론트엔드
    ├── index.html
    ├── css/styles.css
    ├── js/              # config, api, chat, data, conversations, main
    ├── build.js         # Vercel 빌드 시 API_BASE_URL 주입 스크립트
    └── vercel.json
```

## 로컬 실행 방법

### 1) 사전 준비

- Python 3.10 이상 (권장: 3.11~3.12. 이 저장소 작성 시점 기준 Python 3.14는 일부 패키지의 사전 빌드 wheel이 아직
  부족해 로컬 설치가 실패할 수 있습니다.)
- Node.js (프론트엔드 빌드 스크립트 실행용, 배포 시에만 필요하며 로컬 개발엔 필수 아님)
- Firebase 프로젝트 + Firestore 활성화 + 서비스 계정 키(JSON) 발급
- OpenAI API 키

### 2) 백엔드

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # (Windows) / source .venv/bin/activate (macOS/Linux)
pip install -r requirements.txt

copy .env.example .env        # (Windows) / cp .env.example .env
# .env 파일에 OPENAI_API_KEY, FIREBASE_SERVICE_ACCOUNT_JSON, ALLOWED_ORIGINS 채우기

# 샘플 데이터를 Firestore에 업로드 (최초 1회)
python seed_data.py

# 서버 실행
uvicorn app.main:app --reload
```

- 브라우저에서 http://localhost:8000/docs 로 Swagger UI 확인
- `python seed_data.py --dry-run` 으로 Firestore 업로드 없이 `sample_data.json` 미리보기 가능

### 3) 프론트엔드

로컬에서는 빌드 없이 `frontend/js/config.js`의 `API_BASE_URL`이 이미 `http://localhost:8000`으로 설정되어 있습니다.

```bash
cd frontend
python -m http.server 3000
# 또는 VSCode Live Server 등 정적 서버 사용
```

- 브라우저에서 http://localhost:3000 접속

## 환경 변수 (최소 세트)

### 백엔드 (Render)

| 변수 | 설명 |
|---|---|
| `OPENAI_API_KEY` | OpenAI API 키 |
| `FIREBASE_SERVICE_ACCOUNT_JSON` | Firebase 서비스 계정 키 JSON 전체를 문자열로 저장 |
| `ALLOWED_ORIGINS` | CORS 허용 도메인 (콤마 구분, 예: `https://your-frontend.vercel.app`) |
| `CHAT_MODEL` | (선택) 기본값 `gpt-4o-mini` |
| `CHAT_MAX_TOKENS` | (선택) 기본값 `500`, 비용 관리를 위한 응답 토큰 제한 |

### 프론트엔드 (Vercel)

| 변수 | 설명 |
|---|---|
| `API_BASE_URL` | 배포된 백엔드(Render) URL. `frontend/build.js`가 빌드 시 `js/config.js`에 주입 |

## 배포 방법 요약

**백엔드 (Render)**
1. GitHub에 저장소 푸시
2. Render → New Web Service → 이 저장소 연결, Root Directory를 `backend`로 지정
3. Build Command: `pip install -r requirements.txt`, Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. 위 환경 변수 등록 후 배포
5. `{배포 URL}/docs`에서 Swagger UI 접속 확인

**프론트엔드 (Vercel)**
1. Vercel → New Project → 이 저장소 연결, Root Directory를 `frontend`로 지정
2. 환경 변수 `API_BASE_URL`에 Render 배포 URL 입력
3. Build Command는 `vercel.json`에 정의된 `npm run build`(=`node build.js`)가 자동 사용됨
4. 배포 후 접속하여 동작 확인

## API 요약

| 메서드 | 경로 | 설명 |
|---|---|---|
| POST | `/api/data` | 참가자 수 데이터 추가 |
| GET | `/api/data` | 데이터 목록 조회 |
| PUT | `/api/data/{id}` | 데이터 수정 |
| DELETE | `/api/data/{id}` | 데이터 삭제 |
| GET | `/api/data/summary` | 기간/통계/추세 요약 (프롬프트 주입용) |
| POST | `/api/conversations` | 대화 저장 |
| GET | `/api/conversations` | 대화 목록 조회 (메시지 미포함) |
| GET | `/api/conversations/{id}` | 특정 대화 전체 메시지 조회 |
| DELETE | `/api/conversations/{id}` | 대화 삭제 |
| POST | `/api/chat` | AI 채팅 (요약 조회 → 시스템 프롬프트 주입 → GPT 호출 → 대화 자동 저장) |

## 제출 스크린샷

배포 후 아래 화면을 캡처해 이 섹션에 추가하세요.

- [ ] 데이터 요약이 보이는 채팅 화면 (질문 + 답변 포함)
- [ ] 데이터 관리 화면 (추가/수정/삭제 중 1개 동작이 보이도록)
- [ ] 대화 기록 화면 (불러오기 동작이 보이도록)
