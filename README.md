# Internal File Search

사내 폴더를 색인하고 파일명과 폴더 경로를 기준으로 필요한 문서를 검색하는 로컬 웹 애플리케이션입니다. 검색어의 연도, 최근 문서 표현, 파일 형식 등을 해석하며 결과 필터링, 페이지 이동, 파일 경로 복사를 지원합니다.

> 현재 버전: `v0.1.0`  
> 실행 환경: Windows, Python 3.12, Node.js 20.19 이상 또는 22.12 이상

## 프로젝트 구성

```text
InternalFileSearch/
├─ backend/
│  ├─ app/
│  │  ├─ api/          # 검색, 색인, 상태 확인 API
│  │  ├─ core/         # 환경설정과 공통 시간 처리
│  │  ├─ database/     # SQLite 연결과 데이터 모델
│  │  ├─ schemas/      # API 응답 스키마
│  │  ├─ services/     # 문서 색인, 질의 분석, 검색 로직
│  │  └─ main.py       # FastAPI 진입점
│  ├─ .env.example     # 백엔드 환경설정 예제
│  ├─ create_db.py     # 데이터베이스 수동 생성 도구
│  └─ run_index.py     # 문서 수동 색인 도구
├─ frontend/
│  ├─ public/          # 정적 파일
│  ├─ src/             # React 화면, API 클라이언트, 타입
│  ├─ .env.example     # 프런트엔드 환경설정 예제
│  ├─ package.json
│  └─ package-lock.json
├─ requirements.txt    # Python 패키지
├─ .gitignore
├─ LICENSE              # 저작권 및 사용 조건
└─ README.md
```

주요 기술은 FastAPI, SQLAlchemy, SQLite, React, TypeScript, Vite입니다.

색인 대상 확장자는 다음과 같습니다.

`ppt`, `pptx`, `pdf`, `doc`, `docx`, `xls`, `xlsx`, `csv`, `txt`, `hwp`, `hwpx`, `jpg`, `jpeg`, `png`, `zip`

## 프로젝트 프로그램 설치방법

### 1. 필수 프로그램

- Python 3.12 권장
- Node.js 24 LTS 권장
  - Vite 8 최소 조건: Node.js 20.19 이상 또는 22.12 이상
- VS Code는 선택 사항이며 실행에 반드시 필요하지는 않습니다.

Node.js 설치 시 npm이 함께 설치됩니다. 별도의 SQLite 서버, TypeScript 또는 Vite 전역 설치는 필요하지 않습니다.

### 2. 백엔드 설치

백엔드는 Python으로 실행됩니다. 프로젝트마다 사용하는 Python 패키지와 버전이 서로 충돌하지 않도록 **가상환경(venv)** 을 만든 뒤, 해당 가상환경 안에 필요한 패키지를 설치합니다.

먼저 다운로드하거나 복제한 프로젝트의 최상위 폴더인 `InternalFileSearch` 폴더에서 PowerShell을 엽니다.

현재 위치가 프로젝트 루트인지 확인합니다.

```powershell
pwd
```

폴더 안에 다음과 같이 `backend`, `frontend`, `requirements.txt` 등이 보이면 올바른 위치입니다.

```text
InternalFileSearch/
├─ backend/
├─ frontend/
├─ requirements.txt
└─ README.md
```

#### 2-1. Python 설치 확인

다음 명령어를 실행합니다.

```powershell
python --version
```

예시:

```text
Python 3.12.x
```

이 프로젝트는 **Python 3.12 사용을 권장합니다.**

`python` 명령을 찾을 수 없다는 메시지가 나오면 Python을 먼저 설치한 뒤 PowerShell 또는 VS Code를 다시 실행합니다.

#### 2-2. Python 가상환경 생성

프로젝트 루트에서 다음 명령어를 실행합니다.

```powershell
python -m venv venv
```

이 명령은 프로젝트 루트에 `venv`라는 폴더를 생성합니다.

```text
InternalFileSearch/
├─ backend/
├─ frontend/
├─ venv/              # Python 가상환경
├─ requirements.txt
└─ README.md
```

가상환경은 이 프로젝트에서 사용하는 Python 패키지를 별도로 관리하기 위한 공간입니다.

예를 들어 다른 Python 프로젝트에서 FastAPI나 SQLAlchemy의 다른 버전을 사용하고 있더라도, 이 프로젝트의 `venv` 내부 패키지와 서로 영향을 주지 않습니다.

`venv` 폴더는 자동으로 생성되는 실행 환경이므로 GitHub에 업로드하지 않습니다.

> 이 프로젝트에서는 가상환경을 별도로 활성화하지 않고 `.\venv\Scripts\python.exe`를 직접 호출하는 방식을 사용합니다.  
> 따라서 PowerShell의 실행 정책 때문에 `Activate.ps1`이 차단되는 문제를 피할 수 있습니다.

#### 2-3. pip 업데이트

생성한 가상환경의 Python을 사용하여 pip를 최신 버전으로 업데이트합니다.

```powershell
.\venv\Scripts\python.exe -m pip install --upgrade pip
```

