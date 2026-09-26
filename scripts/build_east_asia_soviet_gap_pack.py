import hashlib
import json
import mimetypes
import os
import time
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
VOL = ROOT / "data" / "volumes"
IMG_EA = ROOT / "assets" / "images" / "east_asia_gap_round1_2026-09-26"
IMG_SU = ROOT / "assets" / "images" / "soviet_gap_round4_2026-09-26"
CACHE = ROOT / "sources" / "cache" / "user_atlases"
for path in (VOL, IMG_EA, IMG_SU, CACHE):
    path.mkdir(parents=True, exist_ok=True)

UA = "world-medals/1.0 (offline research catalogue)"


def fetch(url, dest):
    if dest.is_file() and dest.stat().st_size:
        data = dest.read_bytes()
        with Image.open(dest) as im:
            im.verify()
        return hashlib.sha256(data).hexdigest(), len(data)
    if os.environ.get("WORLD_MEDALS_NO_NETWORK") == "1":
        raise RuntimeError("not cached")
    clean = url.split("?", 1)[0]
    if "upload.wikimedia.org/wikipedia/commons/" in clean:
        filename = urllib.parse.unquote(clean.rsplit("/", 1)[-1])
        clean = "https://commons.wikimedia.org/wiki/Special:Redirect/file/" + urllib.parse.quote(filename, safe="()_-.,%") + "?width=1200"
    req = urllib.request.Request(clean, headers={"User-Agent": UA})
    last_error = None
    for attempt in range(1):
        try:
            with urllib.request.urlopen(req, timeout=45) as response:
                data = response.read()
            break
        except Exception as exc:
            last_error = exc
            time.sleep(2)
    else:
        raise last_error
    dest.write_bytes(data)
    with Image.open(dest) as im:
        im.verify()
    time.sleep(1.2)
    return hashlib.sha256(data).hexdigest(), len(data)


def commons_file_page(url):
    name = urllib.parse.unquote(url.split("/commons/", 1)[-1]).split("?", 1)[0]
    name = name.split("/", 2)[-1]
    return "https://commons.wikimedia.org/wiki/File:" + urllib.parse.quote(name, safe="()_-.,%")


