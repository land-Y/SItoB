import bpy
from bpy.props import BoolProperty , FloatVectorProperty


#アーマチュアのエディット中ボーンの位置をリセット
#ロールもリセットするがどのような影響がでるか未検証

def ResetBone(oAdd):
    for a in bpy.data.armatures:
        for b in a.edit_bones:
            if b.select_tail:
                if b.parent == None:
                    c  = b.head
                    d = oAdd
                    e = list(map(lambda x,y:x+y,c,d))
                    b.roll = 0
                    b.tail = e

                else:
                    c  = b.head
                    d = oAdd
                    e = list(map(lambda x,y:x+y,c,d))
                    b.tail = e
                    b.roll = 0

            if b.select_head:
                if b.parent == None:
                    b.head = [0,0,0]
                    b.roll = 0

                else:
                    c  = b.parent.tail 
                    d = oAdd
                    e = list(map(lambda x,y:x+y,c,d))
                    b.head = e
                    b.roll = 0



#SRTを初期値に戻す。回転はまだ何かリセットすべきものある？
def si_ResetSRT(oDelta,oVector):
    for i in bpy.context.selected_objects:

        i.location[0] = 0
        i.location[1] = 0
        i.location[2] = 0
        
        i.rotation_euler[0] = 0
        i.rotation_euler[1] = 0
        i.rotation_euler[2] = 0
        i.rotation_quaternion[0] = 1
        i.rotation_quaternion[1] = 0
        i.rotation_quaternion[2] = 0
        i.rotation_quaternion[3] = 0
        i.rotation_axis_angle[0] = 0
        i.rotation_axis_angle[1] = 0
        i.rotation_axis_angle[2] = 0
        i.rotation_axis_angle[3] = 0
        
        i.scale[0] = 1
        i.scale[1] = 1
        i.scale[2] = 1
        
        #reset delta
        if oDelta == 1:
            i.delta_location[0] = 0
            i.delta_location[1] = 0
            i.delta_location[2] = 0
            
            i.delta_rotation_euler[0] = 0
            i.delta_rotation_euler[1] = 0
            i.delta_rotation_euler[2] = 0
            
            i.scale[0] = 1
            i.scale[1] = 1
            i.scale[2] = 1

        #もしモードがPOSEならトランスフォームすべてクリア
        oMode = bpy.context.object.mode
        if oMode == "POSE":
            bpy.ops.pose.transforms_clear()

        #もしモードがEDITでアーマチュアならボーンの初期化
        if oMode == "EDIT":
            ResetBone(oVector)


class si_ResetSRT_OT_object(bpy.types.Operator):
    bl_idname = "object.si_resetsrt"
    bl_label = "Reset All Transform and Delta"
    bl_description = "Reset All Transform and Delta"
    bl_options = {'REGISTER', 'UNDO'} 

    si_bool : BoolProperty(default=True, name = "Reset Delta", description = "Reset Delta")
    si_VEC : FloatVectorProperty(subtype='TRANSLATION',default=(0.0, 0.0, 0.0), name = "Offset(BoneOnly)")
 
    def execute(self, context,):
        oBool = self.si_bool
        oVec = self.si_VEC

        si_ResetSRT(oBool,oVec)


        return {'FINISHED'}
