import cv2
import numpy as np
import random
import pygame

# sounds
pygame.mixer.init()

jump_sound = pygame.mixer.Sound('sounds/jump.wav')
game_over_sound = pygame.mixer.Sound('sounds/game_over.mp3')
start_sound = pygame.mixer.Sound('sounds/start.wav')
pygame.mixer.music.load('sounds/background.mp3')
pygame.mixer.music.set_volume(0.1)
pygame.mixer.music.play(-1, 0.0)

# load Haar Cascade classifier for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# initialize the webcam for capturing video
cap = cv2.VideoCapture(0)

# get webcam dimensions
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(f"Webcam resolution: {frame_width}x{frame_height}")

# GAME VARIABLES
player_width, player_height = 50, 50 
player_velocity = 0
fall_force = 1
jump_strength = -20
scroll_offset = 200
score = 0 
on_platform = True

# player position
player_x = 0
player_y = 0

# platform setup
platform_width, platform_height = 80, 20  
min_platform_gap_y = 80
max_platform_gap_y = 100
screen_width = frame_width
screen_height = frame_height

# sprites
player_sprite = cv2.imread('img/character_bato.png', cv2.IMREAD_UNCHANGED)
platform_sprite = cv2.imread('img/platform.png', cv2.IMREAD_UNCHANGED)
player_sprite = cv2.resize(player_sprite, (player_width, player_height))
platform_sprite = cv2.resize(platform_sprite, (platform_width, platform_height))

initial_platform = (screen_width // 2 - platform_width // 2, screen_height - platform_height) 
platforms = [initial_platform]

# Function to overlay a sprite (player/platform) onto a frame
def overlay_sprite(frame, sprite, x, y):
    sprite_height, sprite_width, _ = sprite.shape

    # Ensure the sprite fits within the frame boundaries
    if x + sprite_width > frame.shape[1] or y + sprite_height > frame.shape[0]:
        return frame

    # Separate the color (RGB) and alpha channels
    # For transparency and blending
    sprite_color = sprite[:, :, :3]
    sprite_alpha = sprite[:, :, 3]

    # Extract the region of interest (ROI) in the frame where the sprite will be placed
    roi = frame[y:y+sprite_height, x:x+sprite_width]

    # Blend the sprite with the frame using the alpha channel
    for c in range(3): 
        roi[:, :, c] = roi[:, :, c] * (1 - sprite_alpha / 255.0) + sprite_color[:, :, c] * (sprite_alpha / 255.0)

    frame[y:y+sprite_height, x:x+sprite_width] = roi
    return frame

def generate_platform_above(last_platform_y):
    new_x = random.randint(50, screen_width - platform_width)
    new_y = last_platform_y - random.randint(min_platform_gap_y, max_platform_gap_y) 
    return (new_x, new_y)

def detect_face_and_move_player(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    if len(faces) > 0:
        faces = sorted(faces, key=lambda x: x[2] * x[3], reverse=True)
        (x, y, w, h) = faces[0]

        # player's horizontal position
        player_x = x + w // 2 - player_width // 2

        # Clip the player's position to stay within screen boundaries
        player_x = np.clip(player_x, 0, frame.shape[1] - player_width)
        return player_x
    
    return None 

def show_menu():
    pygame.init()
    screen = pygame.display.set_mode((400, 300))
    pygame.display.set_caption("Game Menu")

    # Load sprites
    title_sprite = pygame.image.load('img/title.png')
    play_button_sprite = pygame.image.load('img/play.png')
    exit_button_sprite = pygame.image.load('img/cancel.png')

    title_sprite = pygame.transform.scale(title_sprite, (180, 100))
    play_button_sprite = pygame.transform.scale(play_button_sprite, (110, 35))
    exit_button_sprite = pygame.transform.scale(exit_button_sprite, (110, 35))

    # Calculate center position for buttons and title
    title_x = (screen.get_width() - title_sprite.get_width()) // 2
    play_button_x = (screen.get_width() - 100) // 2
    exit_button_x = (screen.get_width() - 100) // 2
    title_y = 30 
    play_button_y = 160
    exit_button_y = 220

    title_rect = pygame.Rect(title_x, title_y, title_sprite.get_width(), title_sprite.get_height())
    play_button_rect = pygame.Rect(play_button_x, play_button_y, 100, 50)
    exit_button_rect = pygame.Rect(exit_button_x, exit_button_y, 100, 50)

    while True:
        screen.fill((255, 255, 255))

        # Add the elements
        screen.blit(title_sprite, title_rect.topleft)
        screen.blit(play_button_sprite, play_button_rect.topleft)
        screen.blit(exit_button_sprite, exit_button_rect.topleft)

        pygame.display.flip()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button_rect.collidepoint(event.pos):
                    return True
                elif exit_button_rect.collidepoint(event.pos):
                    pygame.quit()
                    return False 

# Function to reset game state
def reset_game():
    global player_x, player_y, player_velocity, score, platforms, on_platform
    player_x = 0
    player_y = 0
    player_velocity = 0
    score = 0
    platforms = [initial_platform]
    on_platform = True
    pygame.mixer.music.play(-1, 0.0)

# function for the gameplay
def update_game():
    global player_x, player_y, player_velocity, score, platforms, on_platform

    # Capture a new frame from the webcam
    ret, frame = cap.read()
    if not ret:
        return False, frame

    frame = cv2.flip(frame, 1)

    # Detect face and move player accordingly
    detected_player_x = detect_face_and_move_player(frame)
    if detected_player_x is not None:
        player_x = detected_player_x

    if not on_platform:
        player_velocity += fall_force
        player_y += player_velocity

    # Check for collisions with platforms
    on_platform = False
    for px, py in platforms:
        if px < player_x + player_width and px + platform_width > player_x:
            if player_y + player_height <= py and player_y + player_height + player_velocity >= py:
                # Player hits the platform, perform a jump
                player_velocity = jump_strength
                player_y = py - player_height
                on_platform = True
                jump_sound.play()
                break

    # Follow camera or screen view
    if player_y < scroll_offset:
        diff = scroll_offset - player_y
        player_y += diff
        platforms = [(px, py + diff) for px, py in platforms]
        score += diff

        # Generate new platforms above the screen as needed
        while platforms[-1][1] > 0:
            platforms.append(generate_platform_above(platforms[-1][1]))


    # Remove platforms that go below the screen view
    platforms = [p for p in platforms if p[1] >= 0]

    # GAME OVER
    if player_y > screen_height: 
        pygame.mixer.music.stop()
        game_over_sound.play()
        cv2.putText(frame, "GAME OVER", (180, 240), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
        cv2.putText(frame, f"Final Score: {score}", (180, 280), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.imshow('Doodle Jump', frame)
        cv2.waitKey(2000)
        cv2.destroyWindow('Doodle Jump')
        return False, frame

    # Overlay the player sprite on the frame
    try:
        frame = overlay_sprite(frame, player_sprite, player_x, player_y)
    except Exception as e:
        print(f"Error with player position: x={player_x}, y={player_y} - {e}")

    # Overlay platform sprites on the frame
    for px, py in platforms:
        try:
            frame = overlay_sprite(frame, platform_sprite, px, py)
        except Exception as e:
            print(f"Error with platform position: x={px}, y={py} - {e}")

    # Display the current score on the screen
    cv2.putText(frame, f'Score: {score}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    cv2.imshow('Doodle Jump', frame)
    return True, frame

# Main game loop
while True:
    reset_game() 
    if show_menu():
        start_sound.play()
        
        while True:
            success, frame = update_game()
            if not success:
                break 
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    else:
        break

cap.release()
cv2.destroyAllWindows()
