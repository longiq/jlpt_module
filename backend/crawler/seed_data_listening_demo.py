import urllib.parse


def _svg_uri(svg: str) -> str:
    return "data:image/svg+xml;charset=utf-8," + urllib.parse.quote(svg)


# --- SVG Definitions ---

_FLOOR_PLAN_SVG = (
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 300' width='400' height='300'>"
    "<rect width='400' height='300' fill='#f5f5f5'/>"
    # Outer walls
    "<rect x='20' y='20' width='360' height='260' fill='none' stroke='#333' stroke-width='4'/>"
    # Interior walls - vertical divider
    "<line x1='200' y1='20' x2='200' y2='300' stroke='#333' stroke-width='3'/>"
    # Interior walls - horizontal dividers
    "<line x1='20' y1='160' x2='200' y2='160' stroke='#333' stroke-width='3'/>"
    "<line x1='200' y1='180' x2='380' y2='180' stroke='#333' stroke-width='3'/>"
    # Room fills
    # Living room (top-left)
    "<rect x='22' y='22' width='176' height='136' fill='#d4edff'/>"
    # Kitchen (bottom-left)
    "<rect x='22' y='162' width='176' height='136' fill='#fff9c4'/>"
    # Bedroom (top-right)
    "<rect x='202' y='22' width='176' height='156' fill='#e8f5e9'/>"
    # Toilet (bottom-right)
    "<rect x='202' y='182' width='176' height='116' fill='#fce4ec'/>"
    # Room labels
    "<text x='110' y='95' text-anchor='middle' font-family='sans-serif' font-size='16' font-weight='bold' fill='#1a237e'>リビング</text>"
    "<text x='110' y='235' text-anchor='middle' font-family='sans-serif' font-size='16' font-weight='bold' fill='#827717'>キッチン</text>"
    "<text x='290' y='105' text-anchor='middle' font-family='sans-serif' font-size='16' font-weight='bold' fill='#1b5e20'>寝室</text>"
    "<text x='290' y='245' text-anchor='middle' font-family='sans-serif' font-size='16' font-weight='bold' fill='#880e4f'>トイレ</text>"
    # Door indicators (small gaps)
    "<rect x='196' y='100' width='8' height='20' fill='#f5f5f5'/>"
    "<rect x='196' y='220' width='8' height='20' fill='#f5f5f5'/>"
    "<rect x='100' y='156' width='20' height='8' fill='#f5f5f5'/>"
    "<rect x='280' y='176' width='20' height='8' fill='#f5f5f5'/>"
    # Title
    "<text x='200' y='292' text-anchor='middle' font-family='sans-serif' font-size='11' fill='#555'>間取り図</text>"
    "</svg>"
)

