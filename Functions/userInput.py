"""
Various methods for user input are included here using the inquirer library.
"""

import os
import inquirer
import sys

def deviceInclusion(devices):
    listOfDeviceNames = []
    for device in devices:
        listOfDeviceNames.append(device.hostname)

    questions = [
        inquirer.Checkbox(
            name = "Approved",
            message = "Select the devices to upgrade. Spacebar to toggle, Enter to confirm.",
            choices=listOfDeviceNames
        )
    ]
    return inquirer.prompt(questions)["Approved"]

def identifyDeviceType():
    """
    Description
    -----------
    Prompt the user for the type of device being upgraded.

    Parameters
    ----------
    None

    Returns
    -------
    TBD
    """
    questions = [
        inquirer.List(
            name = "Device Type",
            message = "Which type of device are you upgrading?",
            choices=["Switches","Routers","Firewalls"]
        )
    ]
    return inquirer.prompt(questions)["Device Type"]

def uploadOrUpgrade():
    """
    Description
    -----------
    Prompt the user for the type of device being upgraded.

    Parameters
    ----------
    None

    Returns
    -------
    TBD
    """
    questions = [
        inquirer.List(
            name = "Upload or Upgrade",
            message = "Upload only, or perform upgrade?",
            choices=["Upload Only","Upload & Upgrade"]
        )
    ]
    return inquirer.prompt(questions)["Upload or Upgrade"]

def identifySite(nb):
    """
    Description
    -----------
    Prompt the user for the site name.

    Parameters
    ----------
    None

    Returns
    -------
    TBD
    """
    sites = []
    for site in nb.dcim.sites.all():
        if len(site.name) > 4:
            continue
        else:
            sites.append(site.name)

    questions = [
        inquirer.List(
            name = "Site",
            message = "Which site are you upgrading?",
            choices=sites   
        )
    ]
    return inquirer.prompt(questions)["Site"]

# This function can be improved a bit. Modify the file selection process as appropriate. 
def identifyFiles(deviceType):
    fileDir = "Files/"
    if deviceType == "Switches":
        fileToPush = {}
        for file in os.listdir(fileDir):
            if "cat3k" in file:
                fileToPush['stack'] = file
            elif "c3560cx" in file:
                fileToPush['nonstack'] = file
    
    elif deviceType == "Routers":
        for file in os.listdir(fileDir):
            if "isr4400" in file:
                fileToPush = file
                break
            else:
                continue

    elif deviceType == "Firewalls":
        fileToPush = {}
        for file in os.listdir(fileDir):
            if "asa" in file:
                fileToPush['asa'] = file
            elif "asdm" in file:
                fileToPush['asdm'] = file
            else:
                continue

    return fileToPush
    
def firewallFileIdentification():
    """
    Description
    -----------
    If the user is upgrading firewalls, inquire if the user is going to upgrade the boot file, ASDM, or both.

    Parameters
    ----------
    None

    Returns
    -------
    TBD
    """
    questions = [
        inquirer.Confirm(
            name = "asdm",
            message = "Would you like to upgrade ASDM?",
            default = True
        ),
        inquirer.Confirm(
            name = "boot",
            message = "Would you like to upgrade the ASA boot file?",
            default = True
        )
    ]
    results = inquirer.prompt(questions)
    return {"asdm":results["asdm"],"boot":results["boot"]}

def inventoryReview(payload):
    def cls():
        os.system("cls" if os.name=="nt" else "clear")
    
    cls()
    print("*"*10)
    print("* Review *")
    print("*"*10)
    print("Action: " + payload["operation"])
    print("Selected Devices:")
    for device in payload["devices"]:
        print("\t" + device.hostname)
    print("Selected code to push:")
    if payload["deviceType"] == "Switches":
        print("\tStack Switches: " + payload["file"]["stack"])
        print("\tC3560s: " + payload["file"]["nonstack"])

    elif payload["deviceType"] == "Firewalls":
        if payload["asdmOrBoot"]["boot"]:
            print("\tASA: " + payload["file"]["asa"])
        else:
            pass
        
        if payload["asdmOrBoot"]["asdm"]:
            print("\tASDM: " + payload["file"]["asdm"])
        else:
            pass

    else:
        print("\t" + payload["file"])

    print()
    questions = [
        inquirer.List(
            name = "Continue",
            message = "Would you like to continue with the file upload?",
            choices=["No, quit the application!", "No, I need to make a correction.", "Yes, continue."]
        )
    ]
    result = inquirer.prompt(questions)["Continue"]
    if result == "No, I need to make a correction.":
        cls()
        return True
    elif result == "Yes, continue.":
        return False
    elif result == "No, quit the application!":
        cls()
        sys.exit("Aborting the application runtime.")