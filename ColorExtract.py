# Pillowを使って画像のB成分のみを抽出し新しい画像として保存するサンプル

# Pillow, tkinterを使ってファイルダイアログから画像を選択し、R/G/Bのどれかを抽出して保存
from PIL import Image
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox

def extract_channel(input_path, output_path, channel):
	img = Image.open(input_path).convert('RGB')
	width, height = img.size
	pixels = img.load()
	new_img = Image.new('RGB', (width, height))
	new_pixels = new_img.load()

	for y in range(height):
		for x in range(width):
			r, g, b = pixels[x, y]
			if channel == 'R':
				new_pixels[x, y] = (r, 0, 0)
			elif channel == 'G':
				new_pixels[x, y] = (0, g, 0)
			elif channel == 'B':
				new_pixels[x, y] = (0, 0, b)

	new_img.save(output_path)

def main():
	root = tk.Tk()
	root.withdraw()  # メインウィンドウを表示しない

	# 入力ファイル選択
	input_path = filedialog.askopenfilename(title='画像ファイルを選択', filetypes=[('画像ファイル', '*.png;*.jpg;*.jpeg;*.bmp;*.tif;*.tiff')])
	if not input_path:
		messagebox.showinfo('中止', '画像ファイルが選択されませんでした')
		return

	# チャンネル選択
	channel = simpledialog.askstring('チャンネル選択', '抽出するチャンネルを入力してください (R, G, B):')
	if not channel or channel.upper() not in ['R', 'G', 'B']:
		messagebox.showinfo('中止', '正しいチャンネルが選択されませんでした')
		return
	channel = channel.upper()

	# 保存ファイル選択
	output_path = filedialog.asksaveasfilename(title='保存先を選択', defaultextension='.png', filetypes=[('PNG', '*.png'), ('JPEG', '*.jpg;*.jpeg'), ('BMP', '*.bmp')])
	if not output_path:
		messagebox.showinfo('中止', '保存先が選択されませんでした')
		return

	extract_channel(input_path, output_path, channel)
	messagebox.showinfo('完了', f'保存しました: {output_path}')

if __name__ == "__main__":
	main()
