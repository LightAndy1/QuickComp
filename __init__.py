bl_info = {
    "name": "Quick Comp!",
    "blender": (4, 2, 0),
    "category": "Compositing",
    "version": (1, 0, 1),
    "author": "LightAndy",
    "description": "Quick Comp! is a Blender add-on designed to enhance the rendering process with just a single click (or two).",
    "location": "View3D > N Panel",
    "warning": "This add-on will remove all your existing compositing nodes and add new ones",
    "support": "COMMUNITY",
}

import bpy  # type: ignore #? Disabling warning visualization


# Define properties for the checkboxes
class QuickCompProperties(bpy.types.PropertyGroup):
    lens_slider: bpy.props.IntProperty(
        name="Lens Distortion", default=1, min=1, max=10, subtype="FACTOR"
    )  # type: ignore #? Disabling warning visualization
    glare_slider: bpy.props.IntProperty(
        name="Glare", default=1, min=1, max=10, subtype="FACTOR"
    )  # type: ignore #? Disabling warning visualization
    grain_slider: bpy.props.IntProperty(
        name="Grain", default=1, min=1, max=10, subtype="FACTOR"
    )  # type: ignore #? Disabling warning visualization
    vibrance_slider: bpy.props.IntProperty(
        name="Vibrance", default=1, min=1, max=10, subtype="FACTOR"
    )  # type: ignore #? Disabling warning visualization


# Define the Panel in the N menu
class QuickCompPanel(bpy.types.Panel):
    bl_label = "Quick Comp!"
    bl_idname = "VIEW3D_PT_quick_comp"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Quick Comp!"

    def draw(self, context):
        layout = self.layout

        layout.operator("quick_comp.basic_improve", text="Improve render (Basic)")


class QuickCompSubPanel(bpy.types.Panel):
    bl_label = "Advanced settings"
    bl_idname = "VIEW3D_PT_quick_comp_advanced"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Quick Comp!"
    bl_parent_id = "VIEW3D_PT_quick_comp"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        quick_comp_props = scene.quick_comp_props

        layout.prop(quick_comp_props, "lens_slider")
        layout.prop(quick_comp_props, "glare_slider")
        layout.prop(quick_comp_props, "grain_slider")
        # layout.prop(quick_comp_props, "vibrance_slider")  #todo: Add Vibrance

        layout.operator("quick_comp.complex_render", text="Improve render (Complex)")


# Define the Operator for the button
class QuickCompBasicOperator(bpy.types.Operator):
    bl_idname = "quick_comp.basic_improve"
    bl_label = "Improve render (Basic)"
    bl_description = (
        "This will remove all your existing compositing nodes and add new ones"
    )

    def execute(self, context):
        bpy.context.scene.use_nodes = True
        tree = bpy.context.scene.node_tree
        links = tree.links
        textureList = bpy.data.textures
        nodeCount = 0
        textureCount = 0

        for node in tree.nodes:
            tree.nodes.remove(node)
            nodeCount += 1
        print("Quick Comp! [INFO] Removed " + str(nodeCount) + " nodes")

        for texture in textureList:
            if "film grain qc" in texture.name.lower():
                textureList.remove(texture)
                textureCount += 1
        print("Quick Comp! [INFO] Removed " + str(textureCount) + " textures")

        renderNode = tree.nodes.new(type="CompositorNodeRLayers")
        renderNode.location = (-100, 0)

        outputNode = tree.nodes.new(type="CompositorNodeComposite")
        outputNode.location = (800, 150)

        lensNode = tree.nodes.new(type="CompositorNodeLensdist")
        lensNode.location = (200, 0)
        lensNode.inputs[2].default_value = 0.01
        links.new(renderNode.outputs["Image"], lensNode.inputs["Image"])

        bpy.data.textures.new("Film Grain QC", type="NOISE")

        bwTextureNode = tree.nodes.new(type="CompositorNodeTexture")
        bwTextureNode.location = (0, 300)
        bwTextureNode.texture = bpy.data.textures["Film Grain QC"]

        blurNode = tree.nodes.new(type="CompositorNodeBlur")
        blurNode.location = (200, 300)
        blurNode.filter_type = "FAST_GAUSS"
        blurNode.size_x = 1
        blurNode.size_y = 1
        blurNode.inputs[1].default_value = 2
        links.new(bwTextureNode.outputs["Value"], blurNode.inputs["Image"])

        mixNode = tree.nodes.new(type="CompositorNodeMixRGB")
        mixNode.location = (400, 150)
        mixNode.blend_type = "SUBTRACT"
        mixNode.inputs[0].default_value = 0.014
        links.new(blurNode.outputs["Image"], mixNode.inputs[2])
        links.new(lensNode.outputs["Image"], mixNode.inputs[1])

        glareNode = tree.nodes.new(type="CompositorNodeGlare")
        glareNode.location = (600, 150)
        glareNode.glare_type = "FOG_GLOW"
        glareNode.quality = "HIGH"
        glareNode.mix = -0.881
        glareNode.threshold = 0
        glareNode.size = 9
        links.new(mixNode.outputs["Image"], glareNode.inputs["Image"])
        links.new(glareNode.outputs["Image"], outputNode.inputs["Image"])

        return {"FINISHED"}


