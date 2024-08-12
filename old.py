bl_info = {
    "name": "Quick Comp! FREE",
    "blender": (4, 2, 0),
    "category": "Compositing",
    "version": (1, 0, 0),
    "author": "LightAndy",
    "description": "Quick Comp! (FREE) is a Blender add-on designed to enhance the rendering process with just a single click (or two).",
    "location": "View3D > N Panel",
    "warning": "This add-on will remove all your existing compositing nodes and add new ones",
    "support": "COMMUNITY",
}

import bpy  # type: ignore #? Disabling warning visualization


# Define properties for the checkboxes
class QuickCompProperties(bpy.types.PropertyGroup):
    lens_distortion: bpy.props.BoolProperty(name="Lens Distortion", default=False)  # type: ignore #? Disabling warning visualization
    subtle_glare: bpy.props.BoolProperty(name="Subtle Glare", default=False)  # type: ignore #? Disabling warning visualization
    film_grain: bpy.props.BoolProperty(name="Film Grain", default=False)  # type: ignore #? Disabling warning visualization


# Define the Panel in the N menu
class QuickCompPanel(bpy.types.Panel):
    bl_label = "Quick Comp! PLUS"
    bl_idname = "VIEW3D_PT_quick_comp"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Quick Comp!"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        quick_comp_props = scene.quick_comp_props

        layout.prop(quick_comp_props, "lens_distortion")
        layout.prop(quick_comp_props, "subtle_glare")
        layout.prop(quick_comp_props, "film_grain")
        layout.operator("quick_comp.improve_render", text="Improve render")


