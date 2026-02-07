# // [TEST]: Face recognition diagnostic script
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from deepface import DeepFace
import cv2

print("[TEST] Loading yadveer.png...")
img_path = "known_faces/yadveer.png"

# Test 1: Same image should verify
print("\n[TEST 1] Same image verification...")
try:
    r = DeepFace.verify(img_path, img_path, model_name='VGG-Face', enforce_detection=False)
    print(f"  Result: verified={r['verified']}, distance={r['distance']:.4f}, threshold={r['threshold']:.4f}")
except Exception as e:
    print(f"  ERROR: {e}")

# Test 2: Check if face is detected in the image
print("\n[TEST 2] Face detection in reference image...")
try:
    faces = DeepFace.extract_faces(img_path, detector_backend='retinaface', enforce_detection=False)
    print(f"  Faces found: {len(faces)}")
    for i, f in enumerate(faces):
        print(f"  Face {i}: confidence={f.get('confidence', 'N/A')}")
except Exception as e:
    print(f"  ERROR: {e}")

# Test 3: Simulate webcam crop (small image)
print("\n[TEST 3] Simulating webcam head crop...")
try:
    img = cv2.imread(img_path)
    h, w = img.shape[:2]
    # Take upper 60% as "head crop"
    head_crop = img[0:int(h*0.6), :]
    cv2.imwrite("_test_head_crop.jpg", head_crop)
    
    r = DeepFace.verify("_test_head_crop.jpg", img_path, model_name='VGG-Face', enforce_detection=False, detector_backend='retinaface')
    print(f"  Result: verified={r['verified']}, distance={r['distance']:.4f}")
    os.remove("_test_head_crop.jpg")
except Exception as e:
    print(f"  ERROR: {e}")

print("\n[TEST COMPLETE]")