east_asia = [
    # Republic of Korea: one official plate per award family, showing the complete current insignia set.
    ("ROK-ORD-01", "韩国", "无穷花大勋章", "무궁화대훈장", "大韩民国时期；现行官方图式", "官方图式·完整组件组合；无等级", "https://www.sanghun.go.kr/nation/images/contents/m_img_011.jpg", "https://www.sanghun.go.kr/nation/hunjang.html"),
    ("ROK-ORD-02", "韩国", "建国勋章", "건국훈장", "大韩民国时期；现行官方图式", "官方图式·五等级组合", "https://www.sanghun.go.kr/nation/images/contents/m_img_012.jpg", "https://www.sanghun.go.kr/nation/hunjang.html"),
    ("ROK-ORD-03", "韩国", "国民勋章", "국민훈장", "大韩民国时期；现行官方图式", "官方图式·五等级组合", "https://www.sanghun.go.kr/nation/images/contents/m_img_013.jpg", "https://www.sanghun.go.kr/nation/hunjang.html"),
    ("ROK-ORD-04", "韩国", "武功勋章", "무공훈장", "1950年设立；现行官方图式", "官方图式·五等级组合", "https://www.sanghun.go.kr/nation/images/contents/m_img_014.jpg", "https://www.sanghun.go.kr/nation/hunjang.html"),
    ("ROK-ORD-05", "韩国", "勤政勋章", "근정훈장", "大韩民国时期；现行官方图式", "官方图式·五等级组合", "https://www.sanghun.go.kr/nation/images/contents/m_img_015.jpg", "https://www.sanghun.go.kr/nation/hunjang.html"),
    ("ROK-ORD-06", "韩国", "保国勋章", "보국훈장", "大韩民国时期；现行官方图式", "官方图式·五等级组合", "https://www.sanghun.go.kr/nation/images/contents/m_img_016_1.jpg", "https://www.sanghun.go.kr/nation/hunjang.html"),
    ("ROK-ORD-07", "韩国", "修交勋章", "수교훈장", "大韩民国时期；现行官方图式", "官方图式·六种章名／五级结构组合", "https://www.sanghun.go.kr/nation/images/contents/m_img_021_1.jpg", "https://www.sanghun.go.kr/nation/hunjang.html"),
    ("ROK-ORD-08", "韩国", "产业勋章", "산업훈장", "大韩民国时期；现行官方图式", "官方图式·五等级组合", "https://www.sanghun.go.kr/nation/images/contents/m_img_027_1.jpg", "https://www.sanghun.go.kr/nation/hunjang.html"),
    ("ROK-ORD-09", "韩国", "新村勋章", "새마을훈장", "大韩民国时期；现行官方图式", "官方图式·五等级组合", "https://www.sanghun.go.kr/nation/images/contents/m_img_032_1.jpg", "https://www.sanghun.go.kr/nation/hunjang.html"),
    ("ROK-ORD-10", "韩国", "文化勋章", "문화훈장", "大韩民国时期；现行官方图式", "官方图式·五等级组合", "https://www.sanghun.go.kr/nation/images/contents/m_img_037_1.jpg", "https://www.sanghun.go.kr/nation/hunjang.html"),
    ("ROK-ORD-11", "韩国", "体育勋章", "체육훈장", "大韩民国时期；现行官方图式", "官方图式·五等级组合", "https://www.sanghun.go.kr/nation/images/contents/m_img_042_1.jpg", "https://www.sanghun.go.kr/nation/hunjang.html"),
    ("ROK-ORD-12", "韩国", "科学技术勋章", "과학기술훈장", "大韩民国时期；现行官方图式", "官方图式·五等级组合", "https://www.sanghun.go.kr/nation/images/contents/m_img_047_1.jpg", "https://www.sanghun.go.kr/nation/hunjang.html"),

    # Korean Empire.
    ("KOR-EMP-ORD-01", "大韩帝国", "金尺大勋章", "금척대훈장", "1900年设立", "历史图录插图·完整套件；图示等级构成见原图", "https://upload.wikimedia.org/wikipedia/commons/e/ef/Order_of_the_Gold_cheok.jpg", "https://en.wikipedia.org/wiki/Order_of_the_Golden_Ruler"),
    ("KOR-EMP-ORD-02", "大韩帝国", "瑞星大勋章", "서성대훈장", "1902年设立", "历史图录插图·完整套件；图示等级构成见原图", "https://upload.wikimedia.org/wikipedia/commons/e/e6/Order_of_the_Auspicious_Stars.jpg", "https://en.wikipedia.org/wiki/Order_of_the_Auspicious_Stars"),
    ("KOR-EMP-ORD-03", "大韩帝国", "李花大勋章", "이화대훈장", "1900年设立", "历史图录插图·完整套件；图示等级构成见原图", "https://upload.wikimedia.org/wikipedia/commons/d/da/Order_of_the_Plum_Blossom_01.jpg", "https://en.wikipedia.org/wiki/Order_of_the_Plum_Blossom"),
    ("KOR-EMP-ORD-04", "大韩帝国", "太极章", "태극장", "1900年设立", "历史图录插图·完整套件；图示等级待考", "https://upload.wikimedia.org/wikipedia/commons/5/57/Order_of_the_Taegeuk_01.jpg", "https://en.wikipedia.org/wiki/Order_of_the_Taegeuk"),

    # DPRK object images. Dates are only made exact when the award title itself fixes the anniversary.
    ("PRK-ORD-01", "朝鲜", "祖国解放战争胜利70周年纪念勋章", "조국해방전쟁승리 70돐 기념훈장", "2023年纪念版", "完整实物正面", "https://upload.wikimedia.org/wikipedia/commons/4/4a/Commemorative_Order_%2270th_Year_Anniversary_Of_the_Fatherland_Liberation_War_Victory%22.png", "https://commons.wikimedia.org/wiki/File:Commemorative_Order_%2270th_Year_Anniversary_Of_the_Fatherland_Liberation_War_Victory%22.png"),
    ("PRK-ORD-02", "朝鲜", "人民军建军纪念勋章", "조선인민군 창건 기념훈장", "朝鲜民主主义人民共和国时期", "完整实物正面；具体周年待考", "https://upload.wikimedia.org/wikipedia/commons/d/d0/Commemorative_Order_%22Anniversary_of_the_Foundation_of_the_People%27s_Army%22.jpg", "https://commons.wikimedia.org/wiki/File:Commemorative_Order_%22Anniversary_of_the_Foundation_of_the_People%27s_Army%22.jpg"),
    ("PRK-ORD-03", "朝鲜", "朝鲜民主主义人民共和国成立20周年纪念勋章", "조선민주주의인민공화국 창건 20돐 기념훈장", "1968年纪念版", "完整实物正背面", "https://upload.wikimedia.org/wikipedia/commons/7/7b/Commemorative_Order_20th_Anniversary_of_the_Foundation_of_the_Democratic_People%27s_Republic_of_Korea_-_Obverse_and_reverse.jpg", "https://commons.wikimedia.org/wiki/File:Commemorative_Order_20th_Anniversary_of_the_Foundation_of_the_Democratic_People%27s_Republic_of_Korea_-_Obverse_and_reverse.jpg"),
    ("PRK-ORD-04", "朝鲜", "农业贡献30周年纪念勋章", "농업 공로 30돐 기념훈장", "朝鲜民主主义人民共和国时期", "完整实物正面；原文规范名待考", "https://upload.wikimedia.org/wikipedia/commons/7/74/Commemorative_Order_30th_Anniversary_of_the_Agricultural_Presentation_-_Obverse.jpg", "https://commons.wikimedia.org/wiki/File:Commemorative_Order_30th_Anniversary_of_the_Agricultural_Presentation_-_Obverse.jpg"),
    ("PRK-ORD-05", "朝鲜", "祖国解放战争胜利40周年纪念勋章", "조국해방전쟁승리 40돐 기념훈장", "1993年纪念版", "完整实物正面", "https://upload.wikimedia.org/wikipedia/commons/a/af/Commemorative_Order_40th_Anniversary_of_Fatherland_Liberation_War_Victory_-_Obverse.jpg", "https://commons.wikimedia.org/wiki/File:Commemorative_Order_40th_Anniversary_of_Fatherland_Liberation_War_Victory_-_Obverse.jpg"),
    ("PRK-ORD-06", "朝鲜", "人民军建军60周年纪念勋章", "조선인민군 창건 60돐 기념훈장", "朝鲜民主主义人民共和国时期", "完整实物正面", "https://upload.wikimedia.org/wikipedia/commons/7/73/Commemorative_Order_60th_Anniversary_of_the_People%27s_Army_-_Obverse.jpg", "https://commons.wikimedia.org/wiki/File:Commemorative_Order_60th_Anniversary_of_the_People%27s_Army_-_Obverse.jpg"),
    ("PRK-ORD-07", "朝鲜", "首都建设纪念勋章", "수도건설 기념훈장", "朝鲜民主主义人民共和国时期", "完整实物正面；具体版次待考", "https://upload.wikimedia.org/wikipedia/commons/4/45/Commemorative_Order_Capital_Construction_-_Obverse.jpg", "https://commons.wikimedia.org/wiki/File:Commemorative_Order_Capital_Construction_-_Obverse.jpg"),
    ("PRK-ORD-08", "朝鲜", "军事工程服务荣誉勋章", "군사공병복무영예훈장", "朝鲜民主主义人民共和国时期", "完整实物正面；等级待考", "https://upload.wikimedia.org/wikipedia/commons/7/75/Military_Engineering_Service_Honour..jpg", "https://commons.wikimedia.org/wiki/File:Military_Engineering_Service_Honour..jpg"),
    ("PRK-ORD-09", "朝鲜", "煤矿服务荣誉勋章", "탄광복무영예훈장", "朝鲜民主主义人民共和国时期", "一级；完整实物正面", "https://upload.wikimedia.org/wikipedia/commons/2/21/Order_of_Colliery_Service_Honour_1st_Class_-_Obverse.jpg", "https://commons.wikimedia.org/wiki/File:Order_of_Colliery_Service_Honour_1st_Class_-_Obverse.jpg"),
    ("PRK-ORD-10", "朝鲜", "水产服务荣誉勋章", "수산복무영예훈장", "朝鲜民主主义人民共和国时期", "一级；完整实物正面", "https://upload.wikimedia.org/wikipedia/commons/4/48/Order_of_Fishery_Service_Honour_1st_Class.jpg", "https://commons.wikimedia.org/wiki/File:Order_of_Fishery_Service_Honour_1st_Class.jpg"),
    ("PRK-ORD-11", "朝鲜", "金正日勋章", "김정일훈장", "2012年设立", "完整实物正面", "https://upload.wikimedia.org/wikipedia/commons/b/bb/Order_of_Kim_Jong-il.jpg", "https://commons.wikimedia.org/wiki/File:Order_of_Kim_Jong-il.jpg"),
    ("PRK-ORD-12", "朝鲜", "劳动勋章", "로력훈장", "朝鲜民主主义人民共和国时期", "完整实物正面；具体制作版待考", "https://upload.wikimedia.org/wikipedia/commons/6/61/Order_of_korean_labour.jpg", "https://commons.wikimedia.org/wiki/File:Order_of_korean_labour.jpg"),
    ("PRK-ORD-13", "朝鲜", "军事服务荣誉勋章", "군사복무영예훈장", "朝鲜民主主义人民共和国时期", "一级；完整实物正面", "https://upload.wikimedia.org/wikipedia/commons/f/f9/Order_of_Military_Service_Honour_1st_Class_-_Obverse.jpg", "https://commons.wikimedia.org/wiki/File:Order_of_Military_Service_Honour_1st_Class_-_Obverse.jpg"),
    ("PRK-ORD-14", "朝鲜", "铁路服务荣誉勋章", "철도복무영예훈장", "朝鲜民主主义人民共和国时期", "一级；完整实物正面", "https://upload.wikimedia.org/wikipedia/commons/b/b7/Order_of_Railway_Service_Honour_1st_Class_-_Obverse.jpg", "https://commons.wikimedia.org/wiki/File:Order_of_Railway_Service_Honour_1st_Class_-_Obverse.jpg"),
    ("PRK-ORD-15", "朝鲜", "三大革命红旗勋章", "3대혁명붉은기훈장", "朝鲜民主主义人民共和国时期", "三级；完整实物正面", "https://upload.wikimedia.org/wikipedia/commons/1/1a/Order_of_the_Red_Banner_of_Three_Great_Revolutions_3_-_Obverse.png", "https://commons.wikimedia.org/wiki/File:Order_of_the_Red_Banner_of_Three_Great_Revolutions_3_-_Obverse.png"),

    # Republic of China.
    ("ROC-ORD-01", "中华民国", "国光勋章", "國光勳章", "1937年设立", "完整勋章图；具体制造版待考", "https://upload.wikimedia.org/wikipedia/commons/c/c5/%E5%9C%8B%E5%85%89%E5%8B%B3%E7%AB%A0.jpg", "https://en.wikipedia.org/wiki/Order_of_National_Glory"),
    ("ROC-ORD-02", "中华民国", "青天白日勋章", "青天白日勳章", "1929年设立", "完整勋章图；具体制造版待考", "https://upload.wikimedia.org/wikipedia/commons/3/31/%E9%9D%92%E5%A4%A9%E7%99%BD%E6%97%A5%E5%8B%B3%E7%AB%A0.jpg", "https://en.wikipedia.org/wiki/Order_of_Blue_Sky_and_White_Sun"),
    ("ROC-ORD-03", "中华民国", "宝鼎勋章", "寶鼎勳章", "1929年设立", "完整勋章图；图示等级待考", "https://upload.wikimedia.org/wikipedia/commons/9/99/%E5%AF%B6%E9%BC%8E%E5%8B%B3%E7%AB%A0.jpg", "https://en.wikipedia.org/wiki/Order_of_the_Sacred_Tripod"),
    ("ROC-ORD-04", "中华民国", "云麾勋章", "雲麾勳章", "1935年设立", "完整勋章图；图示等级待考", "https://upload.wikimedia.org/wikipedia/commons/7/7e/%E9%9B%B2%E9%BA%BE%E5%8B%B3%E7%AB%A0.jpg", "https://en.wikipedia.org/wiki/Order_of_the_Cloud_and_Banner"),
    ("ROC-ORD-05", "中华民国", "景星勋章", "景星勳章", "1941年设立", "完整勋章图；图示等级待考", "https://upload.wikimedia.org/wikipedia/commons/c/c6/%E6%99%AF%E6%98%9F%E5%8B%B3%E7%AB%A0.jpg", "https://en.wikipedia.org/wiki/Order_of_Brilliant_Star"),
    ("ROC-ORD-06", "中华民国", "卿云勋章", "卿雲勳章", "1941年设立", "完整勋章图；图示等级待考", "https://upload.wikimedia.org/wikipedia/commons/3/3b/%E5%8D%BF%E9%9B%B2%E5%8B%B3%E7%AB%A0.jpg", "https://en.wikipedia.org/wiki/Order_of_Propitious_Clouds"),
    ("ROC-ORD-07", "中华民国", "采玉大勋章", "采玉大勳章", "1933年设立", "完整勋章图；具体制造版待考", "https://upload.wikimedia.org/wikipedia/commons/6/68/%E9%87%87%E7%8E%89%E5%A4%A7%E5%8B%B3%E7%AB%A0.jpg", "https://en.wikipedia.org/wiki/Order_of_Brilliant_Jade"),
    ("ROC-ORD-08", "中华民国", "中正勋章", "中正勳章", "1980年设立", "完整勋章图；具体制造版待考", "https://upload.wikimedia.org/wikipedia/commons/0/01/%E4%B8%AD%E6%AD%A3%E5%8B%B3%E7%AB%A0.jpg", "https://en.wikipedia.org/wiki/Order_of_Chiang_Chung-Cheng"),
    ("ROC-ORD-09", "中华民国", "中山勋章", "中山勳章", "1941年设立", "完整勋章图；具体制造版待考", "https://upload.wikimedia.org/wikipedia/commons/c/c3/%E4%B8%AD%E5%B1%B1%E5%8B%B3%E7%AB%A0.jpg", "https://en.wikipedia.org/wiki/Order_of_Dr._Sun_Yat-sen"),
    ("ROC-ORD-10", "中华民国", "忠勇勋章", "忠勇勳章", "1944年设立", "完整勋章正面；具体制造版待考", "https://upload.wikimedia.org/wikipedia/commons/9/93/%E5%BF%A0%E5%8B%87%E5%8B%B3%E7%AB%A0_crop.jpg", "https://en.wikipedia.org/wiki/Order_of_Loyalty_and_Valour"),
]


