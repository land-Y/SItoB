import bpy
from bpy.props import BoolProperty



def set_active_tool(tool_name):
    for area in bpy.context.screen.areas:
        if area.type == "VIEW_3D":
            override = bpy.context.copy()
            override["space_data"] = area.spaces[0]
            override["area"] = area
            bpy.ops.wm.tool_set_by_id(override, name=tool_name)
    


class tglPivot_OT_object(bpy.types.Operator):
    bl_idname = "view3d.toggle_pivot_mode"
    bl_label = "toggle pivot mode"
    bl_description = "toggle pivot mode"
    bl_options = {'REGISTER', 'UNDO'} 

    bSnap = BoolProperty(default=True, name = "start Snap", description = "Corser Active Snap")
    eSnap = BoolProperty(default=True, name = "end Snap", description = "Finish Active Snap")

    def execute(self, context,):

        Scene = bpy.data.scenes['Scene']
        Snap = Scene.tool_settings.use_snap
        SnapElement = Scene.tool_settings.snap_elements
        Tra = Scene.transform_orientation_slots[0].type
        Pivot = Scene.tool_settings.transform_pivot_point

        if Tra != 'CURSOR':
            set_active_tool("builtin.cursor")
            Scene.transform_orientation_slots[0].type = 'CURSOR'

            if self.bSnap:
                Scene.tool_settings.use_snap = True
                Scene.tool_settings.snap_elements = {'VERTEX'}
            else:
                Scene.tool_settings.use_snap = False
            Scene.tool_settings.transform_pivot_point = 'CURSOR'
        else:
            Scene.transform_orientation_slots[0].type = 'GLOBAL'
            if self.eSnap:
                Scene.tool_settings.use_snap = False
            else:
                print('Finish')
            Scene.tool_settings.transform_pivot_point = 'BOUNDING_BOX_CENTER'

        return {'FINISHED'}
