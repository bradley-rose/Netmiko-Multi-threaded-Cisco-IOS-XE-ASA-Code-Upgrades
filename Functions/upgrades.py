"""
These methods relate to the proper ways of updating the code to point to the newly-uploaded file, and/or expanding or installing the package file.
"""

def stackSwitchUpgrade(session, fileName, hostname):
    try:
        header = hostname + " - Step 3: Installing new code"

        installMode = session.send_command("show ver | i INSTALL")
        if installMode:
            returnResult = "\n\tExpanding software package..."
            returnResult += "\n\t\t" + session.send_command("request platform software package install switch all file flash:" + fileName + "new auto-copy")
        else:
            returnResult = "\n\tConverting switch from BUNDLE mode to INSTALL mode."
            returnResult += "\n\t\t" + session.send_command("request platform software package expand switch all file flash:" + fileName + "retain-source-file auto-copy overwrite force")
            returnResult += "\n\tUpdating boot statement..."
            session.send_config_set([
                "no boot system",
                "boot system switch all flash:packages.conf"
            ])
            returnResult += "\n\tCopying running-configuration to startup-configuration..."
            returnResult += "\n\t\t" + session.save_config()

        returnResult += "\n\tReloading switch!"
        for command in ["reload", "\n"]:
            session.send_command_timing(command)
    
        print(returnResult)
        return header + returnResult
    
    except Exception as e:
        message = "\nERROR - " + hostname + ": " + str(e) + "\n\n" + "*"*20 + "Completion progress" + "*"*20 + "\n" + returnResult
        print(message)
        return header + message

def iosUpgrade(session, fileName, hostname):
    try: 
        header = hostname + " - Step 3: Updating boot statement"
        print(header)

        session.send_config_set([
            "no boot system",
            "boot system flash flash:" + fileName
        ])

        returnResult = "\n\tCopying running-configuration to startup-configuration..."
        returnResult += "\n\t\t" + session.save_config()

        returnResult += "\n\tReloading switch!"
        for command in ["reload", "\n"]:
            session.send_command_timing(command)
    
        print(returnResult)
        return header + returnResult

    except Exception as e:
        message = "\nERROR - " + hostname + ": " + str(e) + "\n\n" + "*"*20 + "Completion progress" + "*"*20 + "\n" + returnResult
        print(message)
        return header + message
        
def asaUpgrade(session, upgrades, hostname):
    try: 
        asdm = False
        boot = False

        returnResult = ""
        header = hostname + " - Step 3: Updating boot/image statements"
        print(header)

        if "asdm" in upgrades.keys():
            returnResult += "\n\tUpdating ASDM image statement..."
            returnResult += "\n\t\t" + session.send_config_set([
                "no asdm image",
                "asdm image disk0:/" + upgrades["asdm"]
            ])
            asdm = True
        else:
            pass

        if "boot" in upgrades.keys():
            returnResult += "\n\tRemoving old boot statements and replacing with target boot file."
            existingBootStatements = session.send_command("show run | grep boot system")
            updateBootStatements = []
            for statement in existingBootStatements:
                updateBootStatements.append("no " + statement)
            
            updateBootStatements.append("boot system disk0:/" + upgrades["boot"])

            returnResult += "\n\t\t".join(updateBootStatements)
            session.send_config_set(updateBootStatements)

            boot = True
        
        else:
            pass

        if asdm or boot:

            returnResult += "\n\tCopying running-configuration to startup-configuration..."
            returnResult += "\n\t\t" + session.save_config()
            returnResult += "\n\tReloading switch!"
            for command in ["reload", "\n"]:
                session.send_command_timing(command)
        else:
            pass
        
        print(returnResult)
        return header + returnResult

    except Exception as e:
        message = "\nERROR - " + hostname + ": " + str(e) + "\n\n" + "*"*20 + "Completion progress" + "*"*20 + "\n" + returnResult
        print(message)
        return header + message