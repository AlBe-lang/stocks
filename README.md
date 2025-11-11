# 📈 주식 시장 RAG 기반 뉴스레터 시스템

## 🎯 프로젝트 개요

10년차 시니어 개발자가 설계한 **RAG(Retrieval-Augmented Generation) 기반 주식 시장 분석 및 뉴스레터 자동 생성 시스템**입니다.

### 주요 기능
- ✅ 네이버 증권에서 실시간 주식 시장 데이터 수집
- ✅ Pandas를 활용한 데이터 정제 및 분석
- ✅ Matplotlib 기반 시각화 차트 자동 생성
- ✅ Google Gemini 2.5 Flash를 활용한 RAG 기반 인사이트 생성
- ✅ 전문적인 뉴스레터 형식 출력

---

## 🏗️ 시스템 아키텍처

```
자연어 입력 ("오늘자 국내 시장")
    ↓
┌─────────────────────────────────────┐
│  1. 데이터 수집 (BeautifulSoup4)    │
│  - 주요 지수 (코스피, 코스닥)       │
│  - 상승/하락 TOP 종목              │
│  - 주요 뉴스                       │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  2. 데이터 정제 (Pandas)            │
│  - DataFrame 변환                  │
│  - 통계 분석                       │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  3. 시각화 (Matplotlib)             │
│  - 지수 등락률 차트                │
│  - 상승 TOP 5 차트                 │
│  - 하락 TOP 5 차트                 │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  4. RAG 분석 (Gemini 2.5 Flash)     │
│  - 컨텍스트 생성                   │
│  - LLM 기반 인사이트 도출          │
└─────────────────────────────────────┘
    ↓
📄 뉴스레터 출력 (Markdown 형식)
```

---

## 🚀 설치 및 실행

### 1. 환경 설정

```bash
# Python 3.9+ 필요
python --version

# 가상환경 생성 (권장)
python -m venv venv

# 가상환경 활성화
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

### 2. API 키 발급

Google AI Studio에서 Gemini API 키를 발급받으세요:
👉 https://makersuite.google.com/app/apikey

### 3. 실행

```bash
python stock_newsletter.py
```

### 4. 사용법

```
🔑 Gemini API 키를 입력해주세요: [YOUR_API_KEY]

💬 질의를 입력하세요: 오늘자 국내 시장
```

---

## 📊 출력 결과

### 1. 콘솔 출력
- 실시간 처리 진행 상황
- 생성된 뉴스레터 전문

### 2. 파일 출력
```
/mnt/user-data/outputs/
├── newsletter.md              # 뉴스레터 마크다운 파일
├── indices_performance.png    # 주요 지수 차트
├── top_rising.png            # 상승 TOP 5 차트
└── top_falling.png           # 하락 TOP 5 차트
```

---

## 🔧 핵심 클래스 설명

### 1. `StockDataCollector`
```python
# 역할: 웹 스크래핑을 통한 데이터 수집
- collect_market_indices()    # 코스피, 코스닥 등 지수 수집
- collect_top_stocks()        # 상승/하락 종목 수집
- collect_market_news()       # 주요 뉴스 수집
```

### 2. `DataProcessor`
```python
# 역할: 데이터 정제 및 시각화
- process_market_data()       # DataFrame 변환
- create_visualizations()     # 차트 생성
- calculate_market_summary()  # 통계 계산
```

### 3. `RAGNewsletterGenerator`
```python
# 역할: LLM 기반 뉴스레터 생성
- create_context()            # RAG 컨텍스트 구성
- generate_newsletter()       # Gemini API 호출
```

### 4. `StockNewsletterSystem`
```python
# 역할: 전체 파이프라인 통합
- process_query()             # 통합 실행
- save_newsletter()           # 결과 저장
```

---

## 💡 설계 원칙 (시니어 개발자 관점)

### 1. **관심사의 분리 (Separation of Concerns)**
- 각 클래스는 단일 책임 원칙(SRP)을 준수
- 수집 → 정제 → 분석 → 생성의 명확한 파이프라인

### 2. **확장성 (Scalability)**
- 새로운 데이터 소스 추가 용이
- 다른 LLM 모델로 교체 가능한 구조

### 3. **유지보수성 (Maintainability)**
- Type Hints와 Dataclass 활용
- 명확한 함수/클래스 네이밍
- Docstring 작성

### 4. **에러 핸들링**
- Try-Except 블록으로 견고성 확보
- 의미있는 에러 메시지 제공

### 5. **성능 최적화**
- 불필요한 API 호출 최소화
- 데이터 캐싱 가능 구조

---

## 🎨 커스터마이징 가이드

### 1. 다른 웹사이트에서 데이터 수집
```python
class StockDataCollector:
    def __init__(self):
        # URL 변경
        self.base_url = "https://your-site.com"
```

### 2. 시각화 스타일 변경
```python
class DataProcessor:
    @staticmethod
    def create_visualizations():
        # Seaborn 스타일 적용
        import seaborn as sns
        sns.set_style("whitegrid")
```

### 3. LLM 모델 변경
```python
class RAGNewsletterGenerator:
    def __init__(self, api_key: str):
        # 다른 Gemini 모델 사용
        self.model = genai.GenerativeModel('gemini-1.5-pro')
```

---

## 📝 주요 의존성

| 패키지 | 버전 | 용도 |
|--------|------|------|
| beautifulsoup4 | 4.12.2 | 웹 스크래핑 |
| pandas | 2.1.3 | 데이터 처리 |
| matplotlib | 3.8.2 | 시각화 |
| google-generativeai | 0.3.1 | LLM API |
| requests | 2.31.0 | HTTP 요청 |

---

## ⚠️ 주의사항

1. **웹 스크래핑 정책**
   - 네이버 증권 이용약관 준수
   - 과도한 요청 자제 (Rate Limiting)

2. **API 사용량**
   - Gemini API 무료 할당량 확인
   - 과금 방지를 위한 모니터링

3. **데이터 정확성**
   - 실시간 데이터는 지연될 수 있음
   - 투자 결정은 본인 책임

---

## 🔄 향후 개선 사항

- [ ] 실시간 웹소켓 연결
- [ ] 데이터베이스 연동 (PostgreSQL)
- [ ] 이메일 자동 발송 기능
- [ ] 웹 대시보드 구축 (Streamlit/Flask)
- [ ] 다중 언어 지원
- [ ] 주식 예측 모델 통합

---

## 📞 문의 및 기여

- 버그 리포트: GitHub Issues
- 기능 제안: Pull Request 환영
- 라이선스: MIT

---

**개발자**: 10년차 시니어 풀스택 개발자  
**버전**: 1.0.0  
**최종 업데이트**: 2025-11-11