# Define the Operator for the button
class QuickCompOperator(bpy.types.Operator):
    bl_idname = "quick_comp.improve_render"
    bl_label = "Improve Render"
    bl_description = (
        "This will remove all your existing compositing nodes and add new ones"
    )

    def execute(self, context):
        typeSel = bpy.context.scene.quick_comp_props

        if (
            not typeSel.lens_distortion
            and not typeSel.subtle_glare
            and not typeSel.film_grain
        ):
            self.report({"WARNING"}, "No effects selected!")
            return {"FINISHED"}

        bpy.context.scene.use_nodes = True
        tree = bpy.context.scene.node_tree
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
        outputNode.location = (400, 0)

        if (
            typeSel.lens_distortion
            and not typeSel.subtle_glare
            and not typeSel.film_grain
        ):
            lensNode = tree.nodes.new(type="CompositorNodeLensdist")
            lensNode.location = (200, 0)
            lensNode.inputs[2].default_value = 0.01

            links = tree.links
            links.new(renderNode.outputs["Image"], lensNode.inputs["Image"])
            links.new(lensNode.outputs["Image"], outputNode.inputs["Image"])

            print("Quick Comp! [INFO] Lens Distortion applied!")
        if (
            typeSel.subtle_glare
            and not typeSel.lens_distortion
            and not typeSel.film_grain
        ):
            glareNode = tree.nodes.new(type="CompositorNodeGlare")
            glareNode.location = (200, 0)
            glareNode.glare_type = "FOG_GLOW"
            glareNode.quality = "HIGH"
            glareNode.mix = -0.96
            glareNode.threshold = 0
            glareNode.size = 9

            links = tree.links
            links.new(renderNode.outputs["Image"], glareNode.inputs["Image"])
            links.new(glareNode.outputs["Image"], outputNode.inputs["Image"])
        if (
            typeSel.film_grain
            and not typeSel.lens_distortion
            and not typeSel.subtle_glare
        ):
            bpy.data.textures.new("Film Grain QC", type="NOISE")

            textureNode = tree.nodes.new(type="CompositorNodeTexture")
            textureNode.location = (200, 0)
            textureNode.texture = bpy.data.textures["Film Grain QC"]

            blurNode = tree.nodes.new(type="CompositorNodeBlur")
            blurNode.location = (400, 0)
            blurNode.filter_type = "FAST_GAUSS"
            blurNode.size_x = 2
            blurNode.size_y = 2

            mixNode = tree.nodes.new(type="CompositorNodeMixRGB")
            mixNode.location = (600, 0)
            mixNode.blend_type = "OVERLAY"
            mixNode.inputs[0].default_value = 0.1

            outputNode.location = (800, 0)

            links = tree.links
            links.new(textureNode.outputs["Color"], blurNode.inputs["Image"])
            links.new(renderNode.outputs["Image"], mixNode.inputs[1])
            links.new(blurNode.outputs["Image"], mixNode.inputs[2])
            links.new(mixNode.outputs["Image"], outputNode.inputs["Image"])
        if typeSel.lens_distortion and typeSel.subtle_glare and typeSel.film_grain:
            lensNode = tree.nodes.new(type="CompositorNodeLensdist")
            lensNode.location = (200, 0)
            lensNode.inputs[2].default_value = 0.01

            glareNode = tree.nodes.new(type="CompositorNodeGlare")
            glareNode.location = (400, 0)
            glareNode.glare_type = "FOG_GLOW"
            glareNode.quality = "HIGH"
            glareNode.mix = -0.96
            glareNode.threshold = 0
            glareNode.size = 9

            outputNode.location = (600, 0)

            bpy.data.textures.new("Film Grain QC", type="NOISE")

            textureNode = tree.nodes.new(type="CompositorNodeTexture")
            textureNode.location = (-100, 300)
            textureNode.texture = bpy.data.textures["Film Grain QC"]

            blurNode = tree.nodes.new(type="CompositorNodeBlur")
            blurNode.location = (200, 300)
            blurNode.filter_type = "FAST_GAUSS"
            blurNode.size_x = 2
            blurNode.size_y = 2

            mixNode = tree.nodes.new(type="CompositorNodeMixRGB")
            mixNode.location = (400, 300)
            mixNode.blend_type = "OVERLAY"
            mixNode.inputs[0].default_value = 0.1

            links = tree.links
            links.new(renderNode.outputs["Image"], lensNode.inputs["Image"])
            links.new(lensNode.outputs["Image"], outputNode.inputs["Image"])
            links.new(glareNode.outputs["Image"], outputNode.inputs["Image"])
            links.new(textureNode.outputs["Color"], blurNode.inputs["Image"])
            links.new(lensNode.outputs["Image"], mixNode.inputs[1])
            links.new(blurNode.outputs["Image"], mixNode.inputs[2])
            links.new(mixNode.outputs["Image"], glareNode.inputs["Image"])
        if typeSel.lens_distortion and typeSel.subtle_glare and not typeSel.film_grain:
            lensNode = tree.nodes.new(type="CompositorNodeLensdist")
            lensNode.location = (200, 0)
            lensNode.inputs[2].default_value = 0.01

            outputNode.location = (600, 0)

            glareNode = tree.nodes.new(type="CompositorNodeGlare")
            glareNode.location = (400, 0)
            glareNode.glare_type = "FOG_GLOW"
            glareNode.quality = "HIGH"
            glareNode.mix = -0.96
            glareNode.threshold = 0
            glareNode.size = 9

            links = tree.links
            links.new(lensNode.outputs["Image"], glareNode.inputs["Image"])
            links.new(renderNode.outputs["Image"], lensNode.inputs["Image"])
            links.new(glareNode.outputs["Image"], outputNode.inputs["Image"])
        if typeSel.lens_distortion and typeSel.film_grain and not typeSel.subtle_glare:
            lensNode = tree.nodes.new(type="CompositorNodeLensdist")
            lensNode.location = (200, 0)
            lensNode.inputs[2].default_value = 0.01

            bpy.data.textures.new("Film Grain QC", type="NOISE")

            textureNode = tree.nodes.new(type="CompositorNodeTexture")
            textureNode.location = (-100, 300)
            textureNode.texture = bpy.data.textures["Film Grain QC"]

            blurNode = tree.nodes.new(type="CompositorNodeBlur")
            blurNode.location = (200, 300)
            blurNode.filter_type = "FAST_GAUSS"
            blurNode.size_x = 2
            blurNode.size_y = 2

            mixNode = tree.nodes.new(type="CompositorNodeMixRGB")
            mixNode.location = (400, 300)
            mixNode.blend_type = "OVERLAY"
            mixNode.inputs[0].default_value = 0.1

            links = tree.links
            links.new(renderNode.outputs["Image"], lensNode.inputs["Image"])
            links.new(textureNode.outputs["Color"], blurNode.inputs["Image"])
            links.new(blurNode.outputs["Image"], mixNode.inputs[2])
            links.new(lensNode.outputs["Image"], mixNode.inputs[1])
            links.new(mixNode.outputs["Image"], outputNode.inputs["Image"])
        if typeSel.subtle_glare and typeSel.film_grain and not typeSel.lens_distortion:
            glareNode = tree.nodes.new(type="CompositorNodeGlare")
            glareNode.location = (200, 0)
            glareNode.glare_type = "FOG_GLOW"
            glareNode.quality = "HIGH"
            glareNode.mix = -0.96
            glareNode.threshold = 0
            glareNode.size = 9

            bpy.data.textures.new("Film Grain QC", type="NOISE")

            textureNode = tree.nodes.new(type="CompositorNodeTexture")
            textureNode.location = (-100, 300)
            textureNode.texture = bpy.data.textures["Film Grain QC"]

            blurNode = tree.nodes.new(type="CompositorNodeBlur")
            blurNode.location = (200, 300)
            blurNode.filter_type = "FAST_GAUSS"
            blurNode.size_x = 2
            blurNode.size_y = 2

            mixNode = tree.nodes.new(type="CompositorNodeMixRGB")
            mixNode.location = (400, 300)
            mixNode.blend_type = "OVERLAY"
            mixNode.inputs[0].default_value = 0.1

            links = tree.links
            links.new(renderNode.outputs["Image"], mixNode.inputs[1])
            links.new(textureNode.outputs["Color"], blurNode.inputs["Image"])
            links.new(blurNode.outputs["Image"], mixNode.inputs[2])
            links.new(mixNode.outputs["Image"], glareNode.inputs["Image"])
            links.new(glareNode.outputs["Image"], outputNode.inputs["Image"])

        return {"FINISHED"}


# Register and Unregister
classes = [
    QuickCompProperties,
    QuickCompPanel,
    QuickCompOperator,
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
