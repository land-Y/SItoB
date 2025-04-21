bl_info = {
  "name": "SItoB",
  "author": "cvELD",
  "description": "Softimage to Blender",
  "version": (2, 0, 0),
  "blender": (4, 0, 0),
  "support": "COMMUNITY",
  "category": "UI",
  "warning" : "",
  "wiki_url": "https://github.com/land-Y/SItoB/wiki",
  "tracker_url": "https://cveld.net/"
}

#複数ファイルに分割した場合必要
if "bpy" in locals():
	import imp
	imp.reload(si_Subdiv)
	imp.reload(si_ResetSRT)
	imp.reload(si_MoveComponent)
	imp.reload(si_Isolate)
	imp.reload(SeparateComponet_keep)
	imp.reload(si_ToggleHide)
	imp.reload(KnifeProject)
	imp.reload(Tgl_Pivot)
	imp.reload(clipbord_SelectObjectName)
	imp.reload(GatorPlus)
	imp.reload(Sel_whgM_masktgl)
	imp.reload(Tgl_HideObjectType)
else:
	from . import si_Subdiv
	from . import si_ResetSRT
	from . import si_MoveComponent
	from . import si_Isolate
	from . import SeparateComponet_keep
	from . import si_ToggleHide
	from . import KnifeProject
	from . import Tgl_Pivot
	from . import clipbord_SelectObjectName
	from . import GatorPlus
	from . import Sel_whgM_masktgl
	from . import Tgl_HideObjectType


import bpy
from bpy.props import *
from bpy.types import  AddonPreferences
from .properties.props_addon_preference import register_properties, unregister_properties, SIKEYMAP_MT_AddonPreferences
from .properties.props_keymaps import register_keymaps, unregister_keymaps
from .menus.menus_context import register_menus, unregister_menus
from .translation.translation import register as register_translation, unregister as unregister_translation



# 翻訳辞書登録は external translation モジュールで行います

def register():
    # カスタムプロパティ登録
    register_properties()
    # クラス登録
    for cls in classes:
        bpy.utils.register_class(cls)
    # メニュー追加
    register_menus()
    # キーマップ登録
    register_keymaps()
    # 翻訳辞書の登録
    register_translation()

def unregister():
    # メニュー削除
    unregister_menus()
    # キーマップ解除
    unregister_keymaps()
    # プロパティ解除
    unregister_properties()
    # 翻訳辞書の解除
    unregister_translation()
    # クラス解除
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except:
            pass

# 登録するクラス一覧
classes = (
    SIKEYMAP_MT_AddonPreferences,
    *si_Subdiv.classes,
    *si_ResetSRT.classes,
    *si_MoveComponent.classes,
    *si_Isolate.classes,
    *SeparateComponet_keep.classes,
    *si_ToggleHide.classes,
    *KnifeProject.classes,
    *Tgl_Pivot.classes,
    *clipbord_SelectObjectName.classes,
    *GatorPlus.classes,
    *Sel_whgM_masktgl.classes,
    *Tgl_HideObjectType.classes,
)

if __name__ == "__main__":
	register()
