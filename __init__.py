bl_info = {
    "name": "Project Bundler",
    "author": "Kishi Ryusei",
    "version": (1, 2), # バージョン更新
    "blender": (4, 0, 0),
    "location": "File > Export > Project Bundler",
    "description": "フォルダを作成してリソースを一括書き出しします（欠落ファイルはスキップ）",
    "warning": "",
    "wiki_url": "",
    "category": "Import-Export",
}

import bpy
import os
from bpy_extras.io_utils import ExportHelper 

class EXPORT_OT_ProjectPacker(bpy.types.Operator, ExportHelper):
    """プロジェクトを一つのフォルダにまとめて書き出します"""
    bl_idname = "project.pack_export"
    bl_label = "Export Project Bundle"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".blend" 
    filter_glob: bpy.props.StringProperty(
        default="*.blend",
        options={'HIDDEN'},
        maxlen=255,
    )

    def execute(self, context):
        target_filepath = self.filepath
        target_dir = os.path.dirname(target_filepath)
        filename = os.path.basename(target_filepath)
        project_name = os.path.splitext(filename)[0]

        # 1. 保存用の親フォルダを作成
        export_folder_path = os.path.join(target_dir, project_name + "_Bundle")
        os.makedirs(export_folder_path, exist_ok=True)

        final_blend_path = os.path.join(export_folder_path, filename)

        self.report({'INFO'}, "--- Project Bundler 処理開始 ---")

        try:
            # 2. データをパック (Pack All) ※エラー回避版
            # 標準の pack_all() は一つでも欠けると止まるため、手動で画像をループしてパックします
            packed_count = 0
            missing_files = []

            for image in bpy.data.images:
                if image.source == 'FILE' and not image.packed_file:
                    # パスの絶対パス化を試みる
                    abs_path = bpy.path.abspath(image.filepath)
                    if os.path.exists(abs_path):
                        try:
                            image.pack()
                            packed_count += 1
                        except Exception:
                            missing_files.append(image.name)
                    else:
                        # ファイルが無い場合はリストに記録してスキップ
                        if image.filepath: # パスが空でない場合のみ警告
                            missing_files.append(image.name)
            
            if missing_files:
                self.report({'WARNING'}, f"{len(missing_files)} 個のファイルが見つからずスキップされました")
                print("Skipped files:", missing_files)

            # 3. 新しい場所に別名保存
            bpy.ops.wm.save_as_mainfile(filepath=final_blend_path, copy=False)
            
            # 4. データを展開 (Unpack All)
            # 見つからなかったファイル以外を展開します
            bpy.ops.file.unpack_all(method='WRITE_LOCAL') 

            # 5. 自動パック設定を解除して保存
            bpy.context.blend_data.use_autopack = False
            bpy.ops.wm.save_mainfile()
            
            self.report({'INFO'}, f"書き出し成功: {export_folder_path}")
            
            # フォルダを開く（Windows/Mac対応）
            import platform
            if platform.system() == "Windows":
                os.startfile(export_folder_path)
            elif platform.system() == "Darwin": # Mac
                import subprocess
                subprocess.call(["open", export_folder_path])

        except Exception as e:
            self.report({'ERROR'}, f"予期せぬエラー: {str(e)}")
            import traceback
            traceback.print_exc() # コンソール詳細出力
            return {'CANCELLED'}

        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(EXPORT_OT_ProjectPacker.bl_idname, text="Project Bundler (Folder)")

def register():
    bpy.utils.register_class(EXPORT_OT_ProjectPacker)
    bpy.types.TOPBAR_MT_file_export.append(menu_func)

def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(menu_func)
    bpy.utils.unregister_class(EXPORT_OT_ProjectPacker)

if __name__ == "__main__":
    register()
