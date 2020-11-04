import bpy
from bpy.props import BoolProperty



def set_active_tool(tool_name):
    for area in bpy.context.screen.areas:
        if area.type == "VIEW_3D":
            override = bpy.context.copy()
            override["space_data"] = area.spaces[0]
            override["area"] = area
            bpy.ops.wm.tool_set_by_id(override, name=tool_name)
    

def TglCursor(oStartSnap,oEndSnap,oShowCursor):
    Scene = bpy.data.scenes['Scene']
    Snap = Scene.tool_settings.use_snap
    SnapElement = Scene.tool_settings.snap_elements
    Tra = Scene.transform_orientation_slots[0].type
    Pivot = Scene.tool_settings.transform_pivot_point
    ovl = bpy.context.space_data.overlay

    if Tra != 'CURSOR':
        set_active_tool("builtin.cursor")
        Scene.transform_orientation_slots[0].type = 'CURSOR'
        ovl.show_cursor = True
        Scene.tool_settings.use_snap = oStartSnap
        Scene.tool_settings.snap_elements = {'VERTEX'}
        Scene.tool_settings.transform_pivot_point = 'CURSOR'
    else:
        Scene.transform_orientation_slots[0].type = 'GLOBAL'
        Scene.tool_settings.use_snap = oEndSnap
        Scene.tool_settings.transform_pivot_point = 'BOUNDING_BOX_CENTER'
        ovl.show_cursor = oShowCursor

class tglPivot_OT_object(bpy.types.Operator):
    bl_idname = "view3d.toggle_pivot_mode"
    bl_label = "toggle pivot mode"
    bl_description = "toggle pivot mode"
    bl_options = {'REGISTER', 'UNDO'} 

    bSnap = BoolProperty(default=False, name = "start Snap", description = "Corser Active Snap")
    eSnap = BoolProperty(default=False, name = "end Snap", description = "Finish Active Snap")
    oShow = BoolProperty(default=True, name = "Show Cursor", description = "Show cursor")
    def execute(self, context,):

        if self.bSnap:
            oStartSnap = True
        else:
            oStartSnap = False

        if self.eSnap:
            oEndSnap = True
        else:
            oEndSnap = False

        if self.oShow:
            oShowCursor = True
        else:
            oShowCursor = False
        TglCursor(oStartSnap,oEndSnap,oShowCursor)

        return {'FINISHED'}
