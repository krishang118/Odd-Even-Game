# Odd-Even Game

A real-time hand gesture recognition odd-even game where players compete against the computer using finger counting. Built with Python, OpenCV, MediaPipe, and Streamlit, featuring ultra-fast response detection, dark neon aesthetics, and continuous gameplay scoring.

## Features

- Real-time Hand Detection using MediaPipe
- Ultra-fast Response Time tracking (0.67s window)
- Dark Theme with neon aesthetics
- Live Score Display 
- Continuous Gameplay with smooth transitions
- Responsive Layout with side-by-side camera feed
- Accurate Finger Counting algorithm

## Game Rules

1. Choose Your Side: Select ODD or EVEN at the start
2. Wait for the Countdown.
3. Quick Response: Computer shows a number (1-5), you have 0.67 seconds to show 1-5 fingers
4. Win Condition: 
   - If the sum is ODD and you chose ODD → You Win!
   - If the sum is EVEN and you chose EVEN → You Win!
   - Otherwise, Computer Wins!
5. Score Tracking: First to dominate wins!

## How It Works

### Hand Detection
- Uses MediaPipe Hands for real-time hand landmark detection
- Tracks 21 hand landmarks with high accuracy
- Optimized for low latency (model_complexity=0)

### Finger Counting Algorithm
```python
# Thumb: Check if tip is left of knuckle
# Fingers: Check if tip is above middle joint
fingers = 0
if thumb_tip.x < thumb_knuckle.x: fingers += 1
for each_finger:
    if tip.y < middle_joint.y: fingers += 1
```

### Technical Stack

- Frontend: Streamlit (Web UI)
- Computer Vision: OpenCV + MediaPipe
- Hand Detection: MediaPipe Hands Solution
- Language: Python 3.8+
- Styling: Custom CSS with dark theme

## How To Run

1. Make sure you have Python 3.8+ installed, with the laptop/computer having a webcam/camera set up.
2. Clone this repository on your local machine.
3. Install the required dependencies:
```bash
pip install streamlit opencv-python mediapipe numpy Pillow
```
4. Run the game:
```bash
streamlit run OddEvenGame.py
```

## Contributing

Contributions are welcome!

## License

Distributed under the MIT License. 
