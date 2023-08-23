"""
These methods represent clearing irrelevant / unnecessary files from the flash storage file system. Often, these can house dormant files over long periods of time, and if storage gets full when attempting to copy a new file to it, this can cause bricked devices, or simply a waste of time.

These are run in advance of any file-copy process to ensure that there are no issues.
"""

def stackCleanFiles(session, hostname):
    try:
        header = "\n" + hostname + " - Step 1: Clean files"
        print(header)
        returnResult = ""

        output = session.send_command_timing(
            command_string = "request platform software package clean switch all file flash:",
            strip_prompt = False,
            strip_command = False
        )
        if "proceed" in output:
            output += session.send_command_timing(
                command_string="y",
                strip_prompt = False,
                strip_command = False
            )
        
        for line in output.splitlines():
            if "SUCCESS" in line:
                returnResult += "\n\t" + line
        
        returnResult += "\n\tCompleted file clean."
        print(returnResult)
        return header + returnResult
    
    except Exception as e:
        message = "\nERROR - " + hostname + ": " + e + "\n\n" + "*"*20 + "Completion progress" + "*"*20 + "\n" + returnResult
        print(message)
        return header + message
    
def cleanIosFiles(session, newFile, hostname):
    try:
        header = "\n" + hostname + " - Step 1: Clean files"
        print(header)
        returnResult = ""

        deletedFiles = []
        output = session.send_command("show flash: | i .*bin$")
        avoid = [newFile]
        avoid.append(session.send_command("show boot | i flash:.*bin").split("flash:")[1].split(",")[0])
        for line in output.splitlines():
            for element in line.split():
                if element.endswith(".bin"):
                    if "flash/" in element:
                        fileName = element.split("flash/")[1]
                    else:
                        fileName = element
                    
                    if fileName in avoid:
                        continue
                    else:
                        deletedFiles.append(fileName)
                        session.send_multiline([
                            [f"del flash:/{fileName}",r"Delete filename"],
                            ["\n", r"confirm"],
                            ["y", ""]
                        ])
                else:
                    continue
    
        if deletedFiles:
            returnResult += "\n\tFiles deleted: "
            for file in deletedFiles:
                result += "\n\t\t" + file
        
        returnResult += "\n\tCompleted Step 1: Clean files!"
        print(returnResult)
        return header + returnResult
    
    except Exception as e:
        message = "\nERROR - " + hostname + ": " + str(e) + "\n\n" + "*"*20 + "Completion progress" + "*"*20 + "\n" + returnResult
        print(message)
        return header + message

def firewallCleanASDM(session, newFile, hostname):
    try:
        header = "\n" + hostname + " - Step 1(a)sdm: Clean files"
        print(header)
        returnResult = ""
        deletedFiles = []

        output = session.send_command("show flash: | i .*bin$")
        
        # Prevent deletion of current boot file, and the target ASDM file (if it's already on the device).
        avoid = [newFile]
        avoid += session.send_command("show asdm image").split(":/")[1]
        
        for line in output.splitlines():
            for element in line.split():
                if element.endswith(".bin"):
                    fileName = element
                    
                    if fileName in avoid:
                        continue
                    else:
                        deletedFiles.append(fileName)
                        session.send_multiline([
                            [f"del flash:/{fileName}",r"Delete filename"],
                            ["\n", r"confirm"],
                            ["y", ""]
                        ])
                else:
                    continue
        
        if deletedFiles:
            returnResult += "\n\tFiles deleted: "
            for file in deletedFiles:
                returnResult += "\n\t\t" + file

        returnResult += "\n\tCompleted Step 1(a)sdm: Clean files!"
        print(returnResult)
        return header + returnResult

    except Exception as e:
        return "ERROR - " + hostname + ": " + str(e) + "\n\n" + "*"*20 + "Completion progress" + "*"*20 + "\n" + header + returnResult

def firewallCleanBoot(session, newFile, hostname):
    try:
        header = "\n" + hostname + " - Step 1(b)oot: Clean files"
        print(header)
        returnResult = ""

        deletedFiles = []

        allBootFiles = session.send_command("show flash: | i .*SPA$")

        # Prevent deletion of current boot file, and the target boot file (if it's already on the device).
        avoid = [newFile]
        avoid += session.send_command("show run | grep boot system")
        
        for line in allBootFiles.splitlines():
            for element in line.split():
                if element.endswith("SPA"):
                    fileName = element

                    if "firmware" in fileName:
                        continue
                    elif fileName in avoid:
                        continue
                    else:
                        deletedFiles.append(fileName)
                        session.send_multiline([
                            [f"del flash:/{fileName}",r"Delete filename"],
                            ["\n", r"confirm"],
                            ["y", ""]
                        ])

        if deletedFiles:
            returnResult += "\n\tFiles deleted: "
            for file in deletedFiles:
                returnResult += "\n\t\t" + file

        returnResult += "\n\tCompleted Step 1(b)oot: Clean files!"
        print(returnResult)
        return header + returnResult

    except Exception as e:
        return "ERROR - " + hostname + ": " + str(e) + "\n\n" + "*"*20 + "Completion progress" + "*"*20 + "\n" + header + returnResult