soviet = [
    ("USSR-ORD-02", "十月革命勋章", "Орден Октябрьской Революции", "1967-10-31设立", "完整实物正面", "https://upload.wikimedia.org/wikipedia/commons/7/7b/Order_of_the_October_Revolution_%28obverse%29.jpg", "https://en.wikipedia.org/wiki/Order_of_the_October_Revolution"),
    ("USSR-ORD-03", "胜利勋章", "Орден «Победа»", "1943-11-08设立", "华西列夫斯基元帅实物；完整正面", "https://upload.wikimedia.org/wikipedia/commons/5/5b/Orden-Pobeda-Marshal_Vasilevsky.jpg", "https://en.wikipedia.org/wiki/Order_of_Victory"),
    ("USSR-ORD-06", "库图佐夫勋章", "Орден Кутузова", "1942-07-29设立", "完整实物正面；图示等级待考", "https://upload.wikimedia.org/wikipedia/commons/d/d8/Order_of_Kutuzov.jpg", "https://en.wikipedia.org/wiki/Order_of_Kutuzov"),
    ("USSR-ORD-07", "波格丹·赫梅利尼茨基勋章", "Орден Богдана Хмельницкого", "1943-10-10设立", "三级官方图式", "https://upload.wikimedia.org/wikipedia/commons/7/74/%D0%9E%D1%80%D0%B4%D0%B5%D0%BD-%D0%A5%D0%BC%D0%B5%D0%BB%D1%8C%D0%BD%D0%B8%D1%86%D1%8C%D0%BA%D0%BE%D0%B3%D0%BE-3%28%D0%A1%D0%A1%D0%A1%D0%A0%29.png", "https://en.wikipedia.org/wiki/Order_of_Bogdan_Khmelnitsky_(Soviet_Union)"),
    ("USSR-ORD-08", "亚历山大·涅夫斯基勋章", "Орден Александра Невского", "1942-07-29设立", "苏联式官方图式", "https://upload.wikimedia.org/wikipedia/commons/1/13/%D0%9E%D1%80%D0%B4%D0%B5%D0%BD_%D0%90%D0%BB%D0%B5%D0%BA%D1%81%D0%B0%D0%BD%D0%B4%D1%80%D0%B0_%D0%9D%D0%B5%D0%B2%D1%81%D0%BA%D0%BE%D0%B3%D0%BE_Vitalis_Taurus.png", "https://en.wikipedia.org/wiki/Order_of_Alexander_Nevsky"),
    ("USSR-ORD-11", "红星勋章", "Орден Красной Звезды", "1930-04-06设立", "完整实物正面", "https://upload.wikimedia.org/wikipedia/commons/0/0f/Order_of_the_Red_Star.jpg", "https://en.wikipedia.org/wiki/Order_of_the_Red_Star"),
    ("USSR-ORD-12", "卫国战争勋章", "Орден Отечественной войны", "1942-05-20设立", "一级官方图式", "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Order_of_the_Patriotic_War_%28Ist_class%29.svg/1200px-Order_of_the_Patriotic_War_%28Ist_class%29.svg.png", "https://en.wikipedia.org/wiki/Order_of_the_Patriotic_War"),
    ("USSR-ORD-13", "劳动红旗勋章", "Орден Трудового Красного Знамени", "1928-09-07设立", "完整实物正面", "https://upload.wikimedia.org/wikipedia/commons/5/5e/Order_of_the_Red_Banner_of_Labour_OBVERSE.jpg", "https://en.wikipedia.org/wiki/Order_of_the_Red_Banner_of_Labour"),
    ("USSR-ORD-14", "各族人民友谊勋章", "Орден Дружбы народов", "1972-12-17设立", "官方图式", "https://upload.wikimedia.org/wikipedia/commons/1/1e/Orden_De_La_Amistad_De_Los_Pueblos.png", "https://en.wikipedia.org/wiki/Order_of_Friendship_of_Peoples"),
    ("USSR-ORD-15", "荣誉勋章", "Орден «Знак Почёта»", "1935-11-25设立", "完整实物正面", "https://upload.wikimedia.org/wikipedia/commons/1/12/Znakpocheta2.jpg", "https://en.wikipedia.org/wiki/Order_of_the_Badge_of_Honour"),
    ("USSR-ORD-16", "光荣勋章", "Орден Славы", "1943-11-08设立", "三级；完整实物正面", "https://upload.wikimedia.org/wikipedia/commons/3/3c/Order_of_Glory_3rd_class.jpg", "https://en.wikipedia.org/wiki/Order_of_Glory"),
    ("USSR-ORD-17", "母亲光荣勋章", "Орден «Материнская слава»", "1944-07-08设立", "一至三级组合图", "https://upload.wikimedia.org/wikipedia/commons/6/65/Orders_of_Maternal_Glory.jpg", "https://en.wikipedia.org/wiki/Order_of_Maternal_Glory"),
    ("USSR-ORD-18", "英雄母亲勋章", "Орден «Мать-героиня»", "1944-07-08设立", "完整实物正面", "https://upload.wikimedia.org/wikipedia/commons/2/27/MotherHeroine.jpg", "https://en.wikipedia.org/wiki/Mother_Heroine"),
    ("USSR-ORD-19", "劳动光荣勋章", "Орден Трудовой Славы", "1974-01-18设立", "一级；完整实物正面", "https://upload.wikimedia.org/wikipedia/commons/f/f4/Order_of_Labour_Glory_1st.jpg", "https://en.wikipedia.org/wiki/Order_of_Labour_Glory"),
    ("USSR-ORD-20", "在苏联武装力量中为祖国服务勋章", "Орден «За службу Родине в Вооружённых Силах СССР»", "1974-10-28设立", "一级；完整实物正面", "https://upload.wikimedia.org/wikipedia/commons/d/d2/Order_For_Service_to_the_Homeland_1.jpg", "https://en.wikipedia.org/wiki/Order_%22For_Service_to_the_Homeland_in_the_Armed_Forces_of_the_USSR%22"),
    ("USSR-ORD-21", "个人英勇勋章", "Орден «За личное мужество»", "1988-12-28设立", "完整实物正面", "https://upload.wikimedia.org/wikipedia/commons/e/e9/%D0%9E%D1%80%D0%B4%D0%B5%D0%BD_%22%D0%97%D0%B0_%D0%BB%D0%B8%D1%87%D0%BD%D0%BE%D0%B5_%D0%BC%D1%83%D0%B6%D0%B5%D1%81%D1%82%D0%B2%D0%BE%22.jpg", "https://en.wikipedia.org/wiki/Order_%22For_Personal_Courage%22"),
    ("USSR-MED-06", "乌沙科夫奖章", "Медаль Ушакова", "1944-03-03设立", "完整实物正面", "https://upload.wikimedia.org/wikipedia/commons/e/ed/Medal_of_Ushakov.jpg", "https://en.wikipedia.org/wiki/Medal_of_Ushakov"),
    ("USSR-MED-07", "纳希莫夫奖章", "Медаль Нахимова", "1944-03-03设立", "官方图式", "https://upload.wikimedia.org/wikipedia/commons/5/5b/Medal_of_Nakhimov.png", "https://en.wikipedia.org/wiki/Medal_of_Nakhimov"),
]


