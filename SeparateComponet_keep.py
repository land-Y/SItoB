import bpy

#シーン全体のオブジェクト名を取得し、BEFORに格納
#セパレート後のシーン全体オブジェクトを取得しAFTERに格納
#上記の差分を選択して、選択
#エディットモードに変更して、コンポーネントを全選択。

def set_active_tool(tool_name):
    for area in bpy.context.screen.areas:
        if area.type == "VIEW_3D":
            override = bpy.context.copy()
            override["space_data"] = area.spaces[0]
            override["area"] = area
            bpy.ops.wm.tool_set_by_id(name=tool_name, space_type='VIEW_3D')

def SeparateComponent_keep():
    BEFOR = set(obj.name for obj in bpy.data.objects)

    bpy.ops.mesh.duplicate()
    bpy.ops.mesh.separate(type='SELECTED')

    AFTER = set(obj.name for obj in bpy.data.objects)

    olis = AFTER - BEFOR

    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')

    for i in olis:
        obj = bpy.data.objects[i]
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')

#メニュー登録関係
def menu_draw(self, context):
  self.layout.operator("object.separatecomponet_keep")

class SeparateComponent_OT_object(bpy.types.Operator):
    bl_idname = "object.separatecomponet_keep"
    bl_label = "Separate Componet keep"
    bl_description = "Separate Componet keep"
    bl_options = {'REGISTER', 'UNDO'}

    #menu登録
    bpy.types.VIEW3D_MT_edit_mesh_faces.append(menu_draw)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.prepend(menu_draw)

    def execute(self, context,):
        SeparateComponent_keep()
        set_active_tool("builtin.transform")
        return {'FINISHED'}

classes = (
    SeparateComponent_OT_object,
)