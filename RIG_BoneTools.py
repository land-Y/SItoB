import bpy
import importlib
import re
import numpy as np
from bpy.types import IntAttribute , Operator, AddonPreferences, Panel, PropertyGroup
from mathutils import Vector, Matrix
from bpy.props import StringProperty, IntProperty, BoolProperty,FloatProperty,EnumProperty
from . import cvELD_RigIcon
importlib.reload(cvELD_RigIcon)
from .cvELD_RigIcon import *

"""１～２の選択ボーンから新規ボーンを生成するツール。
・限られた数のコンストレインが選択可能。
・グループ分け、レイヤー分け、ディスプレイ表示アイコン設定の自動化。
・その他、スライダー用ボーン、２関節を３関節ボーンに、等もある
・ポーズモードでも、ボーンをペアレントしたりデリートする機能あり
    """

class QuickBone_Utility(object):
    """ よく使うボーン用の補助関数をまとめておくクラス
    PoseBone関係が多いが、よくわからずに突っ込んだので無駄に重複している。
    整理はしたいと思っていたが放置してしまった。
    整理してください """
    def __init__(self,targetBone):
        self.targetBone = targetBone
        self.targetName = self.targetBone.name
        self.armature = self.targetBone.id_data
        self.armatureObj = bpy.context.object
        self.SaveMode = bpy.context.mode
        self.poseBonesSel = bpy.context.selected_pose_bones
        self.poseBonesName = self.armatureObj.pose.bones
        self.poseBoneName = bpy.context.object.pose.bones
        self.EditBone = self.armature.edit_bones
        self.Bones = bpy.context.object.data.bones

    def setLayerFromIndex(self, bone, index ,Add = True):
        """ レイヤー分け """
        for i in range(32):
            bone.layers[index] = True
            if Add == False:
                if i != index:
                    bone.layers[i] = False

    def GetModifires(self):
        """ モデファイアの取得 """
        for i in self.poseBonesSel:
            #モディファイアの適応数
            num = len(i.constraints)
            CnsName = i.name
            return num,CnsName

    def ClearParentPoseMode(self):
        """ ポーズモードでも強制的にペアレントを解除する """
        SaveMode = self.ChangeEditMode()
        for sel in bpy.context.selected_bones:
            self.armature.edit_bones[sel.name].parent = None
        bpy.ops.object.mode_set(mode=SaveMode)

    def DeleteBonePoseMode(self):
        """ ポーズモードでも強制的にボーンをデリートする """
        SaveMode = self.ChangeEditMode()
        bpy.ops.armature.delete()
        bpy.ops.object.mode_set(mode=SaveMode)

    def SelectBoneTwo(self):
        """ 選択したボーンをA,Bと順番定義。選択順が判定できるのは2つまで"""
        oBones = list()
        a = self.targetBone
        oBones.append(a.name)
        #EDITMODE
        if bpy.context.mode == "EDIT_ARMATURE":
            #選択ボーンが一つ以下ならエラー
            if len(bpy.context.selected_bones) <= 1:
                raise RuntimeError("Please select two or more")
            else:
                for b in self.armature.edit_bones:
                    if b.select:
                        oBones.append(b.name)
        #POSEMODE
        elif bpy.context.mode == "POSE":
            if len(self.poseBonesSel) <= 1:
                raise RuntimeError("Please select two or more")
            else:
                for b in self.poseBonesSel:
                    oBones.append(b.name)
        oBones = (list(dict.fromkeys(oBones)))
        A = oBones[1]
        B = oBones[0]
        return A,B

    def FitBones(self,A,B, C=None , FitMethod =  "TtoH" ,oAline = True ,oLength= True):
        """  ボーン２本の長さ合わせたり、向きを合わせる。
                ヘッドとテイルにフィットさせたり等ができる。"""

        bpy.ops.object.mode_set(mode="EDIT")

        A = self.EditBone[A]
        B = self.EditBone[B]
        #Bボーンの長さを一旦格納。
        Blen = B.length
        #Aボーンの向きに合わせる
        directionVector = A.matrix @ Vector((0, 1, 0))
        tailPos = directionVector.lerp(A.head, -1000)


        #Cの中にオブジェクトがある場合は、フィットモードはCの為に
        if C != None:
            C = self.EditBone[C]
            if FitMethod == "TtoH":
                C.head = A.tail
                C.tail = B.head
                C.roll = A.roll
            elif FitMethod == "TtoT":
                C.head = A.tail
                C.tail = B.tail
                C.roll = A.roll
            elif FitMethod == "HtoH":
                C.head = A.head
                C.tail = B.head
                C.roll = A.roll
            elif FitMethod == "HtoT":
                C.head = A.head
                C.tail = B.tail
                C.roll = A.roll
            elif FitMethod == "Fit1stBone":
                C.head = A.head
                C.tail = A.tail
                C.roll = A.roll
            elif FitMethod == "Fit2ndBone":
                C.head = B.head
                C.tail = B.tail
                C.roll = B.roll
            if oLength == True:
                B.length = Blen
            return C.head, C.tail, C.roll
        else:
            #選択ボーンの順にフィット
            if FitMethod == "TtoH":
                B.tail = A.head
                if oLength == True:
                    B.length = Blen
            elif FitMethod == "TtoT":
                B.tail = A.tail
                B.roll = A.roll
                if oLength == True:
                    B.length = Blen
            elif FitMethod == "HtoH":
                B.head = A.head
                B.roll = A.roll
                if oLength == True:
                    B.length = Blen
            elif FitMethod == "HtoT":
                B.head = A.tail
                B.roll = A.roll
                #Bボーンの長さをもとに戻す
                if oAline == True:
                    B.tail = tailPos
                if oLength == False:
                    B.length = A.length

            elif FitMethod == "ALL":
                B.head = A.head
                B.tail = A.tail
                B.roll = A.roll
            if oLength == True:
                B.length = Blen
            return B.head,B.tail,B.roll


    def ChangeEditMode(self):
        """ 現在のモードを記憶しつつEDITモードに変更 """
        SaveMode = bpy.context.mode
        if SaveMode == "EDIT_ARMATURE":
            SaveMode = "EDIT"
        bpy.ops.object.mode_set(mode="EDIT")
        return SaveMode

    def NewBonesSelector(self,SaveMode,newBoneList):
        """ 新規ボーン生成後、選択する。EDITとPOSE両対応 """
        if SaveMode == "EDIT":
            bpy.ops.armature.select_all(action='DESELECT')
            for i in newBoneList:
                self.EditBone[i].select = True
                self.EditBone[i].select_head = True
                self.EditBone[i].select_tail = True
        elif SaveMode == "POSE":
            bpy.ops.pose.select_all(action='DESELECT')
            for i in newBoneList:
                self.Bones[i].select = True


    def SetParentPoseMode(self):
        """ ポーズモードでもペアレント処理が可能に """
        SaveMode = self.ChangeEditMode()
        ActiveBone = bpy.context.active_bone
        for i in bpy.context.selected_bones:
            i.parent = ActiveBone
        bpy.ops.object.mode_set(mode=SaveMode)
        return i

    def getBoneGroups():
        """ Scene中のボーングループ取得 """
        BoneGroupList = []
        boneGroups   = bpy.context.active_object.pose.bone_groups
        print(boneGroups)
        for i in boneGroups:
            BoneGroupList.append(i)
        return BoneGroupList

    def setBoneGroups(self ,BoneName = None , GroupName = "None"):
        """ボーングループの生成"""
        def createBoneGroup(name="", theme = ""):
            boneGroups = bpy.context.active_object.pose.bone_groups
            if name in boneGroups:
                return name
            else:
                boneGroup = boneGroups.new()
                boneGroup.name = name
            boneGroups[name].color_set = theme
            return name


        if GroupName != "None":
            if GroupName == "primary":
                oTem = "THEME01"
            elif GroupName == "secondry":
                oTem = "THEME04"
            elif GroupName ==  "offset":
                oTem = "THEME03"
            elif GroupName ==  "unsel":
                oTem = "THEME13"
            elif GroupName ==  "hide":
                oTem = "THEME10"
            elif GroupName ==  "UPV":
                oTem = "THEME09"
            else:
                oTem = 'DEFAULT'
            oGroup          = createBoneGroup(GroupName, oTem)
            boneGroups      = bpy.context.active_object.pose.bone_groups
            self.poseBoneName[BoneName].bone_group = boneGroups.get(oGroup)
        return

    def clearDriver(self, BoneName = "None",CustomParaName = "None"):
        """ドライバー初期化 カスタムパラメーターの中身も削除"""
        animData = self.armatureObj.animation_data
        #アーマチュアの中にあるベンディボーンのドライバ抽出
        animDataArmature = bpy.context.object.data.bones[BoneName].id_data.animation_data

        if animData == None:
            return
        #ドライバーの場所が２箇所ある。ボーンとベンディボーンで格納場所が異なる。
        DriverList = [driver for driver in animData.drivers if driver.data_path.startswith("""pose.bones["{}"]""".format(BoneName))]
        DriverListArmature = [driver for driver in animDataArmature.drivers if driver.data_path]

        for driver in DriverListArmature:
            paramNameArmature = driver.data_path.replace("""bones["{}"].""".format(BoneName), "")
            print(paramNameArmature)
            self.armatureObj.driver_remove(paramNameArmature)

        for driver in DriverList:
            paramName = driver.data_path.replace("""pose.bones["{}"].""".format(BoneName), "")
            self.poseBonesName[BoneName].driver_remove(paramName)
            #アーマチュアの中にあるベンディボーンのドライバ削除

            if CustomParaName != None:
                CustomParaName = '["'+CustomParaName+'"]'
                self.poseBonesName[BoneName].driver_remove(CustomParaName)
        return

    def BoneNameSwap_LR(self,nameList):
        """ 左右の名称をスワップ。LeftがRightに """
        l = ("l","L","Left","LEFT")
        r = ("r","R","Right","RIGHT")
        repNameList = []
        for name in nameList:
            rep = re.match("(.*)(\.|_)(l$|r$|L$|R$|Left$|Right$|LEFT$|Right$|left$|right$)",name)
            if rep is None:
                continue

            repGroup = list(rep.groups())
            repWord = repGroup[-1]
            if repWord in l:
                repGroup[2] = r[l.index(repWord)]
            elif repWord in r:
                repGroup[2] = l[r.index(repWord)]
            repNameList.append("".join(repGroup))
        return repNameList

    def SymmetrizeBone_Driver(self, BoneList = "None",CustomParaName = "None"):
        """ 未完成：ドライバーのシンメトリ複製 """
        #ドライバーのシンメトリ化
        #選択ボーンの名称判定。L→R Left→Rightなど　#opsは複製後のオブジェクト名を取得しないので選択中の名称で判定する。
        for BoneName in BoneList:
            print(BoneName)
            animData = self.armatureObj.animation_data
            animDataArmature = bpy.context.object.data.bones[BoneName].id_data.animation_data
            if animData == None:
                return
            DriverList = [driver for driver in animData.drivers if driver.data_path.startswith("""pose.bones["{}"]""".format(BoneName))]
            DriverArmatureList = [driver for driver in animDataArmature.drivers if driver.data_path]

            print(DriverList)
            #print(DriverArmatureList)
            for driver in DriverList:

                paramName = driver.data_path.replace("""pose.bones["{}"].""".format(BoneName), "")
                print(paramName)
                self.poseBonesName[BoneName].driver_add(paramName)
                # if CustomParaName != None:
                #     CustomParaName = '["'+CustomParaName+'"]'
                #     self.poseBonesName[BoneName].driver_remove(CustomParaName)
            return

