import bpy
from bpy.props import StringProperty, BoolProperty
import addon_utils
from functools import lru_cache

addon_keymaps = []

# --- 設定 ---
prop_name = "cvELD_SItoBHide"
scene_name = "Scene"
# --- 設定ここまで ---

# カスタムプロパティの登録
def register_properties():
    bpy.types.Scene.cvELD_SItoBHide = StringProperty(
        name="cvELD_SItoBHide",
        description="非表示オブジェクトのリスト",
        default=""
    )
    # 選択の非表示設定用のプロパティは削除（アドオン設定に移動）

def unregister_properties():
    del bpy.types.Scene.cvELD_SItoBHide
    # si_use_hide_setプロパティの削除は不要になりました

# キャッシュを使用してアドオン設定取得を高速化
@lru_cache(maxsize=1)
def get_addon_preferences():
    addon_name = "cvELD_SItoB"
    addon = next((a for a in addon_utils.modules() if a.bl_info['name'] == addon_name), None)
    if addon:
        return bpy.context.preferences.addons[addon.bl_info['name']].preferences
    return None

# 表示設定を取得する関数（キャッシュ対応）
def get_visibility_settings():
    prefs = get_addon_preferences()
    if prefs:
        return (
            prefs.si_use_hide_viewport,
            prefs.si_use_hide_set,
            prefs.si_use_hide_render,
            prefs.si_use_outliner_restriction
        )
    # デフォルト値（設定が見つからない場合）
    return True, True, True, True

# 全てのアウトライナー領域の制限アイコンを表示する
def show_outliner_restriction_icons():
    # 全てのスクリーンを検索
    for screen in bpy.data.screens:
        # 各スクリーン内のアウトライナー領域を検索
        for area in screen.areas:
            if area.type == 'OUTLINER':
                for space in area.spaces:
                    if space.type == 'OUTLINER':
                        # 表示制限アイコンを有効化
                        space.show_restrict_column_hide = True        # 目のアイコン（非表示）
                        space.show_restrict_column_viewport = True    # ビューポート表示制限
                        space.show_restrict_column_render = True      # レンダー表示制限

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
        # 表示設定を取得（一度だけ取得してパフォーマンス向上）
        use_hide_viewport, use_hide_set, use_hide_render, use_outliner_restriction = get_visibility_settings()

        # アウトライナーの制限切り替え機能が有効な場合、全てのアウトライナーの制限アイコンを表示
        if use_outliner_restriction:
            show_outliner_restriction_icons()

        # OUTLINER での処理（より効率的に）
        if context.area.type == 'OUTLINER':
            selected_objs = [bpy.data.objects[item.name] for item in context.selected_ids 
                             if item.bl_rna.identifier == "Object" and item.name in bpy.data.objects]
            
            # 一括で処理して個別の条件チェックを削減
            for obj in selected_objs:
                if use_hide_viewport:
                    new_state = not obj.hide_viewport
                    obj.hide_viewport = new_state
                if use_hide_render:
                    obj.hide_render = new_state if use_hide_viewport else not obj.hide_render
                if use_hide_set:
                    obj.hide_set(new_state if use_hide_viewport else not obj.visible_get())
            
            context.area.tag_redraw()
            return {'FINISHED'}

        # VIEW_3D での処理の最適化
        target_scene = bpy.data.scenes.get(scene_name)
        if not target_scene:
            self.report({'ERROR'}, f"シーン '{scene_name}' が見つかりません。")
            return {'CANCELLED'}

        # 選択されたオブジェクトがある場合の処理（非表示）
        selected_objects = context.selected_objects
        if selected_objects:
            # 名前のリストをまとめて作成
            object_names = [obj.name for obj in selected_objects]
            
            # 表示状態の一括変更（ループ内での条件チェックを削減）
            for obj in selected_objects:
                if use_hide_viewport:
                    obj.hide_viewport = True
                if use_hide_render:
                    obj.hide_render = True
                if use_hide_set:
                    obj.hide_set(True)

            # シーンプロパティを更新（一度だけの文字列処理）
            target_scene[prop_name] = ",".join(object_names)

            # 選択解除（オブジェクトモードの場合のみ）
            if context.mode == 'OBJECT':
                bpy.ops.object.select_all(action='DESELECT')

        # 選択されたオブジェクトがない場合の処理（表示）
        else:
            if prop_name in target_scene:
                value_string = target_scene.get(prop_name, "")
                if value_string:
                    # 名前の一括処理
                    names_to_unhide = [name.strip() for name in value_string.split(',') if name.strip()]
                    
                    if names_to_unhide and context.mode == 'OBJECT':
                        bpy.ops.object.select_all(action='DESELECT')
                        
                        # 事前に存在するオブジェクトのみフィルタリング
                        valid_objects = []
                        for obj_name in names_to_unhide:
                            obj = bpy.data.objects.get(obj_name)
                            if obj:
                                if use_hide_viewport:
                                    obj.hide_viewport = False
                                if use_hide_render:
                                    obj.hide_render = False
                                if use_hide_set:
                                    obj.hide_set(False)
                                valid_objects.append(obj)
                        
                        # 選択処理を一度にまとめる
                        if valid_objects:
                            context.view_layer.objects.active = valid_objects[0]
                            for obj in valid_objects:
                                obj.select_set(True)

        # 表示を更新（必要な場合のみ）
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
        # 表示設定を取得（アウトライナー制限だけ使用）
        _, _, _, use_outliner_restriction = get_visibility_settings()
        
        # アウトライナーの制限切り替え機能が有効な場合、全てのアウトライナーの制限アイコンを表示
        if use_outliner_restriction:
            show_outliner_restriction_icons()
        
        # オブジェクトを一度のみ取得し、繰り返し使用（効率的）
        all_objects = [obj for obj in bpy.data.objects if obj.users > 0]
        
        if context.area.type == 'OUTLINER':
            # アウトライナーの制限切り替え機能部分は削除（上のshow_outliner_restriction_icons関数で対応）
            
            # 一度のループですべての処理を行う
            for obj in all_objects:
                obj.hide_viewport = False
                obj.hide_render = False
                obj.hide_set(False)
            
            context.area.tag_redraw()
            return {'FINISHED'}

        # VIEW_3D の処理
        selected_in_view3d = context.area.type == 'VIEW_3D'
        
        # 非表示オブジェクトのみをフィルタリング（処理対象を減らす）
        hidden_objects = [obj for obj in all_objects if obj.hide_viewport or obj.hide_render]
        
        for obj in hidden_objects:
            obj.hide_viewport = False
            obj.hide_render = False
            obj.hide_set(False)
            # 選択は条件付きで実行
            if selected_in_view3d:
                obj.select_set(True)

        self.report({'INFO'}, f"{len(hidden_objects)}個のオブジェクトを表示しました")
        return {'FINISHED'}

