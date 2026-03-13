import streamlit as st
import yfinance as yf
import FinanceDataReader as fdr
import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime, timedelta

# 파일 경로 자동 인식 (향후 로컬 엑셀 연동 대비)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. 웹 화면 기본 설정 및 여백 압축
st.set_page_config(layout="wide", page_title="일일 지표 대시보드")
st.markdown("""
<style>
    .block-container { padding-top: 2rem; padding-bottom: 1rem; }
    h3 { padding-bottom: 0rem !important; margin-bottom: -0.5rem !important; }
    hr { margin-top: 0.5rem; margin-bottom: 0.5rem; }
    div[data-testid="metric-container"] { margin-bottom: -0.5rem; }
</style>
""", unsafe_allow_html=True)

st.title("📊 나의 실시간 금융 지표 대시보드")

# --- 데이터 수집 함수 모음 ---

def get_yf_data(ticker):
    try:
        data = yf.Ticker(ticker)
        hist = data.history(period="5d")
        if len(hist) >= 2:
            return hist['Close'].iloc[-1], hist['Close'].iloc[-1] - hist['Close'].iloc[-2]
        return 0, 0
    except:
        return 0, 0

def get_fred_data(ticker):
    try:
        start_date = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
        df = fdr.DataReader(f'FRED:{ticker}', start=start_date)
        df = df.dropna()
        if len(df) >= 2:
            curr = float(df.iloc[-1].values[0])
            prev = float(df.iloc[-2].values[0])
            return curr, curr - prev
        return 0, 0
    except:
        return 0, 0

def get_krx_gold():
    try:
        url = "https://finance.naver.com/marketindex/"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        target = soup.select_one('.gold_domestic')
        price_str = target.select_one('.value').text
        price = float(price_str.replace(',', ''))
        
        change_str = target.select_one('.change').text
        change = float(change_str.replace(',', ''))
        
        blind_str = target.select_one('.blind').text
        if "하락" in blind_str:
            change = -change
            
        return price, change
    except:
        return 0, 0

def get_fear_and_greed():
    try:
        url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Referer': 'https://edition.cnn.com/'
        }
        res = requests.get(url, headers=headers)
        data = res.json()
        score = int(data['fear_and_greed']['score'])
        rating = data['fear_and_greed']['rating']
        return score, rating
