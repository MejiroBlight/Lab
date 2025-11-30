import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json


class OnsenData:
    name: str
    latitude: float
    longitude: float
    spring_types: list

with open('Data.json', encoding='utf-8') as f:
    data = json.load(f)

filtered = [d for d in data if 'features' in d and '天然温泉' in d['features']]

onsen_list = []
for item in filtered:
    onsen = OnsenData()
    onsen.name = item['name']
    onsen.latitude = item['latitude']
    onsen.longitude = item['longitude']
    onsen.spring_types = item['spring_types']
    onsen_list.append(onsen)

print(f"Total Onsen with Natural Hot Springs: {len(onsen_list)}")
