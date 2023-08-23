__author__ = "Bradley Rose"
__date__ = "2023-08-23"
__deprecated__ = False
__email__ = "contact@bradleyrose.co"
__status__ = "Production"
__version__ = "1.0.0"

"""
Actions:
    1. Prompts the user for input.
        a) Upload only, or upgrade?
        b) Type of device?
            i) If Firewalls: ASDM, boot, or both?
        c) Which site is in scope?
        d) Queries Netbox for all devices within the category selected in b) and at the site selected in c). Presents these hosts to the user and asks the user to select exactly which devices are in scope.
        e) Scans the relevant file share for related files and digests their file names.
        f) Presents a review screen to the user and allows them to review the devices, the files, and the action to be taken.
        g) User confirms.
    2. A multithreaded process is spawned, one thread per device, and based on the user's selections, the upload and/or upgrade process begins.
        a) A file is opened at the file share > Logs directory for outputting the runtime contents to.
"""

# Importing internal functionality
from Functions.inventory import hostsFromNetbox, inventoryFilter
import Functions.userInput as userInput
from Functions.multithreadHandler import handler

# Importing Python libraries for functionality/operation.
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import pynetbox

nb = pynetbox.api(
    "", # Netbox URL
    ""  # Netbox read-only API key
)

def main():
    while True:
        payload = {}

        # Upload only, or upload & upgrade?
        payload["operation"] = userInput.uploadOrUpgrade()

        # Identify the type of device to upgrade: switch, router, or firewall
        payload["deviceType"] = userInput.identifyDeviceType()

        # For firewalls: upgrade ASDM, boot, or both?
        if payload["deviceType"] == "Firewalls":
            payload["asdmOrBoot"] = userInput.firewallFileIdentification()
        
        # Obtain devices from Netbox after asking the user for the target site.
        devices = hostsFromNetbox(
            typeOfDevice = payload["deviceType"],
            site = userInput.identifySite(nb),
            nb = nb
        )

        # Generate a shortlist of in-scope devices decided by user input.
        payload["devices"] = inventoryFilter(devices)

        # Identify files
        payload["file"] = userInput.identifyFiles(payload["deviceType"])

        # User review!
        loop = userInput.inventoryReview(payload)

        # If the user wants to proceed, execute the following: 
        if not loop:

            # Open a log file
            with open("Logs/" + datetime.now().strftime("%Y-%m-%d_%Hh%Mm") + "_executionLog.txt","w") as outputFile:

                # Spawn the multi-threaded process for upgrading up to a maximum of 10 devices at once.
                with ThreadPoolExecutor(max_workers=10) as execution:
                    results = {execution.submit(handler, payload, device): device for device in payload["devices"]}
                    for thread in as_completed(results):
                        outputFile.write(thread.result())
        
        # If the user wants to make a correction, this file will loop back around.

if __name__ == "__main__":
    main()