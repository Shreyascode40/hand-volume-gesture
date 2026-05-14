# Hand Gesture Volume Control

**Author:** Shreyas

Control your system volume using hand gestures via webcam.

## Features
- Volume control by pinch distance
- Mute/unmute with pinch gesture
- Mouse cursor control with index finger
- Click with middle finger + thumb pinch
- Exit with middle finger up

## Requirements
```
opencv-python
mediapipe
pyautogui
pycaw
numpy
comtypes
```

## Installation
```bash
pip install opencv-python mediapipe pyautogui pycaw numpy comtypes
```

## Usage
```bash
python hand.py
```

## Controls
| Gesture | Action |
|---------|--------|
| Pinch (thumb + index close) | Mute |
| Drag pinch apart | Adjust volume |
| Move hand | Control cursor |
| Middle + thumb pinch | Click |
| Middle finger up | Exit |

## Gesture Reference
![Hand landmarks](https://mediapipe.readthedocs.io/en/latest/solutions/hands.html)

21 hand landmarks are detected for tracking finger positions.