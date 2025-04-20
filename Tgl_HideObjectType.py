import bpy
from bpy.props import StringProperty
from bpy.types import Collection

# シーンにカスタムプロパティを追加
def register_properties():
    Collection.si_hidden_objects = StringProperty(
        name="SItoBHide",
        description="List of hidden objects",
        default=""
    )

def unregister_properties():
    if hasattr(Collection, 'si_hidden_objects'):
        delattr(Collection, 'si_hidden_objects')

def Tgl_HideOverray():
    ovl = bpy.context.space_data.overlay
    ovl.show_extras = not ovl.show_extras
    ovl.show_relationship_lines = not ovl.show_relationship_lines
    ovl.show_object_origins = not ovl.show_object_origins
    ovl.show_motion_paths = not ovl.show_motion_paths
    ovl.show_bones = not ovl.show_bones
    ovl.show_cursor = not ovl.show_cursor
    ovl.show_annotation = not ovl.show_annotation

def All_HideOverray():
    ovl = bpy.context.space_data.overlay
    ovl.show_extras = False
    ovl.show_relationship_lines = False
    ovl.show_object_origins_all = False
    ovl.show_object_origins = False
    ovl.show_motion_paths = False
    ovl.show_bones = False
    ovl.show_cursor = False
    ovl.show_annotation = False

def get_hidden_objects_list():
    """隠れているオブジェクトのリストを取得"""
    master_collection = bpy.context.scene.collection
    if hasattr(master_collection, 'si_hidden_objects') and master_collection.si_hidden_objects:
        return master_collection.si_hidden_objects.split(',')
    return []

def update_hidden_objects_list(hidden_objects):
    """隠れているオブジェクトのリストを更新"""
    master_collection = bpy.context.scene.collection
    if hidden_objects:
        master_collection.si_hidden_objects = ','.join(hidden_objects)
    else:
        if hasattr(master_collection, 'si_hidden_objects'):
            delattr(master_collection, 'si_hidden_objects')

def toggle_selected_objects_visibility():
    """選択中のオブジェクトの表示/非表示をトグル"""
    # 選択中のオブジェクトを取得
    selected_objects = [obj for obj in bpy.context.selected_objects]
    
    if not selected_objects:
        # 選択がなければ、保存されたオブジェクトを表示
        hidden_objects = get_hidden_objects_list()
        if hidden_objects:
            for obj_name in hidden_objects:
                obj = bpy.data.objects.get(obj_name)
                if obj:
                    obj.hide_set(False)
            # プロパティを削除
            update_hidden_objects_list([])
    else:
        # 選択がある場合
        hidden_objects = get_hidden_objects_list()
        
        # 選択中のオブジェクトを非表示に
        for obj in selected_objects:
            obj.hide_set(True)
            if obj.name not in hidden_objects:
                hidden_objects.append(obj.name)
        
        # 非表示リストを更新
        update_hidden_objects_list(hidden_objects)

class Tgl_HideObjectType_OT_object(bpy.types.Operator):
    bl_idname = "view3d.tgl_hide_object_type"
    bl_label = "Toggle Hide Object Type"
    
    def __init__(self, *args, **kwargs):
        bpy.types.Operator.__init__(self, *args, **kwargs)
 
    def execute(self, context):
        # オーバーレイの表示/非表示をトグル
        ovl = bpy.context.space_data.overlay
        if ovl.show_bones == True:
            All_HideOverray()
        else:
            Tgl_HideOverray()
        
        # 選択中のオブジェクトの表示/非表示をトグル
        toggle_selected_objects_visibility()
        
        return {'FINISHED'}

classes = (
    Tgl_HideObjectType_OT_object,
)
