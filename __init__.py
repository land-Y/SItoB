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
import rna_keymap_ui
import os, csv, codecs
from mathutils import Matrix, Vector



#-------------------------------------------------------------------
#辞書登録
def GetTranslationDict():
    dict = {}
        # csvファイルのパスを取得(同階層にあることを想定)
    path = os.path.join(os.path.dirname(__file__), "SiDic.csv")
        # csvファイルを読む
    with codecs.open(path, 'r', 'utf-8') as f:
        reader = csv.reader(f)
        dict['ja_JP'] = {}
        for row in reader:
            if row: # 行に内容がある場合のみ(空行を除外)
                for context in bpy.app.translations.contexts:
                # 辞書内の改行が勝手にエスケープされてしまうので、replace()で変換して、正しく読み込めるようにする
                    dict['ja_JP'][(context, row[1].replace('\\n', '\n'))] = row[0].replace('\\n', '\n')
    return dict
#-------------------------------------------------------------------


#メニューへの登録

#メニュー登録　RIG_BoneTools

class QuiqRigEditModeMenu(bpy.types.Menu):
	bl_label  = 'QuiqRig'
	bl_idname = 'ARMATURE_MT_QuiqRig'
	def draw(self, context):
		self.layout.operator("armature.newbone_fromselect1bone")
		self.layout.operator("armature.newbone_fromselect1bone_offset")
		self.layout.separator()
		self.layout.operator("armature.setparentposemode")
		self.layout.operator("armature.clearparentposemode")
		self.layout.operator("armature.deleteboneposemode")
		self.layout.operator("armature.makeslider")

class QuiqRig_2seL_EditModeMenu(bpy.types.Menu):
	bl_label  = 'QuiqRig Select2Bones'
	bl_idname = 'ARMATURE_MT_QuiqRig_Select2Bones'
	def draw(self, context):
		self.layout.operator("armature.newbone_fromselect2bone")
		self.layout.operator("armature.addjoint")
		self.layout.operator("armature.ikfromselect2bone")
		self.layout.separator()
		self.layout.operator("armature.matchbonetwo")


class QuiqRigPoseModeMenu(bpy.types.Menu):
	bl_label  = 'QuiqRig'
	bl_idname = 'POSE_MT_QuiqRig'
	def draw(self, context):
		self.layout.operator("armature.newbone_fromselect1bone")
		self.layout.operator("armature.newbone_fromselect1bone_offset")
		self.layout.separator()
		self.layout.operator("armature.setparentposemode")
		self.layout.operator("armature.clearparentposemode")
		self.layout.operator("armature.deleteboneposemode")
		self.layout.operator("armature.makeslider")

class QuiqRig_2sel_PoseModeMenu(bpy.types.Menu):
	bl_label  = 'QuiqRig Select2Bones'
	bl_idname = 'POSE_MT_QuiqRig_Select2Bones'
	def draw(self, context):
		self.layout.operator("armature.newbone_fromselect2bone")
		self.layout.operator("armature.addjoint")
		self.layout.operator("armature.ikfromselect2bone")
		self.layout.separator()
		self.layout.operator("armature.matchbonetwo")



def menu_func_edit(self, context):
	self.layout.menu('ARMATURE_MT_QuiqRig')
	self.layout.menu('ARMATURE_MT_QuiqRig_Select2Bones')

def menu_func_pose(self, context):
	self.layout.menu('POSE_MT_QuiqRig')
	self.layout.menu('POSE_MT_QuiqRig_Select2Bones')

# メニューへの登録
def menu_func_show_hide(self, context):
    layout = self.layout
    layout.operator("object.si_toggle_hide", text="ビュー＆レンダー：選択物を隠す/表示")
    layout.operator("object.si_show_hidden_objects", text="ビュー＆レンダー：隠したオブジェクトを表示")
    layout.operator("object.si_hide_unselected", text="ビュー＆レンダー：非選択物を隠す")
    layout.separator()
    layout.operator("view3d.tgl_hide_object_type", text="オブジェクトタイプで隠す")

# アドオンでの設定関数」

