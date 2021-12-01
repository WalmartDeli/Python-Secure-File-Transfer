import socket                   # Socket Programming support
import os
import struct
import random
import math

SERVER_ADDRESS = "127.0.0.1"      # Address of server we want to connect to
SERVER_PORT = 1234              # Port of the server we want to connect to
PATH = os.getcwd()              # Use the programs current directory as the working path

server = socket.socket()                            # Create TCP socket
server.connect((SERVER_ADDRESS, SERVER_PORT))       # User created socket to connection to the target server
print("Connected to: ", SERVER_ADDRESS, " at port ", SERVER_PORT, "\nTo close connection, type: quit")

# Provides list of commands w/ brief explaination.


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

# List files in local directory


def ldir():
    l_files = os.listdir(PATH)  # gets content of folder
    print("Program Directory: " + PATH)

    # prints only files
    for file in l_files:
        filepath = os.path.join(PATH, file)
        if os.path.isfile(filepath):
            print("\t" + file)
    return

# List files in remote directory


def rdir():
    sendMsg("rdir".encode())
    dir = recvMsg().decode()
    print(dir, end="")
    return

# upload file to remote server from directory


def upload(filename):
    if os.path.exists(filename):
        sendMsg("up".encode())
        with open(filename, "rb") as reader:
            file = reader.read()

            filePerms = oct(os.stat(filename).st_mode)[-3:]     # Get file permissions

            # Build Message
            sendMsg(filename.encode())                          # name of file
            sendMsg(filePerms.encode())                         # file perms
            sendMsg(file)                                       # Actual file already in bytes.
    else:
        error = "File [" + filename + "] Does not Exist!"
        print(error)

    return

# download file to remote server from directory


def download(filename):
    message = "down " + filename
    sendMsg(message.encode())
    filePerms = recvMsg().decode()
    if len(filePerms) == 3:
        filePerms = int(filePerms, base=8)
        file = recvMsg()

        with open(filename, "wb") as writer:
            writer.write(file)
            os.chmod(filename, filePerms)
            print("Wrote file ", filename)
    else:
        print(filePerms)

    return

# gracefully exit client program.


def disconnect():
    sendMsg("quit".encode())
    print("\nDisconnecting")
    quit()

# Setup client connection to server. Returns the session key.


def initializeClient():
    keyExchange()
    pass

# Client side of DH Key-Exchange. Returns session key as int.


def keyExchange():
    # Receive prime number from server #

    num = server.recv(16)  # Receive the byte value sent by server (prime number)
    p = int.from_bytes(num, 'little')  # Convert byte to int to be used as p

    # Receive primitive root modulo #

    num1 = server.recv(16)  # Receive the byte value sent by server (prime number)
    g = int.from_bytes(num1, 'little')  # Convert byte to int to be used as p

    # Generation of Client secret key

    cli_sec_key = random.randint(1, p)

    # Compute Client Public Key and exchange with server#

    A_byte = server.recv(16)  # Recieve server public key in bytes
    A = int.from_bytes(A_byte, 'little')  # Convert server public key to int
    B = g**cli_sec_key % p  # Compute client public key
    B_byte = B.to_bytes(16, 'little')  # Convert client public key to bytes
    server.send(B_byte)  # Share client public key with server
    shared_key_cli = A**cli_sec_key % p  # Compute session key from client end
    shared_key_ser_byte = server.recv(16)  # Recieve server session key in bytes
    shared_key_ser = int.from_bytes(shared_key_ser_byte, 'little')  # Store session key in int
    shared_key_cli_byte = shared_key_cli.to_bytes(16, 'little')  # Compute client session key to byte
    server.send(shared_key_ser_byte)  # Share client session key with server
    if(shared_key_ser == shared_key_cli):  # compare client and server session key and if they match procceed
        print("Key match")
    else:
        exit()


# Send message to client. Requires bytes.


def sendMsg(msg):
    # Prefix each message with a 4-byte length (network byte order)
    msg = struct.pack('>I', len(msg)) + msg
    server.sendall(msg)

# Receive Message from client.


def recvMsg():
    # Read message length and unpack it into an integer
    raw_msglen = recvall(4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Read the message data
    return recvall(msglen)


def recvall(n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = bytearray()
    while len(data) < n:
        packet = server.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data


# Input Loop
KEY = initializeClient()
print("Type 'help' to get a list of available commands.")
while True:
    print("> ", end="")

    # Breaks input into array by space
    cmd = input()
    cmdlst = cmd.split(" ")

    # Checks first input arg for command
    if cmdlst[0] == "help":
        help()
    elif cmdlst[0] == "ldir":
        ldir()
    elif cmdlst[0] == "rdir":
        rdir()
    elif cmdlst[0] == "up":
        upload(cmdlst[1])
    elif cmdlst[0] == "down":
        download(cmdlst[1])
    elif cmdlst[0] == "quit":
        disconnect()
    else:
        print("Command " + cmdlst[0] + " not found")
