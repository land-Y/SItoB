import bpy
from bpy.props import BoolProperty



#法線をアクティブにする、既にチェック済み場合は無視。
def oSm(b):
    for o in bpy.context.selected_objects:
        if o.type == 'MESH':
            bpy.ops.object.shade_smooth()
            if o.data.use_auto_smooth == False:
                o.data.use_auto_smooth = True
                o.data.auto_smooth_angle = b
        elif o.type == 'CURVE':
            o.data.splines[0].use_smooth = True


def si_active_normal():
    oCM = bpy.context.object.mode
    if oCM == 'OBJECT':
        oSm(1.0472)
    else:
        bpy.ops.object.mode_set(mode='OBJECT')
        oSm(1.0472)
        bpy.ops.object.mode_set ( mode = oCM )



#サブディビジョンモデファイア削除、法線設定もデフォルトに戻す
def oDeln():
    for o in bpy.context.selected_objects:
        if o.type == 'MESH':
            bpy.ops.object.shade_flat()
            o.data.use_auto_smooth = False
            o.data.auto_smooth_angle = 0.523599
        elif o.type == 'CURVE':
            o.data.splines[0].use_smooth = False

def si_noactive_normal():
    oCM = bpy.context.object.mode
    if oCM == 'OBJECT':
        oDeln()
    else:
        bpy.ops.object.mode_set(mode='OBJECT')
        oDeln()
        bpy.ops.object.mode_set ( mode = oCM )



#サブディビジョン適応。法線適応コマンドのために、
#一々オブジェクトモードに切り替えて実行後、もとに戻す。
def oDel():
    for o in bpy.context.selected_objects:
        for m in o.modifiers:
            if(m.type == "SUBSURF"):
                o.modifiers.remove(m)
    return

def delete_subdiv():
    oCM = bpy.context.object.mode
    if oCM == 'OBJECT':
        oDel()
    else:
        bpy.ops.object.mode_set(mode='OBJECT')
        oDel()
        bpy.ops.object.mode_set ( mode = oCM )

def GetModifires():
    for i in bpy.context.selected_objects:
        #モディファイアの適応数
        num = len(i.modifiers)
        return num

def xsisubdiv(oL,oAdd):
    #サブディビモデファイアの名前が一致したらプレビューの数値を増やす
    for o in bpy.context.selected_objects:
        #メッシュか判定
        if o.type == 'MESH' or 'CURVE':
            #名称規則でSI_subdivが存在しなければ新規でモデファイア生成
            if o.modifiers.get("SI_subdiv") == None:
                #すでに知らん名前のサブディビモデファイアがあれば全てさよならグッバイ
                for m in o.modifiers:
                    if(m.type == "SUBSURF"):
                        o.modifiers.remove(m)
                oLevel =o.modifiers.new("SI_subdiv",type = "SUBSURF")
                oLevel.render_levels = oL
                oLevel.levels = oL
                #ケージモードON
                o.modifiers["SI_subdiv"].show_on_cage = True
                print(o.name + " add SI_subdiv,Set CageMode")

            #名称規則でSI_subdivが存在していれば、サブディビジョンレベルを＋１
            #ただし、知らん名前のSUBSURFがあれば放置
            else:
                for m in o.modifiers:
                    if(m.type == "SUBSURF" and m.name =="SI_subdiv"):
                        m.render_levels = m.render_levels+ oAdd
                        m.levels = m.levels+ oAdd
                        print(o.name + " subdiv level " + str(m.levels))
    #ビューのリフレッシュ
    bpy.context.scene.frame_current = bpy.context.scene.frame_current
    return


class si_del_subdiv_OT_object(bpy.types.Operator):
    bl_idname = "object.si_del_sudiv"
    bl_label = "Delete Subdivision"
    bl_description = "Subdivisions like Softimage"
    bl_options = {'REGISTER', 'UNDO'} 

    def execute(self, context):
        delete_subdiv()
        si_noactive_normal()
        return {'FINISHED'}


class si_add_subdiv_OT_object(bpy.types.Operator):
    bl_idname = "object.si_add_sudiv"
    bl_label = "Add Subdivision"
    bl_description = "Subdivisions like Softimage"
    bl_options = {'REGISTER', 'UNDO'} 

    #モデファイアを最後に移動するオプション
    si_moveindex = BoolProperty(default=True, name = "Move Modifire", description = "Move Modifire")

    def execute(self,context):
        si_active_normal()
        xsisubdiv(1,1)
        
        if self.si_moveindex:
            #選択オブジェクトからモデファイア数を戻す
            num = GetModifires()
            bpy.ops.object.modifier_move_to_index(modifier="SI_subdiv",index= num - 1)
        return {'FINISHED'}


class si_minus_subdiv_OT_object(bpy.types.Operator):
    bl_idname = "object.si_minus_sudiv"
    bl_label = "Subtract subdivision"
    bl_description = "Subdivisions like Softimage"
    bl_options = {'REGISTER', 'UNDO'} 

    def execute(self,context):
        xsisubdiv(1,-1)
        return {'FINISHED'}
