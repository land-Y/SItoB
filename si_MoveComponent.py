import bpy

D   ="DISABLE"
E   ="ENABLE"
T   ="TOGGLE"
S1  ="builtin.select"
#背面選択アドオン「Box Select X-Ray」必須。
#https://blenderartists.org/t/box-select-x-ray/1212316
#なければデフォルトの物を選択ってやりたいけど未対応
S2  ="mesh_tool.select_box_xray"
S3  ="builtin.select_box"

def set_active_tool(tool_name):
    for area in bpy.context.screen.areas:
        if area.type == "VIEW_3D":
            override = bpy.context.copy()
            override["space_data"] = area.spaces[0]
            override["area"] = area
            bpy.ops.wm.tool_set_by_id(override, name=tool_name)
            


def si_MoveComponent(a,b,c,d):    
    mode = bpy.context.active_object.mode
    bpy.ops.object.mode_set(mode='EDIT')
    set_active_tool(d)
    bpy.ops.mesh.select_mode(use_extend=True ,type="VERT",action= a )
    bpy.ops.mesh.select_mode(use_extend=True ,type="EDGE",action= b )
    bpy.ops.mesh.select_mode(use_extend=True ,type="FACE",action= c )


class si_MoveComponent_OT_object(bpy.types.Operator):
    bl_idname = "object.si_movecomponent"
    bl_label = "Move Component Tool"
    bl_description = "Move Component Tool like Softimage"
    bl_options = {'REGISTER', 'UNDO'} 

    def execute(self, context,):
        si_MoveComponent(E,E,E,S1)
        return {'FINISHED'}

class si_MoveComponent1_OT_object(bpy.types.Operator):
    bl_idname = "object.si_movecomponent1"
    bl_label = "Point Select Tool"
    bl_description = "Point Select Tool like Softimage"
    bl_options = {'REGISTER', 'UNDO'} 

    def execute(self, context,):
        si_MoveComponent(E,D,D,S2)
        return {'FINISHED'}
    
class si_MoveComponent2_OT_object(bpy.types.Operator):
    bl_idname = "object.si_movecomponent2"
    bl_label = "Edge Select Tool"
    bl_description = "Edge Select Tool like Softimage"
    bl_options = {'REGISTER', 'UNDO'} 

    def execute(self, context,):
        si_MoveComponent(D,E,D,S2)
        return {'FINISHED'}

class si_MoveComponent3_OT_object(bpy.types.Operator):
    bl_idname = "object.si_movecomponent3"
    bl_label = "Polygon Select Tool"
    bl_description = "Polygon Select Tool like Softimage"
    bl_options = {'REGISTER', 'UNDO'} 

    def execute(self, context,):
        si_MoveComponent(D,D,E,S2)
        return {'FINISHED'}


