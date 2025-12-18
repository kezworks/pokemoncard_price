function scrapeKaunabel() {
  // カーナベルの「151」買取ページURL（必要に応じて調整してください）
  const url = "https://www.ka-nabell.com/?genre=7&category=235&rare=62"; 
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getActiveSheet();
  
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(["日付", "カード名", "買取価格"]);
  }

  const response = UrlFetchApp.fetch(url, {
    "headers": { "User-Agent": "Mozilla/5.0" },
    "muteHttpExceptions": true
  });
  
  const html = response.getContentText();
  const today = Utilities.formatDate(new Date(), "JST", "yyyy-MM-dd");

  // カーナベルの構造に合わせて抽出（商品リストの塊を取得）
  // <li>タグや特定のclassで分割
  const items = html.split('<div class="item_card">');
  let count = 0;

  for (let i = 1; i < items.length; i++) {
    const item = items[i];
    
    // カード名と価格を抽出
    // カーナベルは名前が「p class="name"」、価格が「span class="price"」などの傾向があります
    const nameMatch = item.match(/<p class="name">([\s\S]*?)<\/p>/i);
    const priceMatch = item.match(/<span class="price">([\s\S]*?)<\/span>/i);

    if (nameMatch && priceMatch) {
      let name = nameMatch[1].replace(/<[^>]*>/g, "").trim();
      let price = priceMatch[1].replace(/[^0-9]/g, "");

      // モンスターボール柄を判別
      if (name.includes("モンスターボール")) {
        sheet.appendRow([today, name, parseInt(price)]);
        count++;
      }
    }
  }
  
  Logger.log(count + "件のデータをカーナベルから取得しました！");
}
