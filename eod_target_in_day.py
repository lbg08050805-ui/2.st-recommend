# 파일명: d:/pgm/eod_target/get_pure_leaders.py
# 실행환경: Python 3.11

import FinanceDataReader as fdr
import pandas as pd
from datetime import datetime
import os

def get_market_leaders_final(target_date, top_n=200, min_amount_billion=500):
    try:
        # [상무님 SOP] 데이터 분석 모드 가동 로그
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] {target_date} 기준(최신 시세) 데이터 분석 가동...")
        
        # 1. 데이터 수집: StockListing은 항상 최신(Latest) 데이터를 가져옵니다.
        df = fdr.StockListing('KRX')
        
        # 2. 컬럼명 매핑 (상무님 환경의 오타 'ChagesRatio' 포함 완벽 대응)
        col_map = {
            '등락률': ['ChagesRatio', 'ChangesRatio', 'ChgRate', 'ChangeRate', '등락률'],
            '종목명': ['Name', '종목명'],
            '거래대금': ['Amount', '거래대금'],
            '종목코드': ['Code', 'ISU_CD', '종목코드'],
            '현재가': ['Close', '현재가', '종가']
        }
        
        final_cols = {}
        for key, candidates in col_map.items():
            for cand in candidates:
                if cand in df.columns:
                    final_cols[key] = cand
                    break

        # 3. 데이터 전처리 및 엄격한 필터링 (거래대금 500억 이상)
        df['거래대금_억'] = df[final_cols['거래대금']] / 100_000_000
        
        # 등락률 > 0 및 상무님의 '데이터 순수성' 필터(500억) 적용
        filtered = df[(df[final_cols['등락률']] > 0) & (df['거래대금_억'] >= min_amount_billion)].copy()
        
        # 4. 정렬 및 상위 종목 추출
        sorted_df = filtered.sort_values(by=final_cols['등락률'], ascending=False)
        leaders = sorted_df[[final_cols['종목코드'], final_cols['종목명'], final_cols['현재가'], final_cols['등락률'], '거래대금_억']].head(top_n)
        leaders.columns = ['종목코드', '종목명', '현재가', '등락률', '거래대금_억']
        
        # 5. 저장 (입력하신 날짜로 파일명 생성)
        save_path = "d:/pgm/eod_target/"
        if not os.path.exists(save_path):
            os.makedirs(save_path)
            
        file_name = f"{save_path}PureLeaders_{target_date}.csv"
        leaders.to_csv(file_name, index=False, encoding='utf-8-sig')
        
        print("-" * 50)
        print(f"✅ 분석 완료! 거래대금 500억 이상 [ {len(leaders)} ]개 종목 식별.")
        print(f"💾 결과 저장: {file_name}")
        print("-" * 50)
        
        return leaders

    except Exception as e:
        print(f"❌ 분석 실패: {e}")
        return None

if __name__ == "__main__":
    # 오늘 날짜를 기본값으로 설정
    default_today = datetime.now().strftime('%Y%m%d')
    
    print(f"--- [상무님 전용 주도주 추출기] ---")
    input_date = input(f"분석 기준일 입력 (예: 20260117) [기본값: {default_today}]: ").strip()
    
    # 입력값이 없으면 오늘 날짜 사용, 날짜는 파일명 관리용으로 활용됩니다.
    target_date = input_date if input_date else default_today
    
    # 상무님의 승률 70% 전략: 거래대금 500억 필터 고정
    result = get_market_leaders_final(target_date, top_n=200, min_amount_billion=500)
    
    if result is not None and not result.empty:
        print(result.head(10))
        