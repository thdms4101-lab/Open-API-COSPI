import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="코스피200 주식 추천 시스템",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    .info-box {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2196F3;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3e0;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ff9800;
        margin: 1rem 0;
    }
    .stCheckbox {
        margin: 0.3rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# KOSPI 200 stock codes (top 20 for demo)
KOSPI200_CODES = [
    "005930",  # 삼성전자
    "000660",  # SK하이닉스
    "035720",  # 카카오
    "005380",  # 현대차
    "051910",  # LG화학
    "035420",  # NAVER
    "006400",  # 삼성SDI
    "068270",  # 셀트리온
    "207940",  # 삼성바이오로직스
    "005490",  # POSCO홀딩스
    "012330",  # 현대모비스
    "028260",  # 삼성물산
    "066570",  # LG전자
    "003670",  # 포스코퓨처엠
    "096770",  # SK이노베이션
    "000270",  # 기아
    "017670",  # SK텔레콤
    "034730",  # SK
    "018260",  # 삼성에스디에스
    "032830",  # 삼성생명
]

def get_access_token(app_key, app_secret):
    """Get OAuth access token from KIS API"""
    url = "https://openapi.koreainvestment.com:9443/oauth2/tokenP"
    headers = {"content-type": "application/json"}
    body = {
        "grant_type": "client_credentials",
        "appkey": app_key,
        "appsecret": app_secret
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(body))
        if response.status_code == 200:
            return response.json()['access_token']
        else:
            st.error(f"토큰 발급 실패: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"API 연결 오류: {e}")
        return None

@st.cache_data(ttl=300)
def get_stock_price(app_key, app_secret, stock_code):
    """Get real-time stock price from KIS API"""
    access_token = get_access_token(app_key, app_secret)
    if not access_token:
        return None
    
    url = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/quotations/inquire-price"
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {access_token}",
        "appkey": app_key,
        "appsecret": app_secret,
        "tr_id": "FHKST01010100"
    }
    params = {
        "fid_cond_mrkt_div_code": "J",
        "fid_input_iscd": stock_code
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()['output']
            return {
                "code": stock_code,
                "name": data['hts_kor_isnm'],
                "price": int(data['stck_prpr']),
                "change": float(data['prdy_ctrt']),
                "volume": int(data['acml_vol']),
                "market_cap": int(data.get('hts_avls', 0)) // 100000000  # Convert to 억원
            }
        return None
    except Exception as e:
        return None

@st.cache_data(ttl=300)
def get_real_time_stock_data(app_key, app_secret, use_real_api=False):
    """Get KOSPI 200 stock data - real API or sample data"""
    
    if use_real_api and app_key and app_secret:
        # Real API mode
        stocks = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, code in enumerate(KOSPI200_CODES):
            status_text.text(f"데이터 로딩 중... {i+1}/{len(KOSPI200_CODES)}")
            stock_data = get_stock_price(app_key, app_secret, code)
            if stock_data:
                stocks.append(stock_data)
            progress_bar.progress((i + 1) / len(KOSPI200_CODES))
        
        progress_bar.empty()
        status_text.empty()
        
        if stocks:
            return pd.DataFrame(stocks)
    
    # Sample data mode (fallback or demo)
    stocks = [
        {"code": "005930", "name": "삼성전자", "price": 71000, "change": 2.5, "volume": 15000000, "market_cap": 423000000},
        {"code": "000660", "name": "SK하이닉스", "price": 135000, "change": 3.2, "volume": 5000000, "market_cap": 98000000},
        {"code": "035720", "name": "카카오", "price": 52000, "change": -1.5, "volume": 8000000, "market_cap": 23000000},
        {"code": "005380", "name": "현대차", "price": 195000, "change": 1.8, "volume": 2000000, "market_cap": 41000000},
        {"code": "051910", "name": "LG화학", "price": 425000, "change": 2.1, "volume": 1500000, "market_cap": 30000000},
        {"code": "035420", "name": "NAVER", "price": 215000, "change": -0.5, "volume": 3000000, "market_cap": 35000000},
        {"code": "006400", "name": "삼성SDI", "price": 478000, "change": 4.2, "volume": 800000, "market_cap": 33000000},
        {"code": "068270", "name": "셀트리온", "price": 168000, "change": 1.5, "volume": 4000000, "market_cap": 22000000},
        {"code": "207940", "name": "삼성바이오로직스", "price": 825000, "change": 0.8, "volume": 250000, "market_cap": 59000000},
        {"code": "005490", "name": "POSCO홀딩스", "price": 385000, "change": 2.8, "volume": 900000, "market_cap": 32000000},
    ]
    return pd.DataFrame(stocks)

def calculate_stock_score(stock, criteria):
    """Calculate recommendation score based on criteria"""
    score = 0
    details = []
    
    # 상승 추세 진입 (+4점)
    if criteria['uptrend'] and stock['change'] > 0:
        score += 4
        details.append("상승 추세 진입")
    
    # 강한 상승세 (+2~3점)
    if criteria['strong_uptrend']:
        if stock['change'] > 3:
            score += 3
            details.append("강한 상승세 (3점)")
        elif stock['change'] > 1.5:
            score += 2
            details.append("강한 상승세 (2점)")
    
    # 거래 증가 (+1~2점)
    if criteria['volume_increase']:
        if stock['volume'] > 5000000:
            score += 2
            details.append("거래 증가 (2점)")
        elif stock['volume'] > 2000000:
            score += 1
            details.append("거래 증가 (1점)")
    
    # 적정 가격대 (+1.5점)
    if criteria['price_range']:
        if 50000 <= stock['price'] <= 500000:
            score += 1.5
            details.append("적정 가격대")
    
    # 어제 대비 상승 (+1점)
    if criteria['daily_gain'] and stock['change'] > 0:
        score += 1
        details.append("어제 대비 상승")
    
    # 가격 변동 큼 (-0.5~-1점)
    if criteria['high_volatility']:
        if abs(stock['change']) > 5:
            score -= 1
            details.append("가격 변동 큼 (-1점)")
        elif abs(stock['change']) > 3:
            score -= 0.5
            details.append("가격 변동 큼 (-0.5점)")
    
    return score, details

def display_stock_card(stock, score, details):
    """Display individual stock recommendation card"""
    change_color = "green" if stock['change'] >= 0 else "red"
    change_icon = "📈" if stock['change'] >= 0 else "📉"
    
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        st.markdown(f"### {stock['name']} ({stock['code']})")
        st.markdown(f"**점수:** {score:.1f}점")
    
    with col2:
        st.metric("현재가", f"₩{stock['price']:,}", f"{stock['change']:+.2f}%")
    
    with col3:
        st.metric("거래량", f"{stock['volume']:,}")
    
    with col4:
        st.metric("시가총액", f"{stock['market_cap']:,}억")
    
    if details:
        st.markdown(f"**추천 이유:** {', '.join(details)}")

def main():
    # Header
    st.markdown("# 📈 코스피200 주식 추천 시스템")
    st.markdown("<div class='subtitle'>초보자도 쉽게 이해하는 주식 분석 도구</div>", 
                unsafe_allow_html=True)
    
    # Sidebar - Settings
    with st.sidebar:
        st.markdown("## ⚙️ 설정")
        
        with st.expander("🔑 API 인증 정보", expanded=False):
            st.info("한국투자증권 API를 사용하려면 아래 정보를 입력하세요.")
            app_key = st.text_input("APP KEY", type="password", 
                                   help="한국투자증권 개발자센터에서 발급받은 APP KEY")
            app_secret = st.text_input("APP SECRET", type="password",
                                      help="한국투자증권 개발자센터에서 발급받은 APP SECRET")
            account_number = st.text_input("계좌번호", 
                                          help="8자리 계좌번호")
            
            use_real_api = st.checkbox("실시간 API 사용", value=False,
                                      help="체크하면 실제 API를 호출합니다 (API 키 필요)")
            
            if app_key and app_secret:
                st.success("✅ API 인증 정보가 입력되었습니다")
                if use_real_api:
                    st.info("🔄 실시간 데이터를 사용합니다")
                else:
                    st.warning("📊 샘플 데이터를 사용합니다")
            else:
                st.warning("⚠️ 실제 데이터를 받으려면 API 정보를 입력하세요")
                use_real_api = False
        
        st.markdown("---")
        
        st.markdown("## 📊 분석 설정")
        
        # 주천 종목 개수
        st.markdown("### 추천받을 종목 개수")
        num_recommendations = st.slider("", 1, 20, 5, 
                                       help="추천받고 싶은 종목의 개수를 선택하세요")
        
        # 최소 거래 규모
        st.markdown("### 최소 거래 규모 (억원)")
        min_volume = st.slider("", 10, 1000, 100,
                              help="최소 거래 규모를 설정하세요")
        
        st.markdown("---")
        st.markdown("### 데이터 새로고침")
        if st.button("🔄 데이터 업데이트", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    # Main content
    st.markdown("<div class='info-box'>", unsafe_allow_html=True)
    st.markdown("👉 **왼쪽 메뉴에서 API 정보를 입력하고 '분석 시작하기' 버튼을 눌러주세요!**")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Analysis criteria section
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("## 📌 이 도구는 무엇인가요?")
        st.markdown("""
        코스피200 종목을 자동으로 분석하여 **매수하기 좋은 종목을 추천**해드립니다.
        
        **분석 항목:**
        - ✅ **상승 추세**: 주가가 올라가는 흐름인지 확인
        - ⚡ **상승 속도**: 최근 며칠간 얼마나 빠르게 올랐는지
        - 💰 **거래 활발도**: 사람들이 얼마나 많이 거래하는지
        - 📊 **적정 가격**: 너무 오르거나 떨어지지 않았는지
        - 🔔 **안정성**: 가격 변동이 크지 않은지
        """)
    
    with col2:
        st.markdown("## 💯 추천 점수는 어떻게 계산하나요?")
        st.markdown("각 항목별로 점수를 부여하여 합산합니다:")
        
        criteria_df = pd.DataFrame({
            "항목": ["상승 추세 진입", "강한 상승세", "거래 증가", "적정 가격대", "어제 대비 상승", "가격 변동 큼"],
            "점수": ["+4점", "+2~3점", "+1~2점", "+1.5점", "+1점", "-0.5~-1점"]
        })
        st.dataframe(criteria_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Filter criteria
    st.markdown("## 🎯 분석 항목 선택")
    st.markdown("원하는 분석 조건을 체크하세요:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        uptrend = st.checkbox("✅ 상승 추세 진입", value=True, 
                             help="주가가 올라가는 흐름인지 확인")
        strong_uptrend = st.checkbox("⚡ 강한 상승세", value=True,
                                    help="최근 며칠간 얼마나 빠르게 올랐는지")
    
    with col2:
        volume_increase = st.checkbox("💰 거래 증가", value=True,
                                     help="사람들이 얼마나 많이 거래하는지")
        price_range = st.checkbox("📊 적정 가격대", value=True,
                                 help="너무 오르거나 떨어지지 않았는지")
    
    with col3:
        daily_gain = st.checkbox("🔔 어제 대비 상승", value=True,
                                help="전일 대비 상승했는지")
        high_volatility = st.checkbox("⚠️ 가격 변동 큼 (감점)", value=False,
                                     help="가격 변동이 큰 종목 감점")
    
    criteria = {
        'uptrend': uptrend,
        'strong_uptrend': strong_uptrend,
        'volume_increase': volume_increase,
        'price_range': price_range,
        'daily_gain': daily_gain,
        'high_volatility': high_volatility
    }
    
    st.markdown("---")
    
    # Analyze button
    if st.button("🚀 분석 시작하기", type="primary", use_container_width=True):
        with st.spinner("📊 종목을 분석하고 있습니다..."):
            # Get stock data
            stocks_df = get_real_time_stock_data(
                app_key if 'app_key' in locals() else None,
                app_secret if 'app_secret' in locals() else None,
                use_real_api if 'use_real_api' in locals() else False
            )
            
            # Calculate scores
            scores = []
            for _, stock in stocks_df.iterrows():
                score, details = calculate_stock_score(stock, criteria)
                scores.append({
                    'stock': stock,
                    'score': score,
                    'details': details
                })
            
            # Sort by score
            scores.sort(key=lambda x: x['score'], reverse=True)
            
            # Display results
            st.markdown("## 🏆 추천 종목 결과")
            
            if scores[0]['score'] > 0:
                st.success(f"✅ {num_recommendations}개의 추천 종목을 찾았습니다!")
            else:
                st.warning("⚠️ 현재 조건에 맞는 강력한 추천 종목이 없습니다. 조건을 조정해보세요.")
            
            # Display top recommendations
            for i, item in enumerate(scores[:num_recommendations], 1):
                st.markdown(f"### {i}위. 추천 점수: {item['score']:.1f}점")
                display_stock_card(item['stock'], item['score'], item['details'])
                st.markdown("---")
            
            # Summary statistics
            st.markdown("## 📈 분석 요약")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("분석 종목 수", len(stocks_df))
            with col2:
                positive_stocks = sum(1 for s in scores if s['score'] > 0)
                st.metric("추천 가능 종목", positive_stocks)
            with col3:
                avg_score = sum(s['score'] for s in scores) / len(scores)
                st.metric("평균 점수", f"{avg_score:.2f}")
            with col4:
                max_score = max(s['score'] for s in scores)
                st.metric("최고 점수", f"{max_score:.1f}")
            
            # Score distribution chart
            st.markdown("### 점수 분포")
            score_data = pd.DataFrame([
                {'종목': s['stock']['name'], '점수': s['score']} 
                for s in scores
            ])
            
            fig = px.bar(score_data, x='종목', y='점수', 
                        title='종목별 추천 점수',
                        color='점수',
                        color_continuous_scale='RdYlGn')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    # Warning box
    st.markdown("<div class='warning-box'>", unsafe_allow_html=True)
    st.markdown("""
    **⚠️ 투자 유의사항**
    - 이 도구는 참고용이며, 투자 결정은 본인의 책임입니다
    - 과거 데이터는 미래 수익을 보장하지 않습니다
    - 분산 투자를 권장합니다
    - 손실 가능성을 항상 고려하세요
    """)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>
    📊 코스피200 주식 추천 시스템 | 데이터: 한국투자증권 API (샘플 데이터 표시 중)
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
