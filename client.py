import socket                   # Socket Programming support
import os

SERVER_ADDRESS = "0.0.0.0"      # Address of server we want to connect to
SERVER_PORT = 1234              # Port of the server we want to connect to
PATH = os.getcwd()              # Use the programs current directory as the working path

server = socket.socket()                            # Create TCP socket
server.connect((SERVER_ADDRESS, SERVER_PORT))       # User created socket to connection to the target server
print("Connected to: ", SERVER_ADDRESS , " at port ", SERVER_PORT, "\nTo close connection, type: quit")

#Provides list of commands w/ brief explaination.
def help():
    man = """
    help: Provides list of commands
    ldir: List files in local directory
    rdir: List file in remote directory
    up FILE: Upload a file to the remote server from directory
    down FILE: Download a file to the remote server from directory
    quit: Gracefully exit the program.
    """
    print(man)
    return

#List files in local directory
def ldir():
    l_files = os.listdir(PATH) #gets content of folder
    print("Program Directory: " + PATH)

    #prints only files
    for file in l_files:
        filepath = os.path.join(PATH, file)
        if os.path.isfile(filepath):
            print("\t" + file)
    return

#List files in remote directory
def rdir():
    print("rdir")
    return

#upload file to remote server from directory
def upload():
    print("up")
    return

#download file to remote server from directory
def download():
    print("down")
    return

#gracefully exit client program.
def disconnect():
    print("\nDisconnecting")
    quit()

#Setup client connection to server. Returns the session key.
def initializeClient():
    keyExchange()
    pass

#Client side of DH Key-Exchange. Returns session key as int.
def keyExchange():
    pass

# Input Loop
KEY = initializeClient()
print("Type 'help' to get a list of available commands.")
while True:
    print("> ", end="")
    
    #Breaks input into array by space
    cmd = input()
    cmdlst = cmd.split(" ")

    #Checks first input arg for command
    if cmdlst[0] == "help":
        help()
    elif cmdlst[0] == "ldir":
        ldir()
    elif cmdlst[0] == "rdir":
        rdir()
    elif cmdlst[0] == "up":
        upload()
    elif cmdlst[0] == "down":
        download()
    elif cmdlst[0] == "quit":
        disconnect()
    else:
        print("Command " + cmdlst[0] + " not found")