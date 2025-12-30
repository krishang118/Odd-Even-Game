import streamlit as st
import cv2
import mediapipe as mp
import random
import time
import numpy as np
from PIL import Image
st.set_page_config(
    page_title="Odd-Even Game",
    layout="wide")
st.markdown("""
<style>
    .stApp {
        background-color: #0a0e27;
        overflow: hidden;
    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 1rem;
        max-width: 100%;
    }
    .main-title {
        text-align: center;
        color: #00fff2;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
        text-shadow: 0 0 20px #00fff2;
    }
    .score-display {
        text-align: center;
        color: #00fff2;
        font-size: 5rem;
        font-weight: bold;
        font-family: 'Courier New', monospace;
        margin: 2rem 0;
        text-shadow: 0 0 30px #00fff2;
    }
    .game-status {
        text-align: center;
        color: #e0e0e0;
        font-size: 1.8rem;
        margin: 1rem 0;
    }
    .countdown {
        text-align: center;
        color: #00fff2;
        font-size: 8rem;
        font-weight: bold;
        text-shadow: 0 0 50px #00fff2;
        margin: 3rem 0;
    }
    .computer-number {
        text-align: center;
        color: #ff0055;
        font-size: 10rem;
        font-weight: bold;
        text-shadow: 0 0 50px #ff0055;
        margin: 2rem 0;
    }
    .result-win {
        text-align: center;
        color: #00ff88;
        font-size: 3rem;
        font-weight: bold;
        text-shadow: 0 0 40px #00ff88;
        margin: 2rem 0;
    }
    .result-lose {
        text-align: center;
        color: #ff0055;
        font-size: 3rem;
        font-weight: bold;
        text-shadow: 0 0 40px #ff0055;
        margin: 2rem 0;
    }
    .finger-count {
        text-align: center;
        color: #00fff2;
        font-size: 1.5rem;
        margin: 1rem 0;
    }
    .penalty-text {
        text-align: center;
        color: #ff0055;
        font-size: 2.5rem;
        font-weight: bold;
        margin: 2rem 0;
    }
    .camera-section {
        background-color: #0f1535;
        border: 2px solid #00fff2;
        border-radius: 15px;
        padding: 1rem;
        box-shadow: 0 0 30px rgba(0, 255, 242, 0.3);
    }
    .camera-title {
        text-align: center;
        color: #00fff2;
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .stButton>button {
        background-color: #1a1f3a;
        color: #00fff2;
        border: 2px solid #00fff2;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-size: 1.2rem;
        font-weight: bold;
        transition: all 0.3s;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #00fff2;
        color: #0a0e27;
        box-shadow: 0 0 20px #00fff2;
    }
    [data-testid="stVerticalBlock"] {
        gap: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)
@st.cache_resource
def load_mediapipe():
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5)
    return mp_hands, hands
mp_hands, hands = load_mediapipe()
mp_draw = mp.solutions.drawing_utils
def count_fingers(landmarks):
    if not landmarks:
        return 0    
    fingers = 0    
    if landmarks[4].x < landmarks[3].x:
        fingers += 1
    tip_ids = [8, 12, 16, 20]
    pip_ids = [6, 10, 14, 18]
    for tip, pip in zip(tip_ids, pip_ids):
        if landmarks[tip].y < landmarks[pip].y:
            fingers += 1
    return fingers
if 'game_state' not in st.session_state:
    st.session_state.game_state = 'setup'
    st.session_state.user_choice = None
    st.session_state.countdown = 3
    st.session_state.computer_number = None
    st.session_state.user_fingers = 0
    st.session_state.score_user = 0
    st.session_state.score_computer = 0
    st.session_state.round_result = None
    st.session_state.response_time = None
    st.session_state.number_display_time = None
    st.session_state.has_responded = False
    st.session_state.penalty_reason = ""
    st.session_state.last_countdown_update = time.time()
    st.session_state.result_display_time = None
    st.session_state.camera_active = False
    st.session_state.camera = None
    st.session_state.stop_camera_loop = False
st.markdown('<h1 class="main-title">Odd-Even Game</h1>', unsafe_allow_html=True)
left_col, right_col = st.columns([1, 1])
with left_col:
    left_content = st.empty()
    button_container = st.empty()
with right_col:
    st.markdown('<div class="camera-section">', unsafe_allow_html=True)
    st.markdown('<div class="camera-title">Camera Feed</div>', unsafe_allow_html=True)
    camera_placeholder = st.empty()
    finger_count_placeholder = st.empty()
    st.markdown('</div>', unsafe_allow_html=True)
def render_left_column():
    if st.session_state.game_state == 'setup':
        with left_content.container():
            st.markdown('<div class="game-status">Choose your side:</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("ODD", key="btn_odd"):
                    st.session_state.user_choice = 'odd'
                    st.session_state.game_state = 'countdown'
                    st.session_state.countdown = 3
                    st.session_state.last_countdown_update = time.time()
                    st.session_state.camera_active = True
                    st.session_state.stop_camera_loop = False
                    st.rerun()
            with col_b:
                if st.button("EVEN", key="btn_even"):
                    st.session_state.user_choice = 'even'
                    st.session_state.game_state = 'countdown'
                    st.session_state.countdown = 3
                    st.session_state.last_countdown_update = time.time()
                    st.session_state.camera_active = True
                    st.session_state.stop_camera_loop = False
                    st.rerun()
    elif st.session_state.game_state == 'stopped':
        with left_content.container():
            st.markdown(
                f'<div class="result-win">Final Score: {st.session_state.score_user}:{st.session_state.score_computer}</div>',
                unsafe_allow_html=True)
        with button_container.container():
            if st.button("New Game", key="btn_new_game"):
                st.session_state.game_state = 'setup'
                st.session_state.score_user = 0
                st.session_state.score_computer = 0
                st.session_state.user_choice = None
                st.rerun()
def render_buttons():
    if st.session_state.game_state in ['countdown', 'playing']:
        with button_container.container():
            if st.button("Stop Game", key="btn_stop_active"):
                st.session_state.stop_camera_loop = True
                st.session_state.camera_active = False
                if st.session_state.camera:
                    st.session_state.camera.release()
                    st.session_state.camera = None
                st.session_state.game_state = 'stopped'
                st.rerun()
    elif st.session_state.game_state == 'result':
        with button_container.container():
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Next Round", key="btn_next"):
                    st.session_state.game_state = 'countdown'
                    st.session_state.countdown = 3
                    st.session_state.last_countdown_update = time.time()
            with col2:
                if st.button("", key="btn_stop_result"):
                    st.session_state.stop_camera_loop = True
                    st.session_state.camera_active = False
                    if st.session_state.camera:
                        st.session_state.camera.release()
                        st.session_state.camera = None
                    st.session_state.game_state = 'stopped'
                    st.rerun()
    elif st.session_state.game_state == 'penalty':
        with button_container.container():
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Retry", key="btn_retry"):
                    st.session_state.game_state = 'countdown'
                    st.session_state.countdown = 3
                    st.session_state.last_countdown_update = time.time()
            with col2:
                if st.button("Stop", key="btn_stop_penalty"):
                    st.session_state.stop_camera_loop = True
                    st.session_state.camera_active = False
                    if st.session_state.camera:
                        st.session_state.camera.release()
                        st.session_state.camera = None
                    st.session_state.game_state = 'stopped'
                    st.rerun()
render_left_column()
render_buttons()
if st.session_state.camera_active and not st.session_state.stop_camera_loop:
    if st.session_state.camera is None:
        st.session_state.camera = cv2.VideoCapture(0)
        st.session_state.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        st.session_state.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        st.session_state.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        time.sleep(0.5)    
    cap = st.session_state.camera
    if cap and cap.isOpened():
        while st.session_state.camera_active and not st.session_state.stop_camera_loop:
            ret, frame = cap.read()            
            if not ret:
                break            
            frame = cv2.flip(frame, 1)            
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb_frame.flags.writeable = False
            results = hands.process(rgb_frame)
            rgb_frame.flags.writeable = True
            finger_count = 0
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_draw.draw_landmarks(
                        frame, 
                        hand_landmarks, 
                        mp_hands.HAND_CONNECTIONS,
                        mp_draw.DrawingSpec(color=(0, 255, 242), thickness=3, circle_radius=3),
                        mp_draw.DrawingSpec(color=(0, 255, 136), thickness=3))
                    finger_count = count_fingers(hand_landmarks.landmark)            
            if st.session_state.game_state == 'countdown':
                if time.time() - st.session_state.last_countdown_update >= 1.0:
                    st.session_state.countdown -= 1
                    st.session_state.last_countdown_update = time.time()
                    if st.session_state.countdown < 0:
                        st.session_state.game_state = 'playing'
                        st.session_state.computer_number = random.randint(1, 5)
                        st.session_state.number_display_time = time.time()
                        st.session_state.has_responded = False
                countdown_text = str(st.session_state.countdown) if st.session_state.countdown > 0 else "GO!"
                with left_content.container():
                    st.markdown(
                        f'<div class="score-display">{st.session_state.score_user}:{st.session_state.score_computer}</div>',
                        unsafe_allow_html=True)
                    st.markdown(
                        f'<div class="game-status">Playing: {st.session_state.user_choice.upper()}</div>',
                        unsafe_allow_html=True)
                    st.markdown(f'<div class="countdown">{countdown_text}</div>', unsafe_allow_html=True)
            elif st.session_state.game_state == 'playing':
                elapsed = time.time() - st.session_state.number_display_time
                remaining = max(0, 0.67 - elapsed)                
                if not st.session_state.has_responded and 1 <= finger_count <= 5 and elapsed <= 0.67:
                    st.session_state.user_fingers = finger_count
                    st.session_state.response_time = elapsed
                    st.session_state.has_responded = True
                    total = st.session_state.computer_number + st.session_state.user_fingers
                    is_odd = total % 2 == 1
                    user_wins = (is_odd and st.session_state.user_choice == 'odd') or \
                               (not is_odd and st.session_state.user_choice == 'even')
                    if user_wins:
                        st.session_state.score_user += 1
                        st.session_state.round_result = 'win'
                    else:
                        st.session_state.score_computer += 1
                        st.session_state.round_result = 'lose'
                    st.session_state.game_state = 'result'
                    st.session_state.result_display_time = time.time()
                elif elapsed > 0.67 and not st.session_state.has_responded:
                    st.session_state.penalty_reason = "Too slow. No response in 0.67 seconds."
                    st.session_state.game_state = 'penalty'
                    st.session_state.has_responded = True
                with left_content.container():
                    st.markdown(
                        f'<div class="score-display">{st.session_state.score_user}:{st.session_state.score_computer}</div>',
                        unsafe_allow_html=True)
                    st.markdown(
                        f'<div class="game-status">Playing: {st.session_state.user_choice.upper()}</div>',
                        unsafe_allow_html=True)
                    st.markdown(
                        f'<div class="computer-number">{st.session_state.computer_number}</div>',
                        unsafe_allow_html=True)
                    if remaining > 0:
                        st.progress(remaining / 0.67)
                        st.markdown('<div class="game-status">Show 1-5 fingers!</div>', unsafe_allow_html=True)
            elif st.session_state.game_state == 'result':
                if st.session_state.result_display_time and time.time() - st.session_state.result_display_time >= 3.0:
                    st.session_state.game_state = 'countdown'
                    st.session_state.countdown = 3
                    st.session_state.last_countdown_update = time.time()
                total = st.session_state.computer_number + st.session_state.user_fingers
                is_odd = total % 2 == 1
                result_type = "ODD" if is_odd else "EVEN"
                with left_content.container():
                    st.markdown(
                        f'<div class="score-display">{st.session_state.score_user}:{st.session_state.score_computer}</div>',
                        unsafe_allow_html=True)
                    st.markdown(
                        f'<div class="game-status">Playing: {st.session_state.user_choice.upper()}</div>',
                        unsafe_allow_html=True)
                    st.markdown(
                        f'<div class="game-status">Computer: {st.session_state.computer_number} + You: {st.session_state.user_fingers} = {total} ({result_type})</div>',
                        unsafe_allow_html=True)
                    if st.session_state.round_result == 'win':
                        st.markdown('<div class="result-win">You Win!</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="result-lose">Computer Wins!</div>', unsafe_allow_html=True)
                    st.markdown(
                        f'<div class="finger-count">Response time: {st.session_state.response_time:.3f}s</div>',
                        unsafe_allow_html=True)
            elif st.session_state.game_state == 'penalty':
                with left_content.container():
                    st.markdown(
                        f'<div class="score-display">{st.session_state.score_user}:{st.session_state.score_computer}</div>',
                        unsafe_allow_html=True)
                    st.markdown(
                        f'<div class="game-status">Playing: {st.session_state.user_choice.upper()}</div>',
                        unsafe_allow_html=True)
                    st.markdown('<div class="penalty-text">NO!</div>', unsafe_allow_html=True)
                    st.markdown(
                        f'<div class="game-status">{st.session_state.penalty_reason}</div>',
                        unsafe_allow_html=True)            
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            camera_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)
            finger_count_placeholder.markdown(
                f'<div class="finger-count">Detected: {finger_count} finger{"s" if finger_count != 1 else ""}</div>',
                unsafe_allow_html=True)
            time.sleep(0.033)
    else:
        camera_placeholder.markdown('<div class="game-status">Camera will activate when game starts...</div>', unsafe_allow_html=True)
else:
    camera_placeholder.markdown('<div class="game-status">Camera will activate when game starts...</div>', unsafe_allow_html=True)