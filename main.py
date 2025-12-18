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
        # ステルス性を高めるための設定
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        # 自動操作であることを隠すためのJavaScript
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print(f"アクセス中: {url}")
        try:
            # タイムアウトを長めに設定
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            # ページが完全に読み込まれるまで少し待つ
            page.wait_for_timeout(5000)
            
            # デバッグ用：画面がどう見えているか保存する
            page.screenshot(path="debug_screenshot.png")
            print("デバッグ用のスクリーンショットを保存しました。")
            
            content = page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # クラス名が動的に変わっている可能性を考慮し、より広い範囲で検索
            items = soup.find_all('div', class_='card_unit')
            print(f"検出されたユニット数: {len(items)}")

            for item in items:
                name_elem = item.find('h4', class_='name')
                if name_elem and "モンスターボール" in name_elem.get_text():
                    full_text = name_elem.get_text(strip=True)
                    display_name = full_text.split('(')[0].strip()
                    price_tag = item.find('b', class_='price')
                    price = price_tag.get_text(strip=True).replace('円', '').replace(',', '') if price_tag else "0"
                    
                    card_data.append({
                        "date": today,
                        "card_name": display_name,
                        "price": int(price)
                    })
        except Exception as e:
            print(f"エラー発生: {e}")
        finally:
            browser.close()

    if not card_data:
        print("データが取得できませんでした。")
        return

    # 保存処理（前回と同じ）
    df = pd.DataFrame(card_data)
    file_path = 'monster_ball_prices.csv'
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        old_df = pd.read_csv(file_path)
        df = pd.concat([old_df, df], ignore_index=True)
    df.to_csv(file_path, index=False, encoding='utf-8')
    print(f"成功！ {len(card_data)}件保存しました。")

if __name__ == "__main__":
    scrape_with_browser()
