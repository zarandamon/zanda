# hip_render_tsk.py in hermes/worker/tasks/hip_render_tsk.py
import hou
import sys

def main():

    # Parse command-line arguments
    if len(sys.argv) < 4:
        print("Usage: hip_render.py <scene_path> <render_node> <frame>")
        sys.exit(1)

    scene_path = sys.argv[1]
    render_node_name = sys.argv[2]
    frame = int(sys.argv[3])

    try:
        # Load the Houdini scene
        print(f"Loading scene: {scene_path}")
        hou.hipFile.load(scene_path)

        # Get the render node
        render_node = hou.node(render_node_name)
        if render_node is None:
            raise RuntimeError(f"Render node '{render_node_name}' not found!")

        # Start rendering
        print(f"Rendering frame {frame} on node {render_node_name}...")
        render_node.render()
        print(f"Render completed for frame {frame}.")

    except Exception as e:
        print(f"Error during rendering: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()