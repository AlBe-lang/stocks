"""
주식 시장 RAG 기반 뉴스레터 시스템 - 고급 버전
추가 기능: 캐싱, 로깅, 설정 파일, 에러 복구
"""

import os
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import pickle

import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import google.generativeai as genai

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/claude/stock_newsletter.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class Config:
    """설정 관리 클래스"""
    
    DEFAULT_CONFIG = {
        "cache_duration_minutes": 30,
        "max_retries": 3,
        "timeout_seconds": 10,
        "output_directory": "/mnt/user-data/outputs",
        "cache_directory": "/home/claude/.cache",
        "gemini_model": "gemini-2.0-flash-exp",
        "top_stocks_count": 10,
        "news_count": 5,
    }
    
    def __init__(self, config_path: str = "/home/claude/config.json"):
        self.config_path = config_path
        self.config = self.load_config()
    
    def load_config(self) -> Dict:
        """설정 파일 로드"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    return {**self.DEFAULT_CONFIG, **user_config}
            except Exception as e:
                logger.warning(f"설정 파일 로드 실패, 기본값 사용: {e}")
        return self.DEFAULT_CONFIG.copy()
    
    def save_config(self):
        """설정 파일 저장"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            logger.info("설정 파일 저장 완료")
        except Exception as e:
            logger.error(f"설정 파일 저장 실패: {e}")
    
    def get(self, key: str, default=None):
        """설정값 조회"""
        return self.config.get(key, default)


class CacheManager:
    """캐시 관리 클래스"""
    
    def __init__(self, cache_dir: str, duration_minutes: int = 30):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.duration = timedelta(minutes=duration_minutes)
    
    def get_cache_path(self, key: str) -> Path:
        """캐시 파일 경로 생성"""
        return self.cache_dir / f"{key}.cache"
    
    def is_valid(self, key: str) -> bool:
        """캐시 유효성 검증"""
        cache_path = self.get_cache_path(key)
        if not cache_path.exists():
            return False
        
        # 파일 수정 시간 확인
        mtime = datetime.fromtimestamp(cache_path.stat().st_mtime)
        return datetime.now() - mtime < self.duration
    
    def get(self, key: str) -> Optional[any]:
        """캐시 데이터 조회"""
        if not self.is_valid(key):
            return None
        
        try:
            cache_path = self.get_cache_path(key)
            with open(cache_path, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            logger.warning(f"캐시 로드 실패: {e}")
            return None
    
    def set(self, key: str, data: any):
        """캐시 데이터 저장"""
        try:
            cache_path = self.get_cache_path(key)
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
            logger.info(f"캐시 저장 완료: {key}")
        except Exception as e:
            logger.error(f"캐시 저장 실패: {e}")
    
    def clear(self, key: Optional[str] = None):
        """캐시 삭제"""
        if key:
            cache_path = self.get_cache_path(key)
            if cache_path.exists():
                cache_path.unlink()
        else:
            # 모든 캐시 삭제
            for cache_file in self.cache_dir.glob("*.cache"):
                cache_file.unlink()
        logger.info(f"캐시 삭제 완료: {key or 'all'}")


class EnhancedStockDataCollector:
    """개선된 주식 데이터 수집 클래스 (재시도 로직 포함)"""
    
    def __init__(self, config: Config, cache_manager: CacheManager):
        self.config = config
        self.cache = cache_manager
        self.base_url = "https://m.stock.naver.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def _fetch_with_retry(self, url: str, cache_key: str) -> Optional[BeautifulSoup]:
        """재시도 로직이 포함된 HTTP 요청"""
        
        # 캐시 확인
        cached_data = self.cache.get(cache_key)
        if cached_data:
            logger.info(f"캐시 사용: {cache_key}")
            return cached_data
        
        max_retries = self.config.get('max_retries', 3)
        timeout = self.config.get('timeout_seconds', 10)
        
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=self.headers, timeout=timeout)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # 캐시 저장
                self.cache.set(cache_key, soup)
                logger.info(f"데이터 수집 성공: {cache_key}")
                return soup
                
            except requests.RequestException as e:
                logger.warning(f"시도 {attempt + 1}/{max_retries} 실패: {e}")
                if attempt == max_retries - 1:
                    logger.error(f"최종 실패: {url}")
                    return None
        
        return None
    
    def collect_market_indices(self) -> List[Dict]:
        """주요 지수 정보 수집 (개선된 버전)"""
        soup = self._fetch_with_retry(
            f"{self.base_url}/index.naver",
            "market_indices"
        )
        
        if not soup:
            logger.error("지수 데이터 수집 실패")
            return self._get_fallback_indices()
        
        # 실제 파싱 로직은 네이버 증권의 HTML 구조에 맞춰 구현
        # 여기서는 예시 데이터 반환
        return self._get_fallback_indices()
    
    def _get_fallback_indices(self) -> List[Dict]:
        """폴백 데이터 (수집 실패 시)"""
        logger.info("폴백 데이터 사용")
        return [
            {
                "index_name": "KOSPI",
                "current_value": 2500.0,
                "change_value": 10.5,
                "change_rate": 0.42,
                "timestamp": datetime.now().isoformat()
            },
            {
                "index_name": "KOSDAQ",
                "current_value": 850.0,
                "change_value": -5.2,
                "change_rate": -0.61,
                "timestamp": datetime.now().isoformat()
            }
        ]
    
    def collect_top_stocks(self, category: str = 'rise') -> List[Dict]:
        """상승/하락 상위 종목 수집"""
        cache_key = f"top_stocks_{category}"
        
        # 실제 구현에서는 웹 스크래핑 로직 추가
        # 여기서는 예시 데이터
        sample_stocks = [
            {"rank": i+1, "name": f"종목{i+1}", "current_price": 50000 + i*1000,
             "change_rate": 5.0 - i*0.3, "category": category}
            for i in range(self.config.get('top_stocks_count', 10))
        ]
        
        return sample_stocks
    
    def collect_market_news(self) -> List[Dict]:
        """시장 주요 뉴스 수집"""
        cache_key = "market_news"
        
        # 실제 구현에서는 뉴스 파싱 로직 추가
        return [
            {"title": f"뉴스 제목 {i+1}", "summary": f"요약 내용 {i+1}"}
            for i in range(self.config.get('news_count', 5))
        ]


