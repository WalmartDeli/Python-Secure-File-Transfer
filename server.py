from threading import Thread    # Threading support
import socket                   # Socket Programming support
import os                       # File and other OS Support
import struct                   # Byte packing support

HOST_ADDRESS = "0.0.0.0"    # Servers address (0.0.0.0 for generic access)
HOST_PORT = 1234            # Servers port (Used in client scripts for connection to server)
PATH = os.getcwd()          # Working directory of server

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)      # TCP socket creation
server.bind((HOST_ADDRESS, HOST_PORT))                          # Bind the socket to our chosen address and port
server.listen(4)                                                # Listen for upto 4 connections
connected_clients = []                                          # Maintain list of currently connection clients
print('''
    ███████╗███████╗██████╗ ██╗   ██╗███████╗██████╗ 
    ██╔════╝██╔════╝██╔══██╗██║   ██║██╔════╝██╔══██╗
    ███████╗█████╗  ██████╔╝██║   ██║█████╗  ██████╔╝
    ╚════██║██╔══╝  ██╔══██╗╚██╗ ██╔╝██╔══╝  ██╔══██╗
    ███████║███████╗██║  ██║ ╚████╔╝ ███████╗██║  ██║
    ╚══════╝╚══════╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚═╝  ╚═╝
                          RUNNING                                                                                                                                                   
''')
print("Listening on ", HOST_ADDRESS, " at port ", HOST_PORT, "\n")    


#Setup client connection and returns the session key
def initializeClient(connection):
    key = keyExchange(connection)

#Remove Disconnected Client
def removeClient(target_client, address):
    print(str(address) + " disconnected\nConnections: " + str((len(connected_clients) - 1)))
    if target_client in connected_clients:
        connected_clients.remove(target_client)

#Receive uploaded file from client
def receiveFile(connection):
    filename = recvMsg(connection).decode()
    print("Received Filename: " + filename)

    filePerms = recvMsg(connection).decode()
    print("Received file perms: " + oct(int(filePerms)))
    filePerms = int(filePerms, base=8)

    file = recvMsg(connection)
    print("Received File")

    with open(filename, "wb") as writer:
        writer.write(file)
        os.chmod(filename, filePerms)
        print("Wrote file ", filename)    
    




#Send file to client for download.
def sendFile(connection, filename):
    if os.path.exists(filename):
        with open(filename, "rb") as reader:
            file = reader.read()
            filePerms = oct(os.stat(filename).st_mode)[-3:]     #Get file permissions

            #Build Message
            sendMsg(filePerms.encode(), connection)                         #file perms
            sendMsg(file, connection)                                       #Actual file already in bytes.
    else:
        error = b"File [" + filename.encode() + b"] Does not Exist!"
        sendMsg(error, connection)

#Send client list of files on server.
def sendDir(connection):
    l_files = os.listdir(PATH) #gets content of folder
    dir = "FTP Server Directory:" + "\n"

    #prints only files
    for file in l_files:
        filepath = os.path.join(PATH, file)
        if os.path.isfile(filepath):
            dir = dir + "\t" + file + "\n"

    sendMsg(dir.encode(), connection)
    

#Server side of DH Key-Exchange. Returns session key as int.
def keyExchange(connection):
    pass

#Send message to client
def sendMsg(msg, connection):
    # Prefix each message with a 4-byte length (network byte order)
    msg = struct.pack('>I', len(msg)) + msg
    connection.sendall(msg)

#Receive Message from client. Returns as bytearray.
def recvMsg(connection):
    # Read message length and unpack it into an integer
    raw_msglen = recvall(connection, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Read the message data
    return recvall(connection, msglen)

def recvall(connection, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = bytearray()
    while len(data) < n:
        packet = connection.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data


#Maintain Client Thread
def clientConnection(connection, address):
    key = initializeClient(connection)
    while True:
        message = recvMsg(connection)
        if message == None:
            removeClient(connection, address)
            break
        else:
            message = message.decode()
            print(str(address) + ": " + message)

        #Run Requested Command
        cmdlst = message.split(" ") #splits commands into arg array
        if cmdlst[0] == "rdir":
            sendDir(connection)
        elif cmdlst[0] == "up":
            receiveFile(connection)
        elif cmdlst[0] == "down":
            sendFile(connection, cmdlst[1])
        elif cmdlst[0] == "quit":
            removeClient(connection, address)
            break

#Accept New Clients
while True:
    client, address = server.accept()                                   # Accept new connections
    connected_clients.append(client)                                    # Add new connections to list of active connections
    print(str(address) + " connected\nConnections: " + str(len(connected_clients)))     
    client_thread = Thread(target=clientConnection, args=(client, address))  # Start thread for new connections
    client_thread.daemon = True
    client_thread.start()