class SIKEYMAP_MT_AddonPreferences(AddonPreferences):
	bl_idname = __name__
	tab_addon_menu : EnumProperty(name="Tab", description="", items=[
		('Keymap', "Softimage", "","KEYINGSET",0),
		('OtherTools', "OtherTools", "","KEYINGSET2",1), 
		('RigTools', "RigTools", "","KEYINGSET2",2),
		('Link', "Link", "","URL",3)
	], default='Keymap')

	def draw(self, context):
		layout = self.layout
		row = layout.row(align=True)
		row.prop(self, "tab_addon_menu", expand=True)

		if self.tab_addon_menu == "Keymap":
			self.draw_keymap(context, keymap_Softimage)
		elif self.tab_addon_menu == "RigTools":
			self.draw_keymap(context, keymap_RigTools)
		elif self.tab_addon_menu == "OtherTools":
			self.draw_keymap(context, keymap_OtherTools)
		elif self.tab_addon_menu == "Link":
			row = layout.row()
			row.label(text="Support Twitter:")
			row.operator("wm.url_open", text="cvELD", icon="URL").url = "https://twitter.com/cvELD_info"

	def draw_keymap(self, context, keymap_list):
		box = self.layout.box()
		col = box.column()
		col.label(text="Keymap List:", icon="KEYINGSET")

		wm = context.window_manager
		kc = wm.keyconfigs.user
		old_km_name = ""

		for km_add, kmi_add in keymap_list:
			km = kc.keymaps.get(km_add.name)
			if km:
				if not km.name == old_km_name:
					col.label(text=km.name, icon="DOT")
				col.context_pointer_set("keymap", km)
				rna_keymap_ui.draw_kmi([], kc, km, kmi_add, col, 0)
				col.separator()
				old_km_name = km.name

keymap_Softimage = []
keymap_RigTools = []
keymap_OtherTools = []


def add_hotkey():
	wm = bpy.context.window_manager
	kc = wm.keyconfigs.addon

	if kc:
		# Softimageキーマップ
		km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
		kmi = km.keymap_items.new('object.si_del_sudiv', 'NUMPAD_MINUS', 'PRESS', shift=True)
		keymap_Softimage.append((km, kmi))

		km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
		kmi = km.keymap_items.new('object.si_add_sudiv', 'NUMPAD_PLUS', 'PRESS')
		keymap_Softimage.append((km, kmi))

		km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
		kmi = km.keymap_items.new('object.si_minus_sudiv', 'NUMPAD_MINUS', 'PRESS')
		keymap_Softimage.append((km, kmi))

		km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
		kmi = km.keymap_items.new('object.si_resetsrt', 'R', 'PRESS', ctrl=True, shift=True)
		keymap_Softimage.append((km, kmi))

		km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
		kmi = km.keymap_items.new('object.si_movecomponent', 'M', 'PRESS')
		keymap_Softimage.append((km, kmi))

		km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
		kmi = km.keymap_items.new('object.si_movecomponent1', 'T', 'ANY')
		keymap_Softimage.append((km, kmi))

		km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
		kmi = km.keymap_items.new('object.si_movecomponent2', 'E', 'ANY')
		keymap_Softimage.append((km, kmi))

		km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
		kmi = km.keymap_items.new('object.si_movecomponent3', 'U', 'ANY')
		keymap_Softimage.append((km, kmi))

		km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
		kmi = km.keymap_items.new('object.si_toggle_hide', 'H', 'PRESS')
		keymap_Softimage.append((km, kmi))

		km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
		kmi = km.keymap_items.new('object.si_show_hidden_objects', 'H', 'PRESS', shift=True)
		keymap_Softimage.append((km, kmi))

		km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
		kmi = km.keymap_items.new('object.si_hide_unselected', 'H', 'PRESS', alt=True)
		keymap_Softimage.append((km, kmi))

		# RigToolsキーマップ
		km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
		kmi = km.keymap_items.new('object.gator_plus', 'G', 'PRESS', alt=True)
		keymap_RigTools.append((km, kmi))

		km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
		kmi = km.keymap_items.new('object.gator_plus_deletevertex_modifier', 'G', 'PRESS', ctrl=True, shift=True, alt=True)
		keymap_RigTools.append((km, kmi))

		km = kc.keymaps.new(name='Weight Paint', space_type='VIEW_3D')
		kmi = km.keymap_items.new('view3d.sel_wheigtmaskmode', 'LEFTMOUSE', 'PRESS', ctrl=True, alt=True)
		keymap_RigTools.append((km, kmi))

		km = kc.keymaps.new(name='Weight Paint', space_type='VIEW_3D')
		kmi = km.keymap_items.new('view3d.sel_wheigtmaskmode_tgl', 'LEFTMOUSE', 'PRESS', shift=True, ctrl=True, alt=True)
		keymap_RigTools.append((km, kmi))

		# OtherToolsキーマップ
		km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
		kmi = km.keymap_items.new('view3d.tgl_hide_object_type', 'Q', 'PRESS', ctrl=True)
		keymap_OtherTools.append((km, kmi))

		km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
		kmi = km.keymap_items.new('object.separatecomponet_keep', 'D', 'PRESS', ctrl=True, alt=True)
		keymap_OtherTools.append((km, kmi))

		km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
		kmi = km.keymap_items.new('object.knife_project_cut_through', 'N', 'PRESS', ctrl=True, alt=True)
		keymap_OtherTools.append((km, kmi))

		km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
		kmi = km.keymap_items.new('view3d.clipbord_select_object', 'C', 'PRESS', ctrl=True, shift=True)
		keymap_OtherTools.append((km, kmi))

		km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
		kmi = km.keymap_items.new('view3d.toggle_pivot_mode', 'D', 'PRESS')
		keymap_OtherTools.append((km, kmi))

