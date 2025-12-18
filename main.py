import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os

def scrape_monster_ball_mirrors():
    url = "https://yuyu-tei.jp/buy/poc/s/sv02a"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"}
    
    try:
        response = requests.get(url, headers=headers)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"Error fetching data: {e}")
        return

    card_data = []
    today = datetime.now().strftime('%Y-%m-%d')
    items = soup.find_all('div', class_='card_unit')

    for item in items:
        name_tag = item.find('h4', class_='name')
        full_name = name_tag.get_text(strip=True) if name_tag else ""
        
        # --- ここで「モンスターボール」だけをフィルタリング ---
        # 「モンスターボール柄」が含まれ、かつ「マスターボール柄」が含まれないものを抽出
        if "モンスターボール柄" in full_name:
            # 読みやすくするために名前を少し整える（オプション）
            display_name = full_name.replace("(モンスターボール柄/ミラー仕様)", "").strip()
            
            rarity_tag = item.find('span', class_='rarity')
            rarity = rarity_tag.get_text(strip=True) if rarity_tag else ""

            price_tag = item.find('b', class_='price')
            price_text = price_tag.get_text(strip=True).replace('円', '').replace(',', '') if price_tag else "0"
            
            card_data.append({
                "date": today,
                "card_name": display_name,
                "rarity": rarity,
                "price": int(price_text)
            })

    if not card_data:
        print("モンスターボールミラーのデータが見つかりませんでした。")
        return

    new_df = pd.DataFrame(card_data)
    file_path = 'monster_ball_prices.csv' # 専用のファイル名に

    # 既存データがあれば追記、なければ新規
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        old_df = pd.read_csv(file_path)
        combined_df = pd.concat([old_df, new_df], ignore_index=True)
    else:
        combined_df = new_df

    combined_df.to_csv(file_path, index=False, encoding='utf-8')
    print(f"{today}分: モンスターボールミラー {len(new_df)}件を保存しました。")

if __name__ == "__main__":
    scrape_monster_ball_mirrors()
