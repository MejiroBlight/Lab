import cv2
import os
import shutil
import tempfile
from tkinter import Tk, filedialog, simpledialog
import platform

def get_drive_letter(path):
    """
    指定されたパスのドライブ文字（Windowsの場合）またはルートパス（Linux/Macの場合）を取得します。
    """
    if platform.system() == 'Windows':
        return os.path.splitdrive(path)[0]
    else:
        # Linux/Macでは最上位ディレクトリを取得
        return os.path.abspath(path).split(os.sep)[1]

def is_nas_path(script_path, target_path):
    """
    現在のスクリプトのドライブと指定フォルダのドライブが異なる場合、NASと判定します。
    """
    script_drive = get_drive_letter(script_path)
    target_drive = get_drive_letter(target_path)
    return script_drive != target_drive

def copy_with_progress(source_folder, dest_folder):
    """
    フォルダを一時ディレクトリにコピーし、進捗を表示します。
    """
    # コピーする全ファイルのリストを取得
    all_files = []
    for root, _, files in os.walk(source_folder):
        for file in files:
            all_files.append(os.path.join(root, file))

    total_files = len(all_files)
    print(f"コピーするファイル数: {total_files}")

    for index, src_path in enumerate(all_files, start=1):
        # コピー先のパスを生成
        relative_path = os.path.relpath(src_path, source_folder)
        dest_path = os.path.join(dest_folder, relative_path)

        # コピー先のフォルダを作成
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)

        # ファイルをコピー
        shutil.copy2(src_path, dest_path)

        # 進捗状況を表示
        print(f"コピー進捗: {index}/{total_files} ({(index / total_files) * 100:.2f}%)")

def copy_folder_to_temp(source_folder):
    """
    指定されたフォルダを一時ディレクトリにコピーし、進捗を表示します。
    """
    temp_dir = tempfile.mkdtemp()  # 一時ディレクトリ作成
    dest_folder = os.path.join(temp_dir, os.path.basename(source_folder))
    print(f"フォルダを一時ディレクトリにコピー中: {dest_folder}")
    copy_with_progress(source_folder, dest_folder)
    return dest_folder

def create_video_from_bmp():
    # Tkinterの初期化
    root = Tk()
    root.withdraw()  # Tkinterウィンドウを隠す

    # スクリプトの実行パス
    script_path = os.path.abspath(__file__)

    # フォルダ選択ダイアログ
    folder_path = filedialog.askdirectory(title="BMPファイルが格納されたフォルダを選択してください")
    if not folder_path:
        print("フォルダが選択されませんでした。終了します。")
        return

    # 画像表示時間の指定
    display_time = simpledialog.askfloat("画像表示時間", "1枚の画像の表示時間を秒単位で指定してください（例: 0.5）:")
    if display_time is None:
        print("画像表示時間が指定されませんでした。終了します。")
        return

    # フォルダがNAS上にある場合、一時フォルダにコピー
    temp_folder = None
    if is_nas_path(script_path, folder_path):
        print("指定されたフォルダはNAS上にあると判定されました。一時フォルダにコピーします...")
        temp_folder = copy_folder_to_temp(folder_path)
        folder_path = temp_folder

    # フォルダ内のBMPファイルを取得
    images = [f for f in os.listdir(folder_path) if f.lower().endswith('.bmp')]
    if not images:
        print("指定されたフォルダにBMPファイルがありません。終了します。")
        return

    images.sort()  # ファイル名順にソート（任意）

    # 最初の画像を読み込み、解像度を取得
    first_image_path = os.path.join(folder_path, images[0])
    first_image = cv2.imread(first_image_path)
    height, width, _ = first_image.shape

    # 動画ファイルの保存パス
    save_path = filedialog.asksaveasfilename(
        title="保存する動画ファイル名を指定してください",
        defaultextension=".mp4",
        filetypes=[("MP4ファイル", "*.mp4")]
    )
    if not save_path:
        print("保存先が指定されませんでした。終了します。")
        return

    # 動画ファイルの設定
    fps = int(1 / display_time)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # MP4形式
    video_writer = cv2.VideoWriter(save_path, fourcc, fps, (width, height))

    # BMP画像を動画に追加（進捗を表示）
    total_images = len(images)
    print(f"全{total_images}枚の画像を処理します...")

    for index, image_name in enumerate(images):
        image_path = os.path.join(folder_path, image_name)
        image = cv2.imread(image_path)
        if image is None:
            print(f"画像の読み込みに失敗しました: {image_path}")
            continue

        video_writer.write(image)

        # 進捗状況を表示
        print(f"BMP読み込み: {index + 1}/{total_images} ({(index + 1) / total_images * 100:.2f}%)")

    video_writer.release()
    print(f"動画が作成されました: {save_path}")
    print("処理が完了しました。")

    # 一時フォルダの削除
    if temp_folder:
        print(f"一時フォルダを削除します: {temp_folder}")
        shutil.rmtree(temp_folder)

if __name__ == "__main__":
    create_video_from_bmp()

