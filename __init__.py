bl_info = {
  "name": "softimage to Blender",
  "author": "cvELD",
  "version": (1, 0, 0),
  "blender": (2, 80, 0),
  "location": "Softimage SHORTCUT",
  "support": "TESTING",
  "category": "UI",
  "warning" : "",
  "wiki_url": "https://github.com/land-Y/SItoB/wiki",
  "tracker_url": "https://cveld.net/"
}

#複数ファイルに分割した場合必要
if "bpy" in locals():
    import imp
    imp.reload(si_subdiv)
    imp.reload(si_resetSRT)
    imp.reload(si_MoveComponent)

else:
    from . import si_subdiv
    from . import si_resetSRT
    from . import si_MoveComponent


import bpy
from bpy.props import *
from bpy.types import  AddonPreferences
import rna_keymap_ui 
import os, csv, codecs




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


# メニューを構築する関数

class SIKEYMAP_MT_AddonPreferences(AddonPreferences):
	bl_idname = __name__
	tab_addon_menu : EnumProperty(name="Tab", description="", items=[('Keymap', "Softimage", "","KEYINGSET",0),('OtherTools', "OtherTools", "","KEYINGSET2",1), ('Link', "Link", "","URL",2)], default='Keymap')


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

        #si_ResetSRT
		km = wm.keyconfigs.addon.keymaps.new(name = 'Animation')
		kmi = km.keymap_items.new('object.si_resetsrt', 'R', 'PRESS',ctrl = True ,shift = True )
		keymap_Softimage.append((km, kmi))

        #si_movecomponent
		km = wm.keyconfigs.addon.keymaps.new(name = 'Mesh')
		kmi = km.keymap_items.new('object.si_movecomponent', 'M', 'PRESS' )
		keymap_Softimage.append((km, kmi))

		#si_Active componetnt Vertex Edge Face
		km = wm.keyconfigs.addon.keymaps.new(name = 'Mesh')
		kmi = km.keymap_items.new('object.si_movecomponent1', 'T', 'ANY' )
		keymap_Softimage.append((km, kmi))

		#si_Active componetnt Vertex Edge Face
		km = wm.keyconfigs.addon.keymaps.new(name = 'Mesh')
		kmi = km.keymap_items.new('object.si_movecomponent2', 'E', 'ANY' )
		keymap_Softimage.append((km, kmi))

		#si_Active componetnt Vertex Edge Face
		km = wm.keyconfigs.addon.keymaps.new(name = 'Mesh')
		kmi = km.keymap_items.new('object.si_movecomponent3', 'U', 'ANY' )
		keymap_Softimage.append((km, kmi))


		#-----------自作ツール以外のアドオンやハック系などなど
		#OtherTools
		km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
		kmi = km.keymap_items.new("outliner.si_toggle_hide", 'H', 'PRESS')
		keymap_OtherTools.append((km, kmi))


def remove_hotkey():
	for km, kmi in keymap_Softimage:
		km.keymap_items.remove(kmi)
	keymap_Softimage.clear()


#読み込んだファイルからクラスを読み込み
classes = (
SIKEYMAP_MT_AddonPreferences,
si_subdiv.si_del_subdiv_OT_object,
si_subdiv.si_add_subdiv_OT_object,
si_subdiv.si_minus_subdiv_OT_object,

si_resetSRT.si_resetSRT_OT_object,


si_MoveComponent.si_MoveComponent_OT_object,
si_MoveComponent.si_MoveComponent1_OT_object,
si_MoveComponent.si_MoveComponent2_OT_object,
si_MoveComponent.si_MoveComponent3_OT_object,


)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)
	add_hotkey()

	#辞書登録
	translation_dict = GetTranslationDict()
	bpy.app.translations.register(__name__, translation_dict)

def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)
	remove_hotkey()
	
	#辞書解除
	bpy.app.translations.unregister(__name__)


if __name__ == "__main__":
	register()
