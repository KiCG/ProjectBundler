# __init__.py
bl_info = {
    "name": "Project Bundler",
    "author": "Kishi Ryusei",
    "version": (1, 6),
    "blender": (4, 0, 0),
    "location": "File > Export > Project Bundler",
    "category": "Import-Export",
}

import bpy
from .operator import EXPORT_OT_ProjectPacker # 分割したファイルを読み込む

classes = (
    EXPORT_OT_ProjectPacker,
)

def menu_func(self, context):
    self.layout.operator(EXPORT_OT_ProjectPacker.bl_idname, text="Project Bundler (Folder)")

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_file_export.append(menu_func)

def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(menu_func)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
