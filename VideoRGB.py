import cv2
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt

# 動画ファイルを読み込む
def load_video():
    global current_video, cap, original_width, original_height
    filepath = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi *.mkv")])
    if filepath:
        current_video = filepath
        cap = cv2.VideoCapture(filepath)
        original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        display_frame(0)  # 初期フレームを表示
        scrollbar.config(to=int(cap.get(cv2.CAP_PROP_FRAME_COUNT) - 1))  # フレーム数を設定

# 指定したフレーム番号での画像を表示
def display_frame(frame_number):
    global current_frame, resized_frame
    current_frame = frame_number
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = cap.read()
    if ret:
        # フレームをTkinterに表示するために縮小
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        resized_frame = cv2.resize(frame_rgb, (fixed_width, fixed_height))
        img = Image.fromarray(resized_frame)
        img_tk = ImageTk.PhotoImage(img)
        label_image.config(image=img_tk)
        label_image.image = img_tk

# スクロールバーでフレーム位置を更新
def on_scroll(event):
    frame_number = scrollbar.get()
    display_frame(int(frame_number))

# フレーム画像上でクリックされた位置を取得
def on_click(event):
    global selected_x, selected_y, original_x, original_y
    # クリック位置の座標（縮小後）を取得
    selected_x = event.x
    selected_y = event.y
    
    # 座標を元のフレーム解像度に変換
    original_x = int(selected_x * original_width / fixed_width)
    original_y = int(selected_y * original_height / fixed_height)
    print(f"選択した縮小後の座標: x={selected_x}, y={selected_y}")
    print(f"元の座標に変換: x={original_x}, y={original_y}")

# 解析ボタンが押されたときに解析を実行
def analyze_video():
    if not current_video or selected_x is None or selected_y is None:
        print("動画がロードされていないか、座標が選択されていません")
        return

    cap = cv2.VideoCapture(current_video)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    rgb_values = []
    region_size = int(entry_region_size.get())  # ユーザーが入力した取得領域サイズ

    # 選択された座標近辺の平均RGB値を各フレームで取得
    for frame_idx in range(frame_count):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # 選択された点近辺の領域サイズを元の座標で計算
            x1 = max(0, original_x - region_size // 2)
            y1 = max(0, original_y - region_size // 2)
            x2 = min(frame_rgb.shape[1], original_x + region_size // 2)
            y2 = min(frame_rgb.shape[0], original_y + region_size // 2)

            # 選択された領域の平均RGBを計算
            region = frame_rgb[y1:y2, x1:x2]
            avg_color = np.mean(region, axis=(0, 1))  # 近辺の平均RGB値
            rgb_values.append(avg_color)

    cap.release()

    # RGB値の変化をグラフで表示
    rgb_values = np.array(rgb_values)
    plt.figure()
    plt.plot(rgb_values[:, 0], color='red', label='R')
    plt.plot(rgb_values[:, 1], color='green', label='G')
    plt.plot(rgb_values[:, 2], color='blue', label='B')
    plt.xlabel('Frame')
    plt.ylabel('Average RGB')
    plt.legend()
    plt.show()

# Tkinter ウィンドウのセットアップ
root = tk.Tk()
root.title("動画解析アプリ")
root.geometry("800x600")

# 動画フレームを表示するラベル
label_image = tk.Label(root)
label_image.pack()
label_image.bind("<Button-1>", on_click)  # クリックイベントをバインド

# ファイル読み込みボタン
btn_load = tk.Button(root, text="動画を読み込む", command=load_video)
btn_load.pack()

# 解析ボタン
btn_analyze = tk.Button(root, text="解析を開始", command=analyze_video)
btn_analyze.pack()

# RGB取得領域のサイズを入力するエントリーボックス
tk.Label(root, text="RGB取得領域サイズ (ピクセル)").pack()
entry_region_size = tk.Entry(root)
entry_region_size.insert(0, "5")  # デフォルトサイズ5x5
entry_region_size.pack()

# 横スクロールバー
scrollbar = ttk.Scale(root, from_=0, to=100, orient="horizontal", command=on_scroll)
scrollbar.pack(fill="x")

# グローバル変数
current_video = ""
cap = None
selected_x = None
selected_y = None
original_x = None
original_y = None
current_frame = 0

# 画像の表示サイズを固定 (例: 500x400ピクセル)
fixed_width = 500
fixed_height = 400
resized_frame = None
original_width = None
original_height = None

# メインループ
root.mainloop()
