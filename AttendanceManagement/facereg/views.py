import cv2
import pandas as pd
from .simple_facerec import SimpleFacerec
from datetime import datetime
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
import os
def index(request):
    return render(request,'index.html')
def detect_faces(request):
    # Path to save the detection data
    data_file = os.path.join(settings.MEDIA_ROOT, 'detections.xlsx')
    
    # Encode faces from a folder
    sfr = SimpleFacerec()
    sfr.load_encoding_images(os.path.join(settings.MEDIA_ROOT, "images/"))
    
    # Load Camera
    cap = cv2.VideoCapture(0)

    # List to store detection data without repetition
    detection_data = []

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Failed to grab frame")
            break

        # Detect Faces
        face_locations, face_names = sfr.detect_known_faces(frame)

        if face_names:
            print(f"Detected names: {face_names}")  # Debugging: Print detected names in current frame
        else:
            print("No faces detected in this frame.")

        for face_loc, name in zip(face_locations, face_names):
            # Avoid registering the same name multiple times
            if name != "Unknown" and not any(d['Name'] == name for d in detection_data):
                y1, x2, y2, x1 = face_loc[0], face_loc[1], face_loc[2], face_loc[3]

                cv2.putText(frame, name, (x1, y1 - 10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 200), 2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 200), 4)

                # Add the detected name and timestamp to the list
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                detection_data.append({'Name': name, 'Timestamp': timestamp})
                print(f"Recorded: {name} at {timestamp}")  # Debugging: Print recorded name and timestamp

                print(f"Total detections recorded: {len(detection_data)}")  # Debugging: Print total detections

                # Convert to DataFrame and Save to Excel
                df = pd.DataFrame(detection_data)
                try:
                    df.to_excel(data_file, index=False)
                    print("Data successfully saved to detections.xlsx")
                except Exception as e:
                    print(f"Error saving to Excel: {e}")

        # Display the frame (optional)
        cv2.imshow("Frame", frame)

        key = cv2.waitKey(1)
        if key == 27 or key == ord('q'):  # Press ESC or 'q' to quit
            break

    # Release the camera and close windows
    cap.release()
    cv2.destroyAllWindows()

    return HttpResponse(f"Face detection completed. Data saved to {data_file}")



import os
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from .forms import ImageUploadForm

def upload_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Get the uploaded file and user-provided name
            image = form.cleaned_data['image']
            image_name = form.cleaned_data['image_name']
            
            # Create a new file name with the provided name and original file extension
            ext = os.path.splitext(image.name)[1]
            new_filename = f"{image_name}{ext}"
            
            # Save the file to the media/images directory
            image_path = os.path.join(settings.MEDIA_ROOT, 'images', new_filename)
            with open(image_path, 'wb+') as destination:
                for chunk in image.chunks():
                    destination.write(chunk)
            
            return HttpResponse(f"Image successfully uploaded and saved as {new_filename}")

    else:
        form = ImageUploadForm()

    return render(request, 'upload.html', {'form': form})
import base64
import os
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from io import BytesIO
from PIL import Image
import re

@csrf_exempt
def capture_and_save_image(request):
    if request.method == 'POST':
        image_data = request.POST.get('image_data')
        image_name = request.POST.get('image_name')

        # Extract the base64 string and remove the prefix
        image_data = re.sub('^data:image/.+;base64,', '', image_data)
        image_data = base64.b64decode(image_data)

        # Create a new file name with the provided name and .png extension
        new_filename = f"{image_name}.png"
        image_path = os.path.join(settings.MEDIA_ROOT, 'images', new_filename)

        # Save the image data to a file
        with open(image_path, 'wb') as file:
            file.write(image_data)

        return HttpResponse(f"Image successfully captured and saved as {new_filename}")

    return render(request, 'capture.html')
