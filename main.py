import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os

def scrape_and_append():
    url = "https://yuyu-tei.jp/buy/poc/s/sv02a"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(url, headers=headers)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"Error fetching data: {e}")
        return

    card_data = []
    # 日本時間に合わせた日付取得（サーバーは海外にあるため）
    today = datetime.now().strftime('%Y-%m-%d')
    items = soup.find_all('div', class_='card_unit')

    for item in items:
        name = item.find('h4', class_='name').get_text(strip=True) if item.find('h4', class_='name') else "不明"
        rarity = item.find('span', class_='rarity').get_text(strip=True) if item.find('span', class_='rarity') else ""
        price_text = item.find('b', class_='price').get_text(strip=True).replace('円', '').replace(',', '') if item.find('b', class_='price') else "0"
        
        card_data.append({
            "date": today,
            "name": name,
            "rarity": rarity,
            "price": int(price_text)
        })

    new_df = pd.DataFrame(card_data)

    # 既存のデータがあれば読み込んで合体させる
    file_path = 'data.csv'
    if os.path.exists(file_path):
        old_df = pd.read_csv(file_path)
        combined_df = pd.concat([old_df, new_df], ignore_index=True)
    else:
        combined_df = new_df

    # 保存
    combined_df.to_csv(file_path, index=False, encoding='utf-8', sep=',')
    print(f"{today}分のデータを追記しました。合計: {len(combined_df)}行")

if __name__ == "__main__":
    scrape_and_append()
