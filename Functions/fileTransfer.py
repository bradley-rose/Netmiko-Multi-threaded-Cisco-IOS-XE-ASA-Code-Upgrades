"""
This file is for cleaning files, and for utilizing the Netmiko file_transfer function which performs MD5 file verification along with SCP file copy functionality.

1. Each device falls into one of the four following methods:
    a) stackSwitchUpload
    b) iosUpload (non-stack switches and routers)
    c) firewallUploadASDM (Uploading ASDM to firewalls)
    d) firewallUploadBoot (Uploading boot file to firewalls)
2. The appropriate clean method from cleanFiles.py is called.
3. uploadFile() is called to organize information for logging and operation.
4. transferFile() is finally called to perform the file transfer / verification.
"""

from netmiko import file_transfer
from Functions.cleanFiles import stackCleanFiles, cleanIosFiles, firewallCleanASDM, firewallCleanBoot

def transferFile(session,fullPath):
    fileName = fullPath.split("/")[-1]
    
    return file_transfer(
        session,
        source_file="Files/" + fullPath,
        dest_file = fileName,
        file_system = "flash:",
        direction = "put",
        overwrite_file = False
    )

def uploadFile(session, filePath, hostname):
    try:
        header = "\n" + hostname + " - Step 2: File transfer & verify\n\tEvaluating: " + filePath
        print(header)

        result = transferFile(session, filePath)
        
        returnResult = "\n\t\tFile transferred: " + str(result["file_transferred"])
        if not result["file_transferred"]:
            returnResult += " (already on device)"
        returnResult += "\n\t\tMD5 verified: " + str(result["file_verified"])
        print(returnResult)
        return header + returnResult
    
    except Exception as e:
        message = "\nERROR - " + hostname + ": " + str(e) + "\n\n" + "*"*20 + "Completion progress" + "*"*20 + "\n" + result
        print(message)
        return header + message

def stackSwitchUpload(session, filePath, hostname):
    cleanResult = stackCleanFiles(session, hostname)
    uploadResult = uploadFile(session, filePath, hostname)
    return cleanResult + "\n" + uploadResult

def iosUpload(session, filePath, hostname):
    cleanResult = cleanIosFiles(session, filePath, hostname)
    uploadResult = uploadFile(session, filePath, hostname)
    return cleanResult + "\n" + uploadResult

def firewallUploadASDM(session, asdmFile, hostname):
    cleanResult = firewallCleanASDM(session, asdmFile)
    uploadResult = uploadFile(session, asdmFile, hostname)
    return cleanResult + "\n" + uploadResult

def firewallUploadBoot(session, bootFile, hostname):
    cleanResult = firewallCleanBoot(session, bootFile)
    uploadResult = uploadFile(session, bootFile, hostname)
    return cleanResult + "\n" + uploadResult