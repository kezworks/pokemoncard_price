import os
import pandas as pd
from datetime import datetime
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def scrape_with_browser():
    url = "https://yuyu-tei.jp/buy/poc/s/sv02a"
    today = datetime.now().strftime('%Y-%m-%d')
    card_data = []

    with sync_playwright() as p:
        # ブラウザを起動（headless=Trueで画面なし実行）
        browser = p.chromium.launch(headless=True)
        # 人間味を出すためにユーザーエージェントを設定
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        print(f"アクセス中: {url}")
        # ページ読み込み完了まで待機
        page.goto(url, wait_until="networkidle")
        
        # 念のため少し待つ（JavaScriptの実行待ち）
        page.wait_for_timeout(3000)

        # ページのHTMLを取得
        content = page.content()
        soup = BeautifulSoup(content, 'html.parser')
        
        items = soup.select('div.card_unit')
        print(f"検出されたユニット数: {len(items)}")

        for item in items:
            name_elem = item.find('h4', class_='name')
            if not name_elem: continue
            
            full_text = name_elem.get_text(strip=True)
            
            # モンスターボールミラーを抽出
            if "モンスターボール" in full_text:
                display_name = full_text.split('(')[0].strip()
                price_tag = item.find('b', class_='price')
                price = price_tag.get_text(strip=True).replace('円', '').replace(',', '') if price_tag else "0"
                
                card_data.append({
                    "date": today,
                    "card_name": display_name,
                    "price": int(price)
                })
        
        browser.close()

    if not card_data:
        print("データが見つかりませんでした。")
        return

    # 保存処理
    df = pd.DataFrame(card_data)
    file_path = 'monster_ball_prices.csv'
    
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        old_df = pd.read_csv(file_path)
        df = pd.concat([old_df, df], ignore_index=True)

    df.to_csv(file_path, index=False, encoding='utf-8')
    print(f"成功！ {len(card_data)}件のデータを保存しました。")

if __name__ == "__main__":
    scrape_with_browser()
