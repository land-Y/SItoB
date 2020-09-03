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

    @classmethod
    def poll(self, context):
        ar = context.screen.areas
        __class__.area = next(
            (a for a in ar if a.type == 'OUTLINER'), None)
        return __class__.area

    def execute(self, context):
        objs = context.view_layer.objects
        sel_objs = {o for o in objs if o.select_get()}
        hid_objs = {o for o in objs if o.hide_get()}

        # Hide selected
        for o in sel_objs:
            o.hide_set(True)

        # Unhide hidden
        for o in hid_objs:
            o.hide_set(False)
        for o in hid_objs:
            o.select_set(True)
        # Select objects marked in outliner
        bpy.ops.outliner.object_operation(
            {'area': __class__.area}, type='SELECT')

        # Re-hide others
        for o in hid_objs:
            if not o.select_get():
                o.hide_set(True)
        return {'FINISHED'}