class QuickCompComplexOperator(bpy.types.Operator):
    bl_idname = "quick_comp.complex_render"
    bl_label = "Improve render (Complex)"
    bl_description = (
        "This will remove all your existing compositing nodes and add new ones"
    )

    def execute(self, context):
        lensSlider = context.scene.quick_comp_props.lens_slider
        glareSlider = context.scene.quick_comp_props.glare_slider
        grainSlider = context.scene.quick_comp_props.grain_slider

        lensSlider = round(0.005 + (lensSlider - 1) * (0.045 / 9), 3)
        glareSlider = round(-0.96 + (glareSlider - 1) * (0.71 / 9), 3)
        grainSlider = round(0.01 + (grainSlider - 1) * (0.04 / 9), 3)

        bpy.context.scene.use_nodes = True
        tree = bpy.context.scene.node_tree
        textureList = bpy.data.textures
        nodeCount = 0
        textureCount = 0
        links = tree.links

        for node in tree.nodes:
            tree.nodes.remove(node)
            nodeCount += 1
        print("Quick Comp! [INFO] Removed " + str(nodeCount) + " nodes")

        for texture in textureList:
            if "film grain qc" in texture.name.lower():
                textureList.remove(texture)
                textureCount += 1
        print("Quick Comp! [INFO] Removed " + str(textureCount) + " textures")

        renderNode = tree.nodes.new(type="CompositorNodeRLayers")
        renderNode.location = (-100, 0)

        outputNode = tree.nodes.new(type="CompositorNodeComposite")
        outputNode.location = (1000, 150)

        viewerNode = tree.nodes.new(type="CompositorNodeViewer")
        viewerNode.location = (1000, 0)

        lensNode = tree.nodes.new(type="CompositorNodeLensdist")
        lensNode.location = (200, 0)
        lensNode.inputs[2].default_value = lensSlider
        links.new(renderNode.outputs["Image"], lensNode.inputs["Image"])

        bpy.data.textures.new("BW Film Grain QC", type="NOISE")
        coNoiseTexture = bpy.data.textures.new("CO Film Grain QC", type="CLOUDS")
        coNoiseTexture.noise_type = "SOFT_NOISE"
        coNoiseTexture.cloud_type = "COLOR"
        coNoiseTexture.noise_scale = 0.01
        coNoiseTexture.noise_depth = 0

        bwTextureNode = tree.nodes.new(type="CompositorNodeTexture")
        bwTextureNode.location = (0, 300)
        bwTextureNode.texture = bpy.data.textures["BW Film Grain QC"]

        blurNode = tree.nodes.new(type="CompositorNodeBlur")
        blurNode.location = (200, 300)
        blurNode.filter_type = "FAST_GAUSS"
        blurNode.size_x = 1
        blurNode.size_y = 1
        blurNode.inputs[1].default_value = 2
        links.new(bwTextureNode.outputs["Value"], blurNode.inputs["Image"])

        bwMixNode = tree.nodes.new(type="CompositorNodeMixRGB")
        bwMixNode.location = (400, 300)
        bwMixNode.blend_type = "MIX"
        bwMixNode.inputs[0].default_value = 0.25
        links.new(blurNode.outputs["Image"], bwMixNode.inputs[1])

        finalMixNode = tree.nodes.new(type="CompositorNodeMixRGB")
        finalMixNode.location = (600, 150)
        finalMixNode.blend_type = "SUBTRACT"
        finalMixNode.inputs[0].default_value = grainSlider
        links.new(bwMixNode.outputs["Image"], finalMixNode.inputs[2])
        links.new(lensNode.outputs["Image"], finalMixNode.inputs[1])

        glareNode = tree.nodes.new(type="CompositorNodeGlare")
        glareNode.location = (800, 150)
        glareNode.glare_type = "FOG_GLOW"
        glareNode.quality = "HIGH"
        glareNode.mix = glareSlider
        glareNode.threshold = 0
        glareNode.size = 9
        links.new(finalMixNode.outputs["Image"], glareNode.inputs["Image"])
        links.new(glareNode.outputs["Image"], outputNode.inputs["Image"])
        links.new(glareNode.outputs["Image"], viewerNode.inputs["Image"])

        coTextureNoise = tree.nodes.new(type="CompositorNodeTexture")
        coTextureNoise.location = (0, 600)
        coTextureNoise.texture = bpy.data.textures["CO Film Grain QC"]

        coMixNode = tree.nodes.new(type="CompositorNodeMixRGB")
        coMixNode.location = (200, 500)
        coMixNode.blend_type = "OVERLAY"
        coMixNode.inputs[0].default_value = 0.5
        links.new(coTextureNoise.outputs["Color"], coMixNode.inputs[1])
        links.new(bwTextureNode.outputs["Value"], coMixNode.inputs[2])
        links.new(coMixNode.outputs["Image"], bwMixNode.inputs[2])

        return {"FINISHED"}


# Register and Unregister
classes = [
    QuickCompProperties,
    QuickCompPanel,
    QuickCompSubPanel,
    QuickCompBasicOperator,
    QuickCompComplexOperator,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.quick_comp_props = bpy.props.PointerProperty(
        type=QuickCompProperties
    )


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.quick_comp_props


if __name__ == "__main__":
    register()
