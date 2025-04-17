import os
import glob
import base64
import ctypes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
pictures_path = os.path.join(os.path.expanduser("~"), "Pictures")
key_path = os.path.join(pictures_path, "encryption_key.txt")

def load_key():
    if not os.path.exists(key_path):
        print("Encryption key not found! Cannot decrypt files.")
        return None
    with open(key_path, "rb") as f:
        return base64.urlsafe_b64decode(f.read())

def decrypt_file(file_path, key):
    try:
        with open(file_path, "rb") as f:
            data = f.read()

        iv, ciphertext = data[:16], data[16:]  # Extract IV and encrypted data
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        with open(file_path, "wb") as f:
            f.write(plaintext.rstrip(b" "))  # Remove padding

    except Exception as e:
        print(f"Failed to decrypt {file_path}: {e}")

def show_recovered_message():
    message = "Your files have been decrypted successfully!"
    ctypes.windll.user32.MessageBoxW(0, message, "Success!", 0x40 | 0x1)

def decrypt_all_files():
    key = load_key()
    if key is None:
        return

    files = glob.glob(os.path.join(desktop_path, "*"))
    for file in files:
        if os.path.isfile(file) and file != key_path and not file.endswith((".ini", ".lnk")):
            decrypt_file(file, key)
            print(f"Decrypted: {file}")

    print("Decryption complete!")
    show_recovered_message()

if __name__ == "__main__":
    decrypt_all_files()
