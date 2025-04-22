# -*- coding: utf-8 -*-
import bpy
from bpy.props import EnumProperty, StringProperty, BoolProperty
from bpy.types import AddonPreferences

from ..panels.keymap_ui import draw_keymap, draw_hide_keymap
from .props_keymaps import keymap_Softimage, keymap_RigTools, keymap_OtherTools

# カスタムプロパティの登録
def register_properties():
    bpy.types.Scene.SItoBHide = StringProperty(
        name="SItoBHide",
        description="非表示オブジェクトのリスト",
        default=""
    )
    bpy.types.Collection.si_hidden_objects = StringProperty(
        name="SI Hidden Objects",
        description="非表示オブジェクトのリスト",
        default=""
    )

# カスタムプロパティの解除
def unregister_properties():
    del bpy.types.Scene.SItoBHide
    del bpy.types.Collection.si_hidden_objects

def get_addon_name():
    return "SItoB"

class SIKEYMAP_MT_AddonPreferences(AddonPreferences):
    bl_idname = get_addon_name()

    # タブ切り替え用のenumプロパティ
    tab_addon_menu: EnumProperty(
        name="Tab",
        description="",
        items=[
            ('Keymap', "Softimage", "", "KEYINGSET", 0),
            ('OtherTools', "OtherTools", "", "KEYINGSET2", 1),
            ('RigTools', "RigTools", "", "KEYINGSET2", 2),
            ('Link', "Link", "", "URL", 3)
        ],
        default='Keymap'
    )
    
    # 表示設定のプロパティ
    si_use_hide_viewport: BoolProperty(
        name="Disable in viewport",
        description="オブジェクトの表示/非表示に hide_viewport を使用します",
        default=True
    )
    
    si_use_hide_set: BoolProperty(
        name="Hide in viewport",
        description="オブジェクトの表示/非表示に hide_set を使用します（目のアイコン）",
        default=True
    )
    
    si_use_hide_render: BoolProperty(
        name="Disable in render",
        description="オブジェクトの表示/非表示に hide_render を使用します",
        default=True
    )
    
    si_use_outliner_restriction: BoolProperty(
        name="Use Outliner Restriction",
        description="アウトライナーの制限の切り替えを使用します",
        default=True
    )

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.prop(self, "tab_addon_menu", expand=True)

        if self.tab_addon_menu == "Keymap":
            # 通常のキーマップを表示（選択の非表示コマンド以外）
            draw_keymap(layout, context, keymap_Softimage)
            
            # 選択の非表示関連の設定をひとつのボックスにまとめる
            box = layout.box()
            
            # ヘッダー
            box.label(text="Hide Selected:", icon="HIDE_ON")
            
            # 選択の非表示関連のキーマップ
            draw_hide_keymap(box, context, keymap_Softimage)
            
            # 区切り線
            box.separator()
            
            # 表示オプション設定
            col = box.column(align=True)
            col.label(text="Display Options:")
            col.prop(self, "si_use_hide_set")
            col.prop(self, "si_use_hide_viewport")
            col.prop(self, "si_use_hide_render")
            col.prop(self, "si_use_outliner_restriction")
            
        elif self.tab_addon_menu == "RigTools":
            draw_keymap(layout, context, keymap_RigTools)
        elif self.tab_addon_menu == "OtherTools":
            draw_keymap(layout, context, keymap_OtherTools)
        elif self.tab_addon_menu == "Link":
            row = layout.row()
            row.label(text="Support Twitter:")
            row.operator("wm.url_open", text="cvELD", icon="URL").url = "https://twitter.com/cvELD_info"

classes = (
    SIKEYMAP_MT_AddonPreferences,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls) 