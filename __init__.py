bl_info = {
    "name": "Project Packer Export",
    "author": "Your Name",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "File > External Data",
    "description": "Pack resources, save to new folder, and unpack.",
    "warning": "",
    "wiki_url": "",
    "category": "Import-Export",
}

import bpy
import os

# オペレーター（機能本体）の定義
class EXPORT_OT_ProjectPacker(bpy.types.Operator):
    """現在のプロジェクトをパックして別フォルダに書き出します"""
    bl_idname = "project.pack_export" # システム上のID（一意である必要がある）
    bl_label = "Export Project Package" # メニューに表示される名前
    bl_options = {'REGISTER', 'UNDO'} # アンドゥ可能にする設定

    def execute(self, context):
        # 1. 現在のBlendファイルの情報を取得
        current_filepath = bpy.data.filepath
        if not current_filepath:
            self.report({'ERROR'}, "エラー: 先にBlendファイルを保存してください。")
            return {'CANCELLED'}

        # パス情報の整理
        current_dir = os.path.dirname(current_filepath)
        filename = os.path.basename(current_filepath)
        project_name = os.path.splitext(filename)[0]

        # 2. 出力先のフォルダを作成
        export_root_dir = os.path.join(current_dir, project_name + "_Packed") # フォルダ名が重複しないよう _Packed を付与
        os.makedirs(export_root_dir, exist_ok=True)
        
        # 新しいBlendファイルのパス
        new_blend_path = os.path.join(export_root_dir, filename)

        self.report({'INFO'}, "--- 処理開始 ---")

        # 3. データを全てパック (Pack All)
        try:
            bpy.ops.file.pack_all()
            
            # 4. 新しい場所に別名保存
            # copy=Falseなので、現在開いているファイルが新しいファイルに切り替わります
            bpy.ops.wm.save_as_mainfile(filepath=new_blend_path, copy=False)
            
            # 5. データを展開 (Unpack All) -> 'textures' フォルダ生成
            bpy.ops.file.unpack_all(method='WRITE_LOCAL') 

            # 6. 自動パック設定を解除して保存
            bpy.context.blend_data.use_autopack = False
            bpy.ops.wm.save_mainfile()
            
            self.report({'INFO'}, f"完了: {export_root_dir} に書き出しました")
            
            # フォルダをエクスプローラーで開く（オプション：Windowsの場合）
            # os.startfile(export_root_dir) 

        except Exception as e:
            self.report({'ERROR'}, f"エラーが発生しました: {str(e)}")
            return {'CANCELLED'}

        return {'FINISHED'}

# メニューへの追加処理
def menu_func(self, context):
    self.layout.operator(EXPORT_OT_ProjectPacker.bl_idname)

# 登録処理
def register():
    bpy.utils.register_class(EXPORT_OT_ProjectPacker)
    # 「ファイル」>「外部データ」メニューに追加
    bpy.types.TOPBAR_MT_file_external_data.append(menu_func)

# 解除処理
def unregister():
    bpy.types.TOPBAR_MT_file_external_data.remove(menu_func)
    bpy.utils.unregister_class(EXPORT_OT_ProjectPacker)

if __name__ == "__main__":
    register()
