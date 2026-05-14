"""
Static seed dataset of authentic JLPT-style questions.

Provides two public symbols:

* ``get_seed_questions()``  — returns a list of ~100 question dicts.
* ``seed_database(db_session)`` — inserts those questions if the table is empty.

Question dict schema
--------------------
level          : str   – "N1" … "N5"
question_type  : str   – "vocabulary" | "grammar" | "reading"
question_text  : str   – question stem (Japanese)
option_a–d     : str   – answer choices
correct_answer : str   – "A" | "B" | "C" | "D"
explanation    : str   – brief explanation (Japanese)
source_url     : str   – empty string for seed data
passage        : str   – reading passage (reading questions only; else "")
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# N5 — Vocabulary (8 questions)
# ---------------------------------------------------------------------------

_N5_VOCAB: list[dict] = [
    {
        "level": "N5",
        "question_type": "vocabulary",
        "question_text": "「水」の読み方はどれですか。",
        "option_a": "みず",
        "option_b": "かわ",
        "option_c": "うみ",
        "option_d": "やま",
        "correct_answer": "A",
        "explanation": "「水」は「みず」と読みます。川（かわ）、海（うみ）、山（やま）はそれぞれ別の漢字です。",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N5",
        "question_type": "vocabulary",
        "question_text": "「大きい」の反対のことばはどれですか。",
        "option_a": "ながい",
        "option_b": "ちいさい",
        "option_c": "たかい",
        "option_d": "おもい",
        "correct_answer": "B",
        "explanation": "「大きい」の反対は「小さい（ちいさい）」です。",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N5",
        "question_type": "vocabulary",
        "question_text": "「食べる」の意味はどれですか。",
        "option_a": "のむ",
        "option_b": "みる",
        "option_c": "たべる",
        "option_d": "かく",
        "correct_answer": "C",
        "explanation": "「食べる」は「たべる（to eat）」という意味です。",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N5",
        "question_type": "vocabulary",
        "question_text": "「月曜日」は英語で何ですか。",
        "option_a": "Sunday",
        "option_b": "Tuesday",
        "option_c": "Wednesday",
        "option_d": "Monday",
        "correct_answer": "D",
        "explanation": "「月曜日（げつようび）」は Monday です。",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N5",
        "question_type": "vocabulary",
        "question_text": "「右」の読み方はどれですか。",
        "option_a": "ひだり",
        "option_b": "まえ",
        "option_c": "みぎ",
        "option_d": "うしろ",
        "correct_answer": "C",
        "explanation": "「右」は「みぎ（right）」と読みます。「左」は「ひだり」です。",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N5",
        "question_type": "vocabulary",
        "question_text": "「毎朝」の読み方はどれですか。",
        "option_a": "まいあさ",
        "option_b": "まいばん",
        "option_c": "まいにち",
        "option_d": "まいしゅう",
        "correct_answer": "A",
        "explanation": "「毎朝」は「まいあさ（every morning）」と読みます。",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N5",
        "question_type": "vocabulary",
        "question_text": "「電話」の意味はどれですか。",
        "option_a": "テレビ",
        "option_b": "でんしゃ",
        "option_c": "でんわ",
        "option_d": "ラジオ",
        "correct_answer": "C",
        "explanation": "「電話（でんわ）」は telephone という意味です。",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N5",
        "question_type": "vocabulary",
        "question_text": "（　）に入る言葉を選んでください。「今日は天気が（　）です。」",
        "option_a": "おいしい",
        "option_b": "いい",
        "option_c": "むずかしい",
        "option_d": "いそがしい",
        "correct_answer": "B",
        "explanation": "天気の状態を表すには「いい（良い）」が自然です。「天気がいいです」＝「The weather is nice.」",
        "source_url": "",
        "passage": "",
    },
]


# ---------------------------------------------------------------------------
# N5 — Grammar (8 questions)
# ---------------------------------------------------------------------------

_N5_GRAMMAR: list[dict] = [
    {
        "level": "N5",
        "question_type": "grammar",
        "question_text": "わたし___がくせいです。",
        "option_a": "は",
        "option_b": "が",
        "option_c": "を",
        "option_d": "に",
        "correct_answer": "A",
        "explanation": "「は」は主題（トピック）を示す助詞です。「わたしは学生です」は「I am a student」という意味です。",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N5",
        "question_type": "grammar",
        "question_text": "これ___ほんです。",
        "option_a": "を",
        "option_b": "に",
        "option_c": "は",
        "option_d": "で",
        "correct_answer": "C",
        "explanation": "「これは本です」は「This is a book」という意味です。「は」が主題を示します。",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N5",
        "question_type": "grammar",
        "question_text": "まいにち にほんご___べんきょうします。",
        "option_a": "が",
        "option_b": "を",
        "option_c": "は",
        "option_d": "の",
        "correct_answer": "B",
        "explanation": "「を」は他動詞の目的語を示す助詞です。「日本語を勉強する」＝「study Japanese」",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N5",
        "question_type": "grammar",
        "question_text": "きのう えいが___みました。",
        "option_a": "で",
        "option_b": "に",
        "option_c": "を",
        "option_d": "と",
        "correct_answer": "C",
        "explanation": "「映画を見る」の「を」は目的格助詞です。",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N5",
        "question_type": "grammar",
        "question_text": "としょかん___ほんをかります。",
        "option_a": "で",
        "option_b": "を",
        "option_c": "が",
        "option_d": "は",
        "correct_answer": "A",
        "explanation": "「で」は行為が行われる場所を示す助詞です。「図書館で本を借りる」＝「borrow books at the library」",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N5",
        "question_type": "grammar",
        "question_text": "あした ともだち___あいます。",
        "option_a": "を",
        "option_b": "で",
        "option_c": "に",
        "option_d": "が",
        "correct_answer": "C",
        "explanation": "「に」は移動の方向・対象を示します。「友達に会う」＝「meet a friend」",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N5",
        "question_type": "grammar",
        "question_text": "これは たなか___ほんです。",
        "option_a": "が",
        "option_b": "の",
        "option_c": "は",
        "option_d": "を",
        "correct_answer": "B",
        "explanation": "「の」は所有を表す助詞です。「田中の本」＝「Tanaka's book」",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N5",
        "question_type": "grammar",
        "question_text": "「学校___いきます」の（　）に入る助詞はどれですか。",
        "option_a": "を",
        "option_b": "が",
        "option_c": "で",
        "option_d": "に",
        "correct_answer": "D",
        "explanation": "「に」は移動の目的地を示します。「学校に行く」＝「go to school」",
        "source_url": "",
        "passage": "",
    },
]


# ---------------------------------------------------------------------------
# N5 — Reading (4 questions)
# ---------------------------------------------------------------------------

_N5_READING_PASSAGE_1 = (
    "たなかさんは まいあさ ６じに おきます。"
    "そして、かおをあらって、あさごはんをたべます。"
    "あさごはんのあと、はをみがいて、がっこうへいきます。"
    "がっこうは うちから あるいて じゅっぷんです。"
)

_N5_READING_PASSAGE_2 = (
    "わたしのいえは としょかんの ちかくに あります。"
    "としょかんには まいにち いきます。"
    "としょかんは しずかで、とても すきです。"
    "よく そこで にほんごを べんきょうします。"
)

_N5_READING: list[dict] = [
    {
        "level": "N5",
        "question_type": "reading",
        "question_text": "田中さんは毎朝何時に起きますか。",
        "option_a": "5時",
        "option_b": "6時",
        "option_c": "7時",
        "option_d": "8時",
        "correct_answer": "B",
        "explanation": "文章に「まいあさ６じにおきます」とあります。",
        "source_url": "",
        "passage": _N5_READING_PASSAGE_1,
    },
    {
        "level": "N5",
        "question_type": "reading",
        "question_text": "田中さんの学校はうちからどのくらいかかりますか。",
        "option_a": "バスで10分",
        "option_b": "電車で10分",
        "option_c": "歩いて10分",
        "option_d": "車で10分",
        "correct_answer": "C",
        "explanation": "「がっこうはうちからあるいてじゅっぷんです」とあります。",
        "source_url": "",
        "passage": _N5_READING_PASSAGE_1,
    },
    {
        "level": "N5",
        "question_type": "reading",
        "question_text": "「わたし」は図書館で何をしますか。",
        "option_a": "ほんをかります",
        "option_b": "ともだちとはなします",
        "option_c": "にほんごをべんきょうします",
        "option_d": "おんがくをききます",
        "correct_answer": "C",
        "explanation": "「よくそこでにほんごをべんきょうします」とあります。",
        "source_url": "",
        "passage": _N5_READING_PASSAGE_2,
    },
    {
        "level": "N5",
        "question_type": "reading",
        "question_text": "「わたし」は図書館についてどう思っていますか。",
        "option_a": "うるさくていやだ",
        "option_b": "しずかでとてもすき",
        "option_c": "ちょっとつまらない",
        "option_d": "ときどきこわい",
        "correct_answer": "B",
        "explanation": "「としょかんはしずかで、とてもすきです」とあります。",
        "source_url": "",
        "passage": _N5_READING_PASSAGE_2,
    },
]


# ---------------------------------------------------------------------------
# N4 — Vocabulary (8 questions)
# ---------------------------------------------------------------------------

_N4_VOCAB: list[dict] = [
    {
        "level": "N4",
        "question_type": "vocabulary",
        "question_text": "「集める」の意味はどれですか。",
        "option_a": "なくす",
        "option_b": "ためる",
        "option_c": "あつめる",
        "option_d": "わける",
        "correct_answer": "C",
        "explanation": "「集める（あつめる）」は to collect / to gather という意味です。",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N4",
        "question_type": "vocabulary",
        "question_text": "「予約」の読み方はどれですか。",
        "option_a": "よやく",
        "option_b": "よてい",
        "option_c": "よそう",
        "option_d": "よきん",
        "correct_answer": "A",
        "explanation": "「予約（よやく）」は reservation / booking という意味です。",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N4",
        "question_type": "vocabulary",
        "question_text": "「親切」の反対の意味に近いことばはどれですか。",
        "option_a": "やさしい",
        "option_b": "しんせつ",
        "option_c": "つめたい",
        "option_d": "にぎやか",
        "correct_answer": "C",
        "explanation": "「親切（しんせつ）」の反対に近いのは「冷たい（つめたい）」です。冷淡な態度を表します。",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N4",
        "question_type": "vocabulary",
        "question_text": "「失敗」の読み方はどれですか。",
        "option_a": "しっぱい",
        "option_b": "せいこう",
        "option_c": "しっかく",
        "option_d": "しっぽ",
        "correct_answer": "A",
        "explanation": "「失敗（しっぱい）」は failure という意味です。「成功（せいこう）」が反対語です。",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N4",
        "question_type": "vocabulary",
        "question_text": "「引っ越し」の意味はどれですか。",
        "option_a": "旅行すること",
        "option_b": "住む場所を変えること",
        "option_c": "仕事をやめること",
        "option_d": "買い物をすること",
        "correct_answer": "B",
        "explanation": "「引っ越し（ひっこし）」は moving house という意味です。",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N4",
        "question_type": "vocabulary",
        "question_text": "「遅刻」の読み方はどれですか。",
        "option_a": "ちこく",
        "option_b": "えんき",
        "option_c": "きゅうこう",
        "option_d": "そうたい",
        "correct_answer": "A",
        "explanation": "「遅刻（ちこく）」は being late / tardiness という意味です。",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N4",
        "question_type": "vocabulary",
        "question_text": "「退院」の意味はどれですか。",
        "option_a": "病院に入ること",
        "option_b": "病院を出ること",
        "option_c": "会社をやめること",
        "option_d": "学校を卒業すること",
        "correct_answer": "B",
        "explanation": "「退院（たいいん）」は being discharged from hospital という意味です。「入院」が反対語です。",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N4",
        "question_type": "vocabulary",
        "question_text": "「丁寧」の読み方はどれですか。",
        "option_a": "ていねい",
        "option_b": "きれい",
        "option_c": "しずか",
        "option_d": "げんき",
        "correct_answer": "A",
        "explanation": "「丁寧（ていねい）」は polite / careful という意味です。",
        "source_url": "",
        "passage": "",
    },
]


# ---------------------------------------------------------------------------
# N4 — Grammar (8 questions)
# ---------------------------------------------------------------------------

_N4_GRAMMAR: list[dict] = [
    {
        "level": "N4",
        "question_type": "grammar",
        "question_text": "この映画は子ども___見ることができます。",
        "option_a": "でも",
        "option_b": "しか",
        "option_c": "だけ",
        "option_d": "ほど",
        "correct_answer": "A",
        "explanation": "「でも」は「even」の意味で、子どもでも見られる（子どもにも可能）という意味を表します。",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N4",
        "question_type": "grammar",
        "question_text": "雨が降っている___、出かけましょう。",
        "option_a": "のに",
        "option_b": "から",
        "option_c": "ために",
        "option_d": "ながら",
        "correct_answer": "A",
        "explanation": "「のに」は逆接（despite / even though）を表します。「雨が降っているのに出かける」＝「go out despite the rain」",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N4",
        "question_type": "grammar",
        "question_text": "もっと早く起きれば、電車に乗り___のに。",
        "option_a": "られた",
        "option_b": "たかった",
        "option_c": "れた",
        "option_d": "てほしかった",
        "correct_answer": "A",
        "explanation": "「乗れる」の可能形・過去は「乗られた」ではなく「乗れた」ですが、ここでは「〜のに」の反事実条件文で「乗られた（乗ることができた）のに」が文脈上正しいです。",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N4",
        "question_type": "grammar",
        "question_text": "先生は学生に宿題を___ました。",
        "option_a": "だし",
        "option_b": "くれ",
        "option_c": "もらい",
        "option_d": "あげ",
        "correct_answer": "A",
        "explanation": "「出す（だす）」は宿題や課題を与えるときに使います。「先生が宿題を出した」が自然な表現です。",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N4",
        "question_type": "grammar",
        "question_text": "彼女は歌___上手です。",
        "option_a": "に",
        "option_b": "で",
        "option_c": "が",
        "option_d": "の",
        "correct_answer": "C",
        "explanation": "能力・得意を表す「〜が上手だ」の形で「が」を使います。「歌が上手だ」＝「is good at singing」",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N4",
        "question_type": "grammar",
        "question_text": "薬を飲ん___、早く寝てください。",
        "option_a": "てから",
        "option_b": "ながら",
        "option_c": "たり",
        "option_d": "ために",
        "correct_answer": "A",
        "explanation": "「〜てから」は「after doing ~」という順序を表します。「薬を飲んでから寝る」＝「sleep after taking medicine」",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N4",
        "question_type": "grammar",
        "question_text": "この仕事は私に___できません。",
        "option_a": "しか",
        "option_b": "だけ",
        "option_c": "は",
        "option_d": "も",
        "correct_answer": "C",
        "explanation": "「私にはできません」は「I cannot do it」という意味で、「には」が対比・強調を表します。",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N4",
        "question_type": "grammar",
        "question_text": "山田さんは日本語___英語も話せます。",
        "option_a": "だけでなく",
        "option_b": "しか",
        "option_c": "ばかり",
        "option_d": "ほど",
        "correct_answer": "A",
        "explanation": "「〜だけでなく〜も」は「not only ~ but also ~」という意味です。",
        "source_url": "",
        "passage": "",
    },
]


# ---------------------------------------------------------------------------
# N4 — Reading (4 questions)
# ---------------------------------------------------------------------------

_N4_READING_PASSAGE_1 = (
    "先週、友達と一緒に山に登りました。"
    "天気はよかったのですが、山道がとても急で、何度も休みながら登りました。"
    "頂上からの景色は本当に素晴らしく、疲れが全部吹き飛びました。"
    "また来年も登りたいと思っています。"
)

_N4_READING_PASSAGE_2 = (
    "最近、電車の中でスマートフォンを使う人が増えています。"
    "メールを書いたり、ニュースを読んだり、ゲームをしたりしています。"
    "しかし、スマートフォンに夢中になりすぎて、周りの人に迷惑をかけることもあります。"
    "マナーを守って使うことが大切です。"
)

_N4_READING: list[dict] = [
    {
        "level": "N4",
        "question_type": "reading",
        "question_text": "山登りはどうでしたか。",
        "option_a": "天気が悪くて大変だった",
        "option_b": "道が急で大変だったが、景色がよかった",
        "option_c": "とても楽で楽しかった",
        "option_d": "頂上には着けなかった",
        "correct_answer": "B",
        "explanation": "「山道がとても急で」「頂上からの景色は本当に素晴らしく」とあります。",
        "source_url": "",
        "passage": _N4_READING_PASSAGE_1,
    },
    {
        "level": "N4",
        "question_type": "reading",
        "question_text": "筆者は来年について何と言っていますか。",
        "option_a": "もう山には登りたくない",
        "option_b": "別の山に登りたい",
        "option_c": "また同じ山に登りたい",
        "option_d": "友達とは行きたくない",
        "correct_answer": "C",
        "explanation": "「また来年も登りたいと思っています」とあります。",
        "source_url": "",
        "passage": _N4_READING_PASSAGE_1,
    },
    {
        "level": "N4",
        "question_type": "reading",
        "question_text": "電車の中でスマートフォンを使って何をしている人がいますか。",
        "option_a": "電話をかけたり、写真を撮ったりしている",
        "option_b": "メールを書いたり、ニュースを読んだりしている",
        "option_c": "地図を見たり、音楽を聴いたりしている",
        "option_d": "本を読んだり、寝たりしている",
        "correct_answer": "B",
        "explanation": "「メールを書いたり、ニュースを読んだり、ゲームをしたりしています」とあります。",
        "source_url": "",
        "passage": _N4_READING_PASSAGE_2,
    },
    {
        "level": "N4",
        "question_type": "reading",
        "question_text": "筆者がスマートフォンの使用について言いたいことは何ですか。",
        "option_a": "電車でのスマートフォン使用を全面禁止すべきだ",
        "option_b": "スマートフォンは便利なので積極的に使うべきだ",
        "option_c": "マナーを守って使うことが大切だ",
        "option_d": "若者はスマートフォンに頼りすぎている",
        "correct_answer": "C",
        "explanation": "文章の最後に「マナーを守って使うことが大切です」と述べています。",
        "source_url": "",
        "passage": _N4_READING_PASSAGE_2,
    },
]


# ---------------------------------------------------------------------------
# N3 — Vocabulary (8 questions)
# ---------------------------------------------------------------------------

_N3_VOCAB: list[dict] = [
    {
        "level": "N3",
        "question_type": "vocabulary",
        "question_text": "彼女はいつも（　）な服を着ている。センスがいいと思う。",
        "option_a": "おだやか",
        "option_b": "おしゃれ",
        "option_c": "まじめ",
        "option_d": "なだらか",
        "correct_answer": "B",
        "explanation": "「おしゃれ」は fashionable / stylish という意味で、服装や外見のセンスについて使います。",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N3",
        "question_type": "vocabulary",
        "question_text": "この計画は（　）があって、すぐには実行できない。",
        "option_a": "むだ",
        "option_b": "もんだい",
        "option_c": "むり",
        "option_d": "むだづかい",
        "correct_answer": "C",
        "explanation": "「無理（むり）」は impossible / unreasonable という意味で、「無理がある」＝「is impractical / has flaws」",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N3",
        "question_type": "vocabulary",
        "question_text": "「提案」の読み方はどれですか。",
        "option_a": "ていあん",
        "option_b": "ていか",
        "option_c": "ていけい",
        "option_d": "ていど",
        "correct_answer": "A",
        "explanation": "「提案（ていあん）」は proposal / suggestion という意味です。",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N3",
        "question_type": "vocabulary",
        "question_text": "「把握」の意味はどれですか。",
        "option_a": "こわすこと",
        "option_b": "しっかり理解・掌握すること",
        "option_c": "あつめること",
        "option_d": "かくすこと",
        "correct_answer": "B",
        "explanation": "「把握（はあく）」は grasp / understand thoroughly という意味です。「状況を把握する」＝「grasp the situation」",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N3",
        "question_type": "vocabulary",
        "question_text": "会議で彼の意見に（　）する人が多かった。",
        "option_a": "さんせい",
        "option_b": "はんたい",
        "option_c": "ちゅうもく",
        "option_d": "しんぱい",
        "correct_answer": "A",
        "explanation": "「賛成（さんせい）」は agreement / approval という意味です。文脈上「賛成する人が多かった」が自然です。",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N3",
        "question_type": "vocabulary",
        "question_text": "「迷惑」の読み方はどれですか。",
        "option_a": "めいわく",
        "option_b": "まよわく",
        "option_c": "めいかく",
        "option_d": "まよいわく",
        "correct_answer": "A",
        "explanation": "「迷惑（めいわく）」は nuisance / trouble という意味です。",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N3",
        "question_type": "vocabulary",
        "question_text": "彼はその問題を（　）に解決した。",
        "option_a": "かんたん",
        "option_b": "みごと",
        "option_c": "たいへん",
        "option_d": "ふつう",
        "correct_answer": "B",
        "explanation": "「見事（みごと）に」は splendidly / brilliantly という意味の副詞的用法です。",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N3",
        "question_type": "vocabulary",
        "question_text": "「欠点」の意味はどれですか。",
        "option_a": "長所",
        "option_b": "短所・弱点",
        "option_c": "特徴",
        "option_d": "能力",
        "correct_answer": "B",
        "explanation": "「欠点（けってん）」は shortcoming / weak point という意味です。「長所（ちょうしょ）」が反対語です。",
        "source_url": "",
        "passage": "",
    },
]


# ---------------------------------------------------------------------------
# N3 — Grammar (8 questions)
# ---------------------------------------------------------------------------

_N3_GRAMMAR: list[dict] = [
    {
        "level": "N3",
        "question_type": "grammar",
        "question_text": "彼女は病気___、学校に来た。",
        "option_a": "なのに",
        "option_b": "だから",
        "option_c": "ために",
        "option_d": "ので",
        "correct_answer": "A",
        "explanation": "「なのに」は逆接（despite being ~）を表します。病気なのに来た＝「came despite being sick」",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N3",
        "question_type": "grammar",
        "question_text": "試験に合格___ために、毎日勉強しています。",
        "option_a": "した",
        "option_b": "する",
        "option_c": "して",
        "option_d": "しよう",
        "correct_answer": "B",
        "explanation": "「〜するために」は「in order to do ~」という目的を表す表現です。動詞は辞書形を使います。",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N3",
        "question_type": "grammar",
        "question_text": "この映画はとても感動的___、涙が出てきた。",
        "option_a": "なので",
        "option_b": "だのに",
        "option_c": "でも",
        "option_d": "ながら",
        "correct_answer": "A",
        "explanation": "「〜なので」はナ形容詞・名詞に接続する理由を表す表現です。「感動的なので〜」＝「because it was moving, ~」",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N3",
        "question_type": "grammar",
        "question_text": "もう少し早く連絡して___ば、準備できたのに。",
        "option_a": "くれれ",
        "option_b": "もらえれ",
        "option_c": "あげれ",
        "option_d": "やれれ",
        "correct_answer": "A",
        "explanation": "「くれれば」は「if (you) had given me / if (you) had done for me」という意味の授受動詞の条件形です。",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N3",
        "question_type": "grammar",
        "question_text": "田中さん___そんな失礼なことを言うはずがない。",
        "option_a": "に",
        "option_b": "が",
        "option_c": "は",
        "option_d": "で",
        "correct_answer": "C",
        "explanation": "「〜はずがない」は「cannot be / there is no way that」という意味で、「田中さんはそんなことを言うはずがない」が正しい構造です。",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N3",
        "question_type": "grammar",
        "question_text": "時間さえ___ば、旅行に行けるのだが。",
        "option_a": "あれ",
        "option_b": "あり",
        "option_c": "ある",
        "option_d": "あっ",
        "correct_answer": "A",
        "explanation": "「〜さえ〜ば」は「if only ~」という意味の条件表現です。「時間さえあれば」＝「if only I had time」",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N3",
        "question_type": "grammar",
        "question_text": "先生の話によると、試験は来週に___そうだ。",
        "option_a": "なる",
        "option_b": "なり",
        "option_c": "なった",
        "option_d": "なって",
        "correct_answer": "A",
        "explanation": "「〜そうだ（伝聞）」は辞書形・た形に接続します。「なるそうだ」＝「I heard it will become / apparently it will be」",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N3",
        "question_type": "grammar",
        "question_text": "彼女は忙し___も、ボランティア活動を続けている。",
        "option_a": "くて",
        "option_b": "くても",
        "option_c": "ければ",
        "option_d": "いのに",
        "correct_answer": "B",
        "explanation": "「〜くても」はイ形容詞の逆接条件形で「even if/though ~」という意味です。「忙しくても」＝「even though (she is) busy」",
        "source_url": "",
        "passage": "",
    },
]


# ---------------------------------------------------------------------------
# N3 — Reading (4 questions)
# ---------------------------------------------------------------------------

_N3_READING_PASSAGE_1 = (
    "現代の若者はかつてに比べて読書量が減っていると言われています。"
    "スマートフォンやインターネットの普及により、短い文章や動画で情報を得ることが主流になりました。"
    "しかし、読書には想像力を育て、語彙を増やし、集中力を高めるという効果があります。"
    "また、読書を通じて異なる価値観や文化に触れることができ、人生を豊かにしてくれます。"
    "専門家は、たとえ短い時間でも毎日読書する習慣をつけることを勧めています。"
)

_N3_READING_PASSAGE_2 = (
    "日本では少子化が深刻な問題となっています。"
    "出生率の低下により、将来的には労働力不足や社会保障費の増大が懸念されています。"
    "政府はこの問題に対処するために、育児支援の充実や働き方改革を進めています。"
    "一方で、外国からの労働者の受け入れを拡大するという意見もありますが、"
    "文化や言語の違いによる摩擦も予想されるため、慎重な議論が必要です。"
)

_N3_READING: list[dict] = [
    {
        "level": "N3",
        "question_type": "reading",
        "question_text": "若者の読書量が減っている主な原因として、文章で述べられているのはどれですか。",
        "option_a": "本の値段が高くなったから",
        "option_b": "学校での読書教育が不足しているから",
        "option_c": "スマートフォンやインターネットの普及により、情報取得の方法が変わったから",
        "option_d": "若者が忙しくなり、時間がないから",
        "correct_answer": "C",
        "explanation": "「スマートフォンやインターネットの普及により、短い文章や動画で情報を得ることが主流になりました」とあります。",
        "source_url": "",
        "passage": _N3_READING_PASSAGE_1,
    },
    {
        "level": "N3",
        "question_type": "reading",
        "question_text": "専門家が勧めていることは何ですか。",
        "option_a": "毎日長時間読書すること",
        "option_b": "スマートフォンをやめること",
        "option_c": "毎日少しでも読書する習慣をつけること",
        "option_d": "図書館で本を借りること",
        "correct_answer": "C",
        "explanation": "「たとえ短い時間でも毎日読書する習慣をつけることを勧めています」とあります。",
        "source_url": "",
        "passage": _N3_READING_PASSAGE_1,
    },
    {
        "level": "N3",
        "question_type": "reading",
        "question_text": "少子化によって将来起こると懸念されていることはどれですか。",
        "option_a": "環境問題の悪化",
        "option_b": "労働力不足や社会保障費の増大",
        "option_c": "教育の質の低下",
        "option_d": "外国との関係悪化",
        "correct_answer": "B",
        "explanation": "「将来的には労働力不足や社会保障費の増大が懸念されています」とあります。",
        "source_url": "",
        "passage": _N3_READING_PASSAGE_2,
    },
    {
        "level": "N3",
        "question_type": "reading",
        "question_text": "外国人労働者の受け入れ拡大について、筆者はどのような立場を取っていますか。",
        "option_a": "積極的に推進すべきと述べている",
        "option_b": "絶対に反対すべきと述べている",
        "option_c": "様々な問題があるため慎重に議論すべきと述べている",
        "option_d": "既に解決済みの問題だと述べている",
        "correct_answer": "C",
        "explanation": "「文化や言語の違いによる摩擦も予想されるため、慎重な議論が必要です」とあります。",
        "source_url": "",
        "passage": _N3_READING_PASSAGE_2,
    },
]


# ---------------------------------------------------------------------------
# N2 — Vocabulary (8 questions)
# ---------------------------------------------------------------------------

_N2_VOCAB: list[dict] = [
    {
        "level": "N2",
        "question_type": "vocabulary",
        "question_text": "「懸念」の読み方と意味として正しいものはどれですか。",
        "option_a": "けねん・心配・気がかり",
        "option_b": "けんねん・けんけつ・思い出",
        "option_c": "かんねん・あきらめること",
        "option_d": "こうねん・光の年",
        "correct_answer": "A",
        "explanation": "「懸念（けねん）」は concern / worry という意味です。「〜が懸念される」＝「~ is a concern」",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N2",
        "question_type": "vocabulary",
        "question_text": "彼の行動は社会の（　）に反している。",
        "option_a": "きはん",
        "option_b": "きかく",
        "option_c": "きじゅん",
        "option_d": "きそく",
        "correct_answer": "A",
        "explanation": "「規範（きはん）」は norm / standard という意味で、「社会の規範に反する」＝「go against social norms」",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N2",
        "question_type": "vocabulary",
        "question_text": "「斬新」の意味はどれですか。",
        "option_a": "古くて伝統的なこと",
        "option_b": "非常に新しく独創的なこと",
        "option_c": "危険で注意が必要なこと",
        "option_d": "複雑で難しいこと",
        "correct_answer": "B",
        "explanation": "「斬新（ざんしん）」は novel / innovative / strikingly original という意味です。",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N2",
        "question_type": "vocabulary",
        "question_text": "その発言は（　）を招いた。多くの人が誤解した。",
        "option_a": "こうかん",
        "option_b": "ごかい",
        "option_c": "しっかく",
        "option_d": "しょうさん",
        "correct_answer": "B",
        "explanation": "「誤解（ごかい）」は misunderstanding という意味です。「誤解を招く」＝「invite misunderstanding」",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N2",
        "question_type": "vocabulary",
        "question_text": "「緻密」の意味はどれですか。",
        "option_a": "大雑把であること",
        "option_b": "細かく精密であること",
        "option_c": "素早く行動すること",
        "option_d": "強引に進めること",
        "correct_answer": "B",
        "explanation": "「緻密（ちみつ）」は meticulous / detailed / precise という意味です。",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N2",
        "question_type": "vocabulary",
        "question_text": "この問題は（　）しており、簡単には解決できない。",
        "option_a": "せいじゅく",
        "option_b": "ふくざつか",
        "option_c": "たんじゅんか",
        "option_d": "めいかく",
        "correct_answer": "B",
        "explanation": "「複雑化（ふくざつか）している」は「has become complicated」という意味です。",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N2",
        "question_type": "vocabulary",
        "question_text": "「顕著」の読み方はどれですか。",
        "option_a": "けんちょ",
        "option_b": "けんじゃく",
        "option_c": "けいちょ",
        "option_d": "こんちょ",
        "correct_answer": "A",
        "explanation": "「顕著（けんちょ）」は remarkable / conspicuous という意味です。「顕著な変化」＝「remarkable change」",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N2",
        "question_type": "vocabulary",
        "question_text": "「逸脱」の意味はどれですか。",
        "option_a": "正常な状態に戻ること",
        "option_b": "規則やルールに従うこと",
        "option_c": "定められた範囲や基準からはずれること",
        "option_d": "物事が順調に進むこと",
        "correct_answer": "C",
        "explanation": "「逸脱（いつだつ）」は deviation / departure from the norm という意味です。",
        "source_url": "",
        "passage": "",
    },
]


# ---------------------------------------------------------------------------
# N2 — Grammar (8 questions)
# ---------------------------------------------------------------------------

_N2_GRAMMAR: list[dict] = [
    {
        "level": "N2",
        "question_type": "grammar",
        "question_text": "この映画は子ども___、大人も楽しめる作品だ。",
        "option_a": "はもとより",
        "option_b": "ならでは",
        "option_c": "をおいて",
        "option_d": "とあって",
        "correct_answer": "A",
        "explanation": "「〜はもとより〜も」は「not only ~ but also ~」という意味で、子どもはもちろんのこと大人も、という意味になります。",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N2",
        "question_type": "grammar",
        "question_text": "彼女の努力___、今の成功があるのだ。",
        "option_a": "にわたって",
        "option_b": "あっての",
        "option_c": "をめぐって",
        "option_d": "にかわって",
        "correct_answer": "B",
        "explanation": "「〜あっての〜」は「~ exists because of ~」という意味で、「彼女の努力あっての成功」＝「the success owes its existence to her effort」",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N2",
        "question_type": "grammar",
        "question_text": "長年の研究の末、ついに新薬が開発___。",
        "option_a": "されるに至った",
        "option_b": "されることになった",
        "option_c": "するにあたった",
        "option_d": "するとなった",
        "correct_answer": "A",
        "explanation": "「〜に至る（いたる）」は「finally reach / culminate in」という意味で、長い経緯の末に結果に至ったことを表します。",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N2",
        "question_type": "grammar",
        "question_text": "プロ___、そんな基本的なミスは許されない。",
        "option_a": "としては",
        "option_b": "にとっては",
        "option_c": "をもって",
        "option_d": "ならではの",
        "correct_answer": "A",
        "explanation": "「〜としては」は「for / as a ~」という立場・資格を示します。「プロとしては」＝「as a professional」",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N2",
        "question_type": "grammar",
        "question_text": "このデザイン___美しさは、他のブランドには真似できない。",
        "option_a": "ならではの",
        "option_b": "をもとにした",
        "option_c": "にもとづく",
        "option_d": "によっての",
        "correct_answer": "A",
        "explanation": "「〜ならではの〜」は「uniquely ~ / characteristic of ~」という意味で、そのものだけが持つ独自性を表します。",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N2",
        "question_type": "grammar",
        "question_text": "時代の変化___、働き方も大きく変わってきた。",
        "option_a": "につれて",
        "option_b": "にさいして",
        "option_c": "をかわきりに",
        "option_d": "にあたって",
        "correct_answer": "A",
        "explanation": "「〜につれて〜」は「as ~ changes, ~ also changes」という並行的変化を表します。",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N2",
        "question_type": "grammar",
        "question_text": "交通事故を防ぐ___、安全運転を心がけましょう。",
        "option_a": "ためには",
        "option_b": "ことには",
        "option_c": "ものには",
        "option_d": "わけには",
        "correct_answer": "A",
        "explanation": "「〜ためには〜」は「in order to ~ / for the sake of ~」という目的表現です。",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N2",
        "question_type": "grammar",
        "question_text": "彼はどんなに疲れていても、約束を___ことはない。",
        "option_a": "やぶる",
        "option_b": "やぶった",
        "option_c": "やぶり",
        "option_d": "やぶれる",
        "correct_answer": "A",
        "explanation": "「〜ことはない」は辞書形に接続して「(he/she) never does ~」という意味を表します。",
        "source_url": "",
        "passage": "",
    },
]


# ---------------------------------------------------------------------------
# N2 — Reading (4 questions)
# ---------------------------------------------------------------------------

_N2_READING_PASSAGE_1 = (
    "人工知能（AI）技術の急速な発展は、社会に大きな変革をもたらしています。"
    "医療分野では、AIを活用した診断支援システムが普及しつつあり、"
    "早期発見・早期治療の可能性が高まっています。"
    "一方で、AIが人間の仕事を奪うのではないかという懸念も広がっています。"
    "しかし、専門家の多くは、AIはあくまでも人間を補助するツールであり、"
    "創造性や感情的な判断を要する分野では人間の役割が依然として重要だと指摘しています。"
    "重要なのは、AIと人間がそれぞれの強みを活かして協働することではないでしょうか。"
)

_N2_READING_PASSAGE_2 = (
    "日本の伝統文化の一つである茶道は、単なるお茶の飲み方ではなく、"
    "「和敬清寂（わけいせいじゃく）」という精神を体現する芸術です。"
    "和は調和、敬は敬意、清は清潔さ、寂は静けさを意味します。"
    "茶道を通じて人は集中力や礼儀作法を身につけ、日常の喧騒から離れて"
    "心の平静を取り戻すことができます。"
    "近年、外国人観光客の間でも茶道体験が人気を集めており、"
    "日本文化の魅力を世界に発信する役割も担っています。"
)

_N2_READING: list[dict] = [
    {
        "level": "N2",
        "question_type": "reading",
        "question_text": "AI技術の医療分野への活用について、文章ではどのように述べていますか。",
        "option_a": "まだ研究段階であり、実用化は難しい",
        "option_b": "診断支援システムが普及しつつあり、早期発見・治療の可能性が高まっている",
        "option_c": "医師の仕事をすべて代替できる",
        "option_d": "医療費の削減につながっている",
        "correct_answer": "B",
        "explanation": "「AIを活用した診断支援システムが普及しつつあり、早期発見・早期治療の可能性が高まっています」とあります。",
        "source_url": "",
        "passage": _N2_READING_PASSAGE_1,
    },
    {
        "level": "N2",
        "question_type": "reading",
        "question_text": "筆者がAIと人間の関係について最終的に言いたいことは何ですか。",
        "option_a": "AIは人間の仕事を全て奪うだろう",
        "option_b": "AIは使うべきでない",
        "option_c": "AIと人間がそれぞれの強みを活かして協働することが重要だ",
        "option_d": "人間はAIに依存すべきだ",
        "correct_answer": "C",
        "explanation": "文末に「AIと人間がそれぞれの強みを活かして協働することではないでしょうか」と筆者の主張が述べられています。",
        "source_url": "",
        "passage": _N2_READING_PASSAGE_1,
    },
    {
        "level": "N2",
        "question_type": "reading",
        "question_text": "「和敬清寂」の「敬」はどういう意味ですか。",
        "option_a": "調和",
        "option_b": "清潔さ",
        "option_c": "静けさ",
        "option_d": "敬意",
        "correct_answer": "D",
        "explanation": "「和は調和、敬は敬意、清は清潔さ、寂は静けさ」と説明されています。",
        "source_url": "",
        "passage": _N2_READING_PASSAGE_2,
    },
    {
        "level": "N2",
        "question_type": "reading",
        "question_text": "近年の茶道について、文章で述べられていることはどれですか。",
        "option_a": "茶道の人気が日本国内で低下している",
        "option_b": "外国人観光客の間でも茶道体験が人気を集めている",
        "option_c": "茶道は日本人しか理解できない",
        "option_d": "茶道の師匠の数が減っている",
        "correct_answer": "B",
        "explanation": "「外国人観光客の間でも茶道体験が人気を集めており」とあります。",
        "source_url": "",
        "passage": _N2_READING_PASSAGE_2,
    },
]


# ---------------------------------------------------------------------------
# N1 — Vocabulary (8 questions)
# ---------------------------------------------------------------------------

_N1_VOCAB: list[dict] = [
    {
        "level": "N1",
        "question_type": "vocabulary",
        "question_text": "「忖度」の意味として最も適切なものはどれですか。",
        "option_a": "上司の命令に盲目的に従うこと",
        "option_b": "他人の気持ちや意向を推し量って行動すること",
        "option_c": "自分の利益のために嘘をつくこと",
        "option_d": "責任を他人に押しつけること",
        "correct_answer": "B",
        "explanation": "「忖度（そんたく）」は reading between the lines / inferring and acting on another's unspoken wishes という意味です。",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N1",
        "question_type": "vocabulary",
        "question_text": "「瑕疵」の読み方はどれですか。",
        "option_a": "かし",
        "option_b": "けっし",
        "option_c": "きず",
        "option_d": "しっかく",
        "correct_answer": "A",
        "explanation": "「瑕疵（かし）」は defect / flaw という法律用語でもよく使われます。「瑕疵担保責任」は warranty of defects。",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N1",
        "question_type": "vocabulary",
        "question_text": "その芸術家の作品は（　）とした風格を持ち、見る者を圧倒する。",
        "option_a": "こうぜん",
        "option_b": "どうどう",
        "option_c": "りんとう",
        "option_d": "だんこ",
        "correct_answer": "A",
        "explanation": "「堂々（どうどう）」も使えますが、「凛然（りんぜん）」または「昂然（こうぜん）」が「気高さ・威厳のある様子」を表します。ここでは「堂々とした風格」が最も自然です。",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N1",
        "question_type": "vocabulary",
        "question_text": "「恣意的」の意味として正しいものはどれですか。",
        "option_a": "論理的な根拠に基づいていること",
        "option_b": "自分の思いのままに、気ままに行うこと",
        "option_c": "社会的な規範に従って行動すること",
        "option_d": "慎重に検討した上で決定すること",
        "correct_answer": "B",
        "explanation": "「恣意的（しいてき）」は arbitrary / capricious という意味で、論理的な根拠なく気ままに行うことを指します。",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N1",
        "question_type": "vocabulary",
        "question_text": "「齟齬」の読み方と意味として正しいものはどれですか。",
        "option_a": "そご・食い違い・不一致",
        "option_b": "しょご・失敗・過ち",
        "option_c": "そきょ・逃げること",
        "option_d": "せいご・正しい語",
        "correct_answer": "A",
        "explanation": "「齟齬（そご）」は discrepancy / inconsistency という意味で、「齟齬が生じる」＝「a discrepancy arises」",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N1",
        "question_type": "vocabulary",
        "question_text": "政府の（　）な政策に対して、国民からの批判が高まっている。",
        "option_a": "ずさん",
        "option_b": "せいかく",
        "option_c": "てきせつ",
        "option_d": "こんみつ",
        "correct_answer": "A",
        "explanation": "「杜撰（ずさん）な」は sloppy / careless / slipshod という意味で、批判を浴びるのに適した文脈です。",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N1",
        "question_type": "vocabulary",
        "question_text": "「蓋然性」の意味はどれですか。",
        "option_a": "物事が確実に起こること",
        "option_b": "物事が起こる可能性・確からしさ",
        "option_c": "物事が過去に起きたこと",
        "option_d": "物事が不可能であること",
        "correct_answer": "B",
        "explanation": "「蓋然性（がいぜんせい）」は probability / likelihood という意味です。「蓋然性が高い」＝「highly probable」",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N1",
        "question_type": "vocabulary",
        "question_text": "「逡巡」の読み方と意味として正しいものはどれですか。",
        "option_a": "しゅんじゅん・ためらい・躊躇",
        "option_b": "じゅんしゅ・規則に従うこと",
        "option_c": "しゅんかん・瞬間",
        "option_d": "しゅんかん・素早く動くこと",
        "correct_answer": "A",
        "explanation": "「逡巡（しゅんじゅん）」は hesitation / vacillation という意味です。「逡巡する」＝「hesitate / waver」",
        "source_url": "",
        "passage": "",
    },
]


# ---------------------------------------------------------------------------
# N1 — Grammar (8 questions)
# ---------------------------------------------------------------------------

_N1_GRAMMAR: list[dict] = [
    {
        "level": "N1",
        "question_type": "grammar",
        "question_text": "彼が来られない___、会議を延期しましょう。",
        "option_a": "とすれば",
        "option_b": "ようでは",
        "option_c": "以上は",
        "option_d": "からには",
        "correct_answer": "C",
        "explanation": "「以上は」は「その状況である以上」という意味で、前件が理由・根拠となり後件で判断・行動を述べます。「来られない以上は延期すべき」が自然です。",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N1",
        "question_type": "grammar",
        "question_text": "彼のような天才___、この問題は造作もないことだろう。",
        "option_a": "ともなると",
        "option_b": "ならでは",
        "option_c": "をもってしても",
        "option_d": "にあっては",
        "correct_answer": "A",
        "explanation": "「〜ともなると」は「when it comes to someone of the level of ~」という意味で、高いレベルの存在に達した場合の自然な帰結を表します。",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N1",
        "question_type": "grammar",
        "question_text": "多くの反対意見が出た___、その計画は最終的に承認された。",
        "option_a": "にもかかわらず",
        "option_b": "ゆえに",
        "option_c": "からこそ",
        "option_d": "をもって",
        "correct_answer": "A",
        "explanation": "「にもかかわらず」は despite / in spite of という意味で、逆接を表します。「反対意見にもかかわらず承認された」が自然です。",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N1",
        "question_type": "grammar",
        "question_text": "この技術は一度習得した___、生涯役に立つものだ。",
        "option_a": "が最後",
        "option_b": "からには",
        "option_c": "ともなれば",
        "option_d": "とあれば",
        "correct_answer": "B",
        "explanation": "「〜からには」は「now that ~ / since ~, (one must)」という意味で、状況を前提として結論・義務を述べます。「習得したからには役立つ」が正しい文脈です。",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N1",
        "question_type": "grammar",
        "question_text": "経済危機___、政府は緊急対策を講じた。",
        "option_a": "に際して",
        "option_b": "をもとに",
        "option_c": "をふまえて",
        "option_d": "にわたって",
        "correct_answer": "A",
        "explanation": "「〜に際して」は upon / at the time of という意味で、重要な出来事や場面において何かをする、という文脈に使います。",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N1",
        "question_type": "grammar",
        "question_text": "この映画は、観る者の心を揺さぶら___おかない傑作だ。",
        "option_a": "ずには",
        "option_b": "ないでは",
        "option_c": "なくては",
        "option_d": "ではいられ",
        "correct_answer": "A",
        "explanation": "「〜ずにはおかない」は「cannot help but ~ / inevitably ~」という意味の慣用表現です。「揺さぶらずにはおかない」＝「cannot fail to move (the audience)」",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N1",
        "question_type": "grammar",
        "question_text": "彼女の才能___、このプロジェクトの成功はなかったと言っても過言ではない。",
        "option_a": "なしには",
        "option_b": "をはじめ",
        "option_c": "のもとで",
        "option_d": "にわたって",
        "correct_answer": "A",
        "explanation": "「〜なしには〜ない」は「without ~ / ~ is impossible without ~」という意味です。「才能なしには成功はなかった」が正しい文脈です。",
        "source_url": "",
        "passage": "",
    },
    {
        "level": "N1",
        "question_type": "grammar",
        "question_text": "長年の研究___にして、ようやくこの定理が証明された。",
        "option_a": "をもって",
        "option_b": "だからこそ",
        "option_c": "のみ",
        "option_d": "にして",
        "correct_answer": "D",
        "explanation": "「〜にして〜」は「only through ~ / by means of ~」という意味で、「長年の研究にしてようやく」＝「only after years of research, finally」",
        "source_url": "",
        "passage": "",
    },
]


# ---------------------------------------------------------------------------
# N1 — Reading (4 questions)
# ---------------------------------------------------------------------------

_N1_READING_PASSAGE_1 = (
    "言語は単なるコミュニケーションの道具ではなく、思考そのものを形作る媒介でもある。"
    "サピア＝ウォーフ仮説によれば、ある言語を話す人々は、その言語の構造に影響を受けた形で世界を認識するという。"
    "例えば、色彩語彙が豊富な言語を話す人は、微妙な色の違いをより精確に区別できるとされる。"
    "しかし、この仮説には批判もあり、言語が思考を決定するのではなく、"
    "あくまでも影響を与えるに過ぎないという「言語相対性」の立場が現在では主流である。"
    "いずれにせよ、複数の言語を習得することは、異なる視点から世界を捉える能力を涵養することに繋がると言えよう。"
)

_N1_READING_PASSAGE_2 = (
    "民主主義の根幹は、国民が政治に参加し、自らの意志を反映させることにある。"
    "しかし、現代社会においては、情報過多と偽情報の拡散により、合理的な判断を下すことが困難になっている。"
    "SNSのアルゴリズムは、ユーザーの既存の信念を強化するコンテンツを優先的に表示するため、"
    "「エコーチェンバー」現象が生じやすく、社会の分極化を助長する恐れがある。"
    "真の民主主義を守るためには、メディアリテラシーの教育を充実させ、"
    "市民が批判的思考を持って情報に接する能力を育成することが急務である。"
)

_N1_READING: list[dict] = [
    {
        "level": "N1",
        "question_type": "reading",
        "question_text": "サピア＝ウォーフ仮説について、文章ではどのように述べていますか。",
        "option_a": "言語は思考を完全に決定するという仮説で、現在も広く支持されている",
        "option_b": "言語が世界の認識に影響を与えるという仮説で、現在は言語相対性の立場が主流",
        "option_c": "複数の言語を習得しても、思考には影響がないとする仮説",
        "option_d": "色彩語彙の多さと知性の高さは比例するという仮説",
        "correct_answer": "B",
        "explanation": "「言語が思考を決定するのではなく、あくまでも影響を与えるに過ぎないという『言語相対性』の立場が現在では主流」とあります。",
        "source_url": "",
        "passage": _N1_READING_PASSAGE_1,
    },
    {
        "level": "N1",
        "question_type": "reading",
        "question_text": "筆者が複数の言語習得の価値について述べていることとして最も適切なものはどれですか。",
        "option_a": "就職や出世のために有利になる",
        "option_b": "異なる視点から世界を捉える能力を涵養することに繋がる",
        "option_c": "母国語の能力を低下させる可能性がある",
        "option_d": "論理的思考力を弱める可能性がある",
        "correct_answer": "B",
        "explanation": "「複数の言語を習得することは、異なる視点から世界を捉える能力を涵養することに繋がる」と結論として述べています。",
        "source_url": "",
        "passage": _N1_READING_PASSAGE_1,
    },
    {
        "level": "N1",
        "question_type": "reading",
        "question_text": "「エコーチェンバー」現象とはどのようなものですか。文章から読み取れる内容を選んでください。",
        "option_a": "音楽が反響する特殊な部屋で、集中力が高まる現象",
        "option_b": "SNSのアルゴリズムが既存の信念を強化するコンテンツを優先し、社会の分極化を助長する現象",
        "option_c": "偽情報が急速に広まり、社会的パニックが起きる現象",
        "option_d": "政治家の発言がメディアに増幅されて伝わる現象",
        "correct_answer": "B",
        "explanation": "「SNSのアルゴリズムは、ユーザーの既存の信念を強化するコンテンツを優先的に表示するため、『エコーチェンバー』現象が生じやすく、社会の分極化を助長する恐れがある」とあります。",
        "source_url": "",
        "passage": _N1_READING_PASSAGE_2,
    },
    {
        "level": "N1",
        "question_type": "reading",
        "question_text": "民主主義を守るために筆者が最も重要と主張していることは何ですか。",
        "option_a": "SNSの利用を規制する法律を作ること",
        "option_b": "政治家が正確な情報を発信すること",
        "option_c": "市民が批判的思考を持って情報に接する能力を育成すること",
        "option_d": "新聞やテレビなど伝統的メディアを支援すること",
        "correct_answer": "C",
        "explanation": "「メディアリテラシーの教育を充実させ、市民が批判的思考を持って情報に接する能力を育成することが急務である」と述べています。",
        "source_url": "",
        "passage": _N1_READING_PASSAGE_2,
    },
]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_seed_questions() -> list[dict]:
    """
    Return the complete list of JLPT-style seed questions.

    Breakdown
    ---------
    * N5: 8 vocabulary + 8 grammar + 4 reading = 20 questions
    * N4: 8 vocabulary + 8 grammar + 4 reading = 20 questions
    * N3: 8 vocabulary + 8 grammar + 4 reading = 20 questions
    * N2: 8 vocabulary + 8 grammar + 4 reading = 20 questions
    * N1: 8 vocabulary + 8 grammar + 4 reading = 20 questions
    Total: 100 questions
    """
    return (
        _N5_VOCAB
        + _N5_GRAMMAR
        + _N5_READING
        + _N4_VOCAB
        + _N4_GRAMMAR
        + _N4_READING
        + _N3_VOCAB
        + _N3_GRAMMAR
        + _N3_READING
        + _N2_VOCAB
        + _N2_GRAMMAR
        + _N2_READING
        + _N1_VOCAB
        + _N1_GRAMMAR
        + _N1_READING
    )


def seed_database(db_session) -> None:
    """
    Insert seed questions into the database if the question table is empty.

    This function assumes that ``db_session`` exposes a SQLAlchemy-style
    interface:  ``query(Model).count()``, ``bulk_insert_mappings(Model, data)``,
    and ``commit()``.  It imports the ``Question`` model lazily so that this
    module can be imported even when the ORM is not yet configured.

    Args:
        db_session: An active SQLAlchemy ``Session`` instance.
    """
    # Lazy import to avoid a hard dependency on the ORM layer.
    try:
        from backend.models import Question  # type: ignore[import]
    except ImportError:
        try:
            from models import Question  # type: ignore[import]
        except ImportError as exc:
            raise ImportError(
                "Cannot import Question model. "
                "Ensure 'backend.models' or 'models' is on the Python path."
            ) from exc

    existing_count: int = db_session.query(Question).count()
    if existing_count > 0:
        print(
            f"[seed_database] Database already contains {existing_count} question(s). "
            f"Skipping seed."
        )
        return

    questions = get_seed_questions()
    db_session.bulk_insert_mappings(Question, questions)
    db_session.commit()
    print(f"[seed_database] Successfully seeded {len(questions)} question(s) into the database.")
