bl_info = {
  "name": "SItoB",
  "author": "cvELD",
  "description": "Softimage to Blender",
  "version": (1, 3, 1),
  "blender": (2, 93, 0),
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
	imp.reload(si_ResetCamera)
	imp.reload(Tgl_HideObjectType)
	imp.reload(si_Isolate)
	imp.reload(SeparateComponet_keep)
	imp.reload(si_ToggleHide)
	imp.reload(KnifeProject)
	imp.reload(Tgl_Pivot)
	imp.reload(clipbord_SelectObjectName)
	imp.reload(RIG_BoneTools)
	imp.reload(GatorPlus)
	imp.reload(Sel_whgM_masktgl)
else:
	from . import si_Subdiv
	from . import si_ResetSRT
	from . import si_MoveComponent
	from . import si_ResetCamera
	from . import Tgl_HideObjectType
	from . import si_Isolate
	from . import SeparateComponet_keep
	from . import si_ToggleHide
	from . import KnifeProject
	from . import Tgl_Pivot
	from . import clipbord_SelectObjectName
	from . import RIG_BoneTools
	from . import GatorPlus
	from . import Sel_whgM_masktgl


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


# アドオンでの設定関数」

class SIKEYMAP_MT_AddonPreferences(AddonPreferences):
	bl_idname = __name__
	tab_addon_menu : EnumProperty(name="Tab", description="", items=[('Keymap', "Softimage", "","KEYINGSET",0),('OtherTools', "OtherTools", "","KEYINGSET2",1), ('RigTools', "RigTools", "","KEYINGSET2",2),('Link', "Link", "","URL",3)], default='Keymap')


	def draw(self, context):
		layout = self.layout

		row = layout.row(align=True)
		row.prop(self, "tab_addon_menu",expand=True)

		preferences = bpy.context.preferences
		addon_prefs = bpy.context.preferences.addons[__name__].preferences

		if self.tab_addon_menu=="Keymap":
			box = layout.box()
			col = box.column()
			col.label(text="Keymap List:",icon="KEYINGSET")


			wm = bpy.context.window_manager
			kc = wm.keyconfigs.user
			old_km_name = ""
			old_id_l = []
			for km_add, kmi_add in keymap_Softimage:
				km = kc.keymaps[km_add.name]

				for kmi_con in km.keymap_items:
					if kmi_add.idname == kmi_con.idname:
						if not kmi_con.id in old_id_l:
							kmi = kmi_con
							old_id_l.append(kmi_con.id)
							break

				if kmi:
					if not km.name == old_km_name:
						col.label(text=km.name,icon="DOT")
					col.context_pointer_set("keymap", km)
					rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
					col.separator()
					old_km_name = km.name
					kmi = None

		#RigTools Tab用
		elif self.tab_addon_menu=="RigTools":
			box = layout.box()
			col = box.column()
			col.label(text="Keymap List:",icon="KEYINGSET")


			wm = bpy.context.window_manager
			kc = wm.keyconfigs.user
			old_km_name = ""
			old_id_l = []
			for km_add, kmi_add in keymap_RigTools:
				km = kc.keymaps[km_add.name]

				for kmi_con in km.keymap_items:
					if kmi_add.idname == kmi_con.idname:
						if not kmi_con.id in old_id_l:
							kmi = kmi_con
							old_id_l.append(kmi_con.id)
							break

				if kmi:
					if not km.name == old_km_name:
						col.label(text=km.name,icon="DOT")
					col.context_pointer_set("keymap", km)
					rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
					col.separator()
					old_km_name = km.name
					kmi = None


		#OtherToolsタブ用
		elif self.tab_addon_menu=="OtherTools":
			box = layout.box()
			col = box.column()
			col.label(text="Keymap List:",icon="KEYINGSET")


			wm = bpy.context.window_manager
			kc = wm.keyconfigs.user
			old_km_name = ""
			old_id_l = []
			for km_add, kmi_add in keymap_OtherTools:
				km = kc.keymaps[km_add.name]

				for kmi_con in km.keymap_items:
					if kmi_add.idname == kmi_con.idname:
						if not kmi_con.id in old_id_l:
							kmi = kmi_con
							old_id_l.append(kmi_con.id)
							break

				if kmi:
					if not km.name == old_km_name:
						col.label(text=km.name,icon="DOT")
					col.context_pointer_set("keymap", km)
					rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
					col.separator()
					old_km_name = km.name
					kmi = None

		elif self.tab_addon_menu=="Link":
			row = layout.row()
			row.label(text="Support Twitter:")
			row.operator( "wm.url_open", text="cvELD", icon="URL").url = "https://twitter.com/cvELD_info"


keymap_Softimage = []
keymap_RigTools = []
keymap_OtherTools = []


def add_hotkey():
	wm = bpy.context.window_manager
	kc = wm.keyconfigs.addon

	if kc:

		#1
		km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
		kmi = km.keymap_items.new('object.si_del_sudiv', 'NUMPAD_MINUS', 'PRESS' , shift = True )
		keymap_Softimage.append((km, kmi))

		#2
		km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
		kmi = km.keymap_items.new('object.si_add_sudiv', 'NUMPAD_PLUS', 'PRESS')
		keymap_Softimage.append((km, kmi))

        #3
		km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
		kmi = km.keymap_items.new('object.si_minus_sudiv', 'NUMPAD_MINUS', 'PRESS')
		keymap_Softimage.append((km, kmi))

		#si_ResetCamera
		km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
		kmi = km.keymap_items.new('view3d.si_reset_camera', 'R', 'PRESS')
		keymap_Softimage.append((km, kmi))

		#si_isolate
		km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
		kmi = km.keymap_items.new('view3d.si_isolate', 'INSERT', 'PRESS')
		keymap_Softimage.append((km, kmi))

        #si_ResetSRT
		km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
		kmi = km.keymap_items.new('object.si_resetsrt', 'R', 'PRESS',ctrl = True ,shift = True )
		keymap_Softimage.append((km, kmi))


        #si_movecomponent
		km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
		kmi = km.keymap_items.new('object.si_movecomponent', 'M', 'PRESS' )
		keymap_Softimage.append((km, kmi))

		#si_Active componetnt Vertex Edge Face
		km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
		kmi = km.keymap_items.new('object.si_movecomponent1', 'T', 'ANY' )
		keymap_Softimage.append((km, kmi))

		#si_Active componetnt Vertex Edge Face
		km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
		kmi = km.keymap_items.new('object.si_movecomponent2', 'E', 'ANY' )
		keymap_Softimage.append((km, kmi))

		#si_Active componetnt Vertex Edge Face
		km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
		kmi = km.keymap_items.new('object.si_movecomponent3', 'U', 'ANY' )
		keymap_Softimage.append((km, kmi))


		#si_toggle_hide
		km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
		kmi = km.keymap_items.new('outliner.si_toggle_hide', 'H', 'PRESS' )
		keymap_Softimage.append((km, kmi))

		#-----------Rigging用のツール
		#２選択ボーンのアクティブにフィット＆整列
		km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
		kmi = km.keymap_items.new('armature.matchbonetwo', 'L', 'PRESS' ,ctrl = True)
		keymap_RigTools.append((km, kmi))
		#1選択ボーンからボーン生成
		km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
		kmi = km.keymap_items.new('armature.newbone_fromselect1bone', 'B', 'PRESS' ,ctrl = True)
		keymap_RigTools.append((km, kmi))
		#1選択ボーンからボーン生成（オフセット）
		km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
		kmi = km.keymap_items.new('armature.newbone_fromselect1bone_offset', 'B', 'PRESS' ,ctrl = True,alt = True)
		keymap_RigTools.append((km, kmi))
		#2選択ボーンからボーン生成
		km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
		kmi = km.keymap_items.new('armature.newbone_fromselect2bone', 'B', 'PRESS' ,ctrl = True,shift= True)
		#2選択ボーンからジョイントボーン生成
		km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
		kmi = km.keymap_items.new('armature.addjoint', 'J', 'PRESS' ,ctrl = True,shift= True)
		#2選択ボーンからIK生成
		km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
		kmi = km.keymap_items.new('armature.ikfromselect2bone', 'I', 'PRESS' ,ctrl = True,shift= True)
		keymap_RigTools.append((km, kmi))
		#ポーズボーン中でもペアレントできるようにする
		km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
		kmi = km.keymap_items.new('armature.setparentposemode', 'P', 'PRESS' ,ctrl = True)
		keymap_RigTools.append((km, kmi))
		#選択ボーンのペアレントクリア
		km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
		kmi = km.keymap_items.new('armature.clearparentposemode', 'P', 'PRESS' ,shift= True)
		keymap_RigTools.append((km, kmi))
		#ボーンのデリートをPoseModeでも
		km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
		kmi = km.keymap_items.new('armature.deleteboneposemode', 'DEL', 'PRESS' ,ctrl= True,shift= True)
		keymap_RigTools.append((km, kmi))
		#Slyder生成
		km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
		kmi = km.keymap_items.new('armature.makeslider', 'L', 'PRESS' ,ctrl= True,shift= True, alt = True)
		keymap_RigTools.append((km, kmi))

		#Gator+ アクティブオブジェクトに選択オブジェクトのモデファイアと頂点グループ転送
		km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
		kmi = km.keymap_items.new('object.gator_plus', 'G', 'PRESS' ,alt= True)
		keymap_RigTools.append((km, kmi))
		#Gator+ Armatureモデファイア削除と頂点グループ除去
		km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
		kmi = km.keymap_items.new('object.gator_plus_deletevertex_modifier', 'G', 'PRESS' ,ctrl= True,shift= True, alt = True)
		keymap_RigTools.append((km, kmi))

		#ウェイトモードでマスクがONでもクリック選択がが出来る
		km = wm.keyconfigs.addon.keymaps.new(name = 'Weight Paint')
		kmi = km.keymap_items.new('view3d.sel_wheigtmaskmode', 'LEFTMOUSE', 'PRESS' ,ctrl= True,alt= True)
		keymap_RigTools.append((km, kmi))
		#ウェイトモードでマスクがONでもクリック選択がが出来る　トグル選択
		km = wm.keyconfigs.addon.keymaps.new(name = 'Weight Paint')
		kmi = km.keymap_items.new('view3d.sel_wheigtmaskmode_tgl', 'LEFTMOUSE', 'PRESS' ,shift = True,ctrl= True,alt= True)
		keymap_RigTools.append((km, kmi))
		#-----------Softimageには無いけど使ってた機能、自作ツール以外のアドオンやハック系などなど
		#OtherTools

		km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
		kmi = km.keymap_items.new("view3d.tgl_hide_object_type", 'Q', 'PRESS',ctrl = True)
		keymap_OtherTools.append((km, kmi))

		#tgl_hide_object_type オブジェクトビュータイプの表示トグル
		km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
		kmi = km.keymap_items.new('object.separatecomponet_keep', 'D', 'PRESS',ctrl = True ,alt = True )
		keymap_OtherTools.append((km, kmi))

		#エディット以外でもナイフプロジェクト カットスルー
		km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
		kmi = km.keymap_items.new('object.knife_project_cut_through', 'N', 'PRESS',ctrl = True ,alt = True )
		keymap_OtherTools.append((km, kmi))

		#選択ボーンの名前をクリップボードにコピー。又はオブジェクト名
		km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
		kmi = km.keymap_items.new('view3d.clipbord_select_object', 'C', 'PRESS',ctrl = True ,shift = True)
		keymap_OtherTools.append((km, kmi))

		#Pivt modeのスナップやらカーソルに合わせるやらのトグル
		km = wm.keyconfigs.addon.keymaps.new(name = '3D View')
		kmi = km.keymap_items.new('view3d.toggle_pivot_mode', 'D', 'PRESS')
		keymap_OtherTools.append((km, kmi))

def remove_hotkey():
	for km, kmi in keymap_Softimage:
		km.keymap_items.remove(kmi)
	keymap_Softimage.clear()
	for km, kmi in keymap_RigTools:
		km.keymap_items.remove(kmi)
	keymap_RigTools.clear()
	for km, kmi in keymap_OtherTools:
		km.keymap_items.remove(kmi)
	keymap_OtherTools.clear()


#読み込んだファイルからクラスを読み込み
classes = (
SIKEYMAP_MT_AddonPreferences,
si_Subdiv.si_del_subdiv_OT_object,
si_Subdiv.si_add_subdiv_OT_object,
si_Subdiv.si_minus_subdiv_OT_object,

si_ResetSRT.si_ResetSRT_OT_object,

si_ResetCamera.si_ResetCamera_OT_object,

QuiqRigEditModeMenu,
QuiqRig_2seL_EditModeMenu,
QuiqRigPoseModeMenu,
QuiqRig_2sel_PoseModeMenu,

si_MoveComponent.si_MoveComponent_OT_object,
si_MoveComponent.si_MoveComponent1_OT_object,
si_MoveComponent.si_MoveComponent2_OT_object,
si_MoveComponent.si_MoveComponent3_OT_object,
si_Isolate.si_isolate_OT_object,
si_ToggleHide.OUTLINER_OT_si_toggle_hide,

Tgl_HideObjectType.Tgl_HideObjectType_OT_object,

KnifeProject.KnifeProject_OT_object_cut_through,
KnifeProject.KnifeProject_OT_object,
KnifeProject.KnifeProject_OT_CreateSeam_SelFaceBorder,

SeparateComponet_keep.SeparateComponent_OT_object,

Tgl_Pivot.tglPivot_OT_object,
clipbord_SelectObjectName.clipbord_select_object_OT_object,
RIG_BoneTools.MatchBoneTwo_OT_object,
RIG_BoneTools.MakeBoneOne_Offset_OT_object,
RIG_BoneTools.MakeBoneOne_OT_object,
RIG_BoneTools.MakeBoneTwo_OT_object,
RIG_BoneTools.SetParent_OT_object,
RIG_BoneTools.ClearParent_OT_object,
RIG_BoneTools.DeleteBonePoseMode_OT_object,
RIG_BoneTools.MakeBone_AddJoint_OT_object,
RIG_BoneTools.MakeBone_IKfromSelect2Bone_OT_object,
RIG_BoneTools.MakeBone_MakeSlider_OT_object,

Sel_whgM_masktgl.sel_wheigtmaskmode_OT_object,
Sel_whgM_masktgl.sel_wheigtmaskmode_tgl_OT_object,

GatorPlus.gator_plus_OT_object,
GatorPlus.gator_plus_DelArmVertex_OT_object,
)


def register():
	for cls in classes:
		bpy.utils.register_class(cls)
	add_hotkey()

	#メニュー登録
	bpy.types.TOPBAR_MT_edit_armature_add.prepend(menu_func_edit)
	bpy.types.VIEW3D_MT_armature_context_menu.append(menu_func_edit)
	bpy.types.VIEW3D_MT_pose_context_menu.append(menu_func_pose)
	#辞書登録
	translation_dict = GetTranslationDict()
	bpy.app.translations.register(__name__, translation_dict)

def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)
	remove_hotkey()
	#メニュー削除
	bpy.types.TOPBAR_MT_edit_armature_add.remove(menu_func_edit)
	bpy.types.VIEW3D_MT_armature_context_menu.remove(menu_func_edit)
	bpy.types.VIEW3D_MT_pose_context_menu.remove(menu_func_pose)
	#辞書解除
	bpy.app.translations.unregister(__name__)


if __name__ == "__main__":
	register()
