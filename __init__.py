bl_info = {
    "name": "Project Bundler",
    "author": "Kishi Ryusei",
    "version": (1, 6), # バージョン更新
    "blender": (4, 0, 0),
    "location": "File > Export > Project Bundler",
    "description": "リソースを一括書き出しし、テクスチャを自動整理します",
    "warning": "",
    "wiki_url": "",
    "category": "Import-Export",
}

import bpy
import os
import shutil
from collections import defaultdict
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

    # ==========================================
    # UIオプション用のプロパティを定義
    # ==========================================
    delimiter_choice: bpy.props.EnumProperty(
        name="区切り文字",
        description="グループ化の基準にする文字を選びます",
        items=(
            ('_', "アンダースコア (_)", ""),
            ('.', "ドット (.)", ""),
            ('CUSTOM', "カスタム", "任意の文字を入力します"),
        ),
        default='_'
    )

    custom_delimiter: bpy.props.StringProperty(
        name="カスタム文字",
        description="区切りに使用する任意の文字を入力してください",
        default="-"
    )

    split_direction: bpy.props.EnumProperty(
        name="区切る位置",
        description="名前の前から探すか、後ろから探すかを選びます",
        items=(
            ('BACK', "後ろから (最後)", "最後の区切り文字を基準にします (推奨)"),
            ('FRONT', "前から (最初)", "最初の区切り文字を基準にします"),
        ),
        default='BACK'
    )

    min_files_to_group: bpy.props.IntProperty(
        name="フォルダ化の最小ファイル数",
        description="同じグループのファイルがこの数以上ある場合のみフォルダを作成します",
        default=2,
        min=1, # 最小値は1（1つでもフォルダ化する）
        max=100
    )

    # エクスポート画面の右パネルにUIを描画する関数
    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="Smart Folder 設定:")
        
        box.prop(self, "delimiter_choice")
        # 「カスタム」が選ばれた時だけ入力欄を表示する
        if self.delimiter_choice == 'CUSTOM':
            box.prop(self, "custom_delimiter")
            
        box.prop(self, "split_direction")
        
        layout.separator() # 少し隙間を空ける
        
        box2 = layout.box()
        box2.prop(self, "min_files_to_group")
    # ==========================================

    def execute(self, context):
        target_filepath = self.filepath
        target_dir = os.path.dirname(target_filepath)
        filename = os.path.basename(target_filepath)
        project_name = os.path.splitext(filename)[0]

        export_folder_path = os.path.join(target_dir, project_name + "_Bundle")
        os.makedirs(export_folder_path, exist_ok=True)
        final_blend_path = os.path.join(export_folder_path, filename)

        self.report({'INFO'}, "--- Project Bundler 処理開始 ---")

        try:
            # 2. データをパック
            packed_count = 0
            missing_files = []
            for image in bpy.data.images:
                if image.source == 'FILE' and not image.packed_file:
                    abs_path = bpy.path.abspath(image.filepath)
                    if os.path.exists(abs_path):
                        try:
                            image.pack()
                            packed_count += 1
                        except Exception:
                            missing_files.append(image.name)
                    else:
                        if image.filepath:
                            missing_files.append(image.name)
            
            if missing_files:
                self.report({'WARNING'}, f"{len(missing_files)} 個の欠落ファイルをスキップ")

            # 3. 新しい場所に保存
            bpy.ops.wm.save_as_mainfile(filepath=final_blend_path, copy=False)
            
            # 4. データを展開
            bpy.ops.file.unpack_all(method='WRITE_LOCAL') 

            # ==========================================
            # 4.5 テクスチャの自動整理（Smart Folder）
            # ==========================================
            textures_dir = os.path.join(export_folder_path, "textures")
            
            if os.path.exists(textures_dir):
                groups = defaultdict(list)
                
                # 使用する区切り文字を決定
                if self.delimiter_choice == 'CUSTOM':
                    delimiter = self.custom_delimiter
                else:
                    delimiter = self.delimiter_choice
                
                direction = self.split_direction

                for file_name in os.listdir(textures_dir):
                    file_path = os.path.join(textures_dir, file_name)
                    if not os.path.isfile(file_path):
                        continue
                    
                    name_no_ext, ext = os.path.splitext(file_name)
                    
                    # 区切り文字が空でなく、かつファイル名に含まれているかチェック
                    if delimiter and delimiter in name_no_ext:
                        if direction == 'BACK':
                            prefix = name_no_ext.rsplit(delimiter, 1)[0]
                        else:
                            prefix = name_no_ext.split(delimiter, 1)[0]
                        
                        groups[prefix].append(file_name)
                    else:
                        groups["_NO_GROUP_"].append(file_name)
                
                # フォルダ作成・移動・Blenderパス更新
                for prefix, files in groups.items():
                    # 条件: NO_GROUPでない ＆ ファイル数が設定したN個以上
                    if prefix != "_NO_GROUP_" and len(files) >= self.min_files_to_group:
                        subfolder_path = os.path.join(textures_dir, prefix)
                        os.makedirs(subfolder_path, exist_ok=True)
                        
                        for file_name in files:
                            old_path = os.path.join(textures_dir, file_name)
                            new_path = os.path.join(subfolder_path, file_name)
                            
                            shutil.move(old_path, new_path)
                            
                            for img in bpy.data.images:
                                if img.filepath and os.path.basename(img.filepath) == file_name:
                                    img.filepath = f"//textures/{prefix}/{file_name}"
                    # 条件を満たさない（N個未満の）ファイルは、textures フォルダの直下にそのまま残る
            # ==========================================

            # 5. 自動パック設定を解除して保存
            bpy.context.blend_data.use_autopack = False
            bpy.ops.wm.save_mainfile()
            
            self.report({'INFO'}, f"書き出し成功: {export_folder_path}")
            
            import platform
            if platform.system() == "Windows":
                os.startfile(export_folder_path)
            elif platform.system() == "Darwin":
                import subprocess
                subprocess.call(["open", export_folder_path])

        except Exception as e:
            self.report({'ERROR'}, f"予期せぬエラー: {str(e)}")
            import traceback
            traceback.print_exc()
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
