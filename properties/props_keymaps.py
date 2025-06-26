# -*- coding: utf-8 -*-
import bpy

# キーマップリストの定義
keymap_Softimage = []
keymap_RigTools = []
keymap_OtherTools = []

# キーマップ辞書（サンプルコード参考）
keymapDict = {}
keyMapList = [keymapDict]

def addKeyMap(operatorIdname, key, state, dict, shift=False, ctrl=False, alt=False, keyMapName="3D View", spaceType="VIEW_3D"):
    """キーマップを追加する関数（ユーザー設定を優先するよう修正）"""
    windowManager = bpy.context.window_manager

    # アドオン用キーマップ
    addon_keyMap = windowManager.keyconfigs.addon.keymaps.new(name=keyMapName, space_type=spaceType)
    addon_keyMapItem = addon_keyMap.keymap_items.new(operatorIdname, key, state, shift=shift, ctrl=ctrl, alt=alt)
    dict[operatorIdname] = (addon_keyMap, addon_keyMapItem)

    # ユーザー用キーマップに同じ設定が存在するかチェック
    user_keyMap = windowManager.keyconfigs.user.keymaps.find(keyMapName, space_type=spaceType)
    user_has_same = False
    if user_keyMap:
        for kmi in user_keyMap.keymap_items:
            if (
                kmi.idname == operatorIdname and
                kmi.type == key and
                kmi.value == state and
                kmi.shift == shift and
                kmi.ctrl == ctrl and
                kmi.alt == alt
            ):
                user_has_same = True
                break
    # ユーザー設定がなければ新規登録
    if not user_has_same:
        if not user_keyMap:
            user_keyMap = windowManager.keyconfigs.user.keymaps.new(name=keyMapName, space_type=spaceType)
        user_keyMapItem = user_keyMap.keymap_items.new(operatorIdname, key, state, shift=shift, ctrl=ctrl, alt=alt)
    # 既にユーザー設定があれば何もしない

    return (addon_keyMap, addon_keyMapItem)

def getKeyMapAndKeyItem(operatorIdname):
    """キーマップとキーアイテムを取得する関数（サンプルコード参考）"""
    keyMapName = "3D View"
    spaceType = "VIEW_3D"

    # 特別なケース: Outliner関連コマンド
    if operatorIdname in ['object.si_toggle_hide', 'object.si_show_hidden_objects', 'object.si_hide_unselected']:
        # Outlinerキーマップも確認
        for space_name, space_type in [("3D View", "VIEW_3D"), ("Outliner", "OUTLINER")]:
            k_config = bpy.context.window_manager.keyconfigs.user
            k_map = k_config.keymaps.find(space_name, space_type=space_type)
            
            if k_map:
                for keyDic in keyMapList:
                    if operatorIdname in keyDic:
                        _, add_k_item = keyDic[operatorIdname]
                        for k_item in k_map.keymap_items:
                            if k_item.name == add_k_item.name:
                                return (k_map, k_item)
    
    # Weight Paint関連コマンド
    elif operatorIdname in ['view3d.sel_wheigtmaskmode', 'view3d.sel_wheigtmaskmode_tgl']:
        keyMapName = "Weight Paint"
        spaceType = "VIEW_3D"
    
    k_config = bpy.context.window_manager.keyconfigs.user
    k_map = k_config.keymaps.find(keyMapName, space_type=spaceType)
    
    for keyDic in keyMapList:
        if operatorIdname in keyDic:
            _, add_k_item = keyDic[operatorIdname]
            if k_map:
                for k_item in k_map.keymap_items:
                    if k_item.name == add_k_item.name:
                        return (k_map, k_item)
    
    # 見つからない場合はアドオンキーマップから取得
    for keyDic in keyMapList:
        if operatorIdname in keyDic:
            keyMap, keyMapItem = keyDic[operatorIdname]
            return (keyMap, keyMapItem)
    
    return (None, None)