class QuickBone_Tools(object):
    """ 選択ボーンに骨を生やすクラス """
    def __init__(self,targetBone):
        self.targetBone = targetBone
        self.targetName = self.targetBone.name
        self.armature = self.targetBone.id_data
        self.armatureObj = bpy.context.object
        self.SaveMode = bpy.context.mode
        self.poseBonesSel = bpy.context.selected_pose_bones
        self.poseBonesName = self.armatureObj.pose.bones
        self.poseBoneName = bpy.context.object.pose.bones
        self.EditBone = self.armature.edit_bones
        self.EditBoneDataName = bpy.data.armatures[self.armature.name].edit_bones
        self.Bones = bpy.context.object.data.bones

        #クラスインスタンス
        self.QUtil = QuickBone_Utility(self.targetBone)
        self.icon = cvELD_RIG_Icon()

    def newBone_FromSelect1Bone(self,newBoneName = "Bone.000", oMode = "Simple",
                                CustomShapeSize =0.2 ,
                                oHeadorTailBool = True,
                                oSympleParent = False,
                                oRot = True,
                                oTra = True,
                                oScl = True,
                                oLimitRot = False,
                                oLimitLoc = False,
                                BBsize = 0.2,
                                oChainCount = 1,
                                oSeg = 2,
                                SegmentRevers = True,
                                DefomerBoneLayer = 0,
                                AddBoneLayer = True,
                                addLength = 0,
                                oGroupName = None,
                                UPVpos = 2,
                                ):
        """ １選択ボーンで実行すると新規ボーン生成。その後、様々な機能やプロパティを付与 """
        SaveMode = self.QUtil.ChangeEditMode()
        #Poseからのボーン取得では rollが取得できないのでEditBoneに設定し直す
        bpy.ops.object.mode_set(mode='EDIT')
        #生成したボーンのリスト（複数対応のため
        newBoneList = []
        SelBoneNamesList = []

        for i in bpy.context.selected_bones:
            SelBoneNamesList.append(i.name)

        for v in SelBoneNamesList:
            A = self.EditBoneDataName[v]
            directionVector = A.matrix @ Vector((0, 1, 0))
            tailPos = directionVector.lerp(A.head, -10000)
            newBone = self.armature.edit_bones.new(newBoneName)


            def MakeBoneModes():
                """ 何もないシンプルなボーンを生成 """
                if oMode == "Simple":
                    if oHeadorTailBool == True:
                        newBone.head = A.tail
                    else:
                        newBone.head = A.head
                    newBone.tail = tailPos
                    newBone.length = A.length+ addLength
                    newBone.roll = A.roll


                    if oSympleParent == True:
                        newBone.parent = A
                    ReNewBoneName = newBone.name


                #オフセット用のボーン生成
                elif oMode == "Offset":
                    """ 選択ボーンの根本にオフセット用ボーン配置 """
                    A.use_connect = False
                    newBone.head = A.head
                    newBone.tail = tailPos
                    newBone.length = A.length/2 + addLength
                    newBone.roll = A.roll
                    ReNewBoneName = newBone.name = "p_" + A.name
                    ReNewBoneName = newBone.name


                    self.EditBone[ReNewBoneName].parent = A.parent
                    #再ペアレントはボーンの名称で行わないとスコープがズレる対策
                    A.parent = self.EditBone[ReNewBoneName]

                    #アイコン設定、中身はcvELD_Toolsからコピペ、バージョン同期忘れずに
                    bpy.ops.object.mode_set(mode='POSE')
                    self.icon.LoadShape("cs_SiCube")
                    self.poseBoneName[ReNewBoneName].custom_shape = bpy.data.objects["cs_SiCube"]
                    self.poseBoneName[ReNewBoneName].custom_shape_scale = CustomShapeSize


                elif oMode == "Muscle_StretchTo":
                    """ ストレッチボーン """
                    newBone.head = A.tail
                    newBone.tail = tailPos
                    newBone.length = A.length/3+ addLength
                    newBone.roll = A.roll
                    ReNewBoneName = newBone.name = "St_" + A.name
                    ReNewBoneName = newBone.name

                    bpy.ops.object.mode_set(mode='POSE')
                    self.icon.LoadShape("cs_SiCube")
                    self.poseBoneName[ReNewBoneName].custom_shape = bpy.data.objects["cs_SiCube"]
                    self.poseBoneName[ReNewBoneName].custom_shape_scale = CustomShapeSize

                    if oTra == True:
                        STRETCH_TO_cns = self.poseBonesName[A.name].constraints.new("STRETCH_TO")
                        STRETCH_TO_cns.target = self.armatureObj
                        STRETCH_TO_cns.subtarget =  self.poseBoneName[ReNewBoneName].name
                        STRETCH_TO_cns.keep_axis = 'SWING_Y'

                elif oMode == "Muscle_TrackTo":
                    """ トラックボーン """
                    newBone.head = A.tail
                    newBone.tail = tailPos
                    newBone.length = A.length/3+ addLength
                    newBone.roll = A.roll
                    ReNewBoneName = newBone.name = "St_" + A.name
                    ReNewBoneName = newBone.name

                    bpy.ops.object.mode_set(mode='POSE')

                    self.icon.LoadShape("cs_SiCube")
                    self.poseBoneName[ReNewBoneName].custom_shape = bpy.data.objects["cs_SiCube"]
                    self.poseBoneName[ReNewBoneName].custom_shape_scale = CustomShapeSize

                    if oTra == True:
                        TRACK_TO_cns = self.poseBonesName[A.name].constraints.new("TRACK_TO")
                        TRACK_TO_cns.target = self.armatureObj
                        TRACK_TO_cns.subtarget =  self.poseBoneName[ReNewBoneName].name
                        TRACK_TO_cns.use_target_z = True
                        TRACK_TO_cns.track_axis = 'TRACK_Y'
                        TRACK_TO_cns.up_axis = 'UP_Z'


                #回転コンストレインで影響力半分にした補助ボーン生成
                elif oMode == "HalfRot":
                    """ 移動、回転、スケールを半分だけ取得する補助ボーン。肘や膝などに使える """
                    A.use_connect = False
                    newBone.head = A.head
                    newBone.tail = tailPos
                    newBone.length = A.length/3+ addLength
                    newBone.roll = A.roll
                    ReNewBoneName = newBone.name = "O_" + A.name
                    ReNewBoneName = newBone.name
                    #ペアレントモード、親にしてしまうと挙動1,5倍になる。

                    newBone.parent = A.parent

                    #回転コンストレイン設定

                    bpy.ops.object.mode_set(mode='POSE')
                    #移動
                    if oTra == True:
                        COPY_LOCATION_cns = self.poseBonesName[ReNewBoneName].constraints.new("COPY_LOCATION")
                        COPY_LOCATION_cns.target = self.armatureObj
                        COPY_LOCATION_cns.subtarget = A.name
                        COPY_LOCATION_cns.influence = 0.5
                        COPY_LOCATION_cns.target_space = "CUSTOM"
                        COPY_LOCATION_cns.owner_space = "CUSTOM"
                        COPY_LOCATION_cns.space_object = self.armatureObj
                        COPY_LOCATION_cns.space_subtarget = A.name
                    #スケール
                    if oScl == True:
                        COPY_SCALE_cns = self.poseBonesName[ReNewBoneName].constraints.new("COPY_SCALE")
                        COPY_SCALE_cns.target = self.armatureObj
                        COPY_SCALE_cns.subtarget = A.name
                        COPY_SCALE_cns.influence = 0.5
                        COPY_SCALE_cns.target_space = "CUSTOM"
                        COPY_SCALE_cns.owner_space = "CUSTOM"
                        COPY_SCALE_cns.space_object = self.armatureObj
                        COPY_SCALE_cns.space_subtarget = A.name
                    #回転
                    if oRot == True:
                        COPY_ROTATION_cns = self.poseBonesName[ReNewBoneName].constraints.new("COPY_ROTATION")
                        COPY_ROTATION_cns.target = self.armatureObj
                        COPY_ROTATION_cns.subtarget = A.name
                        COPY_ROTATION_cns.mix_mode = 'BEFORE'
                        COPY_ROTATION_cns.influence = 0.5
                        COPY_ROTATION_cns.target_space = "LOCAL"
                        COPY_ROTATION_cns.owner_space = "CUSTOM"
                        COPY_ROTATION_cns.space_object = self.armatureObj
                        COPY_ROTATION_cns.space_subtarget = A.name

                elif oMode == "Segment":
                    """ セグメントボーン。ボーンの指定した割合に配置する。
                    処理が独特で半分から上、または下で切り替えるチェックボックス付き"""
                    A.use_connect = False
                        #interPoseを生成する中心点のベクトル
                    oLin = np.linspace(A.head,A.tail,oSeg +1)
                    if SegmentRevers == True:
                        revers_oLin = list(reversed(oLin))
                        newBone.head = revers_oLin[oSeg-1]
                    else:
                        newBone.head = oLin[oSeg-1]

                    newBone.tail = A.tail
                    newBone.bbone_x = 0.25
                    newBone.bbone_z = 0.25
                    newBone.roll = A.roll
                    ReNewBoneName = newBone.name = "seg_" + A.name
                    #名前被りの場合勝手に001+されていくので名前再取得
                    ReNewBoneName = newBone.name


                    bpy.ops.object.mode_set(mode='POSE')
                    ReNewBoneName = self.poseBonesName[ReNewBoneName].name
                    #トランスフォームコンストレイン
                    if self.poseBonesName[ReNewBoneName].constraints.get("Copy Transforms") == None:
                        COPY_TRANSFORMS_cns = self.poseBonesName[ReNewBoneName].constraints.new("COPY_TRANSFORMS")
                    else:
                        COPY_TRANSFORMS_cns = self.poseBonesName[ReNewBoneName].constraints.get("Copy Transforms")
                    COPY_TRANSFORMS_cns.target = self.armatureObj
                    COPY_TRANSFORMS_cns.subtarget = A.name
                    COPY_TRANSFORMS_cns.target_space = "WORLD"
                    COPY_TRANSFORMS_cns.owner_space = "WORLD"
                    if SegmentRevers == True:
                        COPY_TRANSFORMS_cns.head_tail = 1/oSeg
                    else:
                        COPY_TRANSFORMS_cns.head_tail = 1-(1/oSeg)




                elif oMode == "ChildCns":
                    """ チャイルドコンストレイン """
                    A.use_connect = False
                    newBone.head = A.head
                    newBone.tail = tailPos
                    newBone.length = A.length/1.25+ addLength
                    newBone.bbone_x = 1.2
                    newBone.bbone_z = 0.5
                    newBone.roll = A.roll
                    ReNewBoneName = newBone.name = "sdw_" + A.name
                    ReNewBoneName = newBone.name
                    bpy.ops.object.mode_set(mode='POSE')


                    CHILD_OF_cns = self.poseBonesName[ReNewBoneName].constraints.new("CHILD_OF")
                    CHILD_OF_cns.target = self.armatureObj
                    CHILD_OF_cns.subtarget = A.name

                elif oMode == "IK":
                    """ KアップベクトルはIKのZ＋に配置する、または選択ボーンに切り替え """
                    A.use_connect = False
                    newBone.use_deform = False
                    newBone.head = A.tail
                    newBone.tail = tailPos
                    newBone.length = A.length*0.4+ addLength
                    newBone.roll = A.roll
                    ReNewBoneName = newBone.name = "IK" + A.name
                    ReNewBoneName = ReNewBoneName #名前かぶり対策

                    #UPVボーン生成
                    newUPVBone = self.armature.edit_bones.new("UPV" + A.name)
                    ReNewUPVBoneName = newUPVBone.name #名前かぶり対策

                    newUPVBone.use_deform = False
                    newUPVBone.head = newBone.matrix @ Vector((0, 0, UPVpos))
                    newUPVBone.tail = newBone.matrix @ Vector((0, 1, UPVpos))


                    newUPVBone.length = A.length*0.4+ addLength
                    newUPVBone.roll = A.roll
                    newUPVBone.parent = newBone

                    bpy.ops.object.mode_set(mode='POSE')
                    #IKコンストレイン

                    if self.poseBonesName[A.name].constraints.get("IK") == None:
                        IK_cns = self.poseBonesName[A.name].constraints.new("IK")
                    else:
                        IK_cns = self.poseBonesName[A.name].constraints.get("IK")
                    IK_cns.target = self.armatureObj
                    IK_cns.subtarget = ReNewBoneName
                    IK_cns.pole_target = self.armatureObj
                    IK_cns.pole_subtarget = ReNewUPVBoneName
                    IK_cns.chain_count = oChainCount
                    IK_cns.pole_angle = 1.5708

                    #icon
                    self.icon.LoadShape("cs_SiIK")
                    self.poseBoneName[ReNewBoneName].custom_shape = bpy.data.objects["cs_SiIK"]
                    self.poseBoneName[ReNewBoneName].custom_shape_scale = CustomShapeSize

                    self.icon.LoadShape("cs_SiPyramid")
                    self.poseBoneName[ReNewUPVBoneName].custom_shape = bpy.data.objects["cs_SiPyramid"]
                    self.poseBoneName[ReNewUPVBoneName].custom_shape_scale = CustomShapeSize

                    #UPVは強制グループ
                    self.QUtil.setBoneGroups(BoneName = ReNewUPVBoneName ,GroupName = "UPV")
                return ReNewBoneName

            #メイクボーンモード

            """ 以下はボーン生成後、共有の追加機能を付与 """
            ReNewBoneName = MakeBoneModes()
            newBoneList.append(ReNewBoneName)


            """ 新規ボーンに移動と回転のリミット付与ブール選択 """
            bpy.ops.object.mode_set(mode='POSE')#シーンリフレッシュさせないと骨を認知してくれない
            if oLimitRot == True:
                COPY_LimitRot_cns = self.poseBonesName[ReNewBoneName].constraints.new("LIMIT_ROTATION")
                COPY_LimitRot_cns.owner_space = 'LOCAL'
            if oLimitLoc == True:
                COPY_LimitLoc_cns = self.poseBonesName[ReNewBoneName].constraints.new("LIMIT_LOCATION")
                COPY_LimitLoc_cns.owner_space = 'LOCAL'

            bpy.ops.object.mode_set(mode='EDIT')
            #ボーンLayer
            self.QUtil.setLayerFromIndex(self.EditBone[ReNewBoneName],DefomerBoneLayer,Add=AddBoneLayer)
            #ボーングループ
            self.QUtil.setBoneGroups(BoneName = ReNewBoneName ,GroupName = oGroupName)


            self.EditBone[ReNewBoneName].bbone_x = BBsize
            self.EditBone[ReNewBoneName].bbone_z = BBsize

        #スクリプト実行前のモードに戻す
        bpy.ops.object.mode_set(mode=SaveMode)
        #生成したボーンの選択
        self.QUtil.NewBonesSelector(SaveMode,newBoneList)
        return newBoneList

    def newBone_FromSelect2Bone(self,newBoneName = "default", oMode = "Simple",
                                oSympleParent = False,
                                CustomShapeSize =0.2,
                                BBsize = 0.2,
                                HeadBoneMake = True,
                                OffsetBoneMake = True,
                                oFit = "HtoH",
                                DefomerBoneLayer = 31,
                                SystemBoneLayer = 3,
                                AddBoneLayer = True,
                                addLength = 0,
                                oGroupName = None,
                                ):
        """ ２選択間にボーンを生成 """
        A,B = self.QUtil.SelectBoneTwo()
        SaveMode = self.QUtil.ChangeEditMode()
        #Poseからのボーン取得では rollが取得できないのでEditBoneに設定し直す
        Bone1st = self.EditBone[A]
        Bone2nd = self.EditBone[B]
        BBone = A
        CBone = B

        directionVector1st = Bone1st.matrix @ Vector((0, 1, 0))
        tailPos1st = directionVector1st.lerp(Bone1st.head, -10000)
        directionVector2nd = Bone2nd.matrix @ Vector((0, 1, 0))
        tailPos2nd = directionVector2nd.lerp(Bone2nd.head, -10000)

        if oMode == "Simple":
            oName = "P_"
        elif oMode == "Stretch":
            oName = "Msl_"
            oCNS = "STRETCH_TO"
            oCNSGet = "Stretch To"

        elif oMode == "Track":
            oName = "Tra_"
            oCNS = "TRACK_TO"
            oCNSGet = "Track To"

        elif oMode == "IK":
            oName = "IK_"
            oCNS = "IK"

        #defaultだと、選択１つ目のボーンの名前を利用する。
        if newBoneName == "default":
            newBoneName = oName + Bone1st.name
        newBone = self.armature.edit_bones.new(newBoneName)
        newBone.head = Bone1st.head
        newBone.tail = Bone1st.tail
        newBone.roll = Bone1st.roll
        if oSympleParent == True:
            newBone.parent = Bone1st
        ABone = newBone.name
        #選択中のボーンのHeadとTailにフィットさせる
        self.QUtil.FitBones(BBone,CBone, C=ABone , FitMethod =oFit, oAline = False )

        #生成したボーンの場所からoffsetボーンと先端ボーンの位置を出力する
        #先端ボーン生成ONヘッドかテイルか選択
        if HeadBoneMake == True:
            if newBoneName == "default":
                newBoneName = oName + Bone2nd.name
            newHeadBone = self.armature.edit_bones.new("H_" + newBoneName)
            BBone = newHeadBone.name
            if oFit == "HtoH" or oFit == "TtoH"or oFit == "Fit1stBone"or oFit == "Fit2ndBone":
                newHeadBone.head = Bone2nd.head
            elif oFit == "HtoT" or oFit =="TtoT":
                newHeadBone.head = Bone2nd.tail
            newHeadBone.tail = tailPos2nd
            newHeadBone.roll = Bone2nd.roll
            newHeadBone.length = Bone2nd.length/3+ addLength
            newHeadBone.parent = self.EditBone[B]
            newHeadBone.use_deform = False
        #offsetボーン生成ON
        if OffsetBoneMake == True:
            if newBoneName == "default":
                newBoneName = oName + Bone1st.name
            newOffsetBone = self.armature.edit_bones.new("T_" + newBoneName)
            CBone = newOffsetBone.name
            if oFit == "HtoH" or oFit == "HtoT":
                newOffsetBone.head = Bone1st.head
            elif oFit == "TtoT" or oFit =="TtoH":
                newOffsetBone.head = Bone1st.tail
            newOffsetBone.tail = tailPos1st
            newOffsetBone.roll = Bone1st.roll
            newOffsetBone.length = Bone1st.length/3+ addLength
            newOffsetBone.parent = self.EditBone[A]
            newOffsetBone.use_deform = False
            self.EditBone[ABone].parent = newOffsetBone


        bpy.ops.object.mode_set(mode='POSE')
        #ビューポートディスプレイアイコンは支点と終点のオフセットボーンに付与。
        #A = newBone B = head C = Offset
        icon = cvELD_RIG_Icon()
        icon.LoadShape("cs_SiCube")
        if HeadBoneMake == True:
            self.poseBoneName[BBone].use_custom_shape_bone_size = False
            self.poseBoneName[BBone].custom_shape = bpy.data.objects["cs_SiCube"]
            self.poseBoneName[BBone].custom_shape_scale = CustomShapeSize

        if OffsetBoneMake== True:
            self.poseBoneName[CBone].use_custom_shape_bone_size = False
            self.poseBoneName[CBone].custom_shape = bpy.data.objects["cs_SiCube"]
            self.poseBoneName[CBone].custom_shape_scale = CustomShapeSize





        if oMode == "Stretch" or oMode == "Track":
            """ ストレッチまたはトラックコンストレインを付与 """
            #ポーズモードで骨に動きがあるばあい、コンストレイン.rest_lengthの都合が変わるのに注意
            if self.poseBonesName[ABone].constraints.get(oCNSGet) == None:
                MODE_CNS = self.poseBonesName[ABone].constraints.new(oCNS)
                MODE_CNS.target = self.armatureObj
            else:
                MODE_CNS = self.poseBonesName[ABone].constraints.get(oCNSGet)
            #支点ONの場合、そっちのヘッドに適応
            if HeadBoneMake == True:
                MODE_CNS.subtarget =  self.poseBoneName[BBone].name
            else:
                MODE_CNS.subtarget =  self.poseBoneName[B].name
                if oFit == "HtoT" or oFit == "TtoT":
                    MODE_CNS.head_tail = 1


            #Strachのみ
            if oMode == "Stretch":
                MODE_CNS.keep_axis = 'SWING_Y'
                MODE_CNS.rest_length
            #Trackのみ
            if oMode == "Track":
                MODE_CNS.track_axis = 'TRACK_Y'
                MODE_CNS.up_axis = 'UP_Z'
                MODE_CNS.use_target_z = True

        #ボーンレイヤー

        self.QUtil.setLayerFromIndex(self.Bones[ABone],DefomerBoneLayer,Add=AddBoneLayer)
        self.QUtil.setLayerFromIndex(self.Bones[BBone],SystemBoneLayer,Add=AddBoneLayer)
        self.QUtil.setLayerFromIndex(self.Bones[CBone],SystemBoneLayer,Add=AddBoneLayer)

        #ボーングループ
        self.QUtil.setBoneGroups(BoneName = ABone ,GroupName = oGroupName)
        self.QUtil.setBoneGroups(BoneName = BBone ,GroupName = "offset")
        self.QUtil.setBoneGroups(BoneName = CBone ,GroupName = "offset")

        #新規ボーンの位置合わせ

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.armature.select_all(action='DESELECT')
        self.EditBone[ABone].bbone_x = BBsize
        self.EditBone[ABone].bbone_z = BBsize
        self.EditBone[ABone].select = True
        self.EditBone[ABone].select_head = True
        self.EditBone[ABone].select_tail = True

        bpy.ops.object.mode_set(mode=SaveMode)
        #ボーンが生成されない場合は選択ボーンで出力


        return ABone,BBone,CBone

    def newBone_ChangeJoint(self,newBoneName = "Bone.000",
                            BBsize = 0.2,
                            AddBoneLayer = True,
                            DefomerBoneLayer = 31,
                            oSeg = 6,
                            oHead_Tail = 0.15,
                            oGroupName = None,
                            ):
        """ 膝や肘用の３関節ボーン生成。２本のボーンを選択で実行 """
        newBoneList = []
        A,B = self.QUtil.SelectBoneTwo()
        SaveMode = self.QUtil.ChangeEditMode()
        #Poseからのボーン取得では rollが取得できないのでEditBoneに設定し直す
        Bone1st = self.EditBone[A]
        Bone2nd = self.EditBone[B]

        oLinA = np.linspace(Bone1st.head,Bone1st.tail,oSeg +1)
        oLinB = np.linspace(Bone2nd.head,Bone2nd.tail,oSeg +1)
        revers_oLin = list(reversed(oLinB))

        #選択ボーンの変形はOFF
        Bone1st.use_deform = False
        Bone2nd.use_deform = False

        #ボーンを２つ選択 1st と2ndで定義
        #NewJointA = 1stのHeadとtailのLengthを0.8倍を初期値に、プロパティで任意に変更
        NewJointA = self.armature.edit_bones.new(newBoneName)
        NewJointAName = NewJointA.name
        NewJointA.head = Bone1st.head
        NewJointA.tail = oLinA[oSeg-1]
        NewJointA.roll = Bone1st.roll
        #NewJointA.length = Bone1st.length *oLength
        #NewJointB = 1stの設定と同じ。ただしheadの位置が全長１とすると0.2から開始してtailが１とする。'segment'参照
        NewJointB = self.armature.edit_bones.new(newBoneName)
        NewJointBName = NewJointB.name
        NewJointB.head = revers_oLin[oSeg-1]
        NewJointB.tail = Bone2nd.tail
        NewJointB.roll = Bone2nd.roll
        #NewJointB.length = Bone2nd.length *oLength
        NewJointC = self.armature.edit_bones.new(newBoneName)
        NewJointCName = NewJointC.name
        NewJointC.head = NewJointA.tail
        NewJointC.tail = NewJointB.head
        NewJointC.roll = NewJointA.roll
        #NewJointC = NewJointAのtailからNewJointBのHeadで新規ボーン生成。
        #ペアレント順は A→C→Bとなる。 Cは膝関節部分。
        print(NewJointAName,NewJointBName,NewJointCName)
        self.EditBone[NewJointAName].parent = Bone1st
        self.EditBone[NewJointCName].parent = self.EditBone[NewJointAName]
        self.EditBone[NewJointBName].parent = self.EditBone[NewJointCName]
        #コンストレイン適応。
        bpy.ops.object.mode_set(mode='POSE')

        if self.poseBonesName[NewJointBName].constraints.get("Track To") == None:
            TRACK_TO_cns = self.poseBonesName[NewJointBName].constraints.new("TRACK_TO")
        else:
            TRACK_TO_cns = self.poseBonesName[NewJointBName].constraints.get("Track To")
        TRACK_TO_cns.target = self.armatureObj
        TRACK_TO_cns.subtarget = Bone2nd.name
        TRACK_TO_cns.track_axis = 'TRACK_Y'
        TRACK_TO_cns.up_axis = 'UP_Z'
        TRACK_TO_cns.use_target_z = True
        TRACK_TO_cns.head_tail = 1

        if self.poseBonesName[NewJointCName].constraints.get("Track To") == None:
            TRACK_TO_cns = self.poseBonesName[NewJointCName].constraints.new("TRACK_TO")
        else:
            TRACK_TO_cns = self.poseBonesName[NewJointCName].constraints.get("Track To")
        TRACK_TO_cns.target = self.armatureObj
        TRACK_TO_cns.subtarget = Bone2nd.name
        TRACK_TO_cns.track_axis = 'TRACK_Y'
        TRACK_TO_cns.up_axis = 'UP_Z'
        TRACK_TO_cns.use_target_z = True
        TRACK_TO_cns.head_tail = oHead_Tail


        #ボーンレイヤー
        self.QUtil.setLayerFromIndex(self.Bones[NewJointAName],DefomerBoneLayer,Add=AddBoneLayer)
        self.QUtil.setLayerFromIndex(self.Bones[NewJointBName],DefomerBoneLayer,Add=AddBoneLayer)
        self.QUtil.setLayerFromIndex(self.Bones[NewJointCName],DefomerBoneLayer,Add=AddBoneLayer)
        self.QUtil.setBoneGroups(BoneName = NewJointAName ,GroupName = oGroupName)
        self.QUtil.setBoneGroups(BoneName = NewJointBName ,GroupName = oGroupName)
        self.QUtil.setBoneGroups(BoneName = NewJointCName ,GroupName = oGroupName)
        bpy.ops.object.mode_set(mode=SaveMode)
        self.QUtil.NewBonesSelector(SaveMode,newBoneList)

        return newBoneList

    def IK_FromSelect2Bone(self,
                    CustomShapeSize =0.2,
                    BBsize = 0.2,
                    SystemBoneLayer = 3,
                    AddBoneLayer = True,
                    oGroupName = None,
                    UPVpos = 1,
                    ):
        """ ２つの選択ボーンからIKを生成する　アップベクトル用とIKコントローラー生成 """
        SaveMode = self.QUtil.ChangeEditMode()
        #Poseからのボーン取得では rollが取得できないのでEditBoneに設定し直す
        bpy.ops.object.mode_set(mode='EDIT')
        #生成したボーンのリスト（複数対応のため
        newBoneList = []
        A,B = self.QUtil.SelectBoneTwo()
        #Poseからのボーン取得では rollが取得できないのでEditBoneに設定し直す
        Bone1st = self.EditBone[A]
        Bone2nd = self.EditBone[B]
        directionVector = Bone2nd.matrix @ Vector((0, 1, 0))
        tailPosB = directionVector.lerp(Bone2nd.head, -10000)
        #IK設定時にチェーンの長さに利用する
        oChildren_recursive = len(Bone1st.children_recursive)+1


        #IK
        newIKBone = self.armature.edit_bones.new("IK" + Bone2nd.name)
        ReNewIKBoneName = newIKBone.name
        newIKBone.use_deform = False
        newIKBone.head = Bone2nd.tail
        newIKBone.tail = tailPosB
        newIKBone.length = Bone2nd.length*0.4
        newIKBone.bbone_x = BBsize
        newIKBone.bbone_z = BBsize
        newIKBone.roll = Bone2nd.roll
        newBoneList.append(ReNewIKBoneName)

        #UPVボーン生成
        newUPVBone = self.armature.edit_bones.new("UPV" + Bone2nd.name)
        ReNewUPVBoneName = newUPVBone.name
        newUPVBone.use_deform = False
        newUPVBone.head = newIKBone.matrix @ Vector((0, 0, UPVpos))
        newUPVBone.tail = newIKBone.matrix @ Vector((0, 1, UPVpos))
        newUPVBone.length = Bone2nd.length*0.4
        newUPVBone.bbone_x = BBsize
        newUPVBone.bbone_z = BBsize
        newUPVBone.roll = Bone2nd.roll
        newUPVBone.parent = newIKBone
        newBoneList.append(ReNewUPVBoneName)


        bpy.ops.object.mode_set(mode='POSE')
        #IKコンストレイン

        if self.poseBonesName[Bone2nd.name].constraints.get("IK") == None:
            IK_cns = self.poseBonesName[Bone2nd.name].constraints.new("IK")
        else:
            IK_cns = self.poseBonesName[Bone2nd.name].constraints.get("IK")
        IK_cns.target = self.armatureObj
        IK_cns.subtarget = ReNewIKBoneName
        IK_cns.pole_target = self.armatureObj
        IK_cns.pole_subtarget = ReNewUPVBoneName
        IK_cns.chain_count = oChildren_recursive
        IK_cns.pole_angle = 1.5708

        #icon
        self.icon.LoadShape("cs_SiIK")
        self.poseBoneName[ReNewIKBoneName].custom_shape = bpy.data.objects["cs_SiIK"]
        self.poseBoneName[ReNewIKBoneName].custom_shape_scale = CustomShapeSize

        self.icon.LoadShape("cs_SiPyramid")
        self.poseBoneName[ReNewUPVBoneName].custom_shape = bpy.data.objects["cs_SiPyramid"]
        self.poseBoneName[ReNewUPVBoneName].custom_shape_scale = CustomShapeSize

        #ボーンレイヤー
        self.QUtil.setLayerFromIndex(self.Bones[ReNewIKBoneName],SystemBoneLayer,Add=AddBoneLayer)
        self.QUtil.setLayerFromIndex(self.Bones[ReNewUPVBoneName],SystemBoneLayer,Add=AddBoneLayer)
        self.QUtil.setBoneGroups(BoneName = ReNewIKBoneName ,GroupName = oGroupName)
        self.QUtil.setBoneGroups(BoneName = ReNewUPVBoneName ,GroupName = "UPV")

        bpy.ops.object.mode_set(mode=SaveMode)
        self.QUtil.NewBonesSelector(SaveMode,newBoneList)
        return newBoneList

    def MakeSlider(self,
                    newBoneName = "Slider",
                    CustomShapeSize =0.2,
                    BBsize = 0.2,
                    SystemBoneLayer = 3,
                    AddBoneLayer = True,
                    oMode = "SlideY",
                    oSliderType = "cs_FKIK",
                    oPosition = 1,
                    oCustomPropName = "Switch",
                    oGroupName = "None",
                    AttachIKconstrain_Slider = True,
                    ):
        """ 選択ボーンから、スライダー用のボーン生成。IK-FK切り替え用途やシェイプ用途 """
        SaveMode = self.QUtil.ChangeEditMode()
        bpy.ops.object.mode_set(mode='EDIT')
        newBoneList = []
        SelBoneNamesList = []
        for i in bpy.context.selected_bones:
            SelBoneNamesList.append(i.name)
        for v in SelBoneNamesList:
            bpy.ops.object.mode_set(mode='EDIT')
            A = self.EditBoneDataName[v]
            #プロパティで切り替え中にスコープがずれるから名前保持
            Aname = A.name

            directionVector = A.matrix @ Vector((0, 1, 0))
            tailPos = directionVector.lerp(A.head, -10000)

            if oMode == "SlideY":
                newBoneTXT = self.armature.edit_bones.new(newBoneName+"Base.000")
                newBoneTXT.head = A.head
                newBoneTXT.tail = tailPos
                newBoneTXT.head[2] = newBoneTXT.head[2]+A.length*oPosition
                newBoneTXT.tail[2] = newBoneTXT.tail[2]+A.length*oPosition
                newBoneTXT.length = A.length
                newBoneTXT.roll = A.roll
                newBoneTXT.parent = A
                newBoneTXT.bbone_x = BBsize
                newBoneTXT.bbone_z = BBsize
                newBoneTXT.use_deform = False
                newBoneTXT.hide_select = True
                #カスタムプロパティ生成
                BaseName = newBoneTXT.name
                newBoneList.append(BaseName)

                newBoneSlider = self.armature.edit_bones.new(newBoneName+".000")
                newBoneSlider.head = A.head
                newBoneSlider.tail = tailPos
                newBoneSlider.head[2] = newBoneSlider.head[2]+A.length*oPosition
                newBoneSlider.tail[2] = newBoneSlider.tail[2]+A.length*oPosition
                newBoneSlider.length = A.length*0.5
                newBoneSlider.roll = A.roll
                newBoneSlider.parent = A
                newBoneSlider.bbone_x = BBsize
                newBoneSlider.bbone_z = BBsize
                newBoneSlider.use_deform = False
                SliderName = newBoneSlider.name
                newBoneList.append(SliderName)


                bpy.ops.object.mode_set(mode='POSE')
                self.poseBoneName[BaseName].lock_location[0] = True
                self.poseBoneName[BaseName].lock_location[2] = True
                self.poseBoneName[BaseName].lock_rotation_w = True
                self.poseBoneName[BaseName].lock_rotation[0] = True
                self.poseBoneName[BaseName].lock_rotation[1] = True
                self.poseBoneName[BaseName].lock_rotation[2] = True
                self.poseBoneName[BaseName].lock_scale[0] = True
                self.poseBoneName[BaseName].lock_scale[1] = True
                self.poseBoneName[BaseName].lock_scale[2] = True
                self.poseBoneName[BaseName].custom_shape_scale = CustomShapeSize

                self.icon.LoadShape(oSliderType)
                self.poseBoneName[BaseName].custom_shape = bpy.data.objects[oSliderType]
                self.poseBoneName[BaseName].use_custom_shape_bone_size = False


                self.poseBoneName[SliderName].lock_location[0] = True
                self.poseBoneName[SliderName].lock_location[2] = True
                self.poseBoneName[SliderName].lock_rotation_w = True
                self.poseBoneName[SliderName].lock_rotation[0] = True
                self.poseBoneName[SliderName].lock_rotation[1] = True
                self.poseBoneName[SliderName].lock_rotation[2] = True
                self.poseBoneName[SliderName].lock_scale[0] = True
                self.poseBoneName[SliderName].lock_scale[1] = True
                self.poseBoneName[SliderName].lock_scale[2] = True
                bpy.ops.object.mode_set(mode='POSE')
                self.icon.LoadShape("cs_2Dcapsule")
                self.poseBoneName[SliderName].custom_shape = bpy.data.objects["cs_2Dcapsule"]
                self.poseBoneName[SliderName].use_custom_shape_bone_size = False
                self.poseBoneName[SliderName].custom_shape_scale = CustomShapeSize


                #CNS
                COPY_LimitLoc_cns = self.poseBonesName[SliderName].constraints.new("LIMIT_LOCATION")
                COPY_LimitLoc_cns.owner_space = 'LOCAL'
                COPY_LimitLoc_cns.use_transform_limit = True
                COPY_LimitLoc_cns.use_max_z = True
                COPY_LimitLoc_cns.use_max_y = True
                COPY_LimitLoc_cns.use_max_x = True
                COPY_LimitLoc_cns.use_min_z = True
                COPY_LimitLoc_cns.use_min_y = True
                COPY_LimitLoc_cns.use_min_x = True
                COPY_LimitLoc_cns.max_y = CustomShapeSize*5



                #ドライバ抹殺
                self.QUtil.clearDriver(BoneName = SliderName,
                             CustomParaName =oCustomPropName )

                #SetDriver
                #すでにドライバーがゴミとしてある場合はクリアー
                #カスタムプロパティ生成してドライバ入れる
                self.poseBoneName[SliderName][oCustomPropName] = 0.0
                #ポーズボーンに付与したカスタムプロパティへのアクセスは記述が変なので忘れないように
                Fcurve = self.poseBoneName[SliderName].driver_add('["'+oCustomPropName+'"]')
                Fcurve.driver.type = 'SCRIPTED'

                if oSliderType == "cs_FKIK":
                    Fcurve.driver.expression = "round(lerp(Limit,location_Y,1) / Limit ,3)"
                else:
                    Fcurve.driver.expression = "1 - round(lerp(Limit,location_Y,1) / Limit ,3)"

                var = Fcurve.driver.variables.new()
                var.type = 'TRANSFORMS'
                var.name = "location_Y"


                var.targets[0].id = self.armatureObj
                var.targets[0].bone_target = SliderName
                var.targets[0].transform_type = 'LOC_Y'
                var.targets[0].transform_space = 'LOCAL_SPACE'

                var = Fcurve.driver.variables.new()

                var.type = 'SINGLE_PROP'
                var.name = "Limit"
                var.targets[0].id = self.armatureObj
                var.targets[0].data_path = 'pose.bones["'+ SliderName +'"].constraints[\"Limit Location\"].max_y'

                #もし選択ボーンにIKがあれば影響度と接続する。
                if AttachIKconstrain_Slider == True:
                    if self.poseBonesName[Aname].constraints.get("IK") != None:
                        IK_cns = self.poseBonesName[Aname].constraints.get("IK")
                        Fcurve = IK_cns.driver_add("influence")
                        Fcurve.driver.type = 'SCRIPTED'
                        Fcurve.driver.expression = "slider"
                        var = Fcurve.driver.variables.new()
                        var.type = 'SINGLE_PROP'
                        var.name = "slider"
                        var.targets[0].id = self.armatureObj
                        var.targets[0].bone_target = SliderName
                        var.targets[0].data_path = 'pose.bones["'+ SliderName +'"]["'+oCustomPropName+'"]'

            self.QUtil.setLayerFromIndex(self.Bones[BaseName],SystemBoneLayer,Add=AddBoneLayer)
            self.QUtil.setLayerFromIndex(self.Bones[SliderName],SystemBoneLayer,Add=AddBoneLayer)
            self.QUtil.setBoneGroups(BoneName = BaseName ,GroupName = "unsel")
            self.QUtil.setBoneGroups(BoneName = SliderName ,GroupName = oGroupName)



        bpy.ops.object.mode_set(mode=SaveMode)
        self.QUtil.NewBonesSelector(SaveMode,newBoneList)
        return newBoneList


