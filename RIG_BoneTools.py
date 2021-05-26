import bpy
import importlib
from bpy.types import IntAttribute
from mathutils import Vector, Matrix
from bpy.props import StringProperty, IntProperty, BoolProperty,FloatProperty
from . import cvELD_RigIcon
importlib.reload(cvELD_RigIcon)
from .cvELD_RigIcon import *

#選択ボーンがポーズモードでもペアレント化


#メニュー登録関係
def menu_draw(self, context):
    self.layout.operator("armature.matchbonetwo")
    self.layout.operator("armature.newbone_fromselect1bone_offset")
    self.layout.operator("armature.newbone_fromselect1bone")
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
        self.poseBoneName = bpy.context.object.pose.bones


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

    #２つ選択したボーンで１つ目のヘッドに２つ目のテイルをくっつける
    def AttatchBoneSRT():
        return
    #選択ボーンの親にボーン挿入


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

    def newBone_FromSelect1Bone(self,newBoneName = "Bone.000", Parent = None,CustomShapeSize =0.2):
        SaveMode = self.ChangeEditMode()
        #Poseからのボーン取得では rollが取得できないのでEditBoneに設定し直す

        #選択したボーンは名前で保持しておかないと追加ボーンや親子変更でスコープが狂う
        BoneList = []
        for i in bpy.context.selected_bones:
            BoneList.append(i.name)

        for v in BoneList:
            print(BoneList)
            A = self.armature.edit_bones[v]
            oParent = bpy.context.active_bone.parent
            oChild = bpy.context.active_bone.children
            directionVector = A.matrix @ Vector((0, 1, 0))
            tailPos = directionVector.lerp(A.head, -2)
            newBone = self.armature.edit_bones.new(newBoneName)
            EditBone = self.armature.edit_bones

            if Parent == None:
                newBone.head = A.tail
                newBone.tail = tailPos
                newBone.length = A.length
                newBone.roll = A.roll
                ReNewBoneName = newBoneName


            elif Parent == "Parent":
                A.use_connect = False
                newBone.head = A.head
                newBone.tail = tailPos
                newBone.length = A.length/2
                newBone.bbone_x = 0.25
                newBone.bbone_z = 0.25
                newBone.roll = A.roll
                ReNewBoneName = newBone.name = "p_" + A.name

                #選択ボーンに親が居なければ新規ボーンも親なし、それ以外は親継承
                if oParent != None:
                    EditBone[ReNewBoneName].parent = oParent
                if oChild != None:
                        for i in oChild:
                            i.parent = A
                #再ペアレントはボーンの名称で行わないとスコープがズレる対策
                A.parent = EditBone[ReNewBoneName]

                #アイコン設定、中身はcvELD_Toolsからコピペ、バージョン同期忘れずに

                bpy.ops.object.mode_set(mode='POSE')
                icon = cvELD_RIG_Icon()
                icon.LoadShape("cs_SiCube")
                self.poseBoneName[newBone.name].custom_shape = bpy.data.objects["cs_SiCube"]
                self.poseBoneName[newBone.name].custom_shape_scale = CustomShapeSize
                bpy.ops.object.mode_set(mode='EDIT')


        bpy.ops.armature.select_all(action='DESELECT')
        EditBone[ReNewBoneName].select = True
        EditBone[ReNewBoneName].select_head = True
        EditBone[ReNewBoneName].select_tail = True

        bpy.ops.object.mode_set(mode=SaveMode)
        print("finish")

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

class MakeBoneOne_Offset_OT_object(bpy.types.Operator):
    bl_idname = "armature.newbone_fromselect1bone_offset"
    bl_label = "OffsetBone(Pose OK)"
    bl_description = "SelectBone Make Offset Bone(Pose OK)"
    bl_options = {'REGISTER', 'UNDO'}
    #, name = "CustomShape Size", description = "CustomShape Size"
    size_intProp : FloatProperty(default=0.2,name = "OffsetBone size" ,description="OffsetBone size")

    def execute(self, context):
        Bone = si_BoneTools(bpy.context.active_bone)
        #プロパティが異なるだけで１選択から実行の処理に組み込んだ
        Bone.newBone_FromSelect1Bone(CustomShapeSize = self.size_intProp, Parent = "Parent")
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

class MatchBoneTwo_OT_object(bpy.types.Operator):
    bl_idname = "armature.matchbonetwo"
    bl_label = "Fit and aline select 2 bones"
    bl_description = "Fit and aline select 2 bones"
    bl_options = {'REGISTER', 'UNDO'}

    AlineBool : BoolProperty(name = "Aline", default = True)

    def execute(self, context):
        Bone = si_BoneTools(bpy.context.active_bone)
        #２ボーン選択で１番目をA、２番めをBとする
        A,B = Bone.SelectBoneTwo()

        #Bボーンの長さを一旦格納。
        Blen = B.length
        #Aボーンの向きに合わせる
        directionVector = A.matrix @ Vector((0, 1, 0))
        tailPos = directionVector.lerp(A.head, -2)
        #選択ボーンの順にフィット
        B.head = A.tail
        B.roll = A.roll
        #Bボーンの長さをもとに戻す
        if self.AlineBool:
            B.tail = tailPos
            B.length = Blen
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