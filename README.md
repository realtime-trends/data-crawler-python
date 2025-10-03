# Data Crawler Python

[![update-trends-resource](https://github.com/realtime-trends/data-crawler-python/actions/workflows/update.yml/badge.svg?event=workflow_dispatch)](https://github.com/realtime-trends/data-crawler-python/actions/workflows/update.yml)

실시간 트렌드 데이터를 수집하고 분석하는 Python 크롤러입니다. 한국의 주요 포털 사이트(Nate, Zum)에서 실시간 검색어를 수집하여 통합 트렌드 데이터를 생성합니다.

## 🚀 주요 기능

- **다중 소스 크롤링**: Nate, Zum 포털의 실시간 검색어 수집
- **트렌드 점수 계산**: 가중치 기반 통합 점수 산출
- **중복 키워드 처리**: 유사한 키워드 통합 및 점수 합산
- **변화 추적**: 이전 순위와 비교하여 상승/하락 추이 계산
- **자동화 워크플로우**: GitHub Actions를 통한 주기적 데이터 업데이트

## 📁 프로젝트 구조

```
data-crawler-python/
├── main.py                 # 메인 실행 파일
├── requirements.txt        # Python 의존성 목록
├── .github/workflows/      # GitHub Actions 워크플로우
│   └── update.yml         # 자동 업데이트 워크플로우
├── src/                   # 소스 코드
│   ├── __init__.py       # 모듈 초기화
│   ├── crawl.py          # 크롤링 및 트렌드 계산 로직
│   └── trendjson.py      # JSON 데이터 관리
├── models/               # 데이터 모델
│   ├── trend.py         # 트렌드 데이터 모델
│   └── article.py       # 기사 데이터 모델
└── ref/                 # 참조 파일
    └── except.txt       # 제외할 키워드 목록
```

## 🔧 설치 및 실행

### 사전 요구사항
- Python 3.8.12+
- pip 패키지 매니저

### 설치
```bash
# 저장소 클론
git clone https://github.com/realtime-trends/data-crawler-python.git
cd data-crawler-python

# 의존성 설치
pip install -r requirements.txt
```

### 실행
```bash
python main.py
```

## 📊 데이터 수집 방식

### 1. 포털별 크롤링
- **Zum**: HTML 파싱을 통한 실시간 검색어 추출
- **Nate**: JSON API를 통한 실시간 검색어 수집

### 2. 점수 계산 시스템
```python
WEIGHTS = [20, 19, 18, 17, 16, 15, 14, 13, 12, 11]  # 순위별 가중치
ENGINE_BIAS = {
    "nate": 0.7,    # Nate 엔진 가중치
    "zum": 1.0,     # Zum 엔진 가중치
}
```

### 3. 키워드 처리
- 한자 → 한글 변환 (`hanja` 라이브러리 사용)
- 특수문자 제거 및 공백 정규화
- 제외 키워드 필터링 (`ref/except.txt`)

### 4. 유사도 처리
- 포함 관계 키워드 통합
- 유사도 가중치: 0.7

## 🔄 워크플로우

### 실행 주기
- 10분 간격 (INTERVAL_SECS = 600)
- GitHub Actions를 통한 자동 실행

### 데이터 관리
1. **신규 데이터 수집**: 현재 타임스탬프로 트렌드 데이터 생성
2. **이전 데이터 비교**: 10분 전 데이터와 순위 변화 계산
3. **데이터 정리**: 오래된 타임스탬프 데이터 삭제 (최근 2개만 유지)
4. **JSON 저장**: `data/trends.json`에 결과 저장

## 📝 데이터 모델

### Trend 클래스
```python
@dataclass
class Trend:
    keyword: str        # 검색 키워드
    score: float       # 통합 점수
    maxscore: float    # 최대 점수
    hashed: str        # 키워드 해시값
    delta: int         # 순위 변화 (이전 대비)
    topArticles: List[Article]  # 관련 기사 (현재 미사용)
```

### Article 클래스
```python
@dataclass
class Article:
    title: str         # 기사 제목
    link: str          # 기사 링크
    content: str       # 기사 내용
    thumnail: str      # 썸네일 이미지
```

## ⚙️ GitHub Actions 워크플로우

자동화된 데이터 수집을 위한 워크플로우가 구성되어 있습니다:

- **트리거**: 수동 실행 (workflow_dispatch)
- **환경**: Ubuntu Latest, Python 3.8.12
- **수행 작업**:
  1. 코드 체크아웃
  2. 데이터 저장소 체크아웃
  3. Python 환경 설정
  4. 의존성 설치
  5. 크롤링 스크립트 실행
  6. 결과를 데이터 저장소에 푸시

## 📋 의존성

주요 라이브러리:
- `beautifulsoup4`: HTML 파싱
- `requests`: HTTP 요청
- `hanja`: 한자-한글 변환
- `lxml`: XML/HTML 파서
- `selenium`: 웹 드라이버 (현재 비활성화)

전체 의존성은 `requirements.txt` 참조.

## 🔍 주요 함수

### `main.py`
- 메인 실행 로직
- 타임스탬프 관리
- 데이터 비교 및 업데이트

### `src/crawl.py`
- `calculate_trends()`: 통합 트렌드 계산
- `get_trends_by_engine()`: 포털별 데이터 수집
- `set_delta()`: 순위 변화 계산
- `process_keyword()`: 키워드 전처리

### `src/trendjson.py`
- `TrendJson`: JSON 데이터 관리 클래스
- 읽기, 쓰기, 업데이트, 삭제 기능

## 🚫 제외 키워드

`ref/except.txt`에 정의된 키워드들은 수집 대상에서 제외됩니다:
- Yesbet88
- sanopk

## 🔧 설정

### 시간 간격 설정
```python
INTERVAL_SECS = 600  # 10분 (600초)
```

### 유사도 가중치
```python
SIMILARITY_WEIGHT = 0.7  # 70%
```

## 📈 출력 예시

실행 시 다음과 같은 형태의 트렌드 데이터가 출력됩니다:

```json
[
  {
    "keyword": "검색어1",
    "score": 40.0,
    "maxscore": 20.0,
    "hashed": "a1b2c3d4e5f6g7h8",
    "delta": 999,
    "topArticles": []
  }
]
```

## 🤝 기여하기

1. 이 저장소를 포크합니다
2. 기능 브랜치를 생성합니다 (`git checkout -b feature/AmazingFeature`)
3. 변경사항을 커밋합니다 (`git commit -m 'Add some AmazingFeature'`)
4. 브랜치에 푸시합니다 (`git push origin feature/AmazingFeature`)
5. Pull Request를 생성합니다

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 문의

프로젝트 관련 문의사항이 있으시면 이슈를 생성해주세요.