# class QuickBone_Rigs(object):
#     pass
    #ワンポチで自動でRIGが組み上がる




###########################
###########################

""" 以下はBlenderに登録するための bl_idname クラス """

###########################
###########################

class MakeBoneOne_OT_object(bpy.types.Operator):
    """ １選択ボーンから新規ボーン生成 """
    bl_idname = "armature.newbone_fromselect1bone"
    bl_label = "MakeBone"
    bl_description = "1SelectBone MakeBone"
    bl_options = {'REGISTER', 'UNDO'}

    #グループ分け
    """ 重複 ボーングループ """
    BoneGroupEnum : EnumProperty(
        name="Bone Group",
        description="Bone Group",
        default= "primary",
        items=[
            ( "None",       "None",      "Default"              ),
            ( "primary",    "primary",   "Primary Controls"     ),
            ( "secondry",   "secondry",  "Secondry Controls"    ),
            ( "offset",     "offset",    "systemBone"           ),
            ( "unsel",      "unsel",     "systemBone"           ),
            ( "hide",       "hide",      "systemBone"           ),
        ]
    )

    """ 重複 ディスプレイボーン """
    #ボーンディスプレイタイプ。六角形やら線形やらBBone等
    BoneDisplayType : EnumProperty(
            name="Bone Display Type",
            description="Bone Display Type",
            default= None,
            items=[
                ("OCTAHEDRAL","OCTAHEDRAL","BoneType"),
                ("STICK","STICK","BoneType"),
                ("BBONE","BBONE","BoneType"),
                ("ENVELOPE","ENVELOPE","BoneType"),
                ("WIRE","WIRE","BoneType"),
            ]
        )

    """ コンストレインタイプの変更 """
    MakeBoneMode : EnumProperty(
        name="Make Bone Method",
        description="SimpleBone or OffsetBone",
        default= "Simple",
        items=[
            ("Simple", "Simple","Simple"),
            ("Offset", "Offset","Offset"),
            ("Muscle_StretchTo", "MUSCLE Stretch","MUSCLE Stretch"),
            ("Muscle_TrackTo", "MUSCLE Track","MUSCLE Track"),
            ("HalfRot","Half Rotation","HalfRot"),
            ("ChildCns","Child Constrain","ChildCns"),
            ("Segment","Segment(SplitBone)","Segment"),
            ("IK","IK Constrain","IKcns"),
        ]
    )

    """ 実行後、右下に現れるプロパティたちだが、コンストレインを変更しても暗転する方法が無いため
    ごちゃごちゃに入れてある。 """
    BoneNameProp         : StringProperty(name = "Bone Name", default = "Bone.000")
    HeadorTailBool       : BoolProperty(name = "Simple Bone Head or Tail", default = True)
    ParentON             : BoolProperty(name = "Simple Bone Set Parent", default = True)
    RotON                : BoolProperty(name = "Rotation Constraint", default = True)
    TraON                : BoolProperty(name = "Transform Constraint", default = True)
    SclON                : BoolProperty(name = "Scale Constraint", default = True)
    LimitRoc             : BoolProperty(name = "Limit Rotation", default = False)
    LimitLoc             : BoolProperty(name = "Limit Location", default = False)
    BoneBBsizeProp       : FloatProperty(name = "BendyBone size", default = 0.2)
    AddLengthProp        : FloatProperty(name = "add Length", default = 0)
    ChainCountInt        : IntProperty(name = "IK Chain count", default = 2 ,min = 1)
    SegmentBool          : IntProperty(name = "Segment num", default = 2,min = 2)
    SegmentReversBool    : BoolProperty(name = "Segment Revers", default = True)
    DeformerBoneLayerInt : IntProperty (name ="Deform Layer", default =0 , min=0,max=31)
    AddBoneLayerBool     : BoolProperty (name ="Add Active Layer", default =True)
    CustomShapeSizeProp  : FloatProperty(name = "OffsetBone size", default=0.2,description="OffsetBone size")
    UPVposProp           : FloatProperty(name = "UPV Position", default = 1)


    def execute(self, context):
        """ 実行処理 プロパティを読み込み """
        Bone = QuickBone_Tools(bpy.context.active_bone)
        Bone.newBone_FromSelect1Bone(newBoneName = self.BoneNameProp,
                                    CustomShapeSize = self.CustomShapeSizeProp,
                                    oMode = self.MakeBoneMode,
                                    oHeadorTailBool = self.HeadorTailBool,
                                    oSympleParent = self.ParentON,
                                    oRot = self.RotON,
                                    oTra = self.TraON,
                                    oScl = self.SclON,
                                    BBsize = self.BoneBBsizeProp,
                                    addLength = self.AddLengthProp,
                                    oLimitRot = self.LimitRoc,
                                    oLimitLoc = self.LimitLoc,
                                    oChainCount =self.ChainCountInt,
                                    oSeg =self.SegmentBool,#セグメント用途
                                    SegmentRevers =self.SegmentReversBool,#リニアスペースを逆から読ませる
                                    DefomerBoneLayer = self.DeformerBoneLayerInt,
                                    AddBoneLayer = self.AddBoneLayerBool,
                                    oGroupName = self.BoneGroupEnum,
                                    UPVpos = self.UPVposProp
                                    )
        bpy.context.object.data.display_type = self.BoneDisplayType
        return {'FINISHED'}

