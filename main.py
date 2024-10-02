import pytesseract
from PIL import Image, ImageDraw
import re
import pyautogui
import time
import cv2
import numpy as np

# Here set your own Tesseract PATH pls, if not in PATH
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def preprocess_image_for_ocr(img_path: str) -> cv2.typing.MatLike:
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite('test3.png', gray)

    return gray

def preprocess_expression(text: str) -> str:
    # Cursed processing, still not fully fixed
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


def solve_expression_in_region(image_path: str, region: tuple[int, int, int, int]) -> str | int | None:
    # Open the image
    img = Image.open(image_path)

    cropped_img = img.crop(region)

    # Save image in a dummy path for potential bug fixing
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
    pyautogui.moveTo(x, y, duration=0)
    pyautogui.click()


def take_screenshot(save_path: str):
    screenshot = pyautogui.screenshot()
    screenshot.save(save_path)

(screen_w, screen_l) = pyautogui.size()
(w_mult, l_mult) = (screen_w / 1920, screen_l / 1080) # Relative to my screen's width and length

image_path = "test.png"
# Define the region (left, top, right, bottom) - adjust this depending on where the expression is in the image
region = (750 * w_mult, 520 * l_mult, 1150 * w_mult, 600 * l_mult)

time.sleep(5)

for i in range(1000):
    take_screenshot(image_path)
    result = solve_expression_in_region(image_path, region)
    print(f'Result is {result}')

    if result < 1 or 3 < result: assert False

    if result == 1: click_at_position(900 * w_mult, 640 * l_mult)
    elif result == 2: click_at_position(900 * w_mult, 700 * l_mult)
    else: click_at_position(900 * w_mult, 750 * l_mult)

    time.sleep(1.1)

print(f"Result of the expression: {result}")
