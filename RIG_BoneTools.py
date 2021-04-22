import bpy
from bpy.types import IntAttribute
from mathutils import Vector, Matrix
from bpy.props import StringProperty, IntProperty, BoolProperty

#選択ボーンがポーズモードでもペアレント化できる。

#メニュー登録関係
def menu_draw(self, context):
    self.layout.operator("armature.newbone_fromselect2bone")
    self.layout.operator("armature.setparentposemode")
    self.layout.operator("armature.clearparentposemode")

class si_BoneTools():

    def __init__(self,targetBone):
        self.targetBone = targetBone
        self.targetName = self.targetBone.name
        self.armature = self.targetBone.id_data
        self.armatureObj = bpy.context.object
        self.SaveMode = bpy.context.mode
        self.posebones = bpy.context.selected_pose_bones

    def SelectBoneTwo(self):
        #選択したボーンはA,Bと定義。選択順が判定できるのは2つまで
        oBones = list()
        a = self.targetBone
        oBones.append(a)

        #EDITMODE
        if bpy.context.mode == "EDIT_ARMATURE":
            #選択ボーンが一つ以下ならエラー
            if len(bpy.context.selected_bones) <= 1:
                raise RuntimeError("Please select two or more")
            for b in self.armature.edit_bones:
                if b.select:
                    oBones.append(b)
        #POSEMODE
        elif bpy.context.mode == "POSE":
            if len(self.posebones) <= 1:
                raise RuntimeError("Please select two or more")
            for b in self.posebones:
                b = self.armature.bones[b.name]
                if b.select:
                    oBones.append(b)


        oBones = (list(dict.fromkeys(oBones) ) )
        A = oBones[1]
        B = oBones[0]
        return A,B

    def ChangeEditMode(self):
        SaveMode = bpy.context.mode
        if SaveMode == "EDIT_ARMATURE":
            SaveMode = "EDIT"
        bpy.ops.object.mode_set(mode="EDIT")
        return SaveMode

    def SetParentPoseMode(self):
        SaveMode = self.ChangeEditMode()
        ActiveBone = bpy.context.active_bone
        for i in bpy.context.selected_bones:
            i.parent = ActiveBone
        bpy.ops.object.mode_set(mode=SaveMode)
        return i

    def newBone_FromSelect2Bone(self,newBoneName = "Bone.000"):
        A,B = self.SelectBoneTwo()
        print(A,B)
        SaveMode = self.ChangeEditMode()
        #Poseからのボーン取得では rollが取得できないのでEditBoneに設定し直す
        A = self.armature.edit_bones[A.name]
        B = self.armature.edit_bones[B.name]
        newBone = self.armature.edit_bones.new(newBoneName)
        newBone.head = A.tail
        newBone.tail = B.head
        newBone.roll = A.roll
        bpy.ops.object.mode_set(mode=SaveMode)
        return newBone

    def ClearParentPoseMode(self):
        SaveMode = self.ChangeEditMode()
        for sel in bpy.context.selected_bones:
            self.armature.edit_bones[sel.name].parent = None
        bpy.ops.object.mode_set(mode=SaveMode)


class MakeBone_OT_object(bpy.types.Operator):
    bl_idname = "armature.newbone_fromselect2bone"
    bl_label = "MakeBone can PoseMode"
    bl_description = "Make newBone between 2Selected bones"
    bl_options = {'REGISTER', 'UNDO'}

    #ボーン名をプレファレンスで決めれる
    BoneNameProp : StringProperty(name = "Bone Name", default = "Bone.000")
    #メニューに登録 2箇所。EDITの追加とPOSEのペアレント
    bpy.types.TOPBAR_MT_edit_armature_add.prepend(menu_draw)
    bpy.types.VIEW3D_MT_object_parent.prepend(menu_draw)

    def execute(self, context):
        Bone = si_BoneTools(bpy.context.active_bone)
        Bone.newBone_FromSelect2Bone(newBoneName = self.BoneNameProp)
        return {'FINISHED'}


class SetParent_OT_object(bpy.types.Operator):
    bl_idname = "armature.setparentposemode"
    bl_label = "ParentBone can PoseMode"
    bl_description = "SetParent can Pose&Object Mode"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        Bone = si_BoneTools(bpy.context.active_bone)
        Bone.SetParentPoseMode()
        return {'FINISHED'}

class ClearParent_OT_object(bpy.types.Operator):
    bl_idname = "armature.clearparentposemode"
    bl_label = "ClearParent can PoseMode"
    bl_description = "clearParent can Pose&Object Mode"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        Bone = si_BoneTools(bpy.context.active_bone)
        Bone.ClearParentPoseMode()
        return {'FINISHED'}