class SI_OT_Hide_Unselected(bpy.types.Operator):
    bl_idname = "object.si_hide_unselected"
    bl_label = "SI Hide Unselected"
    bl_description = "hide_viewport"
    bl_options = {'REGISTER', 'UNDO'}

    def __init__(self, *args, **kwargs):
        bpy.types.Operator.__init__(self, *args, **kwargs)

    @classmethod
    def poll(cls, context):
        return context.area.type in {'VIEW_3D', 'OUTLINER'}

    def execute(self, context):
        # 表示設定を一度だけ取得
        use_hide_viewport, use_hide_set, use_hide_render, use_outliner_restriction = get_visibility_settings()
        
        # アウトライナーの制限切り替え機能が有効な場合、全てのアウトライナーの制限アイコンを表示
        if use_outliner_restriction:
            show_outliner_restriction_icons()
        
        # すべてのオブジェクトをリストとして取得（効率的にアクセス）
        all_objects = [obj for obj in bpy.data.objects if obj.users > 0]
        
        if context.area.type == 'OUTLINER':
            # アウトライナーの制限切り替え機能部分は削除（上のshow_outliner_restriction_icons関数で対応）
            
            # アウトライナーで選択されたオブジェクトのセットを作成（高速検索用）
            selected_objs = {bpy.data.objects[item.name] for item in context.selected_ids 
                            if item.bl_rna.identifier == "Object" and item.name in bpy.data.objects}
            
            # 隠したオブジェクトのカウント
            hidden_count = 0
            
            # 選択/非選択で分けて一括処理
            for obj in all_objects:
                is_selected = obj in selected_objs
                
                # 非選択オブジェクトを隠す
                if not is_selected:
                    if use_hide_viewport:
                        obj.hide_viewport = True
                    if use_hide_render:
                        obj.hide_render = True
                    if use_hide_set:
                        obj.hide_set(True)
                    hidden_count += 1
                # 選択オブジェクトを表示
                else:
                    if use_hide_viewport:
                        obj.hide_viewport = False
                    if use_hide_render:
                        obj.hide_render = False
                    if use_hide_set:
                        obj.hide_set(False)
            
            context.area.tag_redraw()
            self.report({'INFO'}, f"{hidden_count}個のオブジェクトを隠しました")
            return {'FINISHED'}

        # VIEW_3D での処理
        # 選択オブジェクトのセットを作成（高速検索用）
        selected_objects = set(context.selected_objects)
        hidden_count = 0

        # 選択/非選択で分けて一括処理
        for obj in all_objects:
            if obj not in selected_objects:
                if use_hide_viewport:
                    obj.hide_viewport = True
                if use_hide_render:
                    obj.hide_render = True
                if use_hide_set:
                    obj.hide_set(True)
                hidden_count += 1
            else:
                if use_hide_viewport:
                    obj.hide_viewport = False
                if use_hide_render:
                    obj.hide_render = False
                if use_hide_set:
                    obj.hide_set(False)

        # 必要な場合のみ再描画
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
    # キャッシュをクリア
    get_addon_preferences.cache_clear()

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
    # キャッシュをクリア
    get_addon_preferences.cache_clear()
