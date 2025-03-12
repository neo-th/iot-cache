from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import os
import base64
import subprocess
import platform

def get_os():
    os_name = platform.system()
    if os_name == "Darwin":
        return "mac"
    elif os_name == "Linux":
        return "linux"
    else:
        return "unknown OS"

def get_serial():

    if get_os() == "mac":
        find_mac_serial = 'system_profiler SPHardwareDataType | grep "Serial Number" | awk \'{print $4}\''
        try:
            return subprocess.check_output(find_mac_serial, shell=True).decode().strip()
        except subprocess.CalledProcessError:
            return "Error retrieving Mac serial"

    elif get_os() == "linux":
        find_linux_serial = 'cat /sys/class/dmi/id/product_serial'
        try:
            return subprocess.check_output(find_linux_serial, shell=True).decode().strip()
        except subprocess.CalledProcessError:
            return "Error retrieving Linux serial"
    
    return "Unknown OS"
    
def derive_key_from_password(password: str, salt: bytes):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    return kdf.derive(password.encode())

def encrypt_value(value: str, serial_number: str):
    salt = os.urandom(16)
    key = derive_key_from_password(serial_number, salt)

    nonce = os.urandom(12)
    cipher = Cipher(algorithms.AES(key), modes.GCM(nonce))
    encryptor = cipher.encryptor()

    ciphertext = encryptor.update(value.encode()) + encryptor.finalize()

    encrypted_data = base64.b64encode(nonce + salt + encryptor.tag + ciphertext).decode()
    return encrypted_data

# Function to decrypt a value
def decrypt_value(encrypted_data: str, serial_number: str):
    raw_data = base64.b64decode(encrypted_data)
    nonce = raw_data[:12]
    salt = raw_data[12:28]
    tag = raw_data[28:44]
    ciphertext = raw_data[44:]

    key = derive_key_from_password(serial_number, salt)

    cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag))
    decryptor = cipher.decryptor()
    
    return decryptor.update(ciphertext) + decryptor.finalize()

def get_hostname():
    hostname = os.uname().nodename
    return ":" + hostname

def call_encrypt(value: str):
    key = get_serial()

    encrypted = encrypt_value(value, key)
    return encrypted

def call_decrypt(value: str):
    key = get_serial()

    decrypted = decrypt_value(value, key)
    return decrypted.decode()
