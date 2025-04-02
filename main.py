# main.py
import cv2
from menu import show_menu
from game import update_game, reset_game, start_sound, cap

def main():
    while True:
        reset_game()
        
        # Show menu and wait for the user to start the game
        if show_menu():  # If play button is pressed, return True and start the game
            start_sound.play()  # Ensure start sound plays, can remove this if unnecessary

            while True:
                success, frame = update_game()  # Update the game logic
                if not success:  # If the game ends (game over), break the loop
                    break
                
                if cv2.waitKey(1) & 0xFF == ord('q'):  # Allows to quit early by pressing 'q'
                    break
        else:
            print("Exiting the game.")
            break 

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
