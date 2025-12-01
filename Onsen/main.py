import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from PIL import Image
from params import Params
from geopy.geocoders import GoogleV3

MAP_NE = [37.54, 137.36]
MAP_SW = [36.13, 136.03]

geolocator = GoogleV3(Params.API_KEY)
geology_types = []
img = Image.open('map.png').convert('RGB')
width, height = img.size
pixels = img.load()

class OnsenData:
    name: str
    latitude: float
    longitude: float
    is_natural: bool
    geology_type: int
    spring_types: list[str]

onsen_list: list[OnsenData] = []

def latlon_to_xy(lat, lon, lat_ne, lon_ne, lat_sw, lon_sw, width, height):
    x = (lon - lon_sw) / (lon_ne - lon_sw) * width
    y = (lat_ne - lat) / (lat_ne - lat_sw) * height
    return int(x), int(y)

def get_or_append_index(lst, value):
    try:
        return lst.index(value)
    except ValueError:
        lst.append(value)
        return len(lst) - 1

with open('Data.json', encoding='utf-8') as f:
    data = json.load(f)

for item in data:
    onsen = OnsenData()
    onsen.name = item['name']
    onsen.latitude = item['latitude']
    onsen.longitude = item['longitude']
    onsen.spring_types = item['spring_types']
    onsen.is_natural = '天然温泉' in item['features']
    onsen.geology_type = -1
    onsen_list.append(onsen)

print(f"Total: {len(onsen_list)}")

for onsen in onsen_list:
    x, y = latlon_to_xy(onsen.latitude, onsen.longitude, MAP_NE[0], MAP_NE[1], MAP_SW[0], MAP_SW[1], width, height)
    if 0 <= x < width and 0 <= y < height:
        color = pixels[x, y]
        onsen.geology_type = get_or_append_index(geology_types, color)
        #print(f"{onsen.name} 地質タイプ: {onsen.geology_type}")
    else:
        #print(f"{onsen.name} 画像範囲外")
        continue

data = pd.DataFrame([{
    'latitude': onsen.latitude,
    'longitude': onsen.longitude,
    'is_natural': onsen.is_natural,
    'geology_type': onsen.geology_type,
    'spring_types': ','.join(onsen.spring_types)
} for onsen in onsen_list])

X = data[['latitude', 'longitude', 'geology_type']]
y = data["is_natural"].astype(int)

categorical_features = ["geology_type"]
numeric_features = ["latitude", "longitude"]

preprocess = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(), categorical_features),
        ("num", "passthrough", numeric_features)
    ]
)

model = Pipeline(steps=[
    ("preprocess", preprocess),
    ("rf", RandomForestClassifier(
        n_estimators=Params.N_ESTIMATORS,
        max_depth=Params.MAX_DEPTH,
        random_state=Params.RANDOM_STATE
    ))
])

model.fit(X, y)

sample_location = geolocator.geocode("金沢駅")
if sample_location is None:
    print("サンプル地点のジオコードに失敗しました")
    exit()
sample_geo_type = -1
sample_x, sample_y = latlon_to_xy(sample_location.latitude, sample_location.longitude, MAP_NE[0], MAP_NE[1], MAP_SW[0], MAP_SW[1], width, height)
if 0 <= sample_x < width and 0 <= sample_y < height:
    sample_color = pixels[sample_x, sample_y]
    sample_geo_type = get_or_append_index(geology_types, sample_color)
sample = pd.DataFrame([{
    'latitude': sample_location.latitude,
    'longitude': sample_location.longitude,
    'geology_type': sample_geo_type
}])

proba = model.predict_proba(sample)[0, 1]
print("予測された温泉存在確率:", proba)