여기서 `pip`는 Python 패키지를 설치하고 관리하는 도구입니다.

#### 2-4. 백엔드 패키지 설치

프로젝트의 `requirements.txt`에는 백엔드 실행에 필요한 Python 패키지 목록이 기록되어 있습니다.

다음 명령어를 실행합니다.

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

FastAPI, SQLAlchemy 등 프로젝트에 필요한 패키지가 `venv` 내부에 설치됩니다.

설치가 정상적으로 완료되었는지 확인하려면 다음 명령어를 실행할 수 있습니다.

```powershell
.\venv\Scripts\python.exe -m pip list
```

패키지 목록이 출력되면 백엔드 설치가 완료된 것입니다.

### 3. 프런트엔드 설치

프런트엔드는 React, TypeScript, Vite를 사용하며 Node.js와 npm으로 패키지를 관리합니다.

#### 3-1. Node.js와 npm 설치 확인

프로젝트 루트에서 다음 명령어를 실행합니다.

```powershell
node -v
npm -v
```

예시:

```text
v24.x.x
11.x.x
```

이 프로젝트는 **Node.js 24 LTS 사용을 권장합니다.**

Vite 8을 사용하기 위해서는 최소 Node.js 20.19 이상 또는 22.12 이상이 필요합니다.

`node` 또는 `npm` 명령을 찾을 수 없다는 메시지가 나오면 Node.js를 먼저 설치한 뒤 PowerShell 또는 VS Code를 다시 실행합니다.

Node.js를 설치하면 npm도 함께 설치되므로 npm을 별도로 설치할 필요는 없습니다.

#### 3-2. frontend 폴더로 이동

프런트엔드 관련 파일은 `frontend` 폴더 안에 있으므로 다음 명령어로 이동합니다.

```powershell
cd frontend
```

현재 위치는 다음과 같은 형태가 됩니다.

```text
InternalFileSearch\frontend
```

#### 3-3. 프런트엔드 패키지 설치

다음 명령어를 실행합니다.

```powershell
npm ci
```

`npm ci`는 `frontend/package-lock.json`에 기록되어 있는 정확한 버전을 기준으로 필요한 패키지를 설치합니다.

설치가 완료되면 `frontend` 폴더 안에 `node_modules` 폴더가 자동으로 생성됩니다.

```text
frontend/
├─ node_modules/       # 설치된 Node.js 패키지
├─ public/
├─ src/
├─ package.json
└─ package-lock.json
```

`node_modules`는 필요한 경우 다시 생성할 수 있으므로 GitHub에 업로드하지 않습니다.

> 일반적인 개발에서는 `npm install`도 사용할 수 있지만, 이 프로젝트를 처음 설치하거나 동일한 개발 환경을 재현할 때는 `package-lock.json`에 기록된 버전을 그대로 설치하는 `npm ci` 사용을 권장합니다.

#### 3-4. 프로젝트 루트로 돌아가기

프런트엔드 패키지 설치가 끝나면 다음 명령어를 실행합니다.

```powershell
cd ..
```

다시 프로젝트 루트인 `InternalFileSearch` 폴더로 이동합니다.

여기까지 완료하면 백엔드와 프런트엔드 실행에 필요한 기본 패키지 설치가 완료됩니다.

### 4. 환경설정

프로젝트 루트에서 예제 파일을 복사합니다.

```powershell
Copy-Item backend\.env.example backend\.env
Copy-Item frontend\.env.example frontend\.env
```

`backend/.env`의 문서 경로를 실제 환경에 맞게 변경합니다.

```dotenv
INDEX_ROOT_PATH=C:\회사문서\공유폴더
```

프런트엔드의 기본 API 주소는 다음과 같습니다.

```dotenv
VITE_API_BASE_URL=http://localhost:8000
```

`.env` 파일에는 PC의 로컬 경로나 민감한 설정이 들어갈 수 있으므로 Git에 커밋하지 마세요. 이 프로젝트의 `.gitignore`는 두 `.env` 파일을 제외하도록 설정되어 있습니다.

## 프로젝트 프로그램 사용법

### 1. 백엔드 실행

프로젝트 루트에서 실행합니다.

