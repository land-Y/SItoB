# -*- coding: utf-8 -*-
import bpy
from bpy.props import EnumProperty, StringProperty
from bpy.types import AddonPreferences

from ..panels.keymap_ui import draw_keymap
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

class SIKEYMAP_MT_AddonPreferences(AddonPreferences):
    bl_idname = "SItoB"
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

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.prop(self, "tab_addon_menu", expand=True)

        if self.tab_addon_menu == "Keymap":
            draw_keymap(layout, context, keymap_Softimage)
        elif self.tab_addon_menu == "RigTools":
            draw_keymap(layout, context, keymap_RigTools)
        elif self.tab_addon_menu == "OtherTools":
            draw_keymap(layout, context, keymap_OtherTools)
        elif self.tab_addon_menu == "Link":
            row = layout.row()
            row.label(text="Support Twitter:")
            row.operator("wm.url_open", text="cvELD", icon="URL").url = "https://twitter.com/cvELD_info" 