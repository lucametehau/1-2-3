import pytesseract
from PIL import Image, ImageDraw
import re
import pyautogui
import time
import cv2
import numpy as np

# here set your own Tesseract PATH pls, if not in PATH
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def preprocess_image_for_ocr(img_path: str) -> cv2.typing.MatLike:
    """
    Preprocesses the image for better OCR results.

    Args:
    - img_path: str, the path of the input image.

    Returns:
    - preprocessed_image: the preprocessed image ready for OCR.
    """

    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite('test3.png', gray)

    return gray

def preprocess_expression(text: str) -> str:
    """
    Preprocesses an expresion, accounting for the mistakes of OCR

    Args:
    - text: str, the expression as a string

    Returns:
    - processed_text: str, the processed expression
    """
    # cursed processing, still not fully fixed
    good_text = ''
    for (i, ch) in enumerate(text):
        if ch == '5':
            if (len(good_text) == 0 or not good_text[i - 1].isdigit()): ch = '3'
            else: ch = '+'
        elif ch == '4': ch = '+'
        good_text += ch

    text = good_text
    good_text = ''
    for (i, ch) in enumerate(text):
        if ch == '+' and i > 0 and text[i - 1] == '+': continue
        good_text += ch

    text = good_text
    while not text[-1].isdigit(): text = text[:-1]

    return text

# print(preprocess_expression('1-1-145+3-3=?'))
# print(preprocess_expression('14+14+2-354+3-1=?'))

# exit(0)

def solve_expression_in_region(image_path: str, region: tuple[int, int, int, int]) -> str | int | None:
    """
    Solves a simple arithmetic expression within a specific region of the image.

    Args:
    - image_path: str, path to the image file.
    - region: tuple, a tuple specifying (left, top, right, bottom) coordinates of the region to crop.

    Returns:
    - result: The evaluated result of the arithmetic expression found in the region.
    """
    # Open the image
    img = Image.open(image_path)

    cropped_img = img.crop(region)
    cropped_img.save('test2.png')
    cropped_img = Image.fromarray(preprocess_image_for_ocr('test2.png'))

    # OCR to extract text from the cropped region
    text = pytesseract.image_to_string(cropped_img)

    print(f'First text was {text}')
    text = preprocess_expression(text)
    print(f'Text is {text}')

    # Use a regular expression to filter only the arithmetic expression
    expression = re.findall(r'[\d\+\-\*/\(\)]+', text)

    if not expression:
        return "No arithmetic expression found."

    try:
        result = eval(expression[0])
    except Exception as e:
        return f"Error solving expression: {e}"

    return result

def click_at_position(x: int, y: int):
    """
    Moves the mouse to (x, y) coordinates and performs a click.
    
    Args:
    - x: int, the x-coordinate on the screen.
    - y: int, the y-coordinate on the screen.
    """
    pyautogui.moveTo(x, y, duration=0)
    pyautogui.click()


def take_screenshot(save_path: str):
    """
    Takes a screenshot of the screen and saves it to the specified file path.
    
    Args:
    - save_path: str, the path where the screenshot will be saved (including file name and extension).
    """
    time.sleep(1)
    screenshot = pyautogui.screenshot()
    screenshot.save(save_path)

image_path = "test.png"
# Define the region (left, top, right, bottom) - adjust this depending on where the expression is in the image
region = (750, 520, 1150, 600)

time.sleep(5)

for i in range(1000):
    take_screenshot(image_path)
    result = solve_expression_in_region(image_path, region)
    print(f'Result is {result}')

    if result < 1 or 3 < result: assert False

    if result == 1: click_at_position(900, 640)
    elif result == 2: click_at_position(900, 700)
    else: click_at_position(900, 750)

    time.sleep(0.6)

print(f"Result of the expression: {result}")
