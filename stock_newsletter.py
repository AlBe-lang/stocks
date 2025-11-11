"""
주식 시장 RAG 기반 뉴스레터 생성 시스템
Author: Senior Full-Stack Developer
Version: 1.0.0
"""

import os
import re
from datetime import datetime
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import google.generativeai as genai
from dataclasses import dataclass
import json
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False


@dataclass
class MarketData:
    """시장 데이터 구조"""
    index_name: str
    current_value: float
    change_value: float
    change_rate: float
    timestamp: str


@dataclass
class StockItem:
    """개별 주식 데이터 구조"""
    rank: int
    name: str
    current_price: int
    change_rate: float
    category: str  # 'rise' or 'fall'


class StockDataCollector:
    """주식 데이터 수집 클래스"""
    
    def __init__(self):
        self.base_url = "https://m.stock.naver.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def collect_market_indices(self) -> List[MarketData]:
        """주요 지수 정보 수집"""
        try:
            url = f"{self.base_url}/index.naver"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            indices_data = []
            
            # 주요 지수 파싱 (코스피, 코스닥, 코스피200)
            index_names = ['KOSPI', 'KOSDAQ', 'KOSPI200']
            
            for idx_name in index_names:
                try:
                    # 실제 네이버 증권 모바일 구조에 맞춰 파싱
                    # 예시 데이터 구조 (실제 HTML 구조에 따라 조정 필요)
                    indices_data.append(MarketData(
                        index_name=idx_name,
                        current_value=2500.0,  # 실제 파싱 데이터로 대체
                        change_value=10.5,
                        change_rate=0.42,
                        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ))
                except Exception as e:
                    print(f"지수 {idx_name} 파싱 오류: {e}")
            
            return indices_data
        except Exception as e:
            print(f"시장 지수 수집 오류: {e}")
            return []
    
    def collect_top_stocks(self, category: str = 'rise') -> List[StockItem]:
        """상승/하락 상위 종목 수집"""
        try:
            # 상승률 상위 또는 하락률 상위
            url = f"{self.base_url}/sise/sise_rise.naver" if category == 'rise' else f"{self.base_url}/sise/sise_fall.naver"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            stocks = []
            
            # 실제 파싱 로직 (예시 데이터)
            sample_stocks = [
                StockItem(1, "삼성전자", 75000, 5.2, category),
                StockItem(2, "SK하이닉스", 142000, 4.8, category),
                StockItem(3, "현대차", 185000, 3.9, category),
                StockItem(4, "LG에너지솔루션", 420000, 3.5, category),
                StockItem(5, "POSCO홀딩스", 385000, 3.2, category),
            ]
            
            return sample_stocks[:10]  # 상위 10개
        except Exception as e:
            print(f"종목 정보 수집 오류: {e}")
            return []
    
    def collect_market_news(self) -> List[Dict[str, str]]:
        """시장 주요 뉴스 수집"""
        try:
            url = f"{self.base_url}/news/news_list.naver?mode=LSS2D&section_id=101&section_id2=258"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            news_list = []
            
            # 뉴스 파싱 (예시)
            sample_news = [
                {"title": "코스피, 외국인 매수에 상승 마감", "summary": "외국인 투자자들의 순매수에 힘입어 상승"},
                {"title": "반도체 업종 강세, SK하이닉스 급등", "summary": "AI 수요 증가로 반도체주 강세"},
                {"title": "2차전지 관련주 혼조세", "summary": "원자재 가격 변동에 따른 영향"},
            ]
            
            return sample_news[:5]
        except Exception as e:
            print(f"뉴스 수집 오류: {e}")
            return []