def remove_hotkey():
	for km, kmi in keymap_Softimage:
		if km and kmi:
			try:
				km.keymap_items.remove(kmi)
			except:
				pass
	keymap_Softimage.clear()
	
	for km, kmi in keymap_RigTools:
		if km and kmi:
			try:
				km.keymap_items.remove(kmi)
			except:
				pass
	keymap_RigTools.clear()
	
	for km, kmi in keymap_OtherTools:
		if km and kmi:
			try:
				km.keymap_items.remove(kmi)
			except:
				pass
	keymap_OtherTools.clear()


#読み込んだファイルからクラスを読み込み
classes = (
SIKEYMAP_MT_AddonPreferences,
si_Subdiv.si_del_subdiv_OT_object,
si_Subdiv.si_add_subdiv_OT_object,
si_Subdiv.si_minus_subdiv_OT_object,

si_ResetSRT.si_ResetSRT_OT_object,

QuiqRigEditModeMenu,
QuiqRig_2seL_EditModeMenu,
QuiqRigPoseModeMenu,
QuiqRig_2sel_PoseModeMenu,

si_MoveComponent.si_MoveComponent_OT_object,
si_MoveComponent.si_MoveComponent1_OT_object,
si_MoveComponent.si_MoveComponent2_OT_object,
si_MoveComponent.si_MoveComponent3_OT_object,
si_Isolate.si_isolate_OT_object,
si_ToggleHide.SI_OT_toggle_hide,
si_ToggleHide.SI_OT_Show_Hidden_Objects,
si_ToggleHide.SI_OT_Hide_Unselected,

KnifeProject.KnifeProject_OT_object_cut_through,
KnifeProject.KnifeProject_OT_object,
KnifeProject.KnifeProject_OT_CreateSeam_SelFaceBorder,

SeparateComponet_keep.SeparateComponent_OT_object,

Tgl_Pivot.tglPivot_OT_object,
clipbord_SelectObjectName.clipbord_select_object_OT_object,

Sel_whgM_masktgl.sel_wheigtmaskmode_OT_object,
Sel_whgM_masktgl.sel_wheigtmaskmode_tgl_OT_object,

GatorPlus.gator_plus_OT_object,
GatorPlus.gator_plus_DelArmVertex_OT_object,

Tgl_HideObjectType.Tgl_HideObjectType_OT_object,
)


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

def unregister_properties():
    del bpy.types.Scene.SItoBHide
    del bpy.types.Collection.si_hidden_objects

def register():
    # カスタムプロパティの登録
    register_properties()
    
    # すべてのクラスを登録
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # メニュー追加
    bpy.types.VIEW3D_MT_edit_armature.append(menu_func_edit)
    bpy.types.VIEW3D_MT_pose.append(menu_func_pose)
    bpy.types.VIEW3D_MT_object_showhide.append(menu_func_show_hide)
    
    # ホットキー登録
    add_hotkey()

    #辞書登録
    translation_dict = GetTranslationDict()
    bpy.app.translations.register(__name__, translation_dict)

def unregister():
    # メニュー削除
    bpy.types.VIEW3D_MT_edit_armature.remove(menu_func_edit)
    bpy.types.VIEW3D_MT_pose.remove(menu_func_pose)
    bpy.types.VIEW3D_MT_object_showhide.remove(menu_func_show_hide)
    
    # ホットキー削除
    remove_hotkey()
    
    # カスタムプロパティの解除
    unregister_properties()
    
    # 辞書解除
    bpy.app.translations.unregister(__name__)
    
    # すべてのクラスのアンレジストリ
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except:
            pass  # すでにアンレジストリされている場合はスキップ


if __name__ == "__main__":
	register()