def build(rows, out_dir, prefix, volume_name, record_name, manifest_name):
    records, images, failures = [], [], []
    for index, row in enumerate(rows, 1):
        if len(row) == 8:
            family, country, name, original, date, variant, url, source = row
        else:
            family, name, original, date, variant, url, source = row
            country = "苏联"
        ext = Path(urllib.parse.urlparse(url).path).suffix.lower()
        if ext not in {".jpg", ".jpeg", ".png", ".webp"}:
            ext = mimetypes.guess_extension("image/jpeg") or ".jpg"
        local = out_dir / f"{prefix}-{index:02d}{ext}"
        try:
            sha, size = fetch(url, local)
        except Exception as exc:
            failures.append({"family": family, "url": url, "error": str(exc)})
            continue
        view = f"{prefix.upper()}-IMG-{index:02d}"
        record_id = f"{family}-V01"
        records.append({
            "id": record_id,
            "family": family,
            "country_zh": country,
            "name": name,
            "original": original,
            "date": date,
            "variant": variant,
            "views": [{"key": view, "label": "完整图样"}],
            "source_ids": [source, commons_file_page(url) if "upload.wikimedia.org" in url else url],
        })
        images.append({
            "view_key": view,
            "local_path": local.relative_to(ROOT).as_posix(),
            "source_page_url": source,
            "original_file_url": url,
            "sha256": sha,
            "bytes": size,
        })
    (VOL / record_name).write_text(json.dumps({
        "as_of": "2026-09-26",
        "volume": volume_name,
        "scope": "来源优先整批差集；总表只作目录线索，正文图片均来自官方页面或已打开的Commons/Wikipedia对象页。",
        "records": records,
        "notes": ["没有使用绶带图作为章体图。", "等级或制造版无法由对象页确定者并入同名family并标待考。"],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    (VOL / manifest_name).write_text(json.dumps({
        "as_of": "2026-09-26",
        "volume": volume_name,
        "images": images,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    return len(records), len(images), failures


ea_counts = build(east_asia, IMG_EA, "eas-gap", "东亚来源优先差集批次1", "east_asia_gap_round1_2026-09-26.json", "east_asia_gap_round1_2026-09-26_manifest.json")
su_counts = "skipped; Soviet gap round 4 is built from the MedalBook directory by build_soviet_medalbook_gap_pack.py"
print({"east_asia": ea_counts, "soviet": su_counts})
