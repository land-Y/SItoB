# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

#参考先を改造
#https://github.com/K-410/blender-scripts/blob/master/2.8/toggle_hide.py


import bpy



class OUTLINER_OT_si_toggle_hide(bpy.types.Operator):
    bl_idname = "outliner.si_toggle_hide"
    bl_label = "si Toggle Hide"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        objs = bpy.context.view_layer.objects
        sel_objs = {o for o in objs if o.select_get()}
        hid_objs = {o for o in objs if o.hide_viewport == True}

        if context.area.type == 'OUTLINER':
            #アウトライナー上で実行すれば、ハイド中でもオブジェクトビューのトグルができる
            OutList = []
            for item in context.selected_ids:
                if item.bl_rna.identifier == "Object":
                    OutList.append(item.name)

            for o in OutList:
                oBlool = bpy.data.objects[o].hide_render
                print(oBlool)
                bpy.data.objects[o].hide_render = not oBlool
                bpy.data.objects[o].hide_viewport = not  oBlool
        else:
            #ビューポート中では以下のスクリプトが実行される
            if len(sel_objs) == 0 :
                for o in hid_objs:
                    o.hide_viewport = False
                    o.hide_render = False
                for o in hid_objs:
                    o.select_set(True)

            else:
                for o in sel_objs:
                    o.hide_viewport = True
                    o.hide_render = True
        return {'FINISHED'}