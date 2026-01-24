import bpy
import os

def export_project_via_packing():
    # 1. 現在のBlendファイルの情報を取得
    current_filepath = bpy.data.filepath
    if not current_filepath:
        print("エラー: 先にBlendファイルを保存してください。")
        return

    # パス情報の整理
    current_dir = os.path.dirname(current_filepath)
    filename = os.path.basename(current_filepath)
    project_name = os.path.splitext(filename)[0]

    # 2. 出力先のフォルダを作成
    # 構成: [現在のフォルダ] / [プロジェクト名] / [blendファイル & textures]
    export_root_dir = os.path.join(current_dir, project_name)
    os.makedirs(export_root_dir, exist_ok=True)
    
    # 新しいBlendファイルのパス
    new_blend_path = os.path.join(export_root_dir, filename)

    print("--- 処理開始 ---")

    # 3. データを全てパック (Pack All)
    # これで外部ファイルが一旦blendファイル内に取り込まれます
    bpy.ops.file.pack_all()
    print("ファイルをパックしました。")

    # 4. 新しい場所に別名保存
    # copy=Trueにすると、元のファイルを開いたまま複製保存しますが、
    # 後の展開操作のために、ここではコンテキストを移す(copy=False)のが一般的です
    bpy.ops.wm.save_as_mainfile(filepath=new_blend_path, copy=False)
    print(f"別名保存しました: {new_blend_path}")

    # 5. データを展開 (Unpack All)
    # method='WRITE_LOCAL' -> 現在のblendファイルの場所にテクスチャを書き出す
    # Blenderの仕様上、通常は 'textures' というフォルダが自動生成されます
    bpy.ops.file.unpack_all(method='WRITE_LOCAL') 
    print("リソースを展開しました。")

    # 6. 自動パック設定を解除
    # 展開後、自動パックがONになったままの場合があるのでOFFにして保存
    bpy.context.blend_data.use_autopack = False
    bpy.ops.wm.save_mainfile()
    
    print("--- 完了: プロジェクトの移行が完了しました ---")

# 実行
export_project_via_packing()