class MakeBoneTwo_OT_object(bpy.types.Operator):
    """ 2選択ボーンから新規ボーン生成。
    １選択からの処理と重複する箇所が多いため、統合したい """

    bl_idname = "armature.newbone_fromselect2bone"
    bl_label = "Between MakeBone"
    bl_description = "2SelectBone Between MakeBone"
    bl_options = {'REGISTER', 'UNDO'}

    """ 重複 ボーングループ """
    BoneGroupEnum : EnumProperty(
        name="Bone Group",
        description="Bone Group",
        default= "primary",
        items=[
            ( "None",       "None",      "Default"              ),
            ( "primary",    "primary",   "Primary Controls"     ),
            ( "secondry",   "secondry",  "Secondry Controls"    ),
            ( "offset",     "offset",    "systemBone"           ),
            ( "unsel",      "unsel",     "systemBone"           ),
            ( "hide",       "hide",      "systemBone"           ),
        ]
    )
    """ 重複 ボーンディスプレイタイプ """
    BoneDisplayType : EnumProperty(
            name="Bone Display Type",
            description="Bone Display Type",
            default= None,
            items=[
                ("OCTAHEDRAL","OCTAHEDRAL","BoneType"),
                ("STICK","STICK","BoneType"),
                ("BBONE","BBONE","BoneType"),
                ("ENVELOPE","ENVELOPE","BoneType"),
                ("WIRE","WIRE","BoneType"),
            ]
        )

    """ ２選択ボーン用の選択できるコンストレイン """
    MakeBoneMode : EnumProperty(
            name="Make Bone Method",
            description="SimpleBone or OffsetBone",
            default= "Simple",
            items=[
                ("Simple", "Simple","Simple"),
                ("Stretch", "Stretch","Stretch"),
                ("Track", "Track","Track"),
            ]
        )

    """ 新規生成したボーンが、２選択ボーンの何処から何処にフィットするか？ """
    FitMode : EnumProperty(
            name="Fit Method",
            description="Bone tail,head Fit Method",
            default='TtoH',
            items=[
            ('TtoH', "tail to head", "Connect two selected bones"),
            ('TtoT', "tail to tail", "Connect two selected bones"),
            ('HtoH', "head to head", "Connect two selected bones"),
            ('HtoT', "head to tail", "Connect two selected bones"),
            ('Fit1stBone', "Fit 1st Bone", "FitAll"),
            ('Fit2ndBone', "Fit 2nd Bone", "FitAll"),
        ]
    )

    #ボーン名をプレファレンスで決めれる
    BoneNameProp             : StringProperty(name = "Bone Name", default = "default")
    BoneBBsizeProp           : FloatProperty(name = "BendyBone size", default = 0.2)
    AddLengthProp            : FloatProperty(name = "add Length", default = 0)
    ParentON                 : BoolProperty(name = "Simple Bone Set Parent", default = True)
    DeformerBoneLayerInt     : IntProperty (name ="Deform Layer", default =31 , min=0,max=31)
    SystemBoneLayerInt       : IntProperty (name ="System Layer", default =3 , min=0,max=31)
    AddBoneLayerBool         : BoolProperty (name ="Add Active Layer", default =True)
    HeadBoneBool             : BoolProperty(name = "Make HeadBone", default = True) #Boolで先端ボーンとoffset装備するか決める
    OffsetBoneBool           : BoolProperty(name = "Make OffsetBone", default = True)
    CustomShapeSizeProp      : FloatProperty(name = "OffsetBone size" ,default=0.2,description="OffsetBone size")

    def execute(self, context):
        """ ２選択ボーンから新規ボーンの実行処理とプロパティ読み込み """
        Bone = QuickBone_Tools(bpy.context.active_bone)
        Bone.newBone_FromSelect2Bone(newBoneName = self.BoneNameProp,
                                    BBsize=self.BoneBBsizeProp ,
                                    oSympleParent=self.ParentON,
                                    oMode = self.MakeBoneMode,
                                    HeadBoneMake = self.HeadBoneBool,
                                    OffsetBoneMake = self.OffsetBoneBool,
                                    oFit = self.FitMode,
                                    DefomerBoneLayer = self.DeformerBoneLayerInt,
                                    SystemBoneLayer = self.SystemBoneLayerInt,
                                    AddBoneLayer = self.AddBoneLayerBool,
                                    CustomShapeSize = self.CustomShapeSizeProp,
                                    addLength = self.AddLengthProp,
                                    oGroupName = self.BoneGroupEnum,
                                    )

        bpy.context.object.data.display_type = self.BoneDisplayType
        return {'FINISHED'}

