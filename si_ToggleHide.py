import bpy
from bpy.props import StringProperty

addon_keymaps = []

# --- 設定 ---
prop_name = "SItoBHide"
scene_name = "Scene"
# --- 設定ここまで ---

# カスタムプロパティの登録
def register_properties():
    bpy.types.Scene.SItoBHide = StringProperty(
        name="SItoBHide",
        description="非表示オブジェクトのリスト",
        default=""
    )

def unregister_properties():
    del bpy.types.Scene.SItoBHide

class SI_OT_toggle_hide(bpy.types.Operator):
    bl_idname = "object.si_toggle_hide"
    bl_label = "SI Toggle Hide"
    bl_description = "選択したオブジェクトを非表示にし、非表示のオブジェクトを再表示します"
    bl_options = {'REGISTER', 'UNDO'}

    def __init__(self, *args, **kwargs):
        bpy.types.Operator.__init__(self, *args, **kwargs)

    @classmethod
    def poll(cls, context):
        return context.area.type in {'VIEW_3D', 'OUTLINER'}

    def execute(self, context):
        if context.area.type == 'OUTLINER':
            # アウトライナー上で実行する場合
            for item in context.selected_ids:
                if item.bl_rna.identifier == "Object":
                    obj = bpy.data.objects[item.name]
                    obj.hide_viewport = not obj.hide_viewport
                    obj.hide_render = obj.hide_viewport
            return {'FINISHED'}

        # --- 以下は VIEW_3D での実行時の処理 ---
        # 対象シーンの取得と存在チェック
        target_scene = bpy.data.scenes.get(scene_name)

        if not target_scene:
            self.report({'ERROR'}, f"シーン '{scene_name}' が見つかりません。")
            return {'CANCELLED'}

        # 現在選択されているオブジェクトを取得
        selected_objects = context.selected_objects

        if selected_objects:
            # --- オブジェクトが選択されている場合の処理 (VIEW_3D) ---
            object_names = []

            # 選択オブジェクトをループし、非表示処理と名前リスト作成
            for obj in selected_objects:
                object_names.append(obj.name)

                # hide_viewport が False なら True にする
                if obj.hide_viewport is False:
                    obj.hide_viewport = True
                # hide_render が False なら True にする
                if obj.hide_render is False:
                    obj.hide_render = True

            # オブジェクト名をカンマ区切りの文字列にする
            value_string = ",".join(object_names)

            # シーンにカスタムプロパティを上書き設定
            target_scene[prop_name] = value_string

            # 選択を解除 (Object Mode である必要がある)
            if context.mode == 'OBJECT':
                bpy.ops.object.select_all(action='DESELECT')

        else:
            # --- オブジェクトが選択されていない場合の処理 (VIEW_3D) ---
            # カスタムプロパティが存在するか確認
            if prop_name in target_scene:
                value_string = target_scene.get(prop_name, "")

                # プロパティの値が空でないか確認
                if value_string:
                    # カンマで分割し、前後の空白を除去した名前のリストを作成
                    names_to_unhide = [name.strip() for name in value_string.split(',') if name.strip()]

                    if names_to_unhide:
                        # 念のため現在の選択をクリア (Object Mode である必要がある)
                        if context.mode == 'OBJECT':
                            bpy.ops.object.select_all(action='DESELECT')

                        found_count = 0
                        objects_to_select = []

                        # プロパティに記録された名前のオブジェクトを処理
                        for obj_name in names_to_unhide:
                            obj = bpy.data.objects.get(obj_name)
                            if obj:
                                obj.hide_viewport = False
                                obj.hide_render = False
                                objects_to_select.append(obj)
                                found_count += 1

                        # 見つかったオブジェクトを選択状態にする
                        if objects_to_select and context.mode == 'OBJECT':
                            context.view_layer.objects.active = objects_to_select[0]
                            for obj in objects_to_select:
                                obj.select_set(True)

        # 3Dビューの表示を更新
        if context.area:
            context.area.tag_redraw()
        return {'FINISHED'}

