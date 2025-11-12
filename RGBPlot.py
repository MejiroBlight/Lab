import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw
import numpy as np
import matplotlib.pyplot as plt
import colorsys
import csv

# 定数
LINE_WIDTH = 3  # 線の太さ
CANVAS_WIDTH = 600
CANVAS_HEIGHT = 400

class ImageAnalysisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("画像解析アプリ")
        self.canvas = tk.Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
        self.canvas.pack()

        self.image = None
        self.image_copy = None  # キャンバスに表示するコピー用のイメージ
        self.scale_factor = 1.0  # 拡大率
        self.start_point = None
        self.end_point = None
        self.rgb_hsv_data = []
        self.current_plot = None  # グラフのウィンドウを管理

        # メニュー設定
        menubar = tk.Menu(root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="画像を開く", command=self.open_image)
        filemenu.add_separator()
        filemenu.add_command(label="終了", command=root.quit)
        menubar.add_cascade(label="ファイル", menu=filemenu)
        root.config(menu=menubar)

        # ボタンとラベル設定
        btn_frame = tk.Frame(root)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # 拡大率表示
        self.scale_label = tk.Label(btn_frame, text="拡大率: 100%")
        self.scale_label.grid(row=0, column=0, padx=5, pady=5)

        # 始点選択ボタンと座標表示
        self.start_button = tk.Button(btn_frame, text="始点を決定", command=self.set_start_mode, bg="lightgray")
        self.start_button.grid(row=1, column=0, padx=5, pady=5)
        self.start_label = tk.Label(btn_frame, text="始点: 未設定")
        self.start_label.grid(row=1, column=1, padx=5, pady=5)

        # 終点選択ボタンと座標表示
        self.end_button = tk.Button(btn_frame, text="終点を決定", command=self.set_end_mode, bg="lightgray")
        self.end_button.grid(row=2, column=0, padx=5, pady=5)
        self.end_label = tk.Label(btn_frame, text="終点: 未設定")
        self.end_label.grid(row=2, column=1, padx=5, pady=5)

        # CSV保存ボタン
        self.csv_button = tk.Button(btn_frame, text="CSV保存", command=self.save_csv)
        self.csv_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

        self.canvas.bind("<Button-1>", self.handle_click)

    def open_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.bmp")])
        if file_path:
            self.image = Image.open(file_path)
            self.scale_image_to_canvas()
            self.display_image()

    def scale_image_to_canvas(self):
        """キャンバスに収まるように画像を拡大・縮小する"""
        img_width, img_height = self.image.size
        scale_w = CANVAS_WIDTH / img_width
        scale_h = CANVAS_HEIGHT / img_height
        self.scale_factor = min(scale_w, scale_h)  # 画像がキャンバスに収まるようにスケールを決定

        new_size = (int(img_width * self.scale_factor), int(img_height * self.scale_factor))
        self.image_copy = self.image.resize(new_size, Image.Resampling.BILINEAR)  # キャンバスサイズに合わせてリサイズ

        # 拡大率ラベルの更新
        self.scale_label.config(text=f"拡大率: {int(self.scale_factor * 100)}%")

    def display_image(self):
        """キャンバスに画像を表示する"""
        self.photo_image = ImageTk.PhotoImage(self.image_copy)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image)

    def set_start_mode(self):
        """始点決定モードに設定"""
        self.mode = 'start'
        self.start_button.config(bg="lightblue")  # 始点モード選択時の色
        self.end_button.config(bg="lightgray")  # 終点モードは未選択状態の色

    def set_end_mode(self):
        """終点決定モードに設定"""
        self.mode = 'end'
        self.end_button.config(bg="lightblue")  # 終点モード選択時の色
        self.start_button.config(bg="lightgray")  # 始点モードは未選択状態の色

    def handle_click(self, event):
        """クリック時に始点か終点を設定"""
        if self.mode == 'start' and self.image_copy:
            # キャンバスのクリック座標を元画像の座標に変換
            self.start_point = (int(event.x / self.scale_factor), int(event.y / self.scale_factor))
            self.start_label.config(text=f"始点: {self.start_point}")
            self.mode = None  # モード解除
            self.start_button.config(bg="lightgray")  # モード解除後は元の色に戻す
        elif self.mode == 'end' and self.image_copy:
            # キャンバスのクリック座標を元画像の座標に変換
            self.end_point = (int(event.x / self.scale_factor), int(event.y / self.scale_factor))
            self.end_label.config(text=f"終点: {self.end_point}")
            self.mode = None  # モード解除
            self.end_button.config(bg="lightgray")  # モード解除後は元の色に戻す

        if self.start_point and self.end_point:
            # 新しい始点と終点が決まったら画像を再コピー
            self.image_copy = self.image.resize(
                (int(self.image.width * self.scale_factor), int(self.image.height * self.scale_factor))
            )
            self.draw_line_on_image()
            self.analyze_line()

    def draw_line_on_image(self):
        """始点と終点を結ぶ赤い線を画像上に描画する"""
        if self.image_copy:
            draw = ImageDraw.Draw(self.image_copy)
            # 元画像の始点と終点をキャンバス上の座標に変換
            scaled_start = (int(self.start_point[0] * self.scale_factor), int(self.start_point[1] * self.scale_factor))
            scaled_end = (int(self.end_point[0] * self.scale_factor), int(self.end_point[1] * self.scale_factor))
            draw.line([scaled_start, scaled_end], fill="red", width=LINE_WIDTH)
            self.display_image()

    def analyze_line(self):
        """線上のRGBとHSV値を解析し、散布図を表示"""
        if self.image is None or self.start_point is None or self.end_point is None:
            return

        # 以前のグラフウィンドウを閉じる
        if self.current_plot:
            plt.close(self.current_plot)

        # 画像をnumpy配列に変換
        image_array = np.array(self.image)

        # 線上の点を取得する
        x1, y1 = self.start_point
        x2, y2 = self.end_point
        num_points = max(abs(x2 - x1), abs(y2 - y1))
        x_values = np.linspace(x1, x2, num=num_points, dtype=int)
        y_values = np.linspace(y1, y2, num=num_points, dtype=int)

        self.rgb_hsv_data = []
        for idx, (x, y) in enumerate(zip(x_values, y_values)):
            r, g, b = image_array[y, x, :3]  # RGB値を取得
            hsv = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)  # HSV値に変換
            distance = np.sqrt((x - x1)**2 + (y - y1)**2)  # 始点からの距離を計算
            self.rgb_hsv_data.append({
                "distance": distance,
                "x": x,
                "y": y,
                "rgb": (r, g, b),
                "hsv": (int(hsv[0] * 360), int(hsv[1] * 100), int(hsv[2] * 100))
            })

        self.plot_rgb()

    def plot_rgb(self):
        """RGBの散布図を描画"""
        if not self.rgb_hsv_data:
            return

        distances = np.array([d["distance"] for d in self.rgb_hsv_data])
        rgb_values = np.array([d["rgb"] for d in self.rgb_hsv_data])

        # 新しいプロットウィンドウを作成
        self.current_plot = plt.figure()

        # RGBの散布図
        plt.scatter(distances, rgb_values[:, 0], color='r', label="R")
        plt.scatter(distances, rgb_values[:, 1], color='g', label="G")
        plt.scatter(distances, rgb_values[:, 2], color='b', label="B")
        plt.title("RGB散布図", fontname="MS Gothic")
        plt.xlabel("始点からの距離", fontname="MS Gothic")
        plt.ylabel("RGB値", fontname="MS Gothic")
        plt.legend()

        plt.tight_layout()
        plt.show()

    def save_csv(self):
        """RGBとHSV値をCSVとして保存"""
        if not self.rgb_hsv_data:
            messagebox.showerror("エラー", "データがありません。")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            with open(file_path, mode="w", newline='', encoding='shift-jis') as file:
                writer = csv.writer(file)
                # ヘッダー行
                writer.writerow(["距離", "x", "y", "R", "G", "B", "H", "S", "V"])
                for data in self.rgb_hsv_data:
                    distance = data["distance"]
                    x, y = data["x"], data["y"]
                    r, g, b = data["rgb"]
                    h, s, v = data["hsv"]
                    writer.writerow([distance, x, y, r, g, b, h, s, v])

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageAnalysisApp(root)
    root.mainloop()
