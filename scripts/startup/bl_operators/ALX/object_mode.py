from typing import Final

import bpy

TD_object_types: Final[set[str]] = {
    "MESH",
    "CURVE",
    "SURFACE",
    "META",
    "FONT",
    "CURVES",
    "POINTCLOUD",
    "VOLUME",
    "GPENCIL",
    "GREASEPENCIL",
    "ARMATURE",
    "LATTICE",
    "EMPTY",
    "LIGHT",
    "LIGHT_PROBE",
    "CAMERA",
    "SPEAKER",
}


class ALX_OT_ObjectMode_SetToObject(bpy.types.Operator):
    bl_label = ""
    bl_idname = "alx.operator_set_to_object_mode"
    bl_options = {"REGISTER"}

    @staticmethod
    def execute(self, context):
        bpy.ops.object.mode_set(mode="OBJECT")
        return {"FINISHED"}


class ALX_OT_ObjectMode_SetToPose(bpy.types.Operator):
    bl_label = ""
    bl_idname = "alx.operator_set_to_pose_mode"
    bl_options = {"REGISTER"}

    @staticmethod
    def execute(self, context):
        if context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

        if len(context.selected_objects) > 0:
            armatures = filter(
                lambda obj: obj is not None,
                [
                    selected_object if (selected_object.type == "ARMATURE") else selected_object.find_armature()
                    for selected_object in context.selected_objects
                    if (selected_object.type in ["MESH", "ARMATURE"])
                ],
            )

            for armature in armatures:
                armature.hide_set(False, view_layer=context.view_layer)
                armature.hide_viewport = False

                armature.select_set(True, view_layer=context.view_layer)

            bpy.ops.object.mode_set(mode="POSE")

        return {"FINISHED"}


class ALX_OT_ObjectMode_SetToPaintWeight(bpy.types.Operator):
    bl_label = ""
    bl_idname = "alx.operator_set_to_paint_weight_mode"
    bl_options = {"REGISTER"}

    @staticmethod
    def execute(self, context):
        if context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

        if len(context.selected_objects) > 0:
            mesh = None
            armature = None

            if context.active_object.type == "MESH":

                mesh = context.active_object
                armature = context.active_object.find_armature()
                if armature is not None:
                    armature.hide_set(False, view_layer=context.view_layer)
                    armature.hide_viewport = False

                    armature.select_set(True, view_layer=context.view_layer)
                else:
                    return {"CANCELLED"}

            else:
                if context.active_object.type == "ARMATURE":
                    for selected_object in context.selected_objects:
                        if selected_object.type == "MESH":
                            mesh = selected_object
                            armature = selected_object.find_armature()

                            if (armature is not None) and (armature is context.active_object):
                                armature.select_set(True, view_layer=context.view_layer)
                                context.view_layer.objects.active = selected_object
                                break

            if (armature is not None) or (mesh is not None):
                bpy.ops.object.mode_set(mode="WEIGHT_PAINT")

        return {"FINISHED"}


class ALX_OT_ObjectMode_SetToEditMesh(bpy.types.Operator):
    bl_label = ""
    bl_idname = "alx.operator_set_to_edit_mesh_mode"
    bl_options = {"REGISTER"}

    target_selection_mode: bpy.props.StringProperty(name="", default="", options={"HIDDEN"})  # type: ignore

    @staticmethod
    def execute(self, context):
        if context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

        if len(context.selected_objects) > 0 and self.target_selection_mode in ["VERT", "EDGE", "FACE"]:
            for selected_object in context.selected_objects:
                if selected_object.type != "MESH":
                    selected_object.select_set(False, view_layer=context.view_layer)
            else:
                if context.active_object is not None and context.active_object.type != "MESH":
                    context.view_layer.objects.active = context.selected_objects[0]

            if context.active_object is not None and context.active_object.type == "MESH":
                bpy.ops.object.mode_set_with_submode(mode="EDIT", mesh_select_mode={self.target_selection_mode})
        return {"FINISHED"}


