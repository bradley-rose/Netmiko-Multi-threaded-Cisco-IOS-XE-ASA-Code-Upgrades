from cryptography.fernet import Fernet

def decryptCredentials(devices):
    with open("Functions/encryptionKey.txt", "rb") as file:
        key = file.read()
    cipher = Fernet(key)
    for device in devices:
        device.username = cipher.decrypt(device.username).decode("UTF-8")
        device.password = cipher.decrypt(device.password).decode("UTF-8")        