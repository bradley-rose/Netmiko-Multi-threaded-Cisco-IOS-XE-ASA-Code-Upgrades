# Netmiko: Multi-threaded Cisco IOS-XE & ASA Code Upgrades
## What is this?
This is my custom-fit solution for patching IOS-XE and ASA devices. It's a bit quirky, but that's what you get when you're locked into legacy updates via SSH/SCP. That said, Kirk Byers is a hero for providing Netmiko and enabling any amount of simplified automation.

## How-to Use
1. Create a symmetric encryption key to encrypt credentials within the Python files. We hate plain-text credentials! Open an interactive Python session and perform the following:

```py
from cryptography.fernet import Fernet
key = Fernet.generate_key()
cipher = Fernet(key)

username = input("Enter your plaintext username here. We'll encrypt it.")
password = input("Same thing for your password. Paste it into here.)

print("Your encryption key: " + str(key).decode("UTF-8"))
print("Your encrypted username: " + str(cipher.encrypt(username.encode("UTF-8"))))
print("Your encrypted password: " + str(cipher.encrypt(password.encode("UTF-8"))))
```

   1. Copy the encryption key to a file at `Functions/encryptionKey.txt`.
   2. Copy the encrypted username to the default username definition within the Device class object in `Functions/inventory.py`.
   3. Copy the encrypted password to the default username definition within the Device class object in `Functions/inventory.py`.

2. Update your Netbox URL and API key in `patching.py`.
3. Update your Netbox filter definitions in `Functions/inventory.py` on lines 26-49. These are unique to each instance of Netbox as the IDs vary.
4. Assess ~line58 to ensure your device platform as pulled from Netbox will resolve to [one of Netmiko's compatible device types](https://github.com/ktbyers/netmiko/blob/develop/PLATFORMS.md). The Device.platform entry **must** resolve to the proper inputs. In most cases for this automation, this will have to be either of `cisco_ios` or `cisco_asa`.

5. Place your IOS and ASA/ASDM code files into `Files/`.
6. Install the required packages. 

```sh
python3 -m pip install -r requirements.txt
```

6. Run `patching.py`!

