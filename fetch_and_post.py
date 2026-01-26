# fetch_and_post.py
import os
import requests
from bs4 import BeautifulSoup
import tweepy

# ① ②：福島データ
def get_fukushima(station_no):
    url = f"http://www.atom-moc.pref.fukushima.jp/public/table/Table.html?stationNo={station_no}&type=0"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.find("table")
    latest = table.find_all("td")[-1].text.strip()
    return latest

# ③：新宿放射線
def get_nsr_shinjuku():
    url = "https://radioactivity.nsr.go.jp/html/13/13000.html"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    vals = soup.select("table")[0].find_all("td")
    return vals[-1].text.strip()

# ④：Guro
def get_iernet_guro():
    url = "https://iernet.kins.re.kr/second_index.asp?sido=1&ke_flag=E"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.find("table", {"id": "GridView1"})
    rows = table.find_all("tr")
    for r in rows:
        cols = r.find_all("td")
        if cols and "Guro" in cols[0].text:
            return cols[1].text.strip()
    return "N/A"

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
    auth = tweepy.OAuth1UserHandler(
        os.environ["CONSUMER_KEY"], os.environ["CONSUMER_SECRET"],
        os.environ["ACCESS_TOKEN"], os.environ["ACCESS_SECRET"]
    )
    api = tweepy.API(auth)
    api.update_status(message)
