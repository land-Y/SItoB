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

def draw_keymap(layout, context, keymap_list):
    box = layout.box()
    col = box.column()
    col.label(text="Keymap List:", icon="KEYINGSET")

    wm = context.window_manager
    kc = wm.keyconfigs.addon  # アドオン用キー設定を取得
    old_km_name = ""
    hide_commands = {'object.si_toggle_hide', 'object.si_show_hidden_objects', 'object.si_hide_unselected'}
    hide_group_header_drawn = False
    hide_group_separator_drawn = False

    # グループ内の最後のアイテムを事前に特定
    last_hide_command_index = -1
    for i, (_, kmi_add) in enumerate(keymap_list):
        if kmi_add and hasattr(kmi_add, 'idname') and kmi_add.idname in hide_commands:
            last_hide_command_index = i

    for i, (km_add, kmi_add) in enumerate(keymap_list):
        if not km_add or not kmi_add:
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
            if hide_group_header_drawn and not hide_group_separator_drawn:
                col.separator()
                hide_group_separator_drawn = True
            col.label(text=km.name, icon="DOT")
            old_km_name = km.name
            hide_group_header_drawn = False
            hide_group_separator_drawn = False

        is_hide_command = hasattr(kmi_add, 'idname') and kmi_add.idname in hide_commands

        # 「選択の非表示」グループのヘッダーを描画
        if is_hide_command and not hide_group_header_drawn:
            col.separator()
            col.label(text="選択の非表示:")
            hide_group_header_drawn = True
            hide_group_separator_drawn = False

        is_last_item_in_hide_group = (i == last_hide_command_index)
        if is_last_item_in_hide_group and not hide_group_separator_drawn:
            col.separator()
        elif not is_hide_command:
            next_is_hide_header = False
            if i + 1 < len(keymap_list):
                _, next_kmi = keymap_list[i+1]
                if next_kmi and hasattr(next_kmi, 'idname') and next_kmi.idname in hide_commands and not hide_group_header_drawn:
                    next_is_hide_header = True
            if not next_is_hide_header:
                col.separator()

    # ループ後の仕上げ区切り
    if hide_group_header_drawn and not hide_group_separator_drawn:
        col.separator() 