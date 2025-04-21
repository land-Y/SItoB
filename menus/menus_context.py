import bpy

# メニュークラスの定義
class QuiqRigEditModeMenu(bpy.types.Menu):
    bl_label = 'QuiqRig'
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
    bl_label = 'QuiqRig Select2Bones'
    bl_idname = 'ARMATURE_MT_QuiqRig_Select2Bones'
    def draw(self, context):
        self.layout.operator("armature.newbone_fromselect2bone")
        self.layout.operator("armature.addjoint")
        self.layout.operator("armature.ikfromselect2bone")
        self.layout.separator()
        self.layout.operator("armature.matchbonetwo")

class QuiqRigPoseModeMenu(bpy.types.Menu):
    bl_label = 'QuiqRig'
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
    bl_label = 'QuiqRig Select2Bones'
    bl_idname = 'POSE_MT_QuiqRig_Select2Bones'
    def draw(self, context):
        self.layout.operator("armature.newbone_fromselect2bone")
        self.layout.operator("armature.addjoint")
        self.layout.operator("armature.ikfromselect2bone")
        self.layout.separator()
        self.layout.operator("armature.matchbonetwo")

# メニュー表示用関数

def menu_func_edit(self, context):
    self.layout.menu('ARMATURE_MT_QuiqRig')
    self.layout.menu('ARMATURE_MT_QuiqRig_Select2Bones')

def menu_func_pose(self, context):
    self.layout.menu('POSE_MT_QuiqRig')
    self.layout.menu('POSE_MT_QuiqRig_Select2Bones')

# ビュー＆レンダー メニュー関数

def menu_func_show_hide(self, context):
    layout = self.layout
    layout.operator('object.si_toggle_hide', text='ビュー＆レンダー：選択物を隠す/表示')
    layout.operator('object.si_show_hidden_objects', text='ビュー＆レンダー：隠したオブジェクトを表示')
    layout.operator('object.si_hide_unselected', text='ビュー＆レンダー：非選択物を隠す')
    layout.separator()
    layout.operator('view3d.tgl_hide_object_type', text='オブジェクトタイプで隠す')

# 登録するクラス一覧
menus_classes = (
    QuiqRigEditModeMenu,
    QuiqRig_2seL_EditModeMenu,
    QuiqRigPoseModeMenu,
    QuiqRig_2sel_PoseModeMenu,
)

# メニューの登録

def register_menus():
    for cls in menus_classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_edit_armature.append(menu_func_edit)
    bpy.types.VIEW3D_MT_pose.append(menu_func_pose)
    bpy.types.VIEW3D_MT_object_showhide.append(menu_func_show_hide)

# メニューの解除

def unregister_menus():
    bpy.types.VIEW3D_MT_edit_armature.remove(menu_func_edit)
    bpy.types.VIEW3D_MT_pose.remove(menu_func_pose)
    bpy.types.VIEW3D_MT_object_showhide.remove(menu_func_show_hide)
    for cls in reversed(menus_classes):
        try:
            bpy.utils.unregister_class(cls)
        except:
            pass 