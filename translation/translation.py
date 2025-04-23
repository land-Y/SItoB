import os
import csv
import codecs
import bpy

# translation.csvから辞書を読み込む
def GetTranslation():
    dict = {}
    path = os.path.join(os.path.dirname(__file__), "translation.csv")
    if os.path.isfile(path):
        with codecs.open(path, "r", "utf-8") as f:
            reader = csv.reader(f)
            dict["ja_JP"] = {}
            for row in reader:
                if row:
                    for context in bpy.app.translations.contexts:
                        dict["ja_JP"][(context, row[1].replace("\\n", "\n"))] = row[0].replace("\\n", "\n")
    return dict

# アドオン有効化時に呼び出す登録関数
def register():
    translation = GetTranslation()
    if translation:
        bpy.app.translations.register("cvELD_SItoB", translation)

# アドオン無効化時に呼び出す解除関数
def unregister():
    try:
        bpy.app.translations.unregister("cvELD_SItoB")
    except:
        print("Untranslation failed.") 