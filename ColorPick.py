# シンプルなカラーピッカーアプリ
# 画像をダイアログから読み込み、クリックした座標とRGB値をコンソールに表示

import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk



class ColorPickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title('カラーピッカー')

        # 上部フレームとボタン
        top_frame = tk.Frame(root)
        top_frame.pack(side=tk.TOP, fill=tk.X)
        select_btn = tk.Button(top_frame, text='画像を選択', command=self.load_image)
        select_btn.pack(side=tk.LEFT, padx=5, pady=5)

        # 座標・RGB表示ラベル
        self.info_label = tk.Label(top_frame, text='座標: (-, -)  RGB: (-, -, -)')
        self.info_label.pack(side=tk.LEFT, padx=10)

        # キャンバス
        self.canvas = tk.Canvas(root)
        self.canvas.pack()
        self.img = None
        self.photo = None
        self.pixels = None

    def load_image(self):
        file_path = filedialog.askopenfilename(title='画像ファイルを選択', filetypes=[('画像ファイル', '*.png;*.jpg;*.jpeg;*.bmp;*.tif;*.tiff')])
        if not file_path:
            print('画像ファイルが選択されませんでした')
            return
        self.img = Image.open(file_path).convert('RGB')
        self.photo = ImageTk.PhotoImage(self.img)
        self.canvas.config(width=self.img.width, height=self.img.height)
        self.canvas.delete('all')
        self.canvas.create_image(0, 0, anchor='nw', image=self.photo)
        self.pixels = self.img.load()
        self.canvas.bind('<Button-1>', self.on_click)
        self.canvas.bind('<Motion>', self.on_motion)
        self.info_label.config(text='座標: (-, -)  RGB: (-, -, -)')

    def on_click(self, event):
        if self.img is None:
            return
        x, y = event.x, event.y
        if 0 <= x < self.img.width and 0 <= y < self.img.height:
            r, g, b = self.pixels[x, y]
            print(f'座標: ({x}, {y}), RGB: ({r}, {g}, {b})')
        else:
            print('画像外をクリックしました')

    def on_motion(self, event):
        if self.img is None:
            self.info_label.config(text='座標: (-, -)  RGB: (-, -, -)')
            return
        x, y = event.x, event.y
        if 0 <= x < self.img.width and 0 <= y < self.img.height:
            r, g, b = self.pixels[x, y]
            self.info_label.config(text=f'座標: ({x}, {y})  RGB: ({r}, {g}, {b})')
        else:
            self.info_label.config(text='座標: (-, -)  RGB: (-, -, -)')

if __name__ == '__main__':
    root = tk.Tk()
    app = ColorPickerApp(root)
    root.mainloop()
