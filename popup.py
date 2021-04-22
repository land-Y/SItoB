import bpy
from bpy.props import IntProperty, FloatProperty, EnumProperty
from bpy.props import FloatVectorProperty, StringProperty

class ShowPopupMessage(bpy.types.Operator):

    bl_idname = "object.show_popup_message"
    bl_label = "ポップアップメッセージ"
    bl_description = "ポップアップメッセージ"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        # ポップアップメッセージ表示
        return wm.invoke_popup(self, width=200, height=100)

    # ポップアップメッセージに表示する内容
    def draw(self, context):
        layout = self.layout
        layout.label("メッセージ")