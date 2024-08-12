bl_info = {
    "name": "Quick Comp!",
    "blender": (4, 2, 0),
    "category": "Compositing",
    "version": (1, 2, 0),
    "author": "LightAndy",
    "description": "Quick Comp! is a Blender add-on designed to enhance the rendering process with just a single click (or two).",
    "location": "View3D > N Panel",
    "warning": "This add-on will remove all your existing compositing nodes and add new ones",
    "support": "COMMUNITY",
}

import bpy  # type: ignore #? Disabling warning visualization


# Define properties for the checkboxes
class QuickCompProperties(bpy.types.PropertyGroup):
    chromatic_slider: bpy.props.IntProperty(
        name="Chromatic aberration", default=2, min=1, max=10, subtype="FACTOR"
    )  # type: ignore #? Disabling warning visualization
    distortion_slider: bpy.props.IntProperty(
        name="Lens distortion", default=7, min=1, max=10, subtype="FACTOR"
    )  # type: ignore #? Disabling warning visualization
    glare_slider: bpy.props.IntProperty(
        name="Glare", default=8, min=1, max=10, subtype="FACTOR"
    )  # type: ignore #? Disabling warning visualization
    grain_slider: bpy.props.IntProperty(
        name="Grain", default=1, min=2, max=10, subtype="FACTOR"
    )  # type: ignore #? Disabling warning visualization
    contrast_slider: bpy.props.IntProperty(
        name="Contrast", default=2, min=1, max=5, subtype="FACTOR"
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

        layout.prop(quick_comp_props, "chromatic_slider")
        layout.prop(quick_comp_props, "distortion_slider")
        layout.prop(quick_comp_props, "glare_slider")
        layout.prop(quick_comp_props, "grain_slider")
        layout.prop(quick_comp_props, "contrast_slider")

        layout.operator("quick_comp.complex_render", text="Improve render (Complex)")


# Define the Operator for the button
class QuickCompBasicOperator(bpy.types.Operator):
    bl_idname = "quick_comp.basic_improve"
    bl_label = "Improve render (Basic)"
    bl_description = (
        "This will remove all your existing compositing nodes and add new ones"
    )

    def execute(self, context):
        currentScene = context.scene
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

        currentScene.view_settings.look = "AgX - Medium Low Contrast"

        renderNode = tree.nodes.new(type="CompositorNodeRLayers")
        renderNode.location = (-100, 0)

        outputNode = tree.nodes.new(type="CompositorNodeComposite")
        outputNode.location = (800, 150)

        lensNode = tree.nodes.new(type="CompositorNodeLensdist")
        lensNode.location = (200, 0)
        lensNode.use_fit = True
        lensNode.inputs[1].default_value = 0.01
        lensNode.inputs[2].default_value = 0.005
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
        mixNode.inputs[0].default_value = 0.01
        links.new(blurNode.outputs["Image"], mixNode.inputs[2])
        links.new(lensNode.outputs["Image"], mixNode.inputs[1])

        glareNode = tree.nodes.new(type="CompositorNodeGlare")
        glareNode.location = (600, 150)
        glareNode.glare_type = "FOG_GLOW"
        glareNode.quality = "HIGH"
        glareNode.mix = -0.8
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
        chromaticSlider = context.scene.quick_comp_props.chromatic_slider
        distortionSlider = context.scene.quick_comp_props.distortion_slider
        glareSlider = context.scene.quick_comp_props.glare_slider
        streaksSlider = glareSlider
        grainSlider = context.scene.quick_comp_props.grain_slider
        contrastSlider = context.scene.quick_comp_props.contrast_slider

        if glareSlider > 7:
            streaksSlider = 0.05 + (streaksSlider - 4) * (0.283 / 9)
        else:
            streaksSlider = 0.05
        glareSlider = round(0.1 + (glareSlider - 1) * (0.9 / 9), 3)
        chromaticSlider = round(0.005 + (chromaticSlider - 1) * (0.045 / 9), 3)
        distortionSlider = round(-0.02 + (distortionSlider - 1) * (0.04 / 9), 3)
        grainSlider = round(0.005 + (grainSlider - 1) * (0.045 / 9), 3)

        currentScene = context.scene
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

        look_map = {
            1: "AgX - Low Contrast",
            2: "AgX - Medium Low Contrast",
            3: "AgX - Base Contrast",
            4: "AgX - Medium High Contrast",
            5: "AgX - High Contrast",
        }
        currentScene.view_settings.look = look_map.get(
            contrastSlider, "AgX - Base Contrast"
        )

        renderNode = tree.nodes.new(type="CompositorNodeRLayers")
        renderNode.location = (-100, 0)

        outputNode = tree.nodes.new(type="CompositorNodeComposite")
        outputNode.location = (1000, 150)

        viewerNode = tree.nodes.new(type="CompositorNodeViewer")
        viewerNode.location = (1000, 0)

        lensNode = tree.nodes.new(type="CompositorNodeLensdist")
        lensNode.location = (200, 0)
        lensNode.use_fit = True
        lensNode.inputs[1].default_value = distortionSlider
        lensNode.inputs[2].default_value = chromaticSlider
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

        streaksGlare = tree.nodes.new(type="CompositorNodeGlare")
        streaksGlare.location = (200, -250)
        streaksGlare.glare_type = "STREAKS"
        streaksGlare.quality = "MEDIUM"
        streaksGlare.mix = 1
        streaksGlare.threshold = 15
        streaksGlare.streaks = 16
        links.new(renderNode.outputs["Image"], streaksGlare.inputs["Image"])

        fogGlare = tree.nodes.new(type="CompositorNodeGlare")
        fogGlare.location = (400, -250)
        fogGlare.glare_type = "FOG_GLOW"
        fogGlare.quality = "HIGH"
        fogGlare.mix = 1
        fogGlare.threshold = 15
        fogGlare.size = 9
        links.new(renderNode.outputs["Image"], fogGlare.inputs["Image"])

        glareMixNode = tree.nodes.new(type="CompositorNodeMixRGB")
        glareMixNode.location = (600, -150)
        glareMixNode.blend_type = "ADD"
        glareMixNode.inputs[0].default_value = streaksSlider
        links.new(fogGlare.outputs["Image"], glareMixNode.inputs[1])
        links.new(streaksGlare.outputs["Image"], glareMixNode.inputs[2])

        finalMixNode = tree.nodes.new(type="CompositorNodeMixRGB")
        finalMixNode.location = (800, 0)
        finalMixNode.blend_type = "ADD"
        finalMixNode.inputs[0].default_value = glareSlider
        links.new(glareMixNode.outputs["Image"], finalMixNode.inputs[2])
        links.new(finalMixNode.outputs["Image"], outputNode.inputs["Image"])
        links.new(finalMixNode.outputs["Image"], viewerNode.inputs["Image"])

        coTextureNoise = tree.nodes.new(type="CompositorNodeTexture")
        coTextureNoise.location = (0, 600)
        coTextureNoise.texture = bpy.data.textures["CO Film Grain QC"]

        firstMixNode = tree.nodes.new(type="CompositorNodeMixRGB")
        firstMixNode.location = (200, 500)
        firstMixNode.blend_type = "OVERLAY"
        firstMixNode.inputs[0].default_value = 0.5
        links.new(coTextureNoise.outputs["Color"], firstMixNode.inputs[1])
        links.new(bwTextureNode.outputs["Value"], firstMixNode.inputs[2])

        bwMixNode = tree.nodes.new(type="CompositorNodeMixRGB")
        bwMixNode.location = (400, 300)
        bwMixNode.blend_type = "SUBTRACT"
        bwMixNode.inputs[0].default_value = grainSlider
        links.new(lensNode.outputs["Image"], bwMixNode.inputs[1])
        links.new(blurNode.outputs["Image"], bwMixNode.inputs[2])

        coMixNode = tree.nodes.new(type="CompositorNodeMixRGB")
        coMixNode.location = (600, 300)
        coMixNode.blend_type = "OVERLAY"
        coMixNode.inputs[0].default_value = grainSlider * 6
        links.new(bwMixNode.outputs["Image"], coMixNode.inputs[1])
        links.new(firstMixNode.outputs["Image"], coMixNode.inputs[2])
        links.new(coMixNode.outputs["Image"], finalMixNode.inputs[1])

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
