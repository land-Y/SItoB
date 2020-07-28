import bpy

class GetRegion3D(bpy.types.Operator):
    #小文字以外うけつけない
    bl_idname = "view3d.getregion3d"
    bl_label = "GetRagion3D"
 
    #処理本体
    def execute(self, context,):
        #マウスカーソル上にあるSpaceView3Dの取得、area.type毎で使える処理が異なるので注意
        #カメラのマトリクスなどは更に.region_3dなどつけて利用。
        #https://docs.blender.org/api/blender2.8/bpy.types.SpaceView3D.html
        area = bpy.context.space_data
        print(area)
        return {'FINISHED'}

#クラス呼び出し
classes = (
GetRegion3D,
)

#blenderにレジスター
def register():
    for cls in classes:
        bpy.utils.register_class(cls)

if __name__ == "__main__":
    register()