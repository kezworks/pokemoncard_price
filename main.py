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
    
    # 全てのカードが入っているボックスを取得
    items = soup.select('div.card_unit')

    for item in items:
        # カード名と詳細テキストをまとめて取得
        name_elem = item.find('h4', class_='name')
        if not name_elem:
            continue
            
        full_text = name_elem.get_text(strip=True)
        
        # 「モンスターボール」というキーワードが含まれているかチェック
        if "モンスターボール" in full_text:
            # 表示をスッキリさせる（ミラーの記述を消す）
            display_name = full_text.split('(')[0].strip()
            
            # 価格の取得
            price_tag = item.find('b', class_='price')
            price_text = price_tag.get_text(strip=True).replace('円', '').replace(',', '') if price_tag else "0"
            
            card_data.append({
                "date": today,
                "card_name": display_name,
                "price": int(price_text)
            })

    if not card_data:
        # 見つからなかった場合、サイトの構造が変わった可能性があるのでHTMLを少し表示して確認
        print("データが見つかりませんでした。サイトの構成を確認してください。")
        return

    # 保存処理
    new_df = pd.DataFrame(card_data)
    file_path = 'monster_ball_prices.csv'
    
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        old_df = pd.read_csv(file_path)
        combined_df = pd.concat([old_df, new_df], ignore_index=True)
    else:
        combined_df = new_df

    combined_df.to_csv(file_path, index=False, encoding='utf-8')
    print(f"{today}分: モンスターボールミラー {len(new_df)}件を保存しました！")

if __name__ == "__main__":
    scrape_monster_ball_mirrors()
