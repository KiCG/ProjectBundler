import bpy
import os
import shutil
import platform
import traceback
from collections import defaultdict

def process_export(operator, context, settings):
    """
    アドオンのメイン処理を行う関数
    """
    # 1. 現在の（元の）ファイルパスを確認
    orig_filepath = bpy.data.filepath
    
    if not orig_filepath:
        operator.report({'ERROR'}, "先にBlendファイルを一度保存して、基準となるパスを決定してください。")
        return {'CANCELLED'}

    # ユーザー設定の取得
    target_filepath = settings.get('filepath')
    delimiter_choice = settings.get('delimiter_choice', '_')
    custom_delimiter = settings.get('custom_delimiter', '-')
    direction = settings.get('split_direction', 'BACK')
    min_files = settings.get('min_files_to_group', 2)

    # パス情報の整理
    target_dir = os.path.dirname(target_filepath)
    filename = os.path.basename(target_filepath)
    project_name = os.path.splitext(filename)[0]

    # 保存用の親フォルダを作成
    export_folder_path = os.path.join(target_dir, project_name + "_Bundle")
    try:
        os.makedirs(export_folder_path, exist_ok=True)
    except OSError as e:
        operator.report({'ERROR'}, f"フォルダ作成エラー: {e}")
        return {'CANCELLED'}

    final_blend_path = os.path.join(export_folder_path, filename)
    textures_dir = os.path.join(export_folder_path, "textures")

    operator.report({'INFO'}, "--- Project Bundler 処理開始 ---")

    # 復元用のパスを記録する辞書
    orig_image_paths = {}

    try:
        # 2. テクスチャのパス記録とグループ化の準備
        groups = defaultdict(list)
        missing_files = []

        delimiter = custom_delimiter if delimiter_choice == 'CUSTOM' else delimiter_choice

        for img in bpy.data.images:
            # 既にパック（埋め込み）されている画像は、いじらずそのままにする
            if img.packed_file:
                continue

            if img.source == 'FILE' and img.filepath:
                abs_path = bpy.path.abspath(img.filepath)
                
                # ファイルが存在しない場合は警告用に記録してスキップ
                if not os.path.exists(abs_path):
                    missing_files.append(img.name)
                    continue

                # 後で復元するために元のパスを記録
                orig_image_paths[img] = img.filepath

                file_name = os.path.basename(abs_path)
                name_no_ext, ext = os.path.splitext(file_name)

                # 区切り文字によるグループ判定
                prefix = "_NO_GROUP_"
                if delimiter and delimiter in name_no_ext:
                    if direction == 'BACK':
                        prefix = name_no_ext.rsplit(delimiter, 1)[0]
                    else:
                        prefix = name_no_ext.split(delimiter, 1)[0]

                groups[prefix].append((img, abs_path, file_name))

        if missing_files:
            operator.report({'WARNING'}, f"{len(missing_files)} 個の欠落ファイルをスキップしました")

        # 3. ファイルの物理コピーと、Blender内のパスの一時書き換え
        if groups:
            os.makedirs(textures_dir, exist_ok=True)

        for prefix, items in groups.items():
            use_subfolder = (prefix != "_NO_GROUP_" and len(items) >= min_files)

            if use_subfolder:
                subfolder_path = os.path.join(textures_dir, prefix)
                os.makedirs(subfolder_path, exist_ok=True)
                # 削除: rel_folder = f"//textures/{prefix}/"
            else:
                subfolder_path = textures_dir
                # 削除: rel_folder = "//textures/"

            for img, abs_path, file_name in items:
                dest_path = os.path.join(subfolder_path, file_name)
                
                # OSの機能を使って画像をコピー
                shutil.copy2(abs_path, dest_path)
                
                # ★修正ポイント：Blenderに「コピー先の絶対パス」を渡し、正しい相対パスを計算させる
                img.filepath = bpy.path.relpath(dest_path)

        # ==========================================
        # 4. 未保存の変更を含めて、Bundle先にセーブする
        # ==========================================
        # ★ copy=True を使うことで、現在の作業状態を維持したまま、指定パスに書き出し保存ができる
        bpy.ops.wm.save_as_mainfile(filepath=final_blend_path, copy=True)

        # ==========================================
        # 5. 【復元処理】書き換えたパスをすべて元に戻す
        # ==========================================
        for img, original_path in orig_image_paths.items():
            img.filepath = original_path

        operator.report({'INFO'}, f"書き出し成功: {export_folder_path}")

        # フォルダを開く（Windows / Mac対応）
        if platform.system() == "Windows":
            os.startfile(export_folder_path)
        elif platform.system() == "Darwin":
            import subprocess
            subprocess.call(["open", export_folder_path])

    except Exception as e:
        # エラーが起きた場合も、確実にパスを元に戻してユーザーのデータを守る
        for img, original_path in orig_image_paths.items():
            img.filepath = original_path
        
        operator.report({'ERROR'}, f"予期せぬエラー: {str(e)}")
        traceback.print_exc()
        return {'CANCELLED'}

    return {'FINISHED'}