```powershell
cd backend
..\venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

- API 기본 주소: <http://localhost:8000>
- API 문서: <http://localhost:8000/docs>
- 상태 확인: <http://localhost:8000/api/health>

백엔드가 처음 실행되면 `backend/files.db`가 자동 생성됩니다.

### 2. 프런트엔드 실행

별도의 PowerShell 터미널을 열어 실행합니다.

```powershell
cd frontend
npm run dev
```

브라우저에서 <http://localhost:5173>에 접속합니다.

### 3. 문서 색인과 검색

1. 화면 하단의 색인 실행 버튼을 눌러 `INDEX_ROOT_PATH` 폴더를 스캔합니다.
2. 색인이 완료되면 검색창에 파일명, 프로젝트명, 연도 또는 파일 형식을 입력합니다.
3. 필요하면 PDF, Excel, PPT, Word 필터를 선택합니다.
4. 결과 카드의 경로 복사 기능으로 파일 경로를 복사합니다.

명령줄에서 색인하려면 백엔드 폴더에서 다음 명령을 실행할 수 있습니다.

```powershell
..\venv\Scripts\python.exe run_index.py
```

## 저작권 및 사용권 정보

Copyright © 2026 RealSWoo(swoo226@oton.kr). All Rights Reserved.

이 프로젝트는 독점 소프트웨어입니다. 저작권자의 사전 서면 허가 없이 소스 코드와 문서를 복제, 수정, 배포, 재라이선스하거나 상업적으로 사용할 수 없습니다. 자세한 내용은 저장소의 `LICENSE` 파일을 확인하세요.

## 프로그래머 정보

- 개발자: RealSWoo(swoo226@oton.kr)
- 문의: [swoo226@oton.kr](mailto:swoo226@oton.kr)

## 버그 및 디버그

### 알려진 사항

- `npm run lint` 실행 시 `IndexStatusPanel.tsx`의 초기 상태 조회 방식에 대해 `react-hooks/set-state-in-effect` 규칙 오류가 보고될 수 있습니다. 실제 프로덕션 빌드와 실행에는 영향을 주지 않지만 추후 코드 개선이 필요합니다.
- 현재 자동화된 테스트 모음은 포함되어 있지 않습니다.
- 백엔드 CORS 허용 주소는 기본적으로 프런트엔드 개발 서버의 `localhost:5173`과 `127.0.0.1:5173`입니다.

### 문제 해결

| 증상 | 확인 방법 |
|---|---|
| `ModuleNotFoundError` 발생 | 프로젝트 루트의 `venv`에 `requirements.txt`를 다시 설치했는지 확인합니다. |
| `npm` 명령을 찾지 못함 | Node.js를 설치한 뒤 터미널과 VS Code를 다시 시작합니다. |
| Vite가 Node.js 버전 오류를 출력함 | `node --version`이 20.19 이상 또는 22.12 이상인지 확인합니다. |
| 검색 결과가 없음 | `backend/.env`의 경로, 색인 실행 여부, 지원 확장자를 확인합니다. |
| 프런트엔드에서 API 연결 실패 | 백엔드 실행 여부와 `frontend/.env`의 API 주소를 확인합니다. |
| 색인 중 접근 오류 발생 | 문서 폴더에 대한 현재 Windows 사용자의 읽기 권한을 확인합니다. |

백엔드 로그를 자세히 보려면 `--log-level debug` 옵션을 추가할 수 있습니다.

```powershell
..\venv\Scripts\python.exe -m uvicorn app.main:app --reload --log-level debug
```

## 참고 및 출처

- [Python 공식 문서](https://docs.python.org/3/)
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [SQLAlchemy 공식 문서](https://docs.sqlalchemy.org/)
- [Pydantic 공식 문서](https://docs.pydantic.dev/)
- [React 공식 문서](https://react.dev/)
- [Vite 공식 문서](https://vite.dev/guide/)
- [Node.js 공식 사이트](https://nodejs.org/)


## 버전 및 업데이트 정보

| 버전 | 날짜 | 주요 내용 |
|---|---|---|
| v0.1.0 | 2026-08-28 | `Internal File Search` 최초 GitHub 정리 버전. 문서 색인, 자연어 검색, 파일 형식 필터, 페이지 이동, 파일 경로 복사, 색인 상태 확인 기능 포함 |

버전 번호는 `주버전.부버전.수정버전` 형태의 시맨틱 버저닝을 따르는 것을 권장합니다.

## FAQ

### Q. 별도의 데이터베이스를 설치해야 하나요?

아니요. Python에 포함된 SQLite를 사용하며 데이터베이스 파일은 백엔드 최초 실행 시 자동 생성됩니다.

### Q. 실제 문서 내용도 데이터베이스에 저장되나요?

현재 색인기는 파일명, 경로, 크기, 수정 시각 등의 메타데이터를 저장합니다. 문서 본문이나 원본 파일 자체를 복사하지 않습니다.

### Q. 네트워크 공유 폴더도 검색할 수 있나요?

백엔드를 실행하는 Windows 계정이 해당 공유 폴더를 읽을 수 있다면 가능합니다. `INDEX_ROOT_PATH`에 접근 가능한 절대 경로 또는 UNC 경로를 지정하세요.

### Q. 새 파일을 추가하면 자동으로 반영되나요?

현재는 색인을 다시 실행해야 반영됩니다. 화면의 색인 실행 버튼이나 `run_index.py`를 사용하세요.

### Q. 프런트엔드와 백엔드를 동시에 실행해야 하나요?

개발 모드에서는 두 서버를 각각 실행해야 합니다. 백엔드는 기본 8000번, 프런트엔드는 기본 5173번 포트를 사용합니다.

### Q. `venv`, `node_modules`, `files.db`를 GitHub에 올려야 하나요?

아니요. 모두 설치 또는 실행 과정에서 다시 생성됩니다. 저장소에는 `requirements.txt`, `package.json`, `package-lock.json`만 포함하면 됩니다.
