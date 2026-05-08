import bpy

def main():
    # Clear existing objects
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # Create a new cube
    bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', location=(0, 0, 0))

    # List all objects in the scene
    print("Objects in the scene:")
    for obj in bpy.data.objects:
        print(f"- {obj.name}")

if __name__ == "__main__":
    main()
