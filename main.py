import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os

def scrape_and_append():
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
        name = name_tag.get_text(strip=True) if name_tag else "不明"
        
        rarity_tag = item.find('span', class_='rarity')
        rarity = rarity_tag.get_text(strip=True) if rarity_tag else ""

        price_tag = item.find('b', class_='price')
        price_text = price_tag.get_text(strip=True).replace('円', '').replace(',', '') if price_tag else "0"
        
        card_data.append({
            "date": today,
            "name": name,
            "rarity": rarity,
            "price": int(price_text)
        })

    new_df = pd.DataFrame(card_data)
    file_path = 'data.csv'

    # --- 修正ポイント：ファイルの存在チェックと中身のチェック ---
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        try:
            old_df = pd.read_csv(file_path)
            combined_df = pd.concat([old_df, new_df], ignore_index=True)
        except Exception as e:
            print(f"既存ファイルの読み込みに失敗したため新規作成します: {e}")
            combined_df = new_df
    else:
        # ファイルが存在しないか、サイズが0の場合は新規作成
        combined_df = new_df

    # 保存（BOMなしUTF-8で保存し、GitHubとの相性を高める）
    combined_df.to_csv(file_path, index=False, encoding='utf-8')
    print(f"{today}分のデータを保存しました。合計: {len(combined_df)}件")

if __name__ == "__main__":
    scrape_and_append()