class ALX_OT_ObjectMode_SetToEditGeneric(bpy.types.Operator):
    bl_label = ""
    bl_idname = "alx.operator_set_to_edit_generic_mode"
    bl_options = {"REGISTER"}

    target_object_type: bpy.props.StringProperty(
        name="target object type", default="", options={"HIDDEN"}
    )  # type: ignore
    target_selection_mode: bpy.props.StringProperty(name="", default="", options={"HIDDEN"})  # type: ignore

    @staticmethod
    def execute(self, context):
        if context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

        if self.target_object_type in TD_object_types:
            match self.target_object_type:

                case "ARMATURE":

                    if self.target_object_sub_mode == "":
                        armature_selection_override = list(
                            filter(
                                lambda object: object is not None,
                                [
                                    (
                                        selected_object
                                        if (selected_object.type == "ARMATURE")
                                        else selected_object.find_armature()
                                    )
                                    for selected_object in context.selected_objects
                                    if (selected_object is not None) and (selected_object.type in ["ARMATURE", "MESH"])
                                ],
                            )
                        )

                        for armature in armature_selection_override:
                            armature.hide_set(False, view_layer=context.view_layer)
                            armature.hide_viewport = False
                            armature.select_set(True)

                            if context.active_object.type != "ARMATURE":
                                context.view_layer.objects.active = armature

                        if (len(context.selected_objects) > 0) and (context.active_object.type == "ARMATURE"):
                            bpy.ops.object.mode_set(mode="EDIT")
                        return {"FINISHED"}

                case "CURVE":
                    # region
                    if self.target_object_sub_mode == "":
                        for selected_object in context.selected_objects:
                            context.view_layer.objects.active = selected_object

                            if context.active_object.type == "CURVE":
                                break

                        if (len(context.selected_objects) > 0) and (context.active_object.type == "CURVE"):
                            bpy.ops.object.mode_set(mode="EDIT")

                    return {"FINISHED"}
                    # endregion

                case "SURFACE":
                    # region
                    if self.target_object_sub_mode == "":
                        for selected_object in context.selected_objects:
                            context.view_layer.objects.active = selected_object

                            if context.active_object.type == "SURFACE":
                                break

                        if (len(context.selected_objects) > 0) and (context.active_object.type == "SURFACE"):
                            bpy.ops.object.mode_set(mode="EDIT")

                    return {"FINISHED"}
                    # endregion

                case "META":
                    # region
                    if self.target_object_sub_mode == "":
                        for selected_object in context.selected_objects:
                            context.view_layer.objects.active = selected_object

                            if context.active_object.type == "META":
                                break

                        if (len(context.selected_objects) > 0) and (context.active_object.type == "META"):
                            bpy.ops.object.mode_set(mode="EDIT")

                    return {"FINISHED"}
                    # endregion

                case "FONT":
                    # region
                    if self.target_object_sub_mode == "":
                        for selected_object in context.selected_objects:
                            context.view_layer.objects.active = selected_object

                            if context.active_object.type == "FONT":
                                break

                        if (len(context.selected_objects) > 0) and (context.active_object.type == "FONT"):
                            bpy.ops.object.mode_set(mode="EDIT")

                    return {"FINISHED"}
                    # endregion

                case "LATTICE":
                    # region
                    if self.target_object_sub_mode == "":
                        for selected_object in context.selected_objects:
                            context.view_layer.objects.active = selected_object

                            if context.active_object.type == "LATTICE":
                                break

                        if (len(context.selected_objects) > 0) and (context.active_object.type == "LATTICE"):
                            bpy.ops.object.mode_set(mode="EDIT")

                    return {"FINISHED"}
                    # endregion

                case "GPENCIL":
                    # region
                    if bpy.app.version[:2] in {(4, 0), (4, 1), (4, 2)}:
                        if self.target_object_sub_mode in ["POINT", "STROKE", "SEGMENT"]:
                            for selected_object in context.selected_objects:
                                context.view_layer.objects.active = selected_object

                                if context.active_object.type == "GPENCIL":
                                    break

                            if (len(context.selected_objects) > 0) and (context.active_object.type == "GPENCIL"):
                                bpy.ops.object.mode_set(mode="EDIT_GPENCIL")
                                context.scene.tool_settings.gpencil_selectmode_edit = self.target_object_sub_mode

                    if bpy.app.version[:2] in {(4, 3), (4, 4)}:
                        if self.target_object_sub_mode in ["POINT", "STROKE", "SEGMENT"]:
                            for selected_object in context.selected_objects:
                                context.view_layer.objects.active = selected_object

                                if context.active_object.type == "GREASEPENCIL":
                                    break

                            if (len(context.selected_objects) > 0) and (context.active_object.type == "GREASEPENCIL"):
                                bpy.ops.object.mode_set(mode="EDIT")
                                context.scene.tool_settings.gpencil_selectmode_edit = self.target_object_sub_mode

                    return {"FINISHED"}
                    # endregion

        return {"FINISHED"}


class ALX_OT_ObjectMode_SetToSculpt(bpy.types.Operator):
    bl_label = ""
    bl_idname = "alx.operator_set_to_sculpt_mode"
    bl_options = {"REGISTER"}

    @staticmethod
    def execute(self, context):

        if context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

        if len(context.selected_objects) > 0:
            sculpt_selection_override = [
                selected_object for selected_object in context.selected_objects if (selected_object.type == "MESH")
            ]

            if len(sculpt_selection_override) == 0:
                return {"CANCELLED"}

            context.view_layer.objects.active = sculpt_selection_override[0]
            bpy.ops.object.mode_set(mode="SCULPT")

        return {"FINISHED"}
