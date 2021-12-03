import socket                   # Socket Programming support
import os
import struct
import random
from cryptography.hazmat.primitives import hashes
import subprocess
import symEncrypt

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
def rdir(encryptObject):
    sendMsg("rdir".encode(), encryptObject)
    dir = recvMsg(encryptObject).decode()
    print(dir, end="")
    return

#upload file to remote server from directory
def upload(filename, encryptObject):
    print(filename)
    if os.path.exists(filename):
        sendMsg("up".encode(), encryptObject)
        with open(filename, "rb") as reader:
            file = reader.read()

            filePerms = oct(os.stat(filename).st_mode)[-3:]     #Get file permissions

            #Build Message
            sendMsg(filename.encode(), encryptObject)                          #name of file
            sendMsg(filePerms.encode(), encryptObject)                         #file perms
            sendMsg(file, encryptObject)                                       #Actual file already in bytes.
    else:
        error = "File [" + filename + "] Does not Exist!"
        print(error)

        
    return

#download file to remote server from directory
def download(filename, encryptObject):
    message = "down " + filename
    sendMsg(message.encode(), encryptObject)
    filePerms = recvMsg(encryptObject).decode()
    if len(filePerms) == 3:
        filePerms = int(filePerms, base=8)
        file = recvMsg(encryptObject)

        with open(filename, "wb") as writer:
            writer.write(file)
            os.chmod(filename, filePerms)
            print("Wrote file ", filename)   
    else:
        print(filePerms)

    return

#gracefully exit client program.
def disconnect(encryptObject):
    sendMsg("quit".encode(), encryptObject)
    print("\nDisconnecting")
    quit()

#Setup client connection to server. Returns the session key.
def initializeClient():
    print("Initializing Connection...")
    certExchange()
    print("Generating Session Key")
    key = keyExchange()
    print("Connection initialized.")
    return key
    

#Client Verify Server Certificate
def certExchange():
    
    # Read ca.pem file
    raw_msglen = recvall(4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    data = bytearray()
    while len(data) < msglen:
        packet = server.recv(msglen - len(data))
        if not packet:
            return None
        data.extend(packet)
    caPem = data

    #Write ca.pem file
    with open("ca.pem", "wb") as writer:
        writer.write(caPem)  

    # Read server-cert.pem file
    raw_msglen = recvall(4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    data = bytearray()
    while len(data) < msglen:
        packet = server.recv(msglen - len(data))
        if not packet:
            return None
        data.extend(packet)
    caPem = data

    #Write server-cert.pem file
    with open("server-cert.pem", "wb") as writer:
        writer.write(caPem)  


    verify = subprocess.check_output(['openssl', 'verify', '-CAfile', 'ca.pem', 'server-cert.pem'])
    os.remove("ca.pem")
    os.remove("server-cert.pem")
    if verify == b"server-cert.pem: OK\n":
        print("Server Cert Verified")
        return
    else:
        print("Error verifying server's certificate with certificate authority")
        disconnect()


#Client side of DH Key-Exchange. Returns session key as int.
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
    digest = hashes.Hash(hashes.SHA256())
    digest.update(str(shared_key_cli).encode())
    key = digest.finalize()
    return key


#Send message to client. Requires bytes.
def sendMsg(msg, encryptObject):

    #Encrypt the message
    msg = encryptObject.encrypt(msg)

    # Prefix each message with a 4-byte length (network byte order)
    msg = struct.pack('>I', len(msg)) + msg
    server.sendall(msg)

#Receive Message from client.
def recvMsg(encryptObject):
    # Read message length and unpack it into an integer
    raw_msglen = recvall(4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Read the message data
    cipher =  recvall(msglen)
    return(encryptObject.decrypt(cipher))

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
encryptObject = symEncrypt.symEncrypt(KEY)
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
        rdir(encryptObject)
    elif cmdlst[0] == "up":
        upload(cmdlst[1], encryptObject)
    elif cmdlst[0] == "down":
        download(cmdlst[1], encryptObject)
    elif cmdlst[0] == "quit":
        disconnect(encryptObject)
    else:
        print("Command " + cmdlst[0] + " not found")