# Pillowを使って画像のB成分のみを抽出し新しい画像として保存するサンプル

# Pillow, tkinterを使ってファイルダイアログから画像を選択し、R/G/Bのどれかを抽出して保存

from PIL import Image
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import os

def extract_channel_image(input_path, output_path, channel):
	img = Image.open(input_path).convert('RGB')
	width, height = img.size
	pixels = img.load()
	new_img = Image.new('RGB', (width, height))
	new_pixels = new_img.load()
	import sys
	for y in range(height):
		for x in range(width):
			r, g, b = pixels[x, y]
			if channel == 'R':
				new_pixels[x, y] = (r, 0, 0)
			elif channel == 'G':
				new_pixels[x, y] = (0, g, 0)
			elif channel == 'B':
				new_pixels[x, y] = (0, 0, b)
		# 進行度を10%単位で表示
		if height >= 10 and y % (height // 10) == 0:
			percent = int(y / height * 100)
			print(f"進行度: {percent}%")
			sys.stdout.flush()
	print("進行度: 100%")
	new_img.save(output_path)

def extract_channel_video(input_path, output_path, channel):
	import cv2
	import sys
	cap = cv2.VideoCapture(input_path)
	if not cap.isOpened():
		messagebox.showerror('エラー', '動画ファイルを開けませんでした')
		return
	fourcc = cv2.VideoWriter_fourcc(*'mp4v')
	fps = cap.get(cv2.CAP_PROP_FPS)
	width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
	height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
	total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
	out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
	channel_idx = {'R':2, 'G':1, 'B':0}[channel]
	frame_num = 0
	next_percent = 0
	while True:
		ret, frame = cap.read()
		if not ret:
			break
		zeros = frame.copy()
		zeros[:,:,:] = 0
		zeros[:,:,channel_idx] = frame[:,:,channel_idx]
		out.write(zeros)
		frame_num += 1
		# 進行度を10%単位で表示
		if total_frames > 0:
			percent = int(frame_num / total_frames * 100)
			if percent >= next_percent and percent <= 100:
				print(f"進行度: {percent}%")
				sys.stdout.flush()
				next_percent += 10
	print("進行度: 100%")
	cap.release()
	out.release()

def is_video_file(path):
	ext = os.path.splitext(path)[1].lower()
	return ext in ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']


def main():
	root = tk.Tk()
	root.withdraw()  # メインウィンドウを表示しない

	# 入力ファイル選択（画像または動画）
	input_path = filedialog.askopenfilename(
		title='画像または動画ファイルを選択',
		filetypes=[
			('画像/動画ファイル', '*.png;*.jpg;*.jpeg;*.bmp;*.tif;*.tiff;*.mp4;*.avi;*.mov;*.mkv;*.wmv;*.flv;*.webm'),
			('すべてのファイル', '*.*')
		]
	)
	if not input_path:
		messagebox.showinfo('中止', 'ファイルが選択されませんでした')
		return

	# チャンネル選択
	channel = simpledialog.askstring('チャンネル選択', '抽出するチャンネルを入力してください (R, G, B):')
	if not channel or channel.upper() not in ['R', 'G', 'B']:
		messagebox.showinfo('中止', '正しいチャンネルが選択されませんでした')
		return
	channel = channel.upper()

	# 保存ファイル選択
	if is_video_file(input_path):
		output_types = [('MP4', '*.mp4'), ('AVI', '*.avi'), ('すべてのファイル', '*.*')]
		default_ext = '.mp4'
	else:
		output_types = [('PNG', '*.png'), ('JPEG', '*.jpg;*.jpeg'), ('BMP', '*.bmp')]
		default_ext = '.png'
	output_path = filedialog.asksaveasfilename(title='保存先を選択', defaultextension=default_ext, filetypes=output_types)
	if not output_path:
		messagebox.showinfo('中止', '保存先が選択されませんでした')
		return

	if is_video_file(input_path):
		try:
			import cv2
		except ImportError:
			messagebox.showerror('エラー', '動画処理にはopencv-pythonが必要です。\npip install opencv-python でインストールしてください。')
			return
		extract_channel_video(input_path, output_path, channel)
	else:
		extract_channel_image(input_path, output_path, channel)
	messagebox.showinfo('完了', f'保存しました: {output_path}')

if __name__ == "__main__":
	main()
