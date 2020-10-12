import bpy
from bpy.props import BoolProperty


#メニュー登録関係
def menu_draw(self, context):
    self.layout.operator("object.createseam_selfaceborder")
    self.layout.operator("object.knife_project_cut_through")
    self.layout.operator("object.knife_project")

def CreateSeam_SelFaceBorder():
    bpy.ops.mesh.region_to_loop()
    bpy.ops.mesh.mark_seam(clear=False)


def knife_project(o):
    oSel = bpy.context.selected_objects
    if len(oSel) != 2:
        print("Please Selecting ProjectionMesh and MeshObject")
    else:
        if bpy.context.mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.knife_project(cut_through= o )

class KnifeProject_OT_CreateSeam_SelFaceBorder(bpy.types.Operator):
    bl_idname = "object.createseam_selfaceborder"
    bl_label = "CreateSeam Border of faces"
    bl_description = "CreateSeam Border of faces"
    bl_options = {'REGISTER', 'UNDO'} 

    def execute(self, context):
        CreateSeam_SelFaceBorder()
        return {'FINISHED'}

class KnifeProject_OT_object_cut_through(bpy.types.Operator):
    bl_idname = "object.knife_project_cut_through"
    bl_label = "Knife Project cut through"
    bl_description = "Knife Project cut through"
    bl_options = {'REGISTER', 'UNDO'} 

    def execute(self, context):
        knife_project(True)
        return {'FINISHED'}

class KnifeProject_OT_object(bpy.types.Operator):
    bl_idname = "object.knife_project"
    bl_label = "Knife Project"
    bl_description = "Knife Project"
    bl_options = {'REGISTER', 'UNDO'} 
    
    #コンテキストメニューに登録
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.prepend(menu_draw)
    bpy.types.VIEW3D_MT_object_context_menu.prepend(menu_draw)


    def execute(self, context):
        knife_project(False)
        return {'FINISHED'}