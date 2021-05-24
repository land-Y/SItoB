# -*- coding: utf-8 -*-
import os
import bpy

class cvELD_RIG_Icon(object):
    """
    BendyRIG用アイコンをicon.blendファイルから取り出す。
    動作確認 blender version: 2.91.2
    """
    def createCollection(self, collectionName="collection", hide=False):
        """指定名のコレクションがあれば無視、なければ生成。"""
        if collectionName not in bpy.data.collections:
            collectionObj = bpy.data.collections.new(collectionName)
            bpy.context.scene.collection.children.link(collectionObj)
            if hide == True:
                collectionObj.hide_viewport = True
            return collectionObj
        else:
            return bpy.data.collections[collectionName]

    def createEmpty(self, emptyName="cs_grp_sub", collection=None):
        """指定名のEmptyがあれば無視、なければ生成。"""
        if emptyName not in bpy.data.objects:
            empty = bpy.data.objects.new("Empty", None)
            empty.name = emptyName
            empty.empty_display_size = 0.01
            empty.empty_display_type = "PLAIN_AXES"
            if collection == None or not type(collection) == bpy.types.Collection:
                bpy.context.collection.objects.link(empty)
            else :
                collection.objects.link(empty)
            return empty

        else:
            return bpy.data.objects[emptyName]

    def LoadShape(self, shapeName="cs_SiCube", emptyName="cs_grp_sub", collectionName="cs_grp_Hack"):
        """iconからシェイプとなるオブジェクトを読み込む"""
        collecttionObj = self.createCollection(collectionName, True)
        empty = self.createEmpty(emptyName, collecttionObj)
        selfDir = os.path.dirname(__file__)
        filepath = os.path.join(selfDir, "icon", "icon.blend")
        if not os.path.isfile(filepath):
            raise IOError("icon.blendがありません。")
        if bpy.data.objects.get(shapeName) == None:
            with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
                data_to.objects = [name for name in data_from.objects if name.startswith(shapeName)]
            for obj in data_to.objects:
                collecttionObj.objects.link(obj)
                obj.parent = bpy.data.objects[empty.name]