class MakeBone_AddJoint_OT_object(bpy.types.Operator):
    """ 膝や肘に使える３関節ボーン生成クラス """
    bl_idname = "armature.addjoint"
    bl_label = "Add Joint"
    bl_description = "2SelectBone add JointBone"
    bl_options = {'REGISTER', 'UNDO'}

    """ 重複 ボーングループ """
    BoneGroupEnum : EnumProperty(
        name="Bone Group",
        description="Bone Group",
        default= "primary",
        items=[
            ( "None",       "None",      "Default"              ),
            ( "primary",    "primary",   "Primary Controls"     ),
            ( "secondry",   "secondry",  "Secondry Controls"    ),
            ( "offset",     "offset",    "systemBone"           ),
            ( "unsel",      "unsel",     "systemBone"           ),
            ( "hide",       "hide",      "systemBone"           ),
        ]
    )

    """ 重複 ディスプレイボーンタイプ """
    BoneDisplayType : EnumProperty(
            name="Bone Display Type",
            description="Bone Display Type",
            default= None,
            items=[
                ("OCTAHEDRAL","OCTAHEDRAL","BoneType"),
                ("STICK","STICK","BoneType"),
                ("BBONE","BBONE","BoneType"),
                ("ENVELOPE","ENVELOPE","BoneType"),
                ("WIRE","WIRE","BoneType"),
            ]
        )
    BoneNameProp             : StringProperty(name = "Bone Name", default = "Bone.000")
    BoneBBsizeProp           : FloatProperty(name = "BendyBone size", default = 0.2)
    AddBoneLayerBool         : BoolProperty (name ="Add Active Layer", default =True)
    DeformerBoneLayerInt     : IntProperty (name ="Deform Layer", default =31 , min=0,max=31)
    SegmentBool              : IntProperty(name = "Segment", default = 6,min = 2 ,max=100)
    HeadTailBool             : FloatProperty(name = "Joint Dir HeadTail%", default = 0.15,min=0,max=1)

    def execute(self, context):
        """ ３関節ボーン実行 """
        Bone = QuickBone_Tools(bpy.context.active_bone)
        #プロパティが異なるだけで１選択から実行の処理に組み込んだ
        Bone.newBone_ChangeJoint(newBoneName = self.BoneNameProp,
                                BBsize=self.BoneBBsizeProp,
                                AddBoneLayer = self.AddBoneLayerBool,
                                DefomerBoneLayer = self.DeformerBoneLayerInt,
                                oSeg = self.SegmentBool,
                                oHead_Tail = self.HeadTailBool,
                                oGroupName = self.BoneGroupEnum,
                                )

        bpy.context.object.data.display_type = self.BoneDisplayType
        return {'FINISHED'}

