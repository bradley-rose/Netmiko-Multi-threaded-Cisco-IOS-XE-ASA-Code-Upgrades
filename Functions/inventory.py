"""
This inventory file takes in user input and returns a List of devices as selected.

**Actions Required**:
    - Credential encryption with Fernet is mandatory. Instructions for creating an encryption key and encrypting your default credentials are in decryption.py.
    - The hostsFromNetbox() function requires you to properly filter your devices based on your Netbox environment.
"""

from Functions.decryption import decryptCredentials
from Functions.userInput import deviceInclusion

class Device:
    def __init__(self,*,hostname, ipAddress, model, platform):
        self.hostname = hostname
        self.ipAddress = ipAddress
        self.username = ""
        self.password = ""
        self.model = model
        self.platform = platform

def hostsFromNetbox(* typeOfDevice, site, nb):

    # This is the section that you'll be required to fill out with your IDs from your Netbox environment. The end result will be a group of Netbox device objects, but you need to give the pynetbox.filter() function the proper inputs.

    # Example Netbox filters
    if typeOfDevice == "Switches":
        devices = nb.dcim.devices.filter(
            has_primary_ip = True,
            role_id = 69,
            platform_id = 420,
            status = "active",
            site_id = nb.dcim.sites.get(name=site).id
        )
    elif typeOfDevice == "Routers":
        devices = nb.dcim.devices.filter(
            has_primary_ip = True,
            role_id = 420,
            platform_id = 69,
            status = "active",
            site_id = nb.dcim.sites.get(name=site).id
        )
    elif typeOfDevice == "Firewalls":
        devices = nb.dcim.devices.filter(
            has_primary_ip = True,
            role_id = 6969,
            platform_id = 420420,
            status = "active",
            site_id = nb.dcim.sites.get(name=site).id
        )

    # Back to the operation!
    allDevices = []
    for device in devices:
        newDevice = Device(
            hostname = device.name.upper(),
            ipAddress = device.primary_ip.address.split("/")[0],
            model = device.device_type.model,
            platform = device.platform.slug
        )

        # Note: newDevice.platform must represent one of the values that Netmiko understands for session instantiation. Manipulate your entries from Netbox to fit the mould of one of those string values.
        # Refer to this: https://github.com/ktbyers/netmiko/blob/develop/PLATFORMS.md

        allDevices.append(newDevice)
    decryptCredentials(allDevices)
    return allDevices

def inventoryFilter(devices):
    approvedDevices = []
    includeDevices = deviceInclusion(devices)
    for device in devices:
        if device.hostname in includeDevices:
            approvedDevices.append(device)
        else:
            continue

    return approvedDevices
