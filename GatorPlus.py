import bpy
from bpy.props import BoolProperty

"""Softimage GatorPlus(自作ツール）のBlender版
    アクティブオブジェクトから複数選択オブジェクトへウェイト転送
    頂点グループの掃除とアーマチュアモデファイア削除機能"""
class ArmatureModifier():
    """アクティブオブジェクトのモデファイアにあるArmatureからプロパティ取得"""
    def __init__(self):

        #ウェイト転送オブジェクト入れ
        self.ObjList = []

        #アクティブオブジェクト名はリムーブ
        self.activeObjName = bpy.context.active_object.name
        self.SelectedObj = bpy.context.selected_objects
        for obj in self.SelectedObj:
            self.ObjList.append(obj.name)
        self.ObjList.remove(self.activeObjName)

        #アクティブオブジェクトのアーマチュアはfor loopでスコープがずれるので名前で定義
        #モデファイアのプロパティ全部取得
        for mod in bpy.data.objects[self.activeObjName].modifiers:
            if mod.type == "ARMATURE":
                self.ActiveObj_Armature = mod
        if self.ActiveObj_Armature != None:
            self.name = self.ActiveObj_Armature.name
            self.Object = self.ActiveObj_Armature.object
            self.vertex_group  = self.ActiveObj_Armature.vertex_group
            self.use_deform_preserve_volume = self.ActiveObj_Armature.use_deform_preserve_volume
            self.use_multi_modifier = self.ActiveObj_Armature.use_multi_modifier
            self.use_vertex_groups = self.ActiveObj_Armature.use_vertex_groups
            self.use_bone_envelopes = self.ActiveObj_Armature.use_bone_envelopes
            self.show_in_editmode = self.ActiveObj_Armature.show_in_editmode
            self.show_on_cage = self.ActiveObj_Armature.show_on_cage

    '''最後に選択したオブジェクト（アクティブオブジェクト）で、ウェイト転送を実行。'''
    def TranslateArmature(self):

        #オブジェクト→データのリンク転送→メッシュデータの転送
        #引数は必要なもの全て埋めなければ動かない。
        bpy.ops.object.data_transfer(data_type='VGROUP_WEIGHTS',
        use_create=True, vert_mapping='NEAREST', use_object_transform=True,
        layers_select_src='ALL', layers_select_dst='NAME',
        mix_mode='REPLACE', mix_factor=1)


        #オブジェクト扱う際も名称を取得してから実行時に実体化する
        for ObjName in self.ObjList:
            obj = bpy.data.objects[ObjName]
            arm = obj.modifiers.get("Armature")
            if arm == None:
                arm = obj.modifiers.new("Armature",type = "ARMATURE")
            arm.name = self.name
            arm.object = self.Object
            arm.vertex_group = self.vertex_group
            arm.use_deform_preserve_volume = self.use_deform_preserve_volume
            arm.use_multi_modifier = self.use_multi_modifier
            arm.use_vertex_groups =  self.use_vertex_groups
            arm.use_bone_envelopes = self.use_bone_envelopes
            arm.show_in_editmode = self.show_in_editmode
            arm.show_on_cage = self.show_on_cage
            print(obj.name + " Transform Finish")

    def DeleteArmatureModifier(self,DelUnlockVertexGroup_bool = True):
        if DelUnlockVertexGroup_bool == True:
            for Obj in self.SelectedObj:
                for arm in Obj.modifiers:
                    if arm.type == "ARMATURE":
                        Obj.modifiers.remove(arm)
                        print(Obj.name + " Delete Armature Modifier")

    def DeleteGroupDefomers(self,DelArmMod_bool = True):
        if DelArmMod_bool == True:
            for Obj in self.SelectedObj:
                Obj.vertex_groups.clear()
                print(Obj.name + "Delete Vertex Groups")

class gator_plus_OT_object(bpy.types.Operator):
    bl_idname = "object.gator_plus"
    bl_label = "Copy Modifier_Armature from ActiveObject"
    bl_description = "Copy Modifier_Armature from ActiveObject"
    bl_options = {'REGISTER', 'UNDO'}

    DelUnlockVertexGroup  : BoolProperty (name ="Copy Modifier_Armature from ActiveObject", default =True)

    def execute(self, context):
        mod = ArmatureModifier()
        mod.TranslateArmature()
        return {'FINISHED'}

class gator_plus_DelArmVertex_OT_object(bpy.types.Operator):
    bl_idname = "object.gator_plus_deletevertex_modifier"
    bl_label = "Delete 'unlocked vertex groups' before Modifire transfer"
    bl_description = "Delete 'unlocked vertex groups' before Modifire transfer"
    bl_options = {'REGISTER', 'UNDO'}

    DelUnlockVertexGroup_bool  : BoolProperty (name ="Delete 'unlocked vertex groups' before Modifire transfer", default =True)
    DelArmMod_bool  : BoolProperty (name ="Delete 'Armature' Modifire", default =True)

    def execute(self, context):
        mod = ArmatureModifier()
        mod.DeleteGroupDefomers(self.DelUnlockVertexGroup_bool)
        mod.DeleteArmatureModifier(self.DelArmMod_bool)
        return {'FINISHED'}

classes = (
    gator_plus_OT_object,
    gator_plus_DelArmVertex_OT_object,
)