class MakeBone_IKfromSelect2Bone_OT_object(bpy.types.Operator):
    """ ２選択ボーンからIKの生成クラス """
    bl_idname = "armature.ikfromselect2bone"
    bl_label = "IK from 2SelectBones"
    bl_description = "IK from 2SelectBones"
    bl_options = {'REGISTER', 'UNDO'}

    """ 重複 ボーングループ """
    BoneGroupEnum : EnumProperty(
        name="Bone Group",
        description="Bone Group",
        default= "primary",
        items=[
            ( "None",       "None",      "Default"              ),
            ( "primary",    "primary",   "Primary Controls"     ),
            ( "secondry",   "secondry",  "Secondry Controls"    ),
            ( "offset",     "offset",    "systemBone"           ),
            ( "unsel",      "unsel",     "systemBone"           ),
            ( "hide",       "hide",      "systemBone"           ),
        ]
    )
    """ 重複 ディスプレイボーン """
    BoneDisplayType : EnumProperty(
            name="Bone Display Type",
            description="Bone Display Type",
            default= None,
            items=[
                ("OCTAHEDRAL","OCTAHEDRAL","BoneType"),
                ("STICK","STICK","BoneType"),
                ("BBONE","BBONE","BoneType"),
                ("ENVELOPE","ENVELOPE","BoneType"),
                ("WIRE","WIRE","BoneType"),
            ]
        )
    BoneBBsizeProp           : FloatProperty(name = "BendyBone size", default = 0.2)
    UPVposProp              : FloatProperty(name = "UPV Position", default = 1)
    AddBoneLayerBool         : BoolProperty (name ="Add Active Layer", default =True)
    CustomShapeSizeProp      : FloatProperty(name = "Shape size", default=0.2,description="Shape size")
    SystemBoneLayerInt       : IntProperty (name ="System Layer", default =3 , min=0,max=31)

    def execute(self, context):
        """ ２選択からIKボーンの実行 """
        Bone = QuickBone_Tools(bpy.context.active_bone)
        #プロパティが異なるだけで１選択から実行の処理に組み込んだ
        Bone.IK_FromSelect2Bone(
                                CustomShapeSize = self.CustomShapeSizeProp,
                                BBsize = self.BoneBBsizeProp,
                                SystemBoneLayer = self.SystemBoneLayerInt,
                                AddBoneLayer = self.AddBoneLayerBool,
                                oGroupName = self.BoneGroupEnum,
                                UPVpos = self.UPVposProp
                                )
        bpy.context.object.data.display_type = self.BoneDisplayType
        return {'FINISHED'}