_SCHEDULE_SVG = (
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 300' width='400' height='300'>"
    "<rect width='400' height='300' fill='#fafafa'/>"
    # Title
    "<text x='200' y='22' text-anchor='middle' font-family='sans-serif' font-size='14' font-weight='bold' fill='#333'>週間スケジュール</text>"
    # Header row background
    "<rect x='10' y='30' width='380' height='34' fill='#5c6bc0'/>"
    # Day headers
    "<text x='84' y='52' text-anchor='middle' font-family='sans-serif' font-size='13' font-weight='bold' fill='white'>月曜日</text>"
    "<text x='150' y='52' text-anchor='middle' font-family='sans-serif' font-size='13' font-weight='bold' fill='white'>火曜日</text>"
    "<text x='216' y='52' text-anchor='middle' font-family='sans-serif' font-size='13' font-weight='bold' fill='white'>水曜日</text>"
    "<text x='282' y='52' text-anchor='middle' font-family='sans-serif' font-size='13' font-weight='bold' fill='white'>木曜日</text>"
    "<text x='348' y='52' text-anchor='middle' font-family='sans-serif' font-size='13' font-weight='bold' fill='white'>金曜日</text>"
    # Time labels column
    "<rect x='10' y='30' width='58' height='34' fill='#3949ab'/>"
    "<text x='39' y='52' text-anchor='middle' font-family='sans-serif' font-size='12' font-weight='bold' fill='white'>時間</text>"
    # Row 1: 9:00
    "<rect x='10' y='64' width='58' height='54' fill='#e8eaf6'/>"
    "<text x='39' y='95' text-anchor='middle' font-family='sans-serif' font-size='11' fill='#333'>9:00</text>"
    "<rect x='68' y='64' width='66' height='54' fill='#bbdefb'/>"
    "<text x='101' y='88' text-anchor='middle' font-family='sans-serif' font-size='12' fill='#0d47a1'>日本語</text>"
    "<text x='101' y='106' text-anchor='middle' font-family='sans-serif' font-size='11' fill='#1565c0'>授業</text>"
    "<rect x='134' y='64' width='66' height='54' fill='#c8e6c9'/>"
    "<text x='167' y='88' text-anchor='middle' font-family='sans-serif' font-size='12' fill='#1b5e20'>数学</text>"
    "<text x='167' y='106' text-anchor='middle' font-family='sans-serif' font-size='11' fill='#2e7d32'>クラス</text>"
    "<rect x='200' y='64' width='66' height='54' fill='#bbdefb'/>"
    "<text x='233' y='88' text-anchor='middle' font-family='sans-serif' font-size='12' fill='#0d47a1'>日本語</text>"
    "<text x='233' y='106' text-anchor='middle' font-family='sans-serif' font-size='11' fill='#1565c0'>授業</text>"
    "<rect x='266' y='64' width='66' height='54' fill='#fff9c4'/>"
    "<text x='299' y='88' text-anchor='middle' font-family='sans-serif' font-size='12' fill='#f57f17'>英語</text>"
    "<text x='299' y='106' text-anchor='middle' font-family='sans-serif' font-size='11' fill='#f9a825'>クラス</text>"
    "<rect x='332' y='64' width='66' height='54' fill='#c8e6c9'/>"
    "<text x='365' y='88' text-anchor='middle' font-family='sans-serif' font-size='12' fill='#1b5e20'>数学</text>"
    "<text x='365' y='106' text-anchor='middle' font-family='sans-serif' font-size='11' fill='#2e7d32'>クラス</text>"
    # Row 2: 13:00
    "<rect x='10' y='118' width='58' height='54' fill='#e8eaf6'/>"
    "<text x='39' y='149' text-anchor='middle' font-family='sans-serif' font-size='11' fill='#333'>13:00</text>"
    "<rect x='68' y='118' width='66' height='54' fill='#fce4ec'/>"
    "<text x='101' y='142' text-anchor='middle' font-family='sans-serif' font-size='12' fill='#880e4f'>音楽</text>"
    "<text x='101' y='160' text-anchor='middle' font-family='sans-serif' font-size='11' fill='#ad1457'>レッスン</text>"
    "<rect x='134' y='118' width='66' height='54' fill='#f3e5f5'/>"
    "<text x='167' y='142' text-anchor='middle' font-family='sans-serif' font-size='12' fill='#4a148c'>体育</text>"
    "<text x='167' y='160' text-anchor='middle' font-family='sans-serif' font-size='11' fill='#6a1b9a'>クラス</text>"
    "<rect x='200' y='118' width='66' height='54' fill='#fce4ec'/>"
    "<text x='233' y='142' text-anchor='middle' font-family='sans-serif' font-size='12' fill='#880e4f'>音楽</text>"
    "<text x='233' y='160' text-anchor='middle' font-family='sans-serif' font-size='11' fill='#ad1457'>レッスン</text>"
    "<rect x='266' y='118' width='66' height='54' fill='#fff9c4'/>"
    "<text x='299' y='142' text-anchor='middle' font-family='sans-serif' font-size='12' fill='#f57f17'>英語</text>"
    "<text x='299' y='160' text-anchor='middle' font-family='sans-serif' font-size='11' fill='#f9a825'>クラス</text>"
    "<rect x='332' y='118' width='66' height='54' fill='#f3e5f5'/>"
    "<text x='365' y='142' text-anchor='middle' font-family='sans-serif' font-size='12' fill='#4a148c'>体育</text>"
    "<text x='365' y='160' text-anchor='middle' font-family='sans-serif' font-size='11' fill='#6a1b9a'>クラス</text>"
    # Row 3: 15:00
    "<rect x='10' y='172' width='58' height='54' fill='#e8eaf6'/>"
    "<text x='39' y='203' text-anchor='middle' font-family='sans-serif' font-size='11' fill='#333'>15:00</text>"
    "<rect x='68' y='172' width='66' height='54' fill='#e0f7fa'/>"
    "<text x='101' y='196' text-anchor='middle' font-family='sans-serif' font-size='12' fill='#006064'>自習</text>"
    "<text x='101' y='214' text-anchor='middle' font-family='sans-serif' font-size='11' fill='#00838f'>時間</text>"
    "<rect x='134' y='172' width='66' height='54' fill='#bbdefb'/>"
    "<text x='167' y='196' text-anchor='middle' font-family='sans-serif' font-size='12' fill='#0d47a1'>日本語</text>"
    "<text x='167' y='214' text-anchor='middle' font-family='sans-serif' font-size='11' fill='#1565c0'>会話</text>"
    "<rect x='200' y='172' width='66' height='54' fill='#e0f7fa'/>"
    "<text x='233' y='196' text-anchor='middle' font-family='sans-serif' font-size='12' fill='#006064'>自習</text>"
    "<text x='233' y='214' text-anchor='middle' font-family='sans-serif' font-size='11' fill='#00838f'>時間</text>"
    "<rect x='266' y='172' width='66' height='54' fill='#c8e6c9'/>"
    "<text x='299' y='196' text-anchor='middle' font-family='sans-serif' font-size='12' fill='#1b5e20'>科学</text>"
    "<text x='299' y='214' text-anchor='middle' font-family='sans-serif' font-size='11' fill='#2e7d32'>実験</text>"
    "<rect x='332' y='172' width='66' height='54' fill='#bbdefb'/>"
    "<text x='365' y='196' text-anchor='middle' font-family='sans-serif' font-size='12' fill='#0d47a1'>日本語</text>"
    "<text x='365' y='214' text-anchor='middle' font-family='sans-serif' font-size='11' fill='#1565c0'>会話</text>"
    # Grid lines
    "<line x1='10' y1='64' x2='398' y2='64' stroke='#9fa8da' stroke-width='1'/>"
    "<line x1='10' y1='118' x2='398' y2='118' stroke='#9fa8da' stroke-width='1'/>"
    "<line x1='10' y1='172' x2='398' y2='172' stroke='#9fa8da' stroke-width='1'/>"
    "<line x1='10' y1='226' x2='398' y2='226' stroke='#9fa8da' stroke-width='1'/>"
    "<line x1='68' y1='30' x2='68' y2='226' stroke='#9fa8da' stroke-width='1'/>"
    "<line x1='134' y1='30' x2='134' y2='226' stroke='#9fa8da' stroke-width='1'/>"
    "<line x1='200' y1='30' x2='200' y2='226' stroke='#9fa8da' stroke-width='1'/>"
    "<line x1='266' y1='30' x2='266' y2='226' stroke='#9fa8da' stroke-width='1'/>"
    "<line x1='332' y1='30' x2='332' y2='226' stroke='#9fa8da' stroke-width='1'/>"
    "<rect x='10' y='30' width='388' height='196' fill='none' stroke='#5c6bc0' stroke-width='2'/>"
    # Caption
    "<text x='200' y='255' text-anchor='middle' font-family='sans-serif' font-size='11' fill='#555'>山田さんの週間スケジュール</text>"
    "</svg>"
)

