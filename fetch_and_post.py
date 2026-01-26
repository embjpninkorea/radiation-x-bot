# fetch_and_post.py
import os
import requests
from bs4 import BeautifulSoup
import tweepy
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# ① ②：福島データ
def get_fukushima(station_no):
    url = f"http://www.atom-moc.pref.fukushima.jp/public/table/Table.html?stationNo={station_no}&type=0"
    r = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")

    table = soup.find("table")
    if table is None:
        return "取得失敗（tableなし）"

    tds = table.find_all("td")
    if not tds:
        return "取得失敗（tdなし）"

    return tds[-1].text.strip()

# ③：新宿放射線
def get_nsr_shinjuku():
    # 東京都（新宿）の最新値CSV
    url = "https://radioactivity.nsr.go.jp/data/13/13000/13000_01.csv"
    r = requests.get(url, headers=HEADERS, timeout=15)

    if r.status_code != 200:
        return "取得失敗"

    lines = r.text.splitlines()
    if len(lines) < 2:
        return "取得失敗"

    # 最終行の線量値（µSv/h）
    last = lines[-1].split(",")
    return last[-1]

# ④：Guro
def get_iernet_guro():
    # Seoul 地域の放射線量 CSV
    url = "https://iernet.kins.re.kr/data/iernet_radiation_seoul.csv"
    r = requests.get(url, headers=HEADERS, timeout=15)

    if r.status_code != 200:
        return "取得失敗"

    lines = r.text.splitlines()
    if len(lines) < 2:
        return "取得失敗"

    header = lines[0].split(",")
    guro_index = None

    # ヘッダから Guro 列を探す
    for i, col in enumerate(header):
        if "Guro" in col:
            guro_index = i
            break

    if guro_index is None:
        return "取得失敗（Guro列なし）"

    # 最新行
    last = lines[-1].split(",")
    return last[guro_index]

if __name__ == "__main__":
    # 取得
    a301 = get_fukushima("301")
    a353 = get_fukushima("353")
    shinjuku = get_nsr_shinjuku()
    guro = get_iernet_guro()

    message = (
        f"放射線量まとめ\n"
        f"301: {a301}\n"
        f"353: {a353}\n"
        f"新宿: {shinjuku}\n"
        f"Guro: {guro}\n"
    )

    # X 投稿
client = tweepy.Client(
    consumer_key=os.environ["CONSUMER_KEY"],
    consumer_secret=os.environ["CONSUMER_SECRET"],
    access_token=os.environ["ACCESS_TOKEN"],
    access_token_secret=os.environ["ACCESS_SECRET"]
)

client.create_tweet(text=message)