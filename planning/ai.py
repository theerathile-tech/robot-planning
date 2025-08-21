from ultralytics import YOLO
from transformers import pipeline
import cv2
from PIL import Image
import numpy as np
import os

model = None
pipe = None

def init_ai():
    global model, pipe
    try:
        model = YOLO("best.pt")
        pipe = pipeline(task="depth-estimation", model="depth-anything/Depth-Anything-V2-Base-hf")
        
        print("AI components initialized successfully")
        return True
        
    except Exception as e:
        print(f"Failed to initialize AI: {e}")
        return False

def convert_opencv_to_pil(opencv_image):
    rgb_image = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(rgb_image)
    return pil_image

def check_location(x_min, y_min, x_max, y_max, frame_width, frame_height):
    object_center_x = (x_min + x_max) // 2
    object_center_y = (y_min + y_max) // 2
    
    frame_center_x = frame_width // 2
    frame_center_y = frame_height // 2
    
    margin_of_error = 10
    
    if object_center_x < frame_center_x - margin_of_error:
        return "left"
    elif object_center_x > frame_center_x + margin_of_error:
        return "right"
    else:
        return "front"

def capture_surroundings():
    current_directory = os.getcwd()
    image_filename = os.path.join(current_directory, "captured_image.jpg")
    
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    if ret:
        cv2.imwrite(image_filename, frame)
        print(f"Image saved to {image_filename}")
    else:
        print("Failed to capture image")
    cap.release()

    return image_filename

def scan_mode():
    global model, pipe

    if model is None:
        print("AI model not initialized")
        return None

    if pipe is None:
        print("Depth estimation pipeline not initialized")
        return None
    
    try:
        image_path = capture_surroundings()
        frame = cv2.imread(image_path)
        
        if frame is None:
            print("Error: Unable to read captured image")
            return None

        results = model(frame)
        names = model.names
        frame_height, frame_width, _ = frame.shape
        
        detected_objects = []
    
        for result in results:
            for box in result.boxes:
                coordinates = box.xyxy
                name = names[int(box.cls)]
                x_min, y_min, x_max, y_max = coordinates[0][0].item(), coordinates[0][1].item(), coordinates[0][2].item(), coordinates[0][3].item()
                
                position = check_location(int(x_min), int(y_min), int(x_max), int(y_max), frame_width, frame_height)
                
                image_crop = frame[int(y_min):int(y_max), int(x_min):int(x_max)]
                if image_crop.size > 0:
                    pil_image = convert_opencv_to_pil(image_crop)
                    depth_map = pipe(pil_image)["depth"]
                    depth_array = np.array(depth_map)  
                    mean_depth = np.median(depth_array)
                    
                    detected_objects.append({
                        'name': name,
                        'depth': mean_depth,
                        'position': position,
                        'coordinates': (x_min, y_min, x_max, y_max)
                    })
        
        return detected_objects

    except Exception as e:
        print(f"Error in scan_mode: {e}")
        import traceback
        traceback.print_exc()
        return None

def cleanup_ai():
    cv2.destroyAllWindows()
