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

# Copyright 2011, Ryan Inch

from bpy.types import PropertyGroup
from bpy.props import StringProperty

layer_collections = {}

collection_tree = []

expanded = []

max_lvl = 0
row_index = 0

def get_max_lvl():
    return max_lvl

def update_col_name(self, context):
    if self.name != self.last_name:
        if self.name == '':
            self.name = self.last_name
            return

        if self.last_name != '':
            layer_collections[self.last_name]["ptr"].collection.name = self.name

            update_property_group(context)

        self.last_name = self.name

class CMListCollection(PropertyGroup):
    name: StringProperty(update=update_col_name)
    last_name: StringProperty()


def update_collection_tree(context):
    global max_lvl
    global row_index
    collection_tree.clear()
    layer_collections.clear()
    max_lvl = 0
    row_index = 0

    init_laycol_list = context.view_layer.layer_collection.children

    master_laycol = {"id": 0,
                     "name": context.view_layer.layer_collection.name,
                     "lvl": -1,
                     "row_index": -1,
                     "visible": True,
                     "has_children": True,
                     "expanded": True,
                     "parent": None,
                     "children": [],
                     "ptr": context.view_layer.layer_collection
                     }

    get_all_collections(context, init_laycol_list, master_laycol, collection_tree, visible=True)


def get_all_collections(context, collections, parent, tree, level=0, visible=False):
    global row_index
    global max_lvl
    
    if level > max_lvl:
        max_lvl = level

    for item in collections:
        laycol = {"id": len(layer_collections) +1,
                  "name": item.name,
                  "lvl": level,
                  "row_index": row_index,
                  "visible":  visible,
                  "has_children": False,
                  "expanded": False,
                  "parent": parent,
                  "children": [],
                  "ptr": item
                  }

        row_index += 1

        layer_collections[item.name] = laycol
        tree.append(laycol)

        if len(item.children) > 0:
            laycol["has_children"] = True

            if item.name in expanded and laycol["visible"]:
                laycol["expanded"] = True
                get_all_collections(context, item.children, laycol, laycol["children"], level+1,  visible=True)

            else:
                get_all_collections(context, item.children, laycol, laycol["children"], level+1)


def update_property_group(context):
    update_collection_tree(context)
    context.scene.CMListCollection.clear()
    create_property_group(context, collection_tree)


def create_property_group(context, tree):
    global in_filter

    for laycol in tree:
        new_cm_listitem = context.scene.CMListCollection.add()
        new_cm_listitem.name = laycol["name"]

        if laycol["has_children"]:
            create_property_group(context, laycol["children"])