_MAP_SVG = (
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 300' width='400' height='300'>"
    # Background (grass/ground)
    "<rect width='400' height='300' fill='#e8f5e9'/>"
    # Roads (grey)
    # Horizontal main road
    "<rect x='0' y='130' width='400' height='40' fill='#bdbdbd'/>"
    # Vertical main road
    "<rect x='170' y='0' width='40' height='300' fill='#bdbdbd'/>"
    # Road markings
    "<line x1='0' y1='150' x2='400' y2='150' stroke='white' stroke-width='2' stroke-dasharray='20,15'/>"
    "<line x1='190' y1='0' x2='190' y2='300' stroke='white' stroke-width='2' stroke-dasharray='20,15'/>"
    # Park (light green) - top left quadrant
    "<rect x='20' y='20' width='130' height='100' fill='#a5d6a7' rx='5'/>"
    "<text x='85' y='60' text-anchor='middle' font-family='sans-serif' font-size='13' font-weight='bold' fill='#1b5e20'>公園</text>"
    "<circle cx='60' cy='80' r='12' fill='#66bb6a'/>"
    "<circle cx='85' cy='75' r='10' fill='#81c784'/>"
    "<circle cx='110' cy='82' r='11' fill='#66bb6a'/>"
    # Station (top right quadrant) - blue
    "<rect x='230' y='20' width='140' height='100' fill='#bbdefb' rx='5'/>"
    "<rect x='250' y='40' width='100' height='60' fill='#1565c0' rx='3'/>"
    "<text x='300' y='75' text-anchor='middle' font-family='sans-serif' font-size='13' font-weight='bold' fill='white'>駅</text>"
    "<rect x='270' y='90' width='20' height='10' fill='#0d47a1'/>"
    "<rect x='310' y='90' width='20' height='10' fill='#0d47a1'/>"
    "<text x='300' y='110' text-anchor='middle' font-family='sans-serif' font-size='11' fill='#1565c0'>Station</text>"
    # Supermarket (bottom left quadrant) - yellow
    "<rect x='20' y='190' width='130' height='90' fill='#fff9c4' rx='5'/>"
    "<rect x='35' y='205' width='100' height='55' fill='#f9a825' rx='3'/>"
    "<text x='85' y='238' text-anchor='middle' font-family='sans-serif' font-size='12' font-weight='bold' fill='white'>スーパー</text>"
    "<text x='85' y='268' text-anchor='middle' font-family='sans-serif' font-size='10' fill='#f57f17'>Super Market</text>"
    # Hospital (bottom right quadrant) - white/red
    "<rect x='230' y='190' width='140' height='90' fill='#fce4ec' rx='5'/>"
    "<rect x='255' y='205' width='90' height='60' fill='white' rx='3' stroke='#e53935' stroke-width='2'/>"
    "<text x='300' y='240' text-anchor='middle' font-family='sans-serif' font-size='13' font-weight='bold' fill='#c62828'>病院</text>"
    # Red cross symbol
    "<rect x='292' y='212' width='16' height='6' fill='#e53935'/>"
    "<rect x='296' y='208' width='8' height='14' fill='#e53935'/>"
    "<text x='300' y='272' text-anchor='middle' font-family='sans-serif' font-size='10' fill='#c62828'>Hospital</text>"
    # North indicator
    "<text x='370' y='30' text-anchor='middle' font-family='sans-serif' font-size='14' font-weight='bold' fill='#333'>N</text>"
    "<line x1='370' y1='33' x2='370' y2='50' stroke='#333' stroke-width='2'/>"
    "<polygon points='370,15 364,33 370,28 376,33' fill='#333'/>"
    "</svg>"
)