class MakeBone_MakeSlider_OT_object(bpy.types.Operator):
    """ １選択からスライダー生成クラス """

    bl_idname = "armature.makeslider"
    bl_label = "MakeSlider"
    bl_description = "MakeSlider"
    bl_options = {'REGISTER', 'UNDO'}

    """ 重複 ボーングループ """
    BoneGroupEnum : EnumProperty(
        name="Bone Group",
        description="Bone Group",
        default= "primary",
        items=[
            ( "None",       "None",      "Default"              ),
            ( "primary",    "primary",   "Primary Controls"     ),
            ( "secondry",   "secondry",  "Secondry Controls"    ),
            ( "offset",     "offset",    "systemBone"           ),
            ( "unsel",      "unsel",     "systemBone"           ),
            ( "hide",       "hide",      "systemBone"           ),
        ]
    )

    """ 重複 ディスプレイボーン """
    BoneDisplayType : EnumProperty(
            name="Bone Display Type",
            description="Bone Display Type",
            default= None,
            items=[
                ("OCTAHEDRAL","OCTAHEDRAL","BoneType"),
                ("STICK","STICK","BoneType"),
                ("BBONE","BBONE","BoneType"),
                ("ENVELOPE","ENVELOPE","BoneType"),
                ("WIRE","WIRE","BoneType"),
            ]
        )
    """ スライダーのカスタムディスプレイアイコンの選択。icon.blendよりアペンド """
    SliderType : EnumProperty(
            name="Slider Type",
            description="Bone Slider Icon",
            default= "cs_FKIK",
            items=[
                ("cs_FKIK",     "FK_IK",      "SliderIcon"),
                ("cs_IKFK",     "IK_FK",      "SliderIcon"),
                ("cs_SliderBar","SliderBar",  "SliderIcon"),
                ("cs_SliderA",  "SliderA",    "SliderIcon"),
                ("cs_SliderB",  "SliderB",    "SliderIcon"),
                ("cs_Empty",    "Empty",      "SliderIcon"),

            ]
        )


    CustomPropNameProp       : StringProperty(name = "CustomParamater Name", default = "Switch")
    BoneNameProp             : StringProperty(name = "Bone Name", default = "Slider")
    BoneBBsizeProp           : FloatProperty(name = "BendyBone size", default = 0.2)
    AddBoneLayerBool         : BoolProperty (name ="Add Active Layer", default =True)
    SystemBoneLayerInt       : IntProperty (name ="System Layer", default =3 , min=0,max=31)
    CustomShapeSizeProp      : FloatProperty(name = "Slyder size", default=0.2,min=0.01,description="Slyder size")
    PositionProp             : FloatProperty(name = "Slider potition", default=1)
    AttachIKinfluenceProp    : BoolProperty (name ="Attach IK influence to Slider", default =True)
    #ボーングループ既存のものがアレば自動でItemに追加したい。やり方がわからない

    def execute(self, context):
        """ １選択ボーンからスライダー生成を実行 """
        Bone = QuickBone_Tools(bpy.context.active_bone)
        Bone.MakeSlider(newBoneName = self.BoneNameProp,
                        CustomShapeSize =self.CustomShapeSizeProp,
                        BBsize = self.BoneBBsizeProp,
                        SystemBoneLayer =self.SystemBoneLayerInt,
                        AddBoneLayer = self.AddBoneLayerBool,
                        oMode = "SlideY",#Sliderの形変更予定
                        oSliderType = self.SliderType,
                        oPosition = self.PositionProp,
                        oCustomPropName = self.CustomPropNameProp,
                        oGroupName = self.BoneGroupEnum,
                        AttachIKconstrain_Slider = self.AttachIKinfluenceProp,
                        )
        bpy.context.object.data.display_type = self.BoneDisplayType
        return {'FINISHED'}

