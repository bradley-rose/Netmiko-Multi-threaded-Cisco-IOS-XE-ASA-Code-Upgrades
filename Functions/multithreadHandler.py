"""
This file serves as a corral point for the multi-threaded process. This is the first point in which an individual device is present.
"""

from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException
from Functions.fileTransfer import stackSwitchUpload, iosUpload, firewallUploadASDM, firewallUploadBoot 
from Functions.upgrades import stackSwitchUpgrade, iosUpgrade, asaUpgrade

def handler(payload, device):
    # Break most of the device object up into a dictionary for Netmiko to work with.
    netmikoDevice = {
        "host":device.ipAddress,
        "username":device.username,
        "password":device.password,
        "device_type":device.platform
    }

    # Begin reporting/logging header.
    result = "*"*25 + "\n" + device.hostname + "\n" + "*"*25 + "\n"

    # Most of the functions are wrapped in Try/Except statements to catch individual errors and identify them in logs, but not allow them to interrupt the parent process and interrupt other threads.

    try:
        # Log into the device via SSH!
        sshSession = ConnectHandler(**netmikoDevice)
        
        # If the deviceType was identified as "Switches", this is relevant.
        if payload["deviceType"] == "Switches":
            
            # Stack switches
            if any(model in device.model for model in ["3650", "3850"]):
                
                # Clean + upload file
                result += stackSwitchUpload(sshSession, payload["file"]["stack"], device.hostname)
                
                # Upgrade (if selected and no errors are present)
                if not payload["operation"] == "Upload Only" and "ERROR" not in result:
                    stackSwitchUpgrade(sshSession, payload["file"]["stack"], device.hostname)
                
                # If not upgrading or errors occurred during the file transfer, the end is nigh.
                else:
                    pass 

            # Non-stack switch (IOS-XE + bin file in bundle mode)
            else:
                
                # Clean + upload file 
                result += iosUpload(sshSession, payload["file"]["nonstack"], device.hostname)

                # Upgrade (if selected and no errors are present)
                if not payload["operation"] == "Upload Only" and "ERROR" not in result:
                    result += iosUpgrade(sshSession, payload["file"]["nonstack"], device.hostname)
                
                # If not upgrading or errors occurred during the file transfer, the end is nigh.
                else:
                    pass 
        
        # Routers!
        elif payload["deviceType"] == "Routers":
            
            # Clean + upload file
            result += iosUpload(sshSession, payload["file"], device.hostname)
            
            # Upgrade (if selected and no errors are present)
            if not payload["operation"] == "Upload Only" and "ERROR" not in result:
                iosUpgrade(sshSession, payload["file"], device.hostname)
            
            # If not upgrading or errors occurred during the file transfer, the end is nigh.
            else:
                pass 
        
        # Firewalls!
        elif payload["deviceType"] == "Firewalls":
            files = {}
            
            # Clean + ASDM upload (if selected)
            if payload["asdmOrBoot"]["asdm"]:
                result += firewallUploadASDM(sshSession, payload["file"]["asdm"], device.hostname)
                files["asdm"] = payload["file"]["asdm"]
            
            # Clean + boot file upload (if selected)
            if payload["asdmOrBoot"]["boot"]:
                result += firewallUploadBoot(sshSession, payload["file"]["boot"], device.hostname)
                files["boot"] = payload["file"]["boot"]

            # Upgrade (if selected and no errors are present)
            if not payload["operation"] == "Upload Only" and "ERROR" not in result:
                asaUpgrade(sshSession, files, device.hostname)

            # If not upgrading or errors occurred during the file transfer, the end is nigh.
            else:
                pass 
        
        # Close the SSH session. We're done interacting with the device!
        sshSession.disconnect()
        
        # Return the result to the main process in patching.py.
        return result
    
    # If the device is unable to be contacted, this error is thrown.
    except NetmikoTimeoutException as e:
        returnResult = "\n" + device.hostname + " - ERROR: Couldn't establish connection (or lost connection) to device." + "\n\nProgress: \n\t" + result + "\n\nError message: \n\t" + str(e)
        return returnResult
    
    # If the wrong credentials are used, this error is thrown.
    except NetmikoAuthenticationException as e:
        returnResult = "\n" + device.hostname + " - ERROR: Incorrect credentials for device." + "\n" + str(e)
        return returnResult