# operator.py
import bpy
from bpy_extras.io_utils import ExportHelper 
from . import core # 裏方のロジックを読み込む

class EXPORT_OT_ProjectPacker(bpy.types.Operator, ExportHelper):
    bl_idname = "project.pack_export"
    bl_label = "Export Project Bundle"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".blend" 
    # ... (filter_glob, delimiter_choice 等のプロパティ定義はそのままここへ) ...

    def draw(self, context):
        # ... (UIの描画ロジックはそのままここへ) ...
        pass

    def execute(self, context):
        # ユーザーがUIで選んだ設定をまとめて、core.pyの関数に渡すだけ！
        settings = {
            'filepath': self.filepath,
            'delimiter_choice': self.delimiter_choice,
            'custom_delimiter': self.custom_delimiter,
            'split_direction': self.split_direction,
            'min_files_to_group': self.min_files_to_group
        }
        
        # 実際の処理は core.py にやらせる
        return core.process_export(self, context, settings)
