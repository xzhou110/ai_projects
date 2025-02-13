import math
import time
import pyautogui
from pynput import keyboard

# Global variable to store the center point.
center_point = None

def on_press(key):
    """
    Callback for keyboard events.
    When F9 is pressed, capture the current mouse position as the center point.
    """
    global center_point
    if key == keyboard.Key.f9:
        center_point = pyautogui.position()
        return False  # Stop the listener

def wait_for_center_key() -> tuple:
    """
    Instructs the user to hover over the drawn center point and press F9.
    
    Returns:
        The (x, y) tuple representing the center point.
    """
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()
    return center_point

def draw_circle(center: tuple, radius: float = 100, num_points: int = 200) -> None:
    """
    Simulates drawing a circle by calculating points along its circumference 
    and moving the mouse through them.
    
    Args:
        center: The (x, y) coordinate of the circle's center.
        radius: The circle's radius in pixels.
        num_points: Number of points to calculate along the circumference.
                   More points yield a smoother circle.
    """
    cx, cy = center
    points = []
    for i in range(num_points + 1):
        theta = 2 * math.pi * i / num_points
        x = cx + radius * math.cos(theta)
        y = cy + radius * math.sin(theta)
        points.append((x, y))
    
    # Move the mouse to the starting point.
    start_point = points[0]
    pyautogui.moveTo(start_point[0], start_point[1], duration=0.5)
    
    # Begin drawing: press and hold the mouse button.
    pyautogui.mouseDown()
    # Use moveTo for each intermediate point with a slight delay.
    for point in points[1:]:
        pyautogui.moveTo(point[0], point[1], duration=0.1)
    pyautogui.mouseUp()

def main() -> None:
    # Step 1: Provide instructions.
    pyautogui.alert(
        "INSTRUCTIONS:\n\n"
        "1. Ensure your browser window (with the Pi Day Challenge game) is active.\n"
        "2. Use the game's tool to draw the center point in the drawing area.\n"
        "3. Once done, hover your mouse over the drawn center point and press F9 to capture it.\n"
        "   (Do NOT click the mouse; just press F9.)"
    )
    
    # Step 2: Wait for the user to capture the center point.
    center = wait_for_center_key()
    if center is None:
        pyautogui.alert("No center point was captured. Exiting.")
        return
    
    # Step 3: Confirm the captured center and allow a brief pause.
    pyautogui.alert(
        f"Center point captured at {center}.\n\n"
        "The automated circle drawing will begin in 3 seconds.\n"
        "Please ensure the drawing area remains active."
    )
    time.sleep(3)
    
    # Step 4: Draw the circle with a fixed radius (adjust as needed).
    radius = 100  # Adjust this value as needed.
    draw_circle(center, radius=radius, num_points=500)
    
    # Step 5: Notify completion.
    pyautogui.alert("Circle drawing complete!")

if __name__ == "__main__":
    main()


