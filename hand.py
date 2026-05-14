import cv2
import numpy as np
import pyautogui
import mediapipe as mp
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import time

volume = None
try:
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
except Exception as e:
    print(f"Audio initialization failed: {e}")

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1)
finger_tips = [4, 8, 12, 16, 20]

cap = cv2.VideoCapture(0)
screen_w, screen_h = pyautogui.size()
vol_status = "Normal"
prev_pinch_distance = None

def get_landmark_coords(landmarks, idx, width, height):
    return int(landmarks.landmark[idx].x * width), int(landmarks.landmark[idx].y * height)

def get_finger_states(landmarks):
    fingers = []
    if landmarks.landmark[4].x < landmarks.landmark[3].x:
        fingers.append(1)
    else:
        fingers.append(0)
    for tip in finger_tips[1:]:
        if landmarks.landmark[tip].y < landmarks.landmark[tip - 2].y:
            fingers.append(1)
        else:
            fingers.append(0)
    return fingers

def select_by_middle_thumb_pinch(middle_x, middle_y, thumb_x, thumb_y, frame):
    distance = math.hypot(middle_x - thumb_x, middle_y - thumb_y)
    if distance < 30:
        pyautogui.click()
        cv2.putText(frame, "Select (Middle-Thumb Pinch)", (10, 250),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 0), 2)
        time.sleep(0.3)
    return frame

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            fingers = get_finger_states(hand_landmarks)

            if fingers == [0, 0, 1, 0, 0]:
                cv2.putText(frame, "Middle Finger Detected - Exiting", (10, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
                cv2.imshow("Hand Gesture Control", frame)
                cv2.waitKey(1500)
                cap.release()
                cv2.destroyAllWindows()
                exit()

            index_x, index_y = get_landmark_coords(hand_landmarks, 8, w, h)
            thumb_x, thumb_y = get_landmark_coords(hand_landmarks, 4, w, h)
            middle_x, middle_y = get_landmark_coords(hand_landmarks, 12, w, h)

            pyautogui.moveTo(screen_w * (index_x / w), screen_h * (index_y / h), duration=0.1)

            pinch_distance = math.hypot(index_x - thumb_x, index_y - thumb_y)
            
            if pinch_distance < 30:
                if volume:
                    volume.SetMute(1, None)
                vol_status = "Muted"
                cv2.putText(frame, "Muted (Pinch Gesture)", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
            elif pinch_distance > 100:
                if volume:
                    volume.SetMute(0, None)
                    current_volume = volume.GetMasterVolumeLevel()
                    min_vol = volume.GetVolumeRange()[0]
                    new_volume = current_volume + 0.5
                    new_volume = min(new_volume, min_vol + 15)
                    volume.SetMasterVolumeLevel(new_volume, None)
                vol_status = "Volume Up"
                cv2.putText(frame, "Volume Up (Spread Fingers)", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            else:
                vol_status = "Normal"
                if prev_pinch_distance is not None and volume:
                    volume.SetMute(0, None)
                    
                    change = prev_pinch_distance - pinch_distance
                    if abs(change) > 5:
                        current_volume = volume.GetMasterVolumeLevel()
                        vol_range = volume.GetVolumeRange()
                        min_vol, max_vol = vol_range[0], vol_range[1]
                        
                        delta = change * (max_vol - min_vol) / 200
                        new_volume = current_volume + delta
                        new_volume = max(min_vol, min(max_vol, new_volume))
                        volume.SetMasterVolumeLevel(new_volume, None)
                        
                        vol_percent = int((new_volume - min_vol) / (max_vol - min_vol) * 100)
                        cv2.putText(frame, f"Volume: {vol_percent}%", (10, 100), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 0), 2)

            frame = select_by_middle_thumb_pinch(middle_x, middle_y, thumb_x, thumb_y, frame)

    cv2.putText(frame, f"Volume: {vol_status}", (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Hand Gesture Control", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    prev_pinch_distance = pinch_distance if 'pinch_distance' in dir() else None

cap.release()
cv2.destroyAllWindows()