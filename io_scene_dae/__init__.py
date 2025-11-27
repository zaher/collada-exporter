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
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####
#
#   Adding compatibility export for OpenSim and SecondLife by Zaher
#
#   Based on:
#
#   https://github.com/godotengine/collada-exporter
#   https://github.com/hkunz/collada-exporter
#
# #####

import bpy

from bpy_extras.io_utils import (
    ImportHelper,
    ExportHelper,
    orientation_helper,
    axis_conversion,
)

from bpy.props import (
        StringProperty,
        BoolProperty,
        FloatProperty,
        EnumProperty,
)

from bpy_extras.io_utils import ExportHelper

bl_info = {
    "name": "Better Collada Exporter",
    "author": "Juan Linietsky, artell, Panthavma, Harry McKenzie, and many",
    "version": (1, 12, 1),
    "blender": (4, 0, 0),
    "location": "File > Import-Export",
    "description": ("Export DAE Scenes. This plugin actually works better! "
                    "Fixed Blender 4.0+ compatibility by removing deprecated method calls."
                    "Fixed OpenSIM/SecondLife compatibility."
                    "Otherwise contact the Godot Engine community."),
    "warning": "",
    "wiki_url": ("https://godotengine.org"),
    "tracker_url": "https://github.com/hkunz/collada-exporter",
    "support": "OFFICIAL",
    "category": "Import-Export"}

if "bpy" in locals():
    import importlib
    if "export_dae" in locals():
        importlib.reload(export_dae)  # noqa

