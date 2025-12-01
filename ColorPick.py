# シンプルなカラーピッカーアプリ
# 画像をダイアログから読み込み、クリックした座標とRGB値をコンソールに表示

import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk




class ColorPickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title('カラーピッカー')

        # 固定ウィンドウサイズ
        self.window_width = 600
        self.window_height = 400
        self.root.geometry(f'{self.window_width}x{self.window_height}')
        self.root.resizable(False, False)

        # 上部フレームとボタン
        top_frame = tk.Frame(root)
        top_frame.pack(side=tk.TOP, fill=tk.X)
        select_btn = tk.Button(top_frame, text='画像を選択', command=self.load_image)
        select_btn.pack(side=tk.LEFT, padx=5, pady=5)

        # 座標・RGB表示ラベル
        self.info_label = tk.Label(top_frame, text='座標: (-, -)  RGB: (-, -, -)')
        self.info_label.pack(side=tk.LEFT, padx=10)

        # キャンバス
        self.canvas = tk.Canvas(root, width=self.window_width, height=self.window_height)
        self.canvas.pack()
        self.img = None
        self.photo = None
        self.pixels = None
        self.scale_x = 1.0
        self.scale_y = 1.0

    def load_image(self):
        file_path = filedialog.askopenfilename(title='画像ファイルを選択', filetypes=[('画像ファイル', '*.png;*.jpg;*.jpeg;*.bmp;*.tif;*.tiff')])
        if not file_path:
            print('画像ファイルが選択されませんでした')
            return
        self.img = Image.open(file_path).convert('RGB')
        img_w, img_h = self.img.size
        # 拡大縮小率を計算
        scale_x = self.window_width / img_w
        scale_y = self.window_height / img_h
        scale = min(scale_x, scale_y, 1.0)  # 拡大はしない
        disp_w = int(img_w * scale)
        disp_h = int(img_h * scale)
        self.scale_x = img_w / disp_w
        self.scale_y = img_h / disp_h
        resized_img = self.img.resize((disp_w, disp_h), Image.LANCZOS)
        self.photo = ImageTk.PhotoImage(resized_img)
        self.canvas.config(width=self.window_width, height=self.window_height)
        self.canvas.delete('all')
        # 画像を中央に表示
        x_offset = (self.window_width - disp_w) // 2
        y_offset = (self.window_height - disp_h) // 2
        self.canvas.create_image(x_offset, y_offset, anchor='nw', image=self.photo)
        self.pixels = self.img.load()
        self.img_disp_offset = (x_offset, y_offset, disp_w, disp_h)
        self.canvas.bind('<Button-1>', self.on_click)
        self.canvas.bind('<Motion>', self.on_motion)
        self.info_label.config(text='座標: (-, -)  RGB: (-, -, -)')

    def get_img_coords(self, event):
        if not hasattr(self, 'img_disp_offset'):
            return None, None
        x_offset, y_offset, disp_w, disp_h = self.img_disp_offset
        x = event.x - x_offset
        y = event.y - y_offset
        if 0 <= x < disp_w and 0 <= y < disp_h:
            img_x = int(x * self.scale_x)
            img_y = int(y * self.scale_y)
            if 0 <= img_x < self.img.width and 0 <= img_y < self.img.height:
                return img_x, img_y
        return None, None

    def on_click(self, event):
        if self.img is None:
            return
        img_x, img_y = self.get_img_coords(event)
        if img_x is not None and img_y is not None:
            r, g, b = self.pixels[img_x, img_y]
            print(f'座標: ({img_x}, {img_y}), RGB: ({r}, {g}, {b})')
        else:
            print('画像外をクリックしました')

    def on_motion(self, event):
        if self.img is None:
            self.info_label.config(text='座標: (-, -)  RGB: (-, -, -)')
            return
        img_x, img_y = self.get_img_coords(event)
        if img_x is not None and img_y is not None:
            r, g, b = self.pixels[img_x, img_y]
            self.info_label.config(text=f'座標: ({img_x}, {img_y})  RGB: ({r}, {g}, {b})')
        else:
            self.info_label.config(text='座標: (-, -)  RGB: (-, -, -)')

if __name__ == '__main__':
    root = tk.Tk()
    app = ColorPickerApp(root)
    root.mainloop()
