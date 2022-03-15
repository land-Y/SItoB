import bpy
from bpy.props import EnumProperty

def TglCorsor(PivotMode_A,PivotMode_B):
    Scenes = bpy.data.scenes
    for Scene in Scenes:
        SeeneTool = Scene.tool_settings.transform_pivot_point
        if not SeeneTool == PivotMode_A:
            Scene.tool_settings.transform_pivot_point = PivotMode_A
        else:
            Scene.tool_settings.transform_pivot_point = PivotMode_B

class tglPivot_OT_object(bpy.types.Operator):
    bl_idname = "view3d.toggle_pivot_mode"
    bl_label = "toggle pivot mode"
    bl_description = "toggle pivot mode"
    bl_options = {'REGISTER', 'UNDO'}

    PivotModeA : EnumProperty(
        name = "Pivot Mode",
        description = "Pivot Point Select",
        default = "CURSOR",
        items=[
            ("BOUNDING_BOX_CENTER", "BoundingBox", "PivtoMode"),
            ("CURSOR", "Cursor", "PivtoMode"),
            ("INDIVIDUAL_ORIGINS", "Origins", "PivtoMode"),
            ("MEDIAN_POINT", "Median Point", "PivtoMode"),
            ("ACTIVE_ELEMENT", "Active", "PivtoMode"),
        ]
    )

    PivotModeB : EnumProperty(
        name = "Pivot Mode",
        description = "Pivot Point Select",
        default = "INDIVIDUAL_ORIGINS",
        items=[
            ("BOUNDING_BOX_CENTER", "BoundingBox", "PivtoMode"),
            ("CURSOR", "Cursor", "PivtoMode"),
            ("INDIVIDUAL_ORIGINS", "Origins", "PivtoMode"),
            ("MEDIAN_POINT", "Median Point", "PivtoMode"),
            ("ACTIVE_ELEMENT", "Active", "PivtoMode"),
        ]
    )

    def execute(self, context,):

        TglCorsor(self.PivotModeA,self.PivotModeB)

        return {'FINISHED'}