@orientation_helper(axis_forward='Y', axis_up='Z')
class CE_OT_export_dae(bpy.types.Operator, ExportHelper):
    """Selection to DAE"""
    bl_idname = "export_scene.better_dae"
    bl_label = "Export DAE"
    bl_options = {"PRESET"}

    object_types_list = (
            ("MESH", "Mesh", ""),
            ("ARMATURE", "Armature", ""),
            ("CURVE", "Curve", ""),
            ("EMPTY", "Empty", ""),
            ("CAMERA", "Camera", ""),
            ("LAMP", "Lamp", "")
    )

    filename_ext = ".dae"
    filter_glob : StringProperty(default="*.dae", options={"HIDDEN"})

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling
    object_types : EnumProperty(
        name="Object Types",
        options={"ENUM_FLAG"},

        items=object_types_list,
            default={"EMPTY", "CAMERA", "LAMP", "ARMATURE", "MESH", "CURVE"},
        )

    """axis_up: EnumProperty(
        name="Up Axis",
        description="The up axis of the file",
        items=(('X_UP', "X UP", "X Axis Up"),
               ('Y_UP', "Y UP", "Y Axis Up"),
               ('Z_UP', "Z UP", "Z Axis Up")),
        default='Z_UP',
        )
    """

    use_generate_ids : BoolProperty(
        name="Generate IDs",
        description="Generate object, bones and nodes id to new id, do not use Blender names",
        default=False,
        )
    use_export_selected : BoolProperty(
        name="Selected Objects",
        description="Export only selected objects (and visible in active "
                    "layers if that applies).",
        default=True,
        )
    use_mesh_modifiers : BoolProperty(
        name="Apply Modifiers",
        description="Apply modifiers to mesh objects (on a copy!).",
        default=True,
        )
    use_exclude_armature_modifier : BoolProperty(
        name="Exclude Armature Modifier",
        description="Exclude the armature modifier when applying modifiers "
                      "(otherwise animation will be applied on top of the last pose)",
        default=True,
        )
    use_tangent_arrays : BoolProperty(
        name="Tangent Arrays",
        description="Export Tangent and Binormal arrays "
                    "(for normalmapping).",
        default=False,
        )
    use_triangles : BoolProperty(
        name="Triangulate",
        description="Export Triangles instead of Polygons.",
        default=True,
        )

    use_copy_images : BoolProperty(
        name="Copy Images",
        description="Copy Images (create images/ subfolder)",
        default=True,
        )
    use_active_layers : BoolProperty(
        name="Active Layers",
        description="Export only objects on the active layers.",
        default=True,
        )
    use_exclude_ctrl_bones : BoolProperty(
        name="Exclude Control Bones",
        description=("Exclude skeleton bones with names beginning with 'ctrl' "
                     "or bones which are not marked as Deform bones."),
        default=True,
        )
    use_anim : BoolProperty(
        name="Export Animation",
        description="Export keyframe animation",
        default=True,
        )
    use_anim_action_all : BoolProperty(
        name="All Actions",
        description=("Export all actions for the first armature found "
                     "in separate DAE files"),
        default=False,
        )
    use_anim_skip_noexp : BoolProperty(
        name="Skip (-noexp) Actions",
        description="Skip exporting of actions whose name end in (-noexp)."
                    " Useful to skip control animations.",
        default=True,
        )
    use_anim_optimize : BoolProperty(
        name="Optimize Keyframes",
        description="Remove double keyframes",
        default=False,
        )

    use_shape_key_export : BoolProperty(
        name="Shape Keys",
        description="Export shape keys for selected objects.",
        default=False,
        )

    anim_optimize_precision : FloatProperty(
        name="Precision",
        description=("Tolerence for comparing double keyframes "
                     "(higher for greater accuracy)"),
        min=1, max=16,
        soft_min=1, soft_max=16,
        default=6.0,
        )

    use_metadata : BoolProperty(
        name="Use Metadata",
        default=True,
        options={"HIDDEN"},
        )

    @property
    def check_extension(self):
        return True

    ## Execute ##

    def execute(self, context):
        if not self.filepath:
            raise Exception("filepath not set")

        keywords = self.as_keywords(ignore=(
                                            "global_scale",
                                            "filter_glob"
                                            ))

        # global_matrix: from current Blender coordinates system to output coordinates system
        global_matrix = axis_conversion(
            from_forward=self.axis_forward,
            from_up=self.axis_up,
        ).to_4x4().inverted()

        keywords["global_matrix"] = global_matrix

        from . import export_dae
        return export_dae.save(self, context, **keywords)

    ## Draw ##

    def draw(self, context):

        main = self.layout

        ###### Objects #######

        header, panel = main.panel("objects")
        header.label(text="Object Types")
        if panel:
            column = panel.column(align=True)
            #for index, item in enumerate(self.bl_rna.properties["object_types"].enum_items):
            for item in self.object_types_list:
                column.prop_enum(self, "object_types", item[0])

        ###### Options #######

        header, panel = main.panel("options")
        header.label(text="Options")
        if panel:
            column = panel.column(align=False)
            column.prop(self, "use_generate_ids", toggle=False)
            column.prop(self, "use_export_selected", toggle=False)
            column.prop(self, "axis_forward")
            column.prop(self, "axis_up")

        ###### Mesh #######

        header, panel = main.panel("geometry")
        header.label(text="Geometry")

        if panel:
            column = panel.column(align=True)

            column.prop(self, "use_mesh_modifiers", toggle=False)
            column.prop(self, "use_tangent_arrays", toggle=False)
            column.prop(self, "use_triangles", toggle=False)

        ###### Armature #######

        header, panel = main.panel("armature")
        header.label(text="Armature")

        if panel:
            column = panel.column(align=True)

            column.prop(self, "use_exclude_armature_modifier", toggle=False)
            column.prop(self, "use_copy_images", toggle=False)
            column.prop(self, "use_active_layers", toggle=False)
            column.prop(self, "use_exclude_ctrl_bones", toggle=False)

        ###### Animation #######

        header, panel = main.panel("animation")
        header.label(text="Animation")

        if panel:
            column = panel.column(align=True)

            column.prop(self, "use_anim", toggle=False)
            column.prop(self, "use_anim_action_all", toggle=False)
            column.prop(self, "use_anim_skip_noexp", toggle=False)
            column.prop(self, "use_anim_optimize", toggle=False)
            row = column.row(align = True)
            row.label(text = "Precision")
            row.prop(self, "anim_optimize_precision", text = "")

        ###### Extra #######

        header, panel = main.panel("Extra")
        header.label(text="Extra")

        if panel:
            column = panel.column(align=True)

            column.prop(self, "use_metadata", toggle=False)
            column.prop(self, "use_shape_key_export", toggle=False)



def menu_func(self, context):
    self.layout.operator(CE_OT_export_dae.bl_idname, text="Better Collada (.dae)")


#classes = (CE_OT_export_dae)

def register():
	from bpy.utils import register_class

	register_class(CE_OT_export_dae)

	#bpy.types.INFO_MT_file_export.append(menu_func)
	bpy.types.TOPBAR_MT_file_export.append(menu_func)

def unregister():
	from bpy.utils import unregister_class

	unregister_class(CE_OT_export_dae)

	#bpy.types.INFO_MT_file_export.append(menu_func)
	bpy.types.TOPBAR_MT_file_export.remove(menu_func)

if __name__ == "__main__":
    register()
