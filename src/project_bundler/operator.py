# operator.py
import bpy
from bpy_extras.io_utils import ExportHelper 
from . import core # 同じ階層にある core.py を読み込む

class EXPORT_OT_ProjectPacker(bpy.types.Operator, ExportHelper):
    """プロジェクトを一つのフォルダにまとめて書き出します"""
    bl_idname = "project.pack_export"
    bl_label = "Export Project Bundle"
    bl_options = {'REGISTER', 'UNDO'}

    # ==========================================
    # ファイルブラウザ用の設定
    # ==========================================
    filename_ext = ".blend" 
    filter_glob: bpy.props.StringProperty(
        default="*.blend",
        options={'HIDDEN'},
        maxlen=255,
    )

    # ==========================================
    # UIオプション用のプロパティ（設定項目）を定義
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

    # ==========================================
    # エクスポート画面の右パネルにUIを描画する関数
    # ==========================================
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
    # 実行時の処理（core.pyに丸投げする）
    # ==========================================
    def execute(self, context):
        # ユーザーがUIで選んだ設定を辞書にまとめる
        settings = {
            'filepath': self.filepath,
            'delimiter_choice': self.delimiter_choice,
            'custom_delimiter': self.custom_delimiter,
            'split_direction': self.split_direction,
            'min_files_to_group': self.min_files_to_group
        }
        
        # 実際の処理は core.py の process_export 関数に行わせる
        # self を渡すことで、core側で self.report (メッセージ表示) が使えるようにする
        return core.process_export(self, context, settings)
