import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os

def scrape_monster_ball_mirrors():
    url = "https://yuyu-tei.jp/buy/poc/s/sv02a"
    # ブラウザからのアクセスに見せかけるための魔法の言葉
headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
        "Referer": "https://yuyu-tei.jp/",
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"通信エラー: {e}")
        return

    card_data = []
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 遊々亭の現在のHTML構造に合わせてセレクタを変更
    # 買取価格の各ユニットは 'div.card_unit' または特定の構造の中にある
    items = soup.find_all('div', class_='card_unit')

    if not items:
        print("警告: 'card_unit' が一つも見つかりませんでした。")
        # サイトの中身を少しだけ表示してデバッグ
        print("取得したテキストの冒頭:", soup.text[:200].replace('\n', ' '))
        return

    for item in items:
        # とにかく全てのテキストを結合してチェック
        full_text = item.get_text()
        
        # 「ミラー」や「モンスターボール」が含まれているか判定
        if "モンスターボール" in full_text or "ミラー" in full_text:
            name_tag = item.find('h4')
            name = name_tag.get_text(strip=True) if name_tag else "不明"
            
            price_tag = item.find('b', class_='price')
            price = price_tag.get_text(strip=True).replace('円', '').replace(',', '') if price_tag else "0"
            
            card_data.append({
                "date": today,
                "card_name": name,
                "price": int(price)
            })

    if not card_data:
        print("カードは見つかりましたが、キーワードに一致するものがありませんでした。")
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
    print(f"{today}分: {len(new_df)}件を保存しました！")

if __name__ == "__main__":
    scrape_monster_ball_mirrors()