_BAR_CHART_SVG = (
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 300' width='400' height='300'>"
    "<rect width='400' height='300' fill='#fafafa'/>"
    # Title
    "<text x='200' y='22' text-anchor='middle' font-family='sans-serif' font-size='14' font-weight='bold' fill='#333'>月別売上 (万円)</text>"
    # Chart area background
    "<rect x='55' y='35' width='330' height='200' fill='white' stroke='#e0e0e0' stroke-width='1'/>"
    # Y-axis grid lines and labels
    "<line x1='55' y1='35' x2='385' y2='35' stroke='#e0e0e0' stroke-width='1' stroke-dasharray='4,4'/>"
    "<text x='48' y='39' text-anchor='end' font-family='sans-serif' font-size='11' fill='#666'>100</text>"
    "<line x1='55' y1='85' x2='385' y2='85' stroke='#e0e0e0' stroke-width='1' stroke-dasharray='4,4'/>"
    "<text x='48' y='89' text-anchor='end' font-family='sans-serif' font-size='11' fill='#666'>75</text>"
    "<line x1='55' y1='135' x2='385' y2='135' stroke='#e0e0e0' stroke-width='1' stroke-dasharray='4,4'/>"
    "<text x='48' y='139' text-anchor='end' font-family='sans-serif' font-size='11' fill='#666'>50</text>"
    "<line x1='55' y1='185' x2='385' y2='185' stroke='#e0e0e0' stroke-width='1' stroke-dasharray='4,4'/>"
    "<text x='48' y='189' text-anchor='end' font-family='sans-serif' font-size='11' fill='#666'>25</text>"
    # Axes
    "<line x1='55' y1='235' x2='385' y2='235' stroke='#333' stroke-width='2'/>"
    "<line x1='55' y1='35' x2='55' y2='235' stroke='#333' stroke-width='2'/>"
    # Bars (bar top = 235 - value_px, height = value_px)
    # 1月: 40万 -> 160px -> top=75, height=160
    "<rect x='68' y='75' width='40' height='160' fill='#42a5f5'/>"
    "<text x='88' y='71' text-anchor='middle' font-family='sans-serif' font-size='11' font-weight='bold' fill='#1565c0'>40</text>"
    "<text x='88' y='252' text-anchor='middle' font-family='sans-serif' font-size='12' fill='#333'>1月</text>"
    # 2月: 55万 -> 220px -> top=15 (clamp to 35), use 200*55/100=110px -> top=125, height=110
    "<rect x='123' y='125' width='40' height='110' fill='#66bb6a'/>"
    "<text x='143' y='121' text-anchor='middle' font-family='sans-serif' font-size='11' font-weight='bold' fill='#2e7d32'>55</text>"
    "<text x='143' y='252' text-anchor='middle' font-family='sans-serif' font-size='12' fill='#333'>2月</text>"
    # 3月: 70万 -> 140px -> top=95, height=140
    "<rect x='178' y='95' width='40' height='140' fill='#ffa726'/>"
    "<text x='198' y='91' text-anchor='middle' font-family='sans-serif' font-size='11' font-weight='bold' fill='#e65100'>70</text>"
    "<text x='198' y='252' text-anchor='middle' font-family='sans-serif' font-size='12' fill='#333'>3月</text>"
    # 4月: 90万 -> 180px -> top=55, height=180
    "<rect x='233' y='55' width='40' height='180' fill='#ef5350'/>"
    "<text x='253' y='51' text-anchor='middle' font-family='sans-serif' font-size='11' font-weight='bold' fill='#b71c1c'>90</text>"
    "<text x='253' y='252' text-anchor='middle' font-family='sans-serif' font-size='12' fill='#333'>4月</text>"
    # 5月: 80万 -> 160px -> top=75, height=160
    "<rect x='288' y='75' width='40' height='160' fill='#ab47bc'/>"
    "<text x='308' y='71' text-anchor='middle' font-family='sans-serif' font-size='11' font-weight='bold' fill='#6a1b9a'>80</text>"
    "<text x='308' y='252' text-anchor='middle' font-family='sans-serif' font-size='12' fill='#333'>5月</text>"
    # 6月: 65万 -> 130px -> top=105, height=130
    "<rect x='343' y='105' width='40' height='130' fill='#26c6da'/>"
    "<text x='363' y='101' text-anchor='middle' font-family='sans-serif' font-size='11' font-weight='bold' fill='#006064'>65</text>"
    "<text x='363' y='252' text-anchor='middle' font-family='sans-serif' font-size='12' fill='#333'>6月</text>"
    # Y-axis label
    "<text x='12' y='140' text-anchor='middle' font-family='sans-serif' font-size='11' fill='#555' transform='rotate(-90,12,140)'>売上 (万円)</text>"
    # Caption
    "<text x='200' y='280' text-anchor='middle' font-family='sans-serif' font-size='11' fill='#777'>2024年 上半期売上グラフ</text>"
    "</svg>"
)


