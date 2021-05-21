import bpy
from bpy.props import StringProperty, FloatProperty, EnumProperty




# オブジェクトを並進移動するオペレータ
class SAMPLE24_OT_TranslateObject(bpy.types.Operator):

    bl_idname = "object.sample24_translate_object"
    bl_label = "menu"
    bl_description = "オブジェクトを並進移動します"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        print("test")
        return {'FINISHED'}


# メインメニュー
class SAMPLE24_MT_TranslateObject(bpy.types.Menu):

    bl_idname = "SAMPLE24_MT_TranslateObject"
    bl_label = "オブジェクトの並進移動"
    bl_description = "オブジェクトを並進移動します"

    def draw(self, context):
        layout = self.layout
        # サブメニューの登録
        # bpy.data.objects：オブジェクト一覧
        for o in bpy.data.objects:
            if o.type == 'MESH':
                ops = layout.operator(
                    SAMPLE24_OT_TranslateObject.bl_idname, text=o.name
                )
                ops.obj_name = o.name


def menu_fn(self, context):
    self.layout.separator()
    self.layout.menu(SAMPLE24_MT_TranslateObject.bl_idname)


classes = [
    SAMPLE24_OT_TranslateObject,
    SAMPLE24_MT_TranslateObject,
]


def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.VIEW3D_MT_object.append(menu_fn)
    print("サンプル 2-4: アドオン『サンプル 2-4』が有効化されました。")


def unregister():
    bpy.types.VIEW3D_MT_object.remove(menu_fn)
    for c in classes:
        bpy.utils.unregister_class(c)
    print("サンプル 2-4: アドオン『サンプル 2-4』が無効化されました。")


if __name__ == "__main__":
    register()