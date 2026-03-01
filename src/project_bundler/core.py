# core.py
import bpy
import os
import shutil
from collections import defaultdict

def process_export(operator, context, settings):
    """
    operator: self.report({'INFO'}, ...) などでメッセージを出すために受け取る
    settings: operator.py から渡されたユーザー設定の辞書
    """
    target_filepath = settings['filepath']
    
    # ... (現在の execute の中身である、パック処理、Unpack、
    #      os.makedirs や shutil.move などのメインロジックをここに書く) ...
    
    # ユーザー設定へのアクセス例：
    # delimiter = settings['custom_delimiter'] if settings['delimiter_choice'] == 'CUSTOM' else settings['delimiter_choice']
    
    return {'FINISHED'}
