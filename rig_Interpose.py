import bpy

#選択１をA、選択２をBとしリスト化する。
def Select2obj():
    oSel = bpy.context.selected_objects
    if oSel == []:
        print("please select 2 objects")
    else:
        A = oSel[0]
        B = oSel[1]
        return A,B

A,B = Select2obj()


#emptyを取り出す。
#アーマチュアのボーンが選択されていたらボーンを作成する
#これをCとする
def MakeEmpty(oName):
    oIP = bpy.data.objects.new("empty" ,None)
    bpy.context.scene.collection.objects.link(oIP)
    oIP.empty_display_size = 1
    #'PLAIN_AXES', 'ARROWS', 'SINGLE_ARROW', 'CIRCLE', 'CUBE', 'SPHERE', 'CONE', 'IMAGE'
    oIP.empty_display_type = "ARROWS"
    oIP.name = oName
    return oIP


#Empty呼び出し後ドライバーの入れ物準備
C = MakeEmpty("IP.001")

#カスタムパラメーター用意。ただし最小最大などのパラメーターがONになってない。要チェック
C["TRA"] = 0.5
C["DIR"] = 0.5
C["UPV"] = 0.5
C["SCL"] = 0.5
#C["_RNA_UI"] = {"TRA":{"min":0,"max":1}}


tx = C.driver_add('location',0)
ty = C.driver_add('location',1)
tz = C.driver_add('location',2)

rx = C.driver_add('rotation_euler',0)
ry = C.driver_add('rotation_euler',1)
rz = C.driver_add('rotation_euler',2)

sx = C.driver_add('scale', 0)
sy = C.driver_add('scale', 1)
sz = C.driver_add('scale', 2)



#v.type = 'TRANSFORMS' 'ROTATION_DIFF' 'LOC_DIFF''SINGLE_PROP'
def SetDriver(oLocation,oType,oExp,oName,iType,oObjA,oDP,oLoc,oWS):
    v = oLocation.driver.variables.new()
    oLocation.driver.type = oType
    oLocation.driver.expression = oExp
    v.name = oName
    v.type = iType
    v.targets[0].id = oObjA
    v.targets[0].data_path = oDP
    v.targets[0].transform_type = oLoc
    v.targets[0].transform_space = oWS
    
#にカスタムプロパティの値をセット
def SetDriverCP(oLocation,oName,oType,oID,oDP):
    v = oLocation.driver.variables.new()
    v.name = oName
    v.type = oType
    v.targets[0].id = oID
    v.targets[0].data_path = oDP

#TRA
SetDriver(tx,"SCRIPTED","lerp(x,y,z)","x",'TRANSFORMS',A,'location.x','LOC_X','WORLD_SPACE')
SetDriver(tx,"SCRIPTED","lerp(x,y,z)","y",'TRANSFORMS',B,'location.x','LOC_X','WORLD_SPACE')
SetDriverCP(tx,"z",'SINGLE_PROP',C,'["TRA"]')

SetDriver(ty,"SCRIPTED","lerp(x,y,z)","x",'TRANSFORMS',A,'location.y','LOC_Y','WORLD_SPACE')
SetDriver(ty,"SCRIPTED","lerp(x,y,z)","y",'TRANSFORMS',B,'location.y','LOC_Y','WORLD_SPACE')
SetDriverCP(ty,"z",'SINGLE_PROP',C,'["TRA"]')

SetDriver(tz,"SCRIPTED","lerp(x,y,z)","x",'TRANSFORMS',A,'location.z','LOC_Z','WORLD_SPACE')
SetDriver(tz,"SCRIPTED","lerp(x,y,z)","y",'TRANSFORMS',B,'location.z','LOC_Z','WORLD_SPACE')
SetDriverCP(tz,"z",'SINGLE_PROP',C,'["TRA"]')

#ROT(DIR,UPV)
SetDriver(rx,"SCRIPTED","lerp(x,y,z)","x",'TRANSFORMS',A,'location.x','ROT_X','WORLD_SPACE')
SetDriver(rx,"SCRIPTED","lerp(x,y,z)","y",'TRANSFORMS',B,'location.x','ROT_X','WORLD_SPACE')
SetDriverCP(rx,"z",'SINGLE_PROP',C,'["UPV"]')

SetDriver(ry,"SCRIPTED","lerp(x,y,z)","x",'TRANSFORMS',A,'location.y','ROT_Y','WORLD_SPACE')
SetDriver(ry,"SCRIPTED","lerp(x,y,z)","y",'TRANSFORMS',B,'location.y','ROT_Y','WORLD_SPACE')
SetDriverCP(ry,"z",'SINGLE_PROP',C,'["DIR"]')

SetDriver(rz,"SCRIPTED","lerp(x,y,z)","x",'TRANSFORMS',A,'location.z','ROT_Z','WORLD_SPACE')
SetDriver(rz,"SCRIPTED","lerp(x,y,z)","y",'TRANSFORMS',B,'location.z','ROT_Z','WORLD_SPACE')
SetDriverCP(rz,"z",'SINGLE_PROP',C,'["DIR"]')

#SCL
SetDriver(sx,"SCRIPTED","lerp(x,y,z)","x",'TRANSFORMS',A,'location.x','SCALE_X','WORLD_SPACE')
SetDriver(sx,"SCRIPTED","lerp(x,y,z)","y",'TRANSFORMS',B,'location.x','SCALE_X','WORLD_SPACE')
SetDriverCP(sx,"z",'SINGLE_PROP',C,'["SCL"]')

SetDriver(sy,"SCRIPTED","lerp(x,y,z)","x",'TRANSFORMS',A,'location.y','SCALE_Y','WORLD_SPACE')
SetDriver(sy,"SCRIPTED","lerp(x,y,z)","y",'TRANSFORMS',B,'location.y','SCALE_Y','WORLD_SPACE')
SetDriverCP(sy,"z",'SINGLE_PROP',C,'["SCL"]')

SetDriver(sz,"SCRIPTED","lerp(x,y,z)","x",'TRANSFORMS',A,'location.z','SCALE_Z','WORLD_SPACE')
SetDriver(sz,"SCRIPTED","lerp(x,y,z)","y",'TRANSFORMS',B,'location.z','SCALE_Z','WORLD_SPACE')
SetDriverCP(sz,"z",'SINGLE_PROP',C,'["SCL"]')
#Cにドライバーを付与する。
#位置
#回転
#スケール
#リミット

#update
bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1) 