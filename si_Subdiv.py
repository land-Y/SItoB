import bpy
from bpy.props import BoolProperty, IntProperty

def oSm(b):
    for o in bpy.context.selected_objects:
        if o.type == 'MESH':
            bpy.ops.object.shade_smooth()
            # use_auto_smoothの代わりにautosmooth_angle属性を使用
            if not hasattr(o.data, "autosmooth_angle"):
                print(f"Warning: {o.name} does not have autosmooth_angle attribute")
            else:
                o.data.use_auto_smooth = True
                o.data.autosmooth_angle = b
        elif o.type == 'CURVE':
            o.data.splines[0].use_smooth = True

def si_active_normal():
    oCM = bpy.context.object.mode
    if oCM == 'OBJECT':
        oSm(1.0472)
    else:
        bpy.ops.object.mode_set(mode='OBJECT')
        oSm(1.0472)
        bpy.ops.object.mode_set(mode=oCM)

def oDeln():
    for o in bpy.context.selected_objects:
        if o.type == 'MESH':
            bpy.ops.object.shade_flat()
            # use_auto_smoothの代わりにautosmooth_angle属性を使用
            if hasattr(o.data, "autosmooth_angle"):
                o.data.use_auto_smooth = False
                o.data.autosmooth_angle = 0.523599
        elif o.type == 'CURVE':
            o.data.splines[0].use_smooth = False

def si_noactive_normal():
    oCM = bpy.context.object.mode
    if oCM == 'OBJECT':
        oDeln()
    else:
        bpy.ops.object.mode_set(mode='OBJECT')
        oDeln()
        bpy.ops.object.mode_set(mode=oCM)

# 以下の関数は変更なし
def oDel():
    for o in bpy.context.selected_objects:
        for m in o.modifiers:
            if(m.type == "SUBSURF"):
                o.modifiers.remove(m)
    return

def delete_subdiv():
    oCM = bpy.context.object.mode
    if oCM == 'OBJECT':
        oDel()
    else:
        bpy.ops.object.mode_set(mode='OBJECT')
        oDel()
        bpy.ops.object.mode_set(mode=oCM)

def GetModifires():
    for i in bpy.context.selected_objects:
        num = len(i.modifiers)
        return num

def xsisubdiv(oL, oAdd, maxSubdivCount=3):
    for o in bpy.context.selected_objects:
        if o.type == 'MESH' or o.type == 'CURVE':
            if o.modifiers.get("SI_subdiv") == None:
                for m in o.modifiers:
                    if(m.type == "SUBSURF"):
                        o.modifiers.remove(m)
                oLevel = o.modifiers.new("SI_subdiv", type="SUBSURF")
                oLevel.render_levels = oL
                oLevel.levels = oL
                o.modifiers["SI_subdiv"].show_on_cage = True
                print(o.name + " add SI_subdiv,Set CageMode")
            else:
                for m in o.modifiers:
                    if(m.type == "SUBSURF" or m.name == "SI_subdiv"):
                        if m.render_levels < maxSubdivCount:
                            m.render_levels = m.render_levels + oAdd
                            m.levels = m.levels + oAdd
                            print(o.name + " subdiv level " + str(m.levels))
    bpy.context.scene.frame_current = bpy.context.scene.frame_current
    return

# オペレータークラスは変更なし
class si_del_subdiv_OT_object(bpy.types.Operator):
    bl_idname = "object.si_del_sudiv"
    bl_label = "Delete Subdivision"
    bl_description = "Subdivisions like Softimage"
    bl_options = {'REGISTER', 'UNDO'}

    def __init__(self, *args, **kwargs):
        bpy.types.Operator.__init__(self, *args, **kwargs)

    def execute(self, context):
        delete_subdiv()
        si_noactive_normal()
        return {'FINISHED'}

class si_add_subdiv_OT_object(bpy.types.Operator):
    bl_idname = "object.si_add_sudiv"
    bl_label = "Add Subdivision"
    bl_description = "Subdivisions like Softimage"
    bl_options = {'REGISTER', 'UNDO'}

    def __init__(self, *args, **kwargs):
        bpy.types.Operator.__init__(self, *args, **kwargs)

    si_moveindex : BoolProperty(default=True, name="Move Modifire", description="Move Modifire")
    maxSubdivCountInt : IntProperty(default=3, name="Max Subdivisions", description="Max Subdivisions")

    def execute(self, context):
        si_active_normal()
        xsisubdiv(1, 1, maxSubdivCount=self.maxSubdivCountInt)

        if self.si_moveindex:
            num = GetModifires()
            bpy.ops.object.modifier_move_to_index(modifier="SI_subdiv", index=num - 1)
        return {'FINISHED'}

class si_minus_subdiv_OT_object(bpy.types.Operator):
    bl_idname = "object.si_minus_subdiv"
    bl_label = "Subtract subdivision"
    bl_description = "Subdivisions like Softimage"
    bl_options = {'REGISTER', 'UNDO'}

    def __init__(self, *args, **kwargs):
        bpy.types.Operator.__init__(self, *args, **kwargs)

    def execute(self, context):
        xsisubdiv(1, -1, maxSubdivCount=99)
        return {'FINISHED'}

classes = (
    si_del_subdiv_OT_object,
    si_add_subdiv_OT_object,
    si_minus_subdiv_OT_object,
)
