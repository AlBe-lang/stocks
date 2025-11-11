# 🚀 빠른 시작 가이드

## 1분 안에 시작하기

### Step 1: 패키지 설치
```bash
pip install beautifulsoup4 requests pandas matplotlib google-generativeai
```

### Step 2: API 키 준비
Google AI Studio에서 무료 API 키 발급:
👉 https://makersuite.google.com/app/apikey

### Step 3: 실행
```bash
# 기본 버전 (추천)
python stock_newsletter.py

# 고급 버전 (캐싱, 로깅 포함)
python stock_newsletter_advanced.py
```

### Step 4: 사용
```
🔑 Gemini API 키를 입력해주세요: [여기에 API 키 붙여넣기]

💬 질의를 입력하세요: 오늘자 국내 시장
```

---

## 📁 파일 설명

| 파일명 | 설명 | 난이도 |
|--------|------|--------|
| `stock_newsletter.py` | 기본 버전 - 심플하고 직관적 | ⭐⭐ |
| `stock_newsletter_advanced.py` | 고급 버전 - 캐싱, 로깅, 재시도 | ⭐⭐⭐⭐ |
| `requirements.txt` | 필요한 패키지 목록 | - |
| `README.md` | 상세 문서 | - |

---

## 💡 주요 질의 예시

```
✅ "오늘자 국내 시장"
✅ "오늘자 국내 주식 시장"
✅ "국내 시장 현황"
```

---

## 📊 출력 예시

```markdown
# 📈 오늘의 국내 주식 시장 리포트

## 🎯 시장 개요
코스피는 외국인 매수세에 힘입어 전일 대비 0.42% 상승한 2,500선에서 마감했습니다...

## 📊 주요 지수 동향
- KOSPI: 2,500.00 (▲0.42%)
- KOSDAQ: 850.00 (▼0.61%)

## 🚀 주목할 상승 종목
1. 삼성전자 (+5.2%)
2. SK하이닉스 (+4.8%)
...
```

---

## 🎯 핵심 기능

### ✅ 자동 수집
- 네이버 증권에서 실시간 데이터 크롤링
- 주요 지수, 상승/하락 종목, 뉴스 자동 수집

### ✅ 데이터 분석
- Pandas로 정제 및 통계 분석
- 자동 이상치 탐지

### ✅ 시각화
- Matplotlib 기반 차트 자동 생성
- 지수 등락률, TOP 5 종목 차트

### ✅ AI 인사이트
- Gemini 2.5 Flash 활용
- RAG 기반 맥락 이해
- 전문적인 분석 제공

---

## ⚙️ 고급 기능 (Advanced 버전)

### 🔄 스마트 캐싱
```python
# 30분간 데이터 캐싱으로 API 호출 최소화
system.clear_cache()  # 캐시 초기화
```

### 📝 로깅
```
2025-11-11 10:30:00 - INFO - 데이터 수집 성공
2025-11-11 10:30:05 - INFO - 캐시 사용: market_indices
```

### 🔁 자동 재시도
- 네트워크 오류 시 최대 3회 자동 재시도
- 타임아웃 설정 가능

### ⚙️ 설정 파일
```json
{
  "cache_duration_minutes": 30,
  "max_retries": 3,
  "top_stocks_count": 10
}
```

---

## 🐛 문제 해결

### Q1: ImportError 발생
```bash
# 모든 패키지 재설치
pip install -r requirements.txt --upgrade
```

### Q2: 한글 깨짐
```python
# UTF-8 인코딩 확인
# Windows: 시스템 로케일 설정
```

### Q3: API 키 오류
```
❌ "Invalid API key"
→ https://makersuite.google.com 에서 키 재발급
```

### Q4: 데이터 수집 실패
```
❌ 네이버 증권 접속 불가
→ 네트워크 연결 확인
→ VPN 사용 시 비활성화
```

---

## 🎓 학습 자료

### 초보자를 위한 개념 설명

**RAG (Retrieval-Augmented Generation)란?**
> 외부 데이터를 검색(Retrieval)하여 AI의 답변 생성(Generation)을 향상시키는 기술

**이 프로젝트에서 RAG 동작 방식:**
1. 📥 웹에서 최신 주식 데이터 수집 (Retrieval)
2. 🧹 데이터 정제 및 구조화
3. 🤖 Gemini에 구조화된 데이터 제공 (Augmentation)
4. ✍️ AI가 맥락을 이해하고 인사이트 생성 (Generation)

---

## 📞 지원

- 🐛 버그 리포트: GitHub Issues
- 💡 기능 제안: Pull Request
- 📧 문의: [이메일]

---

**Happy Trading! 📈**
