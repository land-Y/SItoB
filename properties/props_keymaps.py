# -*- coding: utf-8 -*-
import bpy

# キーマップリストの定義
keymap_Softimage = []
keymap_RigTools = []
keymap_OtherTools = []

# ホットキー登録関数
def register_keymaps():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon

    if not kc:
        return

    # Softimageキーマップ
    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new('object.si_del_sudiv', 'NUMPAD_MINUS', 'PRESS', shift=True)
    keymap_Softimage.append((km, kmi))

    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new('object.si_add_sudiv', 'NUMPAD_PLUS', 'PRESS')
    keymap_Softimage.append((km, kmi))

    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new('object.si_minus_subdiv', 'NUMPAD_MINUS', 'PRESS')
    keymap_Softimage.append((km, kmi))

    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new('object.si_resetsrt', 'R', 'PRESS', ctrl=True, shift=True)
    keymap_Softimage.append((km, kmi))

    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new('object.si_movecomponent', 'M', 'PRESS')
    keymap_Softimage.append((km, kmi))

    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new('object.si_movecomponent1', 'T', 'ANY')
    keymap_Softimage.append((km, kmi))

    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new('object.si_movecomponent2', 'E', 'ANY')
    keymap_Softimage.append((km, kmi))

    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new('object.si_movecomponent3', 'U', 'ANY')
    keymap_Softimage.append((km, kmi))

    # 3D View用キー登録
    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new('object.si_toggle_hide', 'H', 'PRESS')
    keymap_Softimage.append((km, kmi))

    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new('object.si_show_hidden_objects', 'H', 'PRESS', shift=True)
    keymap_Softimage.append((km, kmi))

    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new('object.si_hide_unselected', 'H', 'PRESS', alt=True)
    keymap_Softimage.append((km, kmi))

    # Outliner用キー登録
    km = kc.keymaps.new(name='Outliner', space_type='OUTLINER')
    kmi = km.keymap_items.new('object.si_toggle_hide', 'H', 'PRESS')
    keymap_Softimage.append((km, kmi))

    km = kc.keymaps.new(name='Outliner', space_type='OUTLINER')
    kmi = km.keymap_items.new('object.si_show_hidden_objects', 'H', 'PRESS', shift=True)
    keymap_Softimage.append((km, kmi))

    km = kc.keymaps.new(name='Outliner', space_type='OUTLINER')
    kmi = km.keymap_items.new('object.si_hide_unselected', 'H', 'PRESS', alt=True)
    keymap_Softimage.append((km, kmi))

    # RigToolsキーマップ
    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new('object.gator_plus', 'G', 'PRESS', alt=True)
    keymap_RigTools.append((km, kmi))

    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new('object.gator_plus_deletevertex_modifier', 'G', 'PRESS', ctrl=True, shift=True, alt=True)
    keymap_RigTools.append((km, kmi))

    # Weight Paintキーマップ
    km = kc.keymaps.new(name='Weight Paint', space_type='VIEW_3D')
    kmi = km.keymap_items.new('view3d.sel_wheigtmaskmode', 'LEFTMOUSE', 'PRESS', ctrl=True, alt=True)
    keymap_RigTools.append((km, kmi))

    km = kc.keymaps.new(name='Weight Paint', space_type='VIEW_3D')
    kmi = km.keymap_items.new('view3d.sel_wheigtmaskmode_tgl', 'LEFTMOUSE', 'PRESS', shift=True, ctrl=True, alt=True)
    keymap_RigTools.append((km, kmi))

    # OtherToolsキーマップ
    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new('view3d.tgl_hide_object_type', 'Q', 'PRESS', ctrl=True)
    keymap_OtherTools.append((km, kmi))

    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new('object.separatecomponet_keep', 'D', 'PRESS', ctrl=True, alt=True)
    keymap_OtherTools.append((km, kmi))

    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new('object.knife_project_cut_through', 'N', 'PRESS', ctrl=True, alt=True)
    keymap_OtherTools.append((km, kmi))

    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new('view3d.clipbord_select_object', 'C', 'PRESS', ctrl=True, shift=True)
    keymap_OtherTools.append((km, kmi))

    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new('view3d.toggle_pivot_mode', 'D', 'PRESS')
    keymap_OtherTools.append((km, kmi))

def unregister_keymaps():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon

    if kc:
        for km, kmi in keymap_Softimage + keymap_RigTools + keymap_OtherTools:
            try:
                km.keymap_items.remove(kmi)
            except:
                pass

    keymap_Softimage.clear()
    keymap_RigTools.clear()
    keymap_OtherTools.clear() 