class MakeBoneOne_Offset_OT_object(bpy.types.Operator):
    """ １選択からオフセットボーン生成はよく使うので、
    独立してメニューに登録させるためのクラス """
    bl_idname = "armature.newbone_fromselect1bone_offset"
    bl_label = "OffsetBone"
    bl_description = "OffsetBone"
    bl_options = {'REGISTER', 'UNDO'}
    CustomShapeSizeProp : FloatProperty(default=0.2,name = "OffsetBone size" ,description="OffsetBone size")

    def execute(self, context):
        Bone = QuickBone_Tools(bpy.context.active_bone)
        #プロパティが異なるだけで１選択から実行の処理に組み込んだ
        Bone.newBone_FromSelect1Bone(CustomShapeSize = self.CustomShapeSizeProp, oMode = "Offset")
        return {'FINISHED'}

class MatchBoneTwo_OT_object(bpy.types.Operator):
    """ ２選択ボーンからSRTマッチ """
    bl_idname = "armature.matchbonetwo"
    bl_label = "Fit and aline select 2 bones"
    bl_description = "Fit and aline select 2 bones"
    bl_options = {'REGISTER', 'UNDO'}

    AlineBool : BoolProperty(name = "Aline", default = True)
    LengthBool : BoolProperty(name = "Fit Length", default = True)
    FitMode : EnumProperty(
        name="Fit Method",
        description="Bone tail,head Fit Method",
        default='TtoH',
        items=[
            ('TtoH', "tail to head", "Connect two selected bones"),
            ('TtoT', "tail to tail", "Connect two selected bones"),
            ('HtoH', "head to head", "Connect two selected bones"),
            ('HtoT', "head to tail", "Connect two selected bones"),
            ('ALL', "Fit All", "FitAll"),
        ]
    )
    def execute(self, context):
        QUtil = QuickBone_Utility(bpy.context.active_bone)
        SaveMode = QUtil.ChangeEditMode()
        #２ボーン選択で１番目をA、２番めをBとする
        A,B = QUtil.SelectBoneTwo()
        QUtil.FitBones(B,A,
                        FitMethod = self.FitMode,
                        oAline = self.AlineBool,
                        oLength = self.LengthBool,
                        )
        #実行前のモードに戻す
        olist = [A]

        bpy.ops.object.mode_set(mode = SaveMode)
        QUtil.NewBonesSelector(SaveMode,olist)

        return {'FINISHED'}

class SetParent_OT_object(bpy.types.Operator):
    """ ポーズモードでもペアレント化 """
    bl_idname = "armature.setparentposemode"
    bl_label = "SetParent"
    bl_description = "SetParent 2SelectBones"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        QUtil = QuickBone_Utility(bpy.context.active_bone)
        QUtil.SetParentPoseMode()
        return {'FINISHED'}

class ClearParent_OT_object(bpy.types.Operator):
    """ ポーズモードでもペアレントクリア """
    bl_idname = "armature.clearparentposemode"
    bl_label = "ClearParent"
    bl_description = "clearParent"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        QUtil = QuickBone_Utility(bpy.context.active_bone)
        QUtil.ClearParentPoseMode()
        return {'FINISHED'}

class DeleteBonePoseMode_OT_object(bpy.types.Operator):
    """ ポーズモードでもボーンを削除 """
    bl_idname = "armature.deleteboneposemode"
    bl_label = "DeleteBone"
    bl_description = "DeleteBone"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        QUtil = QuickBone_Utility(bpy.context.active_bone)
        QUtil.DeleteBonePoseMode()
        return {'FINISHED'}