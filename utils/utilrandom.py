import os 

def generateUsername(name):
    # Get rid of space
    namewospace = name.replace(" ","")
    #Generate additional chars
    randomuid = os.urandom(3).hex()
    username = namewospace+randomuid
    return username

def generatePassword():
    #Generate simple password
    password = os.urandom(3).hex()
    return password
    