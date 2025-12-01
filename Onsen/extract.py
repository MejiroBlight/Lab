import re
import json
from geopy.geocoders import GoogleV3
from params import Params


geolocator = GoogleV3(Params.API_KEY)

def parse_facility_block(block):
    # 施設名
    name = re.search(r"<span class='nm'>(.*?)</span>", block)
    name = name.group(1) if name else None

    # 住所（市町村＋番地）
    address = re.search(r"<a href='[^']*'>(.*?)</a>([^<]*)", block)
    city = "石川県" + address.group(1) if address else None
    full_address = city + address.group(2).strip() if address else None
    location = geolocator.geocode(full_address) if full_address else None
    print(city, location)
    latitude = location.latitude if location else None
    longitude = location.longitude if location else None

    # 設備
    features = re.findall(r"<div class='flag (?!flag_off)[^']*'>(.*?)</div>", block)

    # 泉質
    spring_types = re.findall(r"<div class='flag (enka|tanjun|tansan|ryusan|nisan)'>(.*?)</div>", block)
    spring_types = [t[1] for t in spring_types]

    return {
        "name": name,
        "latitude": latitude,
        "longitude": longitude,
        "features": features,
        "spring_types": spring_types,
    }

# ファイル読み込み
with open('Data.txt', encoding='utf-8') as f:
    text = f.read()

# 施設ごとに分割
blocks = re.split(r"</tr><tr", text)
data_list = [parse_facility_block(block) for block in blocks if block.strip()]

# JSON保存
with open('Data.json', 'w', encoding='utf-8') as f:
    json.dump(data_list, f, ensure_ascii=False, indent=2)