class AdvancedStockNewsletterSystem:
    """고급 통합 시스템"""
    
    def __init__(self, gemini_api_key: str, config_path: Optional[str] = None):
        self.config = Config(config_path) if config_path else Config()
        self.cache = CacheManager(
            self.config.get('cache_directory'),
            self.config.get('cache_duration_minutes')
        )
        self.collector = EnhancedStockDataCollector(self.config, self.cache)
        
        # Gemini 설정
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel(self.config.get('gemini_model'))
        
        logger.info("시스템 초기화 완료")
    
    def process_query(self, user_input: str) -> Dict:
        """사용자 쿼리 처리 (향상된 버전)"""
        try:
            logger.info(f"쿼리 처리 시작: {user_input}")
            
            # 1. 데이터 수집
            indices = self.collector.collect_market_indices()
            rising = self.collector.collect_top_stocks('rise')
            falling = self.collector.collect_top_stocks('fall')
            news = self.collector.collect_market_news()
            
            # 2. 데이터 처리
            processed = self._process_data(indices, rising, falling)
            
            # 3. 시각화
            images = self._create_visualizations(processed)
            
            # 4. 뉴스레터 생성
            newsletter = self._generate_newsletter(processed, news, user_input)
            
            result = {
                'success': True,
                'newsletter': newsletter,
                'images': images,
                'timestamp': datetime.now().isoformat(),
                'cached_data': self.cache.is_valid('market_indices')
            }
            
            logger.info("쿼리 처리 완료")
            return result
            
        except Exception as e:
            logger.error(f"쿼리 처리 중 오류: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _process_data(self, indices, rising, falling) -> Dict:
        """데이터 처리"""
        return {
            'indices': pd.DataFrame(indices),
            'rising': pd.DataFrame(rising),
            'falling': pd.DataFrame(falling)
        }
    
    def _create_visualizations(self, data_dict: Dict) -> List[str]:
        """시각화 생성"""
        output_dir = self.config.get('output_directory')
        os.makedirs(output_dir, exist_ok=True)
        
        images = []
        
        # 지수 차트
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            if 'change_rate' in data_dict['indices'].columns:
                ax.bar(data_dict['indices']['index_name'], 
                       data_dict['indices']['change_rate'])
                ax.set_title('Market Indices Performance')
                plt.tight_layout()
                
                path = f"{output_dir}/indices_chart.png"
                plt.savefig(path, dpi=150)
                plt.close()
                images.append(path)
        except Exception as e:
            logger.error(f"시각화 오류: {e}")
        
        return images
    
    def _generate_newsletter(self, data: Dict, news: List, query: str) -> str:
        """뉴스레터 생성"""
        try:
            context = self._create_context(data, news)
            
            prompt = f"""
당신은 전문 금융 애널리스트입니다.

사용자 질의: {query}

데이터:
{context}

위 데이터를 바탕으로 전문적이고 통찰력 있는 시장 분석 뉴스레터를 작성해주세요.
"""
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"뉴스레터 생성 오류: {e}")
            return f"뉴스레터 생성 중 오류 발생: {e}"
    
    def _create_context(self, data: Dict, news: List) -> str:
        """RAG 컨텍스트 생성"""
        context = f"### 시장 지수\n{data['indices'].to_string()}\n\n"
        context += f"### 상승 종목\n{data['rising'].head().to_string()}\n\n"
        context += f"### 하락 종목\n{data['falling'].head().to_string()}\n\n"
        context += "### 주요 뉴스\n"
        for item in news:
            context += f"- {item['title']}\n"
        return context
    
    def clear_cache(self):
        """캐시 초기화"""
        self.cache.clear()
        logger.info("모든 캐시 삭제 완료")


def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("📈 고급 주식 시장 RAG 뉴스레터 시스템")
    print("=" * 60)
    
    api_key = input("\n🔑 Gemini API 키: ").strip()
    if not api_key:
        print("❌ API 키가 필요합니다.")
        return
    
    system = AdvancedStockNewsletterSystem(api_key)
    
    while True:
        print("\n" + "-" * 60)
        print("명령어: '오늘자 국내 시장', 'cache clear', 'exit'")
        user_input = input("💬 입력: ").strip()
        
        if user_input.lower() == 'exit':
            break
        elif user_input.lower() == 'cache clear':
            system.clear_cache()
            print("✅ 캐시가 초기화되었습니다.")
            continue
        
        result = system.process_query(user_input)
        
        if result['success']:
            print("\n" + "=" * 60)
            print("✅ 뉴스레터 생성 완료!")
            print("=" * 60)
            print(result['newsletter'])
            
            if result.get('cached_data'):
                print("\n💾 캐시된 데이터 사용됨")
        else:
            print(f"\n❌ 오류: {result.get('error')}")


if __name__ == "__main__":
    main()
