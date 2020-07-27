'''
BK-Template Addon (C) 2019 Bookyakuno
Created by Bookyakuno

# ライセンス
## 下記を許可する
1.このファイルをベースとしたアドオンの開発
2. 第1項の配布もしくは販売・商用利用
3. 第1項のライセンスの変更・付与

## 下記は許可しない
- 未加工ファイルの自作発言
- 未加工ファイルの再配布

## 要約
このファイルをベースとしてアドオン開発、開発したものを配布・販売・ライセンスの変更してもいいよ。
自作発言と、加工してないファイルの再配布はやめてね。
'''


import bpy
from bpy.props import StringProperty, IntProperty, BoolProperty
import rna_keymap_ui # キーマップリストに必要

################################################
# アドオン情報
bl_info = {
	"name" : "BK-Template Addon",
	"author" : "Bookyakuno",
	"version" : (1, 0, 0),
	"blender" : (2, 80, 0),
	"location" : "hoge",
	"description" : "hoge",
	"warning" : "",
	"wiki_url" : "",
	"tracker_url" : "",
	"category" : "UI"
}


##################################################
##################################################
# 翻訳辞書
BKTEMPLATE_translation_dict = {
	"en_US": {
	},
	"ja_JP": {
		("*", "hoge"):
		"ほげ",
	}
}


##################################################
##################################################
# アドオン設定
class BKTEMPLATE_Preferences(bpy.types.AddonPreferences):
	bl_idname = __name__
	################################################
	# アドオンプロパティ(ここのプロパティの状態はユーザー設定で保存される)
	si_bool = bpy.props.BoolProperty(default=True, name = "Bool", description = "Bool")


	################################################
	def draw(self, context):
		layout = self.layout

		preferences = bpy.context.preferences
		addon_prefs = bpy.context.preferences.addons[__name__].preferences

		layout.label(text="AddonPreferencesSample")

		layout.prop(addon_prefs,"si_bool")

		################################################
		# キーマップリスト
		box = layout.box()
		col = box.column()

		col.label(text="Keymap List:",icon="KEYINGSET")

		kc = bpy.context.window_manager.keyconfigs.addon
		for km, kmi in addon_keymaps:
			km = km.active()
			col.context_pointer_set("keymap", km)
			rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)



		################################################
		# URL
		row = layout.row()
		row.label(text="Link:",icon="NONE")

		row.operator(
			"wm.url_open", text="gumroad",
			icon="URL").url = "https://gum.co/VLdwV"
		# layout.label(text="",icon="NONE")


################################################
class BKTEMPLATE_OT_SimpleOperator(bpy.types.Operator):
	bl_idname = "bktemplate.simple_operator"
	bl_label = "BK-Template Sample Operator"
	bl_description = "BK-Template Sample Operator"
	bl_options = {'REGISTER', 'UNDO'}

	si_bool = BoolProperty(default=True, name = "si_bool", description = "bktemplate_operator_bool")


	def execute(self, context):
		addon_prefs = bpy.context.preferences.addons[__name__].preferences

		# スザンヌを追加
		bpy.ops.mesh.primitive_monkey_add()

		# オペレーターのブール設定がTrueの場合
		if self.si_bool:
			# X30度回転
			bpy.ops.transform.rotate(value=0.523599, orient_axis='X', orient_type='GLOBAL') #30 Rotate

		# アドオン設定のブール設定がTrueの場合
		if addon_prefs.si_bool:
			# 編集モードにする
			bpy.ops.object.editmode_toggle()



		return {'FINISHED'}



################################################
# クラスの登録
classes = (
BKTEMPLATE_Preferences,
BKTEMPLATE_OT_SimpleOperator,
)


################################################
addon_keymaps = []
def register():
	################################################
	# クラスの登録
	for cls in classes:
		bpy.utils.register_class(cls)

	################################################
	# 辞書の登録
	bpy.app.translations.register(__name__, BKTEMPLATE_translation_dict) # 辞書

	################################################
	# キーマップ
	wm = bpy.context.window_manager.keyconfigs.addon.keymaps.new

	# km = wm(name = 'Mesh', space_type='EMPTY', region_type='WINDOW', modal=False)
	km = wm(name = '3D View Generic', space_type = 'VIEW_3D')
	kmi = km.keymap_items.new("bktemplate.simple_operator", 'Y', 'PRESS', alt=True)
	addon_keymaps.append((km, kmi))
	kmi.active =  True



################################################
def unregister():
	################################################
	#クラスの削除
	for cls in classes:
		bpy.utils.unregister_class(cls)

	################################################
	# 辞書の削除
	bpy.app.translations.unregister(__name__)   # 辞書の削除

	################################################
	# キーマップの削除
	for km, kmi in addon_keymaps:
		km.keymap_items.remove(kmi)
	addon_keymaps.clear()

################################################
if __name__ == "__main__":
	register()
