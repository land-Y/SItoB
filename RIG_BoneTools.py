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
    self.layout.operator("armature.deleteboneposemode")

class si_BoneTools():

    def __init__(self,targetBone):
        self.targetBone = targetBone
        self.targetName = self.targetBone.name
        self.armature = self.targetBone.id_data
        self.armatureObj = bpy.context.object
        self.SaveMode = bpy.context.mode
        self.posebones = bpy.context.selected_pose_bones







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

    def newBone_FromSelect1Bone(self,newBoneName = "Bone.000"):
        SaveMode = self.ChangeEditMode()



        #Poseからのボーン取得では rollが取得できないのでEditBoneに設定し直す
        A = self.armature.edit_bones[self.targetBone.name]
        directionVector = A.matrix @ Vector((0, 1, 0))
        tailPos = directionVector.lerp(A.head, -2)
        newBone = self.armature.edit_bones.new(newBoneName)
        newBone.head = A.tail
        newBone.tail = tailPos
        newBone.length = A.length
        newBone.roll = A.roll
        bpy.ops.armature.select_all(action='DESELECT')
        newBone.select = True
        newBone.select_head = True
        newBone.select_tail = True
        bpy.ops.object.mode_set(mode=SaveMode)


        return newBone

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


    def DeleteBonePoseMode(self):
        SaveMode = self.ChangeEditMode()
        bpy.ops.armature.delete()
        bpy.ops.object.mode_set(mode=SaveMode)

class MakeBoneOne_OT_object(bpy.types.Operator):
    bl_idname = "armature.newbone_fromselect1bone"
    bl_label = "1SelectBone MakeBone(Pose OK)"
    bl_description = "1SelectBone MakeBone(Pose OK)"
    bl_options = {'REGISTER', 'UNDO'}

    #ボーン名をプレファレンスで決めれる
    BoneNameProp : StringProperty(name = "Bone Name", default = "Bone.000")
    #メニューに登録 2箇所。EDITの追加とPOSEのペアレント
    bpy.types.TOPBAR_MT_edit_armature_add.prepend(menu_draw)
    bpy.types.VIEW3D_MT_object_parent.prepend(menu_draw)

    def execute(self, context):
        Bone = si_BoneTools(bpy.context.active_bone)
        Bone.newBone_FromSelect1Bone(newBoneName = self.BoneNameProp)
        return {'FINISHED'}

class MakeBoneTwo_OT_object(bpy.types.Operator):
    bl_idname = "armature.newbone_fromselect2bone"
    bl_label = "2SelectBone Between MakeBone(Pose OK)"
    bl_description = "Make newBone between 2Selected bones"
    bl_options = {'REGISTER', 'UNDO'}

    #ボーン名をプレファレンスで決めれる
    BoneNameProp : StringProperty(name = "Bone Name", default = "Bone.000")


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

class DeleteBonePoseMode_OT_object(bpy.types.Operator):
    bl_idname = "armature.deleteboneposemode"
    bl_label = "DeleteBone can PoseMode"
    bl_description = "DeleteBone can Pose&Object Mode"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        Bone = si_BoneTools(bpy.context.active_bone)
        Bone.DeleteBonePoseMode()
        return {'FINISHED'}