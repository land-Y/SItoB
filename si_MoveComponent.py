import bpy

S1 = "builtin.select"
# Background selection addon "Box Select X-Ray" required.
# https://blenderartists.org/t/box-select-x-ray/1212316
S2 = "mesh_tool.select_box_xray"
S3 = "builtin.select_box"
S4 = "builtin.move"

def set_active_tool(tool_name):
    for area in bpy.context.screen.areas:
        if area.type == "VIEW_3D":
            with bpy.context.temp_override(area=area):
                bpy.ops.wm.tool_set_by_id(name=tool_name)

def si_MoveComponent(a, b, c, select_tool):
    oSel = bpy.context.selected_objects
    for o in oSel:
        if o.type == "MESH":
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.context.tool_settings.mesh_select_mode = (a, b, c)
            set_active_tool(select_tool)
        elif o.type in {"CURVE", "SURFACE"}:
            bpy.ops.object.mode_set(mode='EDIT')
            set_active_tool(S4)
        elif o.type == "ARMATURE":
            if bpy.context.mode == "POSE":
                print("Pose now")
            else:
                bpy.ops.object.mode_set(mode='EDIT')

class si_MoveComponent_OT_object(bpy.types.Operator):
    bl_idname = "object.si_movecomponent"
    bl_label = "Move Component Tool"
    bl_description = "Move Component Tool like Softimage"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        si_MoveComponent(True, True, True, S1)
        return {'FINISHED'}

class si_MoveComponent1_OT_object(bpy.types.Operator):
    bl_idname = "object.si_movecomponent1"
    bl_label = "Point Select Tool"
    bl_description = "Point Select Tool like Softimage"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        si_MoveComponent(True, False, False, S2)
        return {'FINISHED'}

class si_MoveComponent2_OT_object(bpy.types.Operator):
    bl_idname = "object.si_movecomponent2"
    bl_label = "Edge Select Tool"
    bl_description = "Edge Select Tool like Softimage"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        si_MoveComponent(False, True, False, S2)
        return {'FINISHED'}

class si_MoveComponent3_OT_object(bpy.types.Operator):
    bl_idname = "object.si_movecomponent3"
    bl_label = "Polygon Select Tool"
    bl_description = "Polygon Select Tool like Softimage"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        si_MoveComponent(False, False, True, S2)
        return {'FINISHED'}

# Registration
classes = (
    si_MoveComponent_OT_object,
    si_MoveComponent1_OT_object,
    si_MoveComponent2_OT_object,
    si_MoveComponent3_OT_object,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