LISTENING_DEMO = [
    {
        "level": "N5",
        "question_type": "listening",
        "is_active": False,
        "question_text": "女の人はどこへ行きますか。",
        "option_a": "リビング",
        "option_b": "キッチン",
        "option_c": "寝室",
        "option_d": "トイレ",
        "correct_answer": "C",
        "explanation": "女の人は疲れたので寝室へ行くと言っています。",
        "source_url": "",
        "passage": (
            "男：もうすぐ夕ご飯ができますよ。\n"
            "女：ありがとう。でも、ちょっと疲れたから、先に休んでもいいですか。\n"
            "男：もちろんです。どうぞ。\n"
            "女：じゃあ、横になってきます。"
        ),
        "image_url": _svg_uri(_FLOOR_PLAN_SVG),
        "audio_url": "",
    },
    {
        "level": "N4",
        "question_type": "listening",
        "is_active": False,
        "question_text": "山田さんが日本語会話のクラスを受けるのは何曜日ですか。",
        "option_a": "月曜日と水曜日",
        "option_b": "火曜日と金曜日",
        "option_c": "水曜日と金曜日",
        "option_d": "月曜日と金曜日",
        "correct_answer": "B",
        "explanation": "スケジュール表を見ると、日本語会話は火曜日と金曜日の15時にあります。",
        "source_url": "",
        "passage": (
            "女：山田さん、今週のスケジュールを確認してもいいですか。\n"
            "男：はい、どうぞ。このスケジュール表を見てください。\n"
            "女：日本語会話のクラスは週に何回ありますか。\n"
            "男：2回です。午後3時から始まります。\n"
            "女：わかりました。ありがとうございます。"
        ),
        "image_url": _svg_uri(_SCHEDULE_SVG),
        "audio_url": "",
    },
    {
        "level": "N4",
        "question_type": "listening",
        "is_active": False,
        "question_text": "病院はどこにありますか。",
        "option_a": "駅の隣",
        "option_b": "公園の南",
        "option_c": "スーパーの向かい",
        "option_d": "公園の隣",
        "correct_answer": "C",
        "explanation": "地図を見ると、病院はスーパーの向かい（道の反対側）にあります。",
        "source_url": "",
        "passage": (
            "男：すみません、この近くに病院はありますか。\n"
            "女：はい、あります。この地図を見てください。\n"
            "男：どこですか。\n"
            "女：スーパーが見えますか？その向かいにありますよ。\n"
            "男：ああ、わかりました。どうもありがとうございます。"
        ),
        "image_url": _svg_uri(_MAP_SVG),
        "audio_url": "",
    },
    {
        "level": "N3",
        "question_type": "listening",
        "is_active": False,
        "question_text": "このお店の売上が一番多かったのは何月ですか。",
        "option_a": "1月",
        "option_b": "3月",
        "option_c": "4月",
        "option_d": "5月",
        "correct_answer": "C",
        "explanation": "グラフを見ると、4月の売上が90万円で最も高くなっています。",
        "source_url": "",
        "passage": (
            "女：このグラフを見てください。今年の上半期の売上です。\n"
            "男：1月は少ないですね。\n"
            "女：そうです。でも、春になるにつれて売上が増えてきました。\n"
            "男：一番売れた月はどれですか。\n"
            "女：このグラフの一番高いバーの月です。その後は少し下がっています。\n"
            "男：なるほど。季節によって売上が変わるんですね。"
        ),
        "image_url": _svg_uri(_BAR_CHART_SVG),
        "audio_url": "",
    },
]


def get_listening_demo_questions() -> list[dict]:
    return LISTENING_DEMO