# ホットキー登録関数
def register_keymaps():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon

    if not kc:
        return

    # Softimageキーマップ
    km, kmi = addKeyMap('object.si_del_sudiv', 'NUMPAD_MINUS', 'PRESS', keymapDict, shift=True)
    keymap_Softimage.append((km, kmi))

    km, kmi = addKeyMap('object.si_add_sudiv', 'NUMPAD_PLUS', 'PRESS', keymapDict)
    keymap_Softimage.append((km, kmi))

    km, kmi = addKeyMap('object.si_minus_subdiv', 'NUMPAD_MINUS', 'PRESS', keymapDict)
    keymap_Softimage.append((km, kmi))

    km, kmi = addKeyMap('object.si_resetsrt', 'R', 'PRESS', keymapDict, ctrl=True, shift=True)
    keymap_Softimage.append((km, kmi))

    km, kmi = addKeyMap('object.si_movecomponent', 'M', 'PRESS', keymapDict)
    keymap_Softimage.append((km, kmi))

    km, kmi = addKeyMap('object.si_movecomponent1', 'T', 'ANY', keymapDict)
    keymap_Softimage.append((km, kmi))

    km, kmi = addKeyMap('object.si_movecomponent2', 'E', 'ANY', keymapDict)
    keymap_Softimage.append((km, kmi))

    km, kmi = addKeyMap('object.si_movecomponent3', 'U', 'ANY', keymapDict)
    keymap_Softimage.append((km, kmi))

    # 3D View用キー登録
    km, kmi = addKeyMap('object.si_toggle_hide', 'H', 'PRESS', keymapDict)
    keymap_Softimage.append((km, kmi))

    km, kmi = addKeyMap('object.si_show_hidden_objects', 'H', 'PRESS', keymapDict, shift=True)
    keymap_Softimage.append((km, kmi))

    km, kmi = addKeyMap('object.si_hide_unselected', 'H', 'PRESS', keymapDict, alt=True)
    keymap_Softimage.append((km, kmi))

    # Outliner用キー登録
    km, kmi = addKeyMap('object.si_toggle_hide', 'H', 'PRESS', keymapDict, keyMapName='Outliner', spaceType='OUTLINER')
    keymap_Softimage.append((km, kmi))

    km, kmi = addKeyMap('object.si_show_hidden_objects', 'H', 'PRESS', keymapDict, shift=True, keyMapName='Outliner', spaceType='OUTLINER')
    keymap_Softimage.append((km, kmi))

    km, kmi = addKeyMap('object.si_hide_unselected', 'H', 'PRESS', keymapDict, alt=True, keyMapName='Outliner', spaceType='OUTLINER')
    keymap_Softimage.append((km, kmi))

    # RigToolsキーマップ
    km, kmi = addKeyMap('object.gator_plus', 'G', 'PRESS', keymapDict, alt=True)
    keymap_RigTools.append((km, kmi))

    km, kmi = addKeyMap('object.gator_plus_deletevertex_modifier', 'G', 'PRESS', keymapDict, ctrl=True, shift=True, alt=True)
    keymap_RigTools.append((km, kmi))

    # Weight Paintキーマップ
    km, kmi = addKeyMap('view3d.sel_wheigtmaskmode', 'LEFTMOUSE', 'PRESS', keymapDict, ctrl=True, alt=True, keyMapName='Weight Paint', spaceType='VIEW_3D')
    keymap_RigTools.append((km, kmi))

    km, kmi = addKeyMap('view3d.sel_wheigtmaskmode_tgl', 'LEFTMOUSE', 'PRESS', keymapDict, shift=True, ctrl=True, alt=True, keyMapName='Weight Paint', spaceType='VIEW_3D')
    keymap_RigTools.append((km, kmi))

    # OtherToolsキーマップ
    km, kmi = addKeyMap('view3d.tgl_hide_object_type', 'Q', 'PRESS', keymapDict, ctrl=True)
    keymap_OtherTools.append((km, kmi))

    km, kmi = addKeyMap('object.separatecomponet_keep', 'D', 'PRESS', keymapDict, ctrl=True, alt=True)
    keymap_OtherTools.append((km, kmi))

    km, kmi = addKeyMap('object.knife_project_cut_through', 'N', 'PRESS', keymapDict, ctrl=True, alt=True)
    keymap_OtherTools.append((km, kmi))

    km, kmi = addKeyMap('view3d.clipbord_select_object', 'C', 'PRESS', keymapDict, ctrl=True, shift=True)
    keymap_OtherTools.append((km, kmi))

    km, kmi = addKeyMap('view3d.toggle_pivot_mode', 'D', 'PRESS', keymapDict)
    keymap_OtherTools.append((km, kmi))

def unregister_keymaps():
    # キーマップ辞書を使用してクリーンアップ（サンプルコード参考）
    for keyDic in keyMapList:
        for km, kmi in keyDic.values():
            try:
                km.keymap_items.remove(kmi)
            except:
                pass
    
    # 辞書をクリア
    for keyDic in keyMapList:
        keyDic.clear()

    keymap_Softimage.clear()
    keymap_RigTools.clear()
    keymap_OtherTools.clear() 