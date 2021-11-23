from threading import Thread    # Threading support
import socket                   # Socket Programming support
import select                   # Ascynchronous I/O with socket support
import os                       # File and other OS Support

HOST_ADDRESS = "0.0.0.0"    # Servers address (0.0.0.0 for generic access)
HOST_PORT = 1234            # Servers port (Used in client scripts for connection to server)
PATH = os.getcwd()

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
def initializeClient():
    key = keyExchange()
    pass

#Remove Disconnected Client
def removeClient():
    pass

#Receive uploaded file from client
def receiveFile():
    pass

#Send file to client for download.
def sendFile():
    pass

#Send client list of files on server.
def sendDir():
    pass

#Server side of DH Key-Exchange. Returns session key as int.
def keyExchange():
    pass

#Maintain Client Thread
def clientConnection(connection, connection_address):
    key = initializeClient()

    pass

#Accept New Clients
while True:
    client_connection, client_addr = server.accept()                                        # Accept new connections
    connected_clients.append(client_connection)                                             # Add new connections to list of active connections
    print(str(client_addr) + " connected\nConnections: " + str(len(connected_clients)))     
    client_thread = Thread(target=clientConnection, args=(client_connection, client_addr))  # Start thread for new connections
    client_thread.daemon = True
    client_thread.start()