class SI_OT_Show_Hidden_Objects(bpy.types.Operator):
    bl_idname = "object.si_show_hidden_objects"
    bl_label = "SI Show Hidden Objects"
    bl_description = "隠したオブジェクトを表示します（ビューポート＆レンダー）"
    bl_options = {'REGISTER', 'UNDO'}

    def __init__(self, *args, **kwargs):
        bpy.types.Operator.__init__(self, *args, **kwargs)

    @classmethod
    def poll(cls, context):
        return context.area.type in {'VIEW_3D', 'OUTLINER'}

    def execute(self, context):
        if context.area.type == 'OUTLINER':
            for obj in bpy.data.objects:
                # アウトライナーに表示される通常のオブジェクトのみを対象にする（ライブラリリンクや非表示データを除く）
                if obj.users > 0:
                    obj.hide_viewport = False
                    obj.hide_render = False
            # Outlinerを再描画して表示状態を更新
            context.area.tag_redraw()
            return {'FINISHED'}

        # すべての隠されたオブジェクトを表示
        selected_in_view3d = context.area.type == 'VIEW_3D' # 3Dビューで実行されたか判定

        for obj in bpy.data.objects:
            if obj.hide_viewport or obj.hide_render:
                obj.hide_viewport = False
                obj.hide_render = False
                # 3Dビューで実行された場合のみ選択状態にする
                if selected_in_view3d:
                    obj.select_set(True)

        self.report({'INFO'}, "すべての隠されたオブジェクトを表示しました")
        return {'FINISHED'}

class SI_OT_Hide_Unselected(bpy.types.Operator):
    bl_idname = "object.si_hide_unselected"
    bl_label = "SI Hide Unselected"
    bl_description = "選択されていないオブジェクトを隠します（ビューポート＆レンダー）"
    bl_options = {'REGISTER', 'UNDO'}

    def __init__(self, *args, **kwargs):
        bpy.types.Operator.__init__(self, *args, **kwargs)

    @classmethod
    def poll(cls, context):
        return context.area.type in {'VIEW_3D', 'OUTLINER'}

    def execute(self, context):
        if context.area.type == 'OUTLINER':
            # アウトライナー上で実行する場合: 選択されたアイテムからオブジェクトを取得
            selected_objs = []
            for item in context.selected_ids:
                if item.bl_rna.identifier == "Object":
                    obj = bpy.data.objects.get(item.name)
                    if obj:
                        selected_objs.append(obj)
            hidden_count = 0
            # 選択されていないオブジェクトを隠し、選択オブジェクトは表示にする
            for obj in bpy.data.objects:
                if obj not in selected_objs:
                    obj.hide_viewport = True
                    obj.hide_render = True
                    hidden_count += 1
                else:
                    obj.hide_viewport = False
                    obj.hide_render = False
            # Outlinerを再描画して表示状態を更新
            context.area.tag_redraw()
            self.report({'INFO'}, f"{hidden_count}個のオブジェクトを隠しました")
            return {'FINISHED'}

        # 現在選択されているオブジェクトを取得
        selected_objects = context.selected_objects
        hidden_count = 0

        # 選択されていないオブジェクトを隠し、選択オブジェクトは表示にする
        for obj in bpy.data.objects:
            if obj not in selected_objects:
                obj.hide_viewport = True
                obj.hide_render = True
                hidden_count += 1
            else:
                obj.hide_viewport = False
                obj.hide_render = False

        # 3Dビューを再描画して表示状態を更新
        if context.area:
            context.area.tag_redraw()

        self.report({'INFO'}, f"{hidden_count}個のオブジェクトを隠しました")
        return {'FINISHED'}

classes = (
    SI_OT_toggle_hide,
    SI_OT_Show_Hidden_Objects,
    SI_OT_Hide_Unselected,
)

def register():
    register_properties()
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    unregister_properties()
    # キーマップアイテム解除
    for km, kmi in addon_keymaps:
        try:
            km.keymap_items.remove(kmi)
        except:
            pass
    addon_keymaps.clear()
