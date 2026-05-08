import os
import bpy
from flask import Flask, request, render_template, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import time

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'static/uploads'
RENDER_FOLDER = 'static/renders'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RENDER_FOLDER'] = RENDER_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RENDER_FOLDER, exist_ok=True)

def render_model(model_path, output_path):
    # Clear existing objects
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # Import the model
    ext = os.path.splitext(model_path)[1].lower()
    try:
        if ext == '.obj':
            bpy.ops.wm.obj_import(filepath=model_path)
        elif ext == '.stl':
            bpy.ops.wm.stl_import(filepath=model_path)
        elif ext in ['.glb', '.gltf']:
            bpy.ops.import_scene.gltf(filepath=model_path)
        elif ext == '.fbx':
            bpy.ops.import_scene.fbx(filepath=model_path)
        else:
            return False, f"Unsupported format: {ext}"
    except Exception as e:
        return False, str(e)

    # Set up basic scene
    # Add a light
    bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))

    # Add a camera
    bpy.ops.object.camera_add(location=(7, -7, 7), rotation=(1.1, 0, 0.785))
    bpy.context.scene.camera = bpy.context.object

    # Center objects and scale if needed (simplistic)
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)

    # Select all meshes and center camera on them if we had a more complex script,
    # but for now let's just render.

    # Render settings
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.device = 'CPU'
    bpy.context.scene.render.filepath = output_path

    # Render
    bpy.ops.render.render(write_still=True)
    return True, "Success"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    render_filename = f"render_{int(time.time())}.png"
    render_path = os.path.join(app.config['RENDER_FOLDER'], render_filename)

    success, message = render_model(filepath, render_path)

    if success:
        return {"render_url": f"/static/renders/{render_filename}"}, 200
    else:
        return {"error": message}, 500

if __name__ == '__main__':
    # Flask with threading can cause issues with bpy, so we run it single-threaded
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=False)