class DataProcessor:
    """데이터 정제 및 분석 클래스"""
    
    @staticmethod
    def process_market_data(indices: List[MarketData], 
                           rising_stocks: List[StockItem],
                           falling_stocks: List[StockItem]) -> Dict:
        """수집된 데이터를 DataFrame으로 정제"""
        
        # 지수 데이터프레임
        indices_df = pd.DataFrame([
            {
                '지수명': idx.index_name,
                '현재가': idx.current_value,
                '전일대비': idx.change_value,
                '등락률(%)': idx.change_rate
            } for idx in indices
        ])
        
        # 상승 종목 데이터프레임
        rising_df = pd.DataFrame([
            {
                '순위': stock.rank,
                '종목명': stock.name,
                '현재가': stock.current_price,
                '등락률(%)': stock.change_rate
            } for stock in rising_stocks
        ])
        
        # 하락 종목 데이터프레임
        falling_df = pd.DataFrame([
            {
                '순위': stock.rank,
                '종목명': stock.name,
                '현재가': stock.current_price,
                '등락률(%)': stock.change_rate
            } for stock in falling_stocks
        ])
        
        return {
            'indices': indices_df,
            'rising': rising_df,
            'falling': falling_df
        }
    
    @staticmethod
    def create_visualizations(data_dict: Dict, output_dir: str = '/mnt/user-data/outputs') -> List[str]:
        """데이터 시각화 생성"""
        os.makedirs(output_dir, exist_ok=True)
        image_paths = []
        
        # 1. 주요 지수 등락률 차트
        fig, ax = plt.subplots(figsize=(10, 6))
        indices_df = data_dict['indices']
        colors = ['green' if x > 0 else 'red' for x in indices_df['등락률(%)']]
        
        ax.barh(indices_df['지수명'], indices_df['등락률(%)'], color=colors, alpha=0.7)
        ax.set_xlabel('Change Rate (%)', fontsize=12)
        ax.set_title('Major Indices Performance', fontsize=14, fontweight='bold')
        ax.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        path1 = f"{output_dir}/indices_performance.png"
        plt.savefig(path1, dpi=150, bbox_inches='tight')
        plt.close()
        image_paths.append(path1)
        
        # 2. 상승 TOP 5 차트
        fig, ax = plt.subplots(figsize=(10, 6))
        rising_df = data_dict['rising'].head(5)
        
        ax.barh(rising_df['종목명'], rising_df['등락률(%)'], color='#2ecc71', alpha=0.7)
        ax.set_xlabel('Change Rate (%)', fontsize=12)
        ax.set_title('Top 5 Rising Stocks', fontsize=14, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        path2 = f"{output_dir}/top_rising.png"
        plt.savefig(path2, dpi=150, bbox_inches='tight')
        plt.close()
        image_paths.append(path2)
        
        # 3. 하락 TOP 5 차트
        fig, ax = plt.subplots(figsize=(10, 6))
        falling_df = data_dict['falling'].head(5)
        
        ax.barh(falling_df['종목명'], falling_df['등락률(%)'], color='#e74c3c', alpha=0.7)
        ax.set_xlabel('Change Rate (%)', fontsize=12)
        ax.set_title('Top 5 Falling Stocks', fontsize=14, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        path3 = f"{output_dir}/top_falling.png"
        plt.savefig(path3, dpi=150, bbox_inches='tight')
        plt.close()
        image_paths.append(path3)
        
        return image_paths
    
    @staticmethod
    def calculate_market_summary(data_dict: Dict) -> Dict:
        """시장 요약 통계 계산"""
        indices_df = data_dict['indices']
        
        summary = {
            'avg_index_change': indices_df['등락률(%)'].mean(),
            'max_rising_rate': data_dict['rising']['등락률(%)'].max() if not data_dict['rising'].empty else 0,
            'min_falling_rate': data_dict['falling']['등락률(%)'].min() if not data_dict['falling'].empty else 0,
            'rising_count': len(data_dict['rising']),
            'falling_count': len(data_dict['falling']),
        }
        
        return summary


class RAGNewsletterGenerator:
    """RAG 기반 뉴스레터 생성 클래스"""
    
    def __init__(self, api_key: str):
        """
        Args:
            api_key: Google Gemini API 키
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    def create_context(self, data_dict: Dict, summary: Dict, news_list: List[Dict]) -> str:
        """RAG 컨텍스트 생성"""
        context = f"""
# 주식 시장 데이터 컨텍스트 (기준: {datetime.now().strftime("%Y년 %m월 %d일")})

## 1. 주요 지수 현황
{data_dict['indices'].to_string(index=False)}

## 2. 상승률 상위 종목
{data_dict['rising'].to_string(index=False)}

## 3. 하락률 상위 종목
{data_dict['falling'].to_string(index=False)}

## 4. 시장 통계 요약
- 평균 지수 등락률: {summary['avg_index_change']:.2f}%
- 최대 상승률: {summary['max_rising_rate']:.2f}%
- 최대 하락률: {summary['min_falling_rate']:.2f}%
- 상승 종목 수: {summary['rising_count']}개
- 하락 종목 수: {summary['falling_count']}개

## 5. 주요 뉴스
"""
        for news in news_list:
            context += f"- {news['title']}: {news['summary']}\n"
        
        return context
    
    def generate_newsletter(self, context: str, user_query: str) -> str:
        """LLM을 활용한 뉴스레터 생성"""
        
        prompt = f"""
당신은 금융 전문 애널리스트입니다. 아래 데이터를 기반으로 전문적이면서도 이해하기 쉬운 주식 시장 뉴스레터를 작성해주세요.

사용자 질의: {user_query}

{context}

다음 형식으로 뉴스레터를 작성해주세요:

# 📈 오늘의 국내 주식 시장 리포트

## 🎯 시장 개요 (Market Overview)
주요 지수의 움직임과 전반적인 시장 분위기를 2-3문장으로 요약

## 📊 주요 지수 동향
각 지수별 상세 분석 (코스피, 코스닥 등)

## 🚀 주목할 상승 종목
상승률 상위 종목과 그 이유 분석

## 📉 하락 종목 분석
하락 종목의 원인과 시사점

## 💡 투자 인사이트
오늘 시장 데이터에서 얻을 수 있는 투자 시사점

## 📰 주요 뉴스 요약
시장에 영향을 준 주요 뉴스

---
*본 리포트는 {datetime.now().strftime("%Y년 %m월 %d일 %H:%M")} 기준으로 작성되었습니다.*
*투자 판단은 본인의 책임하에 이루어져야 합니다.*

전문적이면서도 친근한 톤으로 작성하되, 구체적인 데이터를 활용해주세요.
"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"뉴스레터 생성 중 오류 발생: {e}"


class StockNewsletterSystem:
    """통합 시스템 클래스"""
    
    def __init__(self, gemini_api_key: str):
        self.collector = StockDataCollector()
        self.processor = DataProcessor()
        self.generator = RAGNewsletterGenerator(gemini_api_key)
    
    def process_query(self, user_input: str) -> Dict:
        """사용자 쿼리 처리 메인 파이프라인"""
        
        # 키워드 검증
        keywords = ['오늘자', '국내', '시장', '주식']
        if not any(keyword in user_input for keyword in keywords):
            return {
                'success': False,
                'message': '올바른 키워드를 입력해주세요. 예: "오늘자 국내 시장"'
            }
        
        print("🔄 1단계: 데이터 수집 중...")
        # 1. 데이터 수집
        market_indices = self.collector.collect_market_indices()
        rising_stocks = self.collector.collect_top_stocks('rise')
        falling_stocks = self.collector.collect_top_stocks('fall')
        news_list = self.collector.collect_market_news()
        
        print("🔄 2단계: 데이터 정제 및 분석 중...")
        # 2. 데이터 정제
        processed_data = self.processor.process_market_data(
            market_indices, rising_stocks, falling_stocks
        )
        
        # 3. 통계 분석
        summary = self.processor.calculate_market_summary(processed_data)
        
        print("🔄 3단계: 시각화 생성 중...")
        # 4. 시각화
        image_paths = self.processor.create_visualizations(processed_data)
        
        print("🔄 4단계: RAG 기반 뉴스레터 생성 중...")
        # 5. RAG 컨텍스트 생성
        context = self.generator.create_context(processed_data, summary, news_list)
        
        # 6. LLM 뉴스레터 생성
        newsletter = self.generator.generate_newsletter(context, user_input)
        
        return {
            'success': True,
            'newsletter': newsletter,
            'data': processed_data,
            'summary': summary,
            'images': image_paths,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def save_newsletter(self, result: Dict, output_path: str = '/mnt/user-data/outputs/newsletter.md'):
        """뉴스레터를 파일로 저장"""
        if not result['success']:
            return
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result['newsletter'])
            f.write("\n\n---\n\n")
            f.write("## 📊 데이터 시각화\n\n")
            for img_path in result['images']:
                f.write(f"![Chart]({img_path})\n\n")
        
        print(f"✅ 뉴스레터가 저장되었습니다: {output_path}")


def main():
    """메인 실행 함수"""
    
    print("=" * 60)
    print("📈 주식 시장 RAG 기반 뉴스레터 시스템")
    print("=" * 60)
    
    # API 키 입력
    api_key = input("\n🔑 Gemini API 키를 입력해주세요: ").strip()
    
    if not api_key:
        print("❌ API 키가 필요합니다.")
        return
    
    # 시스템 초기화
    system = StockNewsletterSystem(api_key)
    
    while True:
        print("\n" + "-" * 60)
        user_input = input("💬 질의를 입력하세요 (종료: 'exit'): ").strip()
        
        if user_input.lower() in ['exit', 'quit', '종료']:
            print("👋 시스템을 종료합니다.")
            break
        
        if not user_input:
            continue
        
        # 쿼리 처리
        result = system.process_query(user_input)
        
        if result['success']:
            print("\n" + "=" * 60)
            print("✅ 뉴스레터 생성 완료!")
            print("=" * 60)
            print(result['newsletter'])
            
            # 파일 저장
            system.save_newsletter(result)
            
            print("\n📊 생성된 차트:")
            for img in result['images']:
                print(f"  - {img}")
        else:
            print(f"\n❌ {result['message']}")


if __name__ == "__main__":
    main()
