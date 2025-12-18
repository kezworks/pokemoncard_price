import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time

def scrape_yuyutei_buy_prices(url):
    # 1. サイトにアクセス
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        # 文字化け対策
        response.encoding = response.apparent_encoding
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 2. カード情報を格納するリスト
    card_data = []
    today = datetime.now().strftime('%Y-%m-%d')

    # 3. 各カードのブロック（card_unit）をループ処理
    # 遊々亭の買取ページは主に 'col-xs-6' や 'card_unit' クラスのdivにデータがあります
    items = soup.find_all('div', class_='card_unit')

    for item in items:
        # カード名
        name_tag = item.find('h4', class_='name')
        name = name_tag.get_text(strip=True) if name_tag else "不明"
        
        # レアリティ（h4の中のレアリティ部分や別途タグから取得）
        rarity_tag = item.find('span', class_='rarity')
        rarity = rarity_tag.get_text(strip=True) if rarity_tag else ""

        # 価格
        price_tag = item.find('b', class_='price')
        price_text = price_tag.get_text(strip=True).replace('円', '').replace(',', '') if price_tag else "0"
        
        card_data.append({
            "日付": today,
            "カード名": name,
            "レアリティ": rarity,
            "買取価格(円)": int(price_text)
        })

    # 4. Pandasでデータフレーム化して保存
    df = pd.DataFrame(card_data)
    
    # ファイル名に日付を入れて保存（例: yuyutei_2023-10-27.csv）
    file_name = f"yuyutei_prices_{today}.csv"
    df.to_csv(file_name, index=False, encoding='utf-8-sig')
    
    print(f"集計完了！ {len(df)} 件のデータを '{file_name}' に保存しました。")
    return df

# 実行
target_url = "https://yuyu-tei.jp/buy/poc/s/sv02a"
scrape_yuyutei_buy_prices(target_url)
