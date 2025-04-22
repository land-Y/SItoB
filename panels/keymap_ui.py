# -*- coding: utf-8 -*-
import bpy
# import rna_keymap_ui


def _indented_layout(layout, level):
    indentpx = 16
    if level == 0:
        level = 0.0001
    indent = level * indentpx / bpy.context.region.width
    split = layout.split(factor=indent)
    col = split.column()
    col = split.column()
    return col

def draw_kmi(display_keymaps, kc, km, kmi, layout, level):
    map_type = kmi.map_type
    col = _indented_layout(layout, level)
    # show_expandedフラグに応じてボックス制御
    if kmi.show_expanded:
        col = col.column(align=True)
        box = col.box()
    else:
        box = col.column()
    split = box.split()
    # ヘッダー部分
    row = split.row(align=True)
    row.prop(kmi, "show_expanded", text="", emboss=False)
    row.prop(kmi, "active", text="", emboss=False)
    if km.is_modal:
        row.separator()
        row.prop(kmi, "propvalue", text="")
    else:
        row.label(text=kmi.name)
    # イベントタイプ表示
    row = split.row()
    row.prop(kmi, "map_type", text="")
    if map_type in {"KEYBOARD", "MOUSE", "NDOF"}:
        row.prop(kmi, "type", text="", full_event=True)
    elif map_type == "TWEAK":
        subrow = row.row()
        subrow.prop(kmi, "type", text="")
        subrow.prop(kmi, "value", text="")
    elif map_type == "TIMER":
        row.prop(kmi, "type", text="")
    # 詳細オプション
    if kmi.show_expanded:
        box = col.box()
        split = box.split(factor=0.4)
        sub = split.row()
        if km.is_modal:
            sub.prop(kmi, "propvalue", text="")
        else:
            sub.prop(kmi, "idname", text="")
        if map_type not in {"TEXTINPUT", "TIMER"}:
            subcol = split.column()
            subrow = subcol.row(align=True)
            if map_type == "KEYBOARD":
                subrow.prop(kmi, "type", text="", event=True)
                subrow.prop(kmi, "value", text="")
                subrow_repeat = subrow.row(align=True)
                subrow_repeat.active = kmi.value in {"ANY", "PRESS"}
                subrow_repeat.prop(kmi, "repeat", text="Repeat")
            elif map_type in {"MOUSE", "NDOF"}:
                subrow.prop(kmi, "type", text="")
                subrow.prop(kmi, "value", text="")
            subrow = subcol.row()
            subrow.scale_x = 0.75
            subrow.prop(kmi, "any", toggle=True)
            subrow.prop(kmi, "shift", toggle=True)
            subrow.prop(kmi, "ctrl", toggle=True)
            subrow.prop(kmi, "alt", toggle=True)
            subrow.prop(kmi, "oskey", text="Cmd", toggle=True)
            subrow.prop(kmi, "key_modifier", text="", event=True)
    return box

# 選択の非表示関連コマンドを識別するための定数
HIDE_COMMANDS = {'object.si_toggle_hide', 'object.si_show_hidden_objects', 'object.si_hide_unselected'}

# 選択の非表示関連のキーマップのみを表示する関数
def draw_hide_keymap(layout, context, keymap_list):
    wm = context.window_manager
    kc = wm.keyconfigs.addon
    seen = set()

    for km_add, kmi_add in keymap_list:
        if not km_add or not kmi_add:
            continue

        # 選択の非表示関連コマンドのみ処理
        if not hasattr(kmi_add, 'idname') or kmi_add.idname not in HIDE_COMMANDS:
            continue

        # 重複をスキップ
        if kmi_add.idname in seen:
            continue
        seen.add(kmi_add.idname)

        # 対応するKeyMapオブジェクトを取得
        km = next((km_tmp for km_tmp in kc.keymaps
                   if km_tmp.name == km_add.name and km_tmp.space_type == km_add.space_type), None)
        if not km:
            continue

        # キーマップアイテムを描画
        layout.context_pointer_set("keyconfig", kc)
        layout.context_pointer_set("keymap", km)
        layout.context_pointer_set("keymap_item", kmi_add)
        draw_kmi([], kc, km, kmi_add, layout, 0)

def draw_keymap(layout, context, keymap_list):
    box = layout.box()
    col = box.column()
    col.label(text="Keymap List:", icon="KEYINGSET")

    wm = context.window_manager
    kc = wm.keyconfigs.addon  # アドオン用キー設定を取得
    old_km_name = ""

    for i, (km_add, kmi_add) in enumerate(keymap_list):
        if not km_add or not kmi_add:
            continue
            
        # 選択の非表示関連コマンドはスキップ（別の関数で表示）
        if hasattr(kmi_add, 'idname') and kmi_add.idname in HIDE_COMMANDS:
            continue

        # 対応するKeyMapオブジェクトを取得
        km = None
        for km_tmp in kc.keymaps:
            if km_tmp.name == km_add.name and km_tmp.space_type == km_add.space_type:
                km = km_tmp
                break
        if not km:
            continue

        # キーマップアイテムを描画
        col.context_pointer_set("keyconfig", kc)
        col.context_pointer_set("keymap", km)
        col.context_pointer_set("keymap_item", kmi_add)
        draw_kmi([], kc, km, kmi_add, col, 0)

        # キーマップ名が変わったらラベル表示
        if km.name != old_km_name:
            col.label(text=km.name, icon="DOT")
            old_km_name = km.name

        col.separator() 