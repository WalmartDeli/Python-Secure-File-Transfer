from threading import Thread    # Threading support
import socket                   # Socket Programming support
import os                       # File and other OS Support
import struct                   # Byte packing support
from math import gcd as bltin_gcd
import random
from cryptography.hazmat.primitives import hashes
import symEncrypt

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
    certExchange(connection)
    key = keyExchange(connection)
    return key

#Remove Disconnected Client
def removeClient(target_client, address):
    print(str(address) + " disconnected\nConnections: " + str((len(connected_clients) - 1)))
    if target_client in connected_clients:
        connected_clients.remove(target_client)

#Receive uploaded file from client
def receiveFile(connection, encryptObject):
    filename = recvMsg(connection, encryptObject).decode()
    print("Received Filename: " + filename)

    filePerms = recvMsg(connection, encryptObject).decode()
    print("Received file perms: " + oct(int(filePerms)))
    filePerms = int(filePerms, base=8)

    file = recvMsg(connection, encryptObject)
    print("Received File")

    with open(filename, "wb") as writer:
        writer.write(file)
        os.chmod(filename, filePerms)
        print("Wrote file ", filename)    
    




#Send file to client for download.
def sendFile(connection, filename, encryptObject):
    if os.path.exists(filename):
        with open(filename, "rb") as reader:
            file = reader.read()
            filePerms = oct(os.stat(filename).st_mode)[-3:]     #Get file permissions

            #Build Message
            sendMsg(filePerms.encode(), connection, encryptObject)                         #file perms
            sendMsg(file, connection, encryptObject)                                       #Actual file already in bytes.
    else:
        error = b"File [" + filename.encode() + b"] Does not Exist!"
        sendMsg(error, connection, encryptObject)

#Send client list of files on server.
def sendDir(connection, encryptObject):
    l_files = os.listdir(PATH) #gets content of folder
    dir = "FTP Server Directory:" + "\n"

    #prints only files
    for file in l_files:
        filepath = os.path.join(PATH, file)
        if os.path.isfile(filepath):
            dir = dir + "\t" + file + "\n"

    sendMsg(dir.encode(), connection, encryptObject)
    

#Client Verify Server Certificate
def certExchange(connection):
    
    #Send ca.pem
    filename = "ca.pem"
    if os.path.exists(filename):
        with open(filename, "rb") as reader:
            file = reader.read()
            msg = struct.pack('>I', len(file)) + file
            connection.sendall(msg)
    else:
        error = b"File [" + filename.encode() + b"] Does not Exist!"
        msg = struct.pack('>I', len(error)) + error
        connection.sendall(msg)

    #Send server-cert.pem
    filename = "server-cert.pem"
    if os.path.exists(filename):
        with open(filename, "rb") as reader:
            file = reader.read()
            msg = struct.pack('>I', len(file)) + file
            connection.sendall(msg)
    else:
        error = b"File [" + filename.encode() + b"] Does not Exist!"
        msg = struct.pack('>I', len(error)) + error
        connection.sendall(msg)



#Server side of DH Key-Exchange. Returns session key as int.
def keyExchange(connection):
     # Selection of prime number and share it with client #

    prime = [76667,76673,76679,76697,76717,76733,76753,76757,76771,76777,76781,76801,87433,87443,87473,87481,87491,87509,87511,87517,87523,87539,87541,87547,87553,87557,87559,87583,87587,87589,87613,87623,87629,87631,87641,87643,87649,87671,87679,87683,87691,87697,87701,87719,87721,87739,87743,87751,87767,87793,87797,87803,87811,87833,87853,87869,87877,87881,87887,87911,87917,87931,87943,87959,87961,87973,87977,87991,88001,88003,88007,88019,88037,88069,88079,88093,88117,88129,88169,88177,88211,88223,88237,88241,88259,88261,88289,88301,88321,88327,88337,88339,88379,88397,88411,88423,88427,88463,88469,88471,88493,88499,88513,88523,88547,88589,88591,88607,88609,88643,88651,88657,88661,88663,88667,88681,88721,88729,88741,88747,88771,88789,88793,88799,88801,88807,88811,88813,88817,88819,88843,88853,88861,88867,88873,88883,88897,88903,88919,88937,88951,88969,88993,88997,89003,89009,89017,89021,89041,89051,89057,89069,89071,89083,89087,89101,89107,89113,89119,89123,89137,89153,89189,89203,89209,89213,89227,89231,89237,89261,89269,89273,89293,89303,89317,89329,89363,89371,89381,89387,89393,89399,89413,89417,89431,89443,89449,89459,89477,89491,89501,89513,89519,89521,89527,89533,89561,89563,89567,89591,89597,89599,89603,89611,89627,89633,89653,89657,89659,89669,89671,89681,89689,89753,89759,89767,89779,89783,89797,89809,89819,89821,89833,89839,89849,89867,89891,89897,89899,89909,89917,89923,89939,89959,89963,89977,89983,89989,90001,90007,90011,90017,90019,90023,90031,90053,90059,90067,90071,90073,90089,90107,90121,90127,90149,90163,90173,90187,90191,90197,90199,90203,90217,90227,90239,90247,90263,90271,90281,90289,90313,90353,90359,90371,90373,90379,90397,90401,90403,90407,90437,90439,90469,90473,90481,90499,90511,90523,90527,90529,90533,90547,90583,90599,90617,90619,90631,90641,90647,90659,90677,90679,90697,90703,90709,90731,90749,90787,90793,90803,90821,90823,90833,90841,90847,90863,90887,90901,90907,90911,90917,90931,90947,90971,90977,90989,90997,91009,91019,91033,91079,91081,91097,91099,91121,91127,91129,91139,91141,91151,91153,91159,91163,91183,91193,91199,91229,91237,91243,91249,91253,91283,91291,91297,91303,91309,91331,91367,91369,91373,91381,91387,91393,91397,91411,91423,91433,91453,91457,91459,91463,91493,91499,91513,91529,91541,91571,91573,91577,91583,91591,91621,91631,91639,91673,91691,91703,91711,91733,91753,91757,91771,91781,91801,91807,91811,91813,91823,91837,91841,91867,91873,91909,91921,91939,91943,91951,91957,91961,91967,91969,91997,92003,92009,92033,92041,92051,92077,92083,92107,92111,92119,92143,92153,92173,92177,92179,92189,92203,92219,92221,92227,92233,92237,92243,92251,92269,92297,92311,92317,92333,92347,92353,92357,92363,92369,92377,92381,92383,92387,92399,92401,92413,92419,92431,92459,92461,92467,92479,92489,92503,92507,92551,92557,92567,92569,92581,92593,92623,92627,92639,92641,92647,92657,92669,92671,92681,92683,92693,92699,92707,92717,92723,92737,92753,92761,92767,92779,92789,92791,92801,92809,92821,92831,92849,92857,92861,92863,92867,92893,92899,92921,92927,92941,92951,92957,92959,92987,92993,93001,93047,93053,93059,93077,93083,93089,93097,93103,93113,93131,93133,93139,93151,93169,93179,93187,93199,93229,93239,93241,93251,93253,93257,93263,93281,93283,93287,93307,93319,93323,93329,93337,93371,93377,93383,93407,93419,93427,93463,93479,93481,93487,93491,93493,93497,93503,93523,93529,93553,93557,93559,93563,93581,93601,93607,93629,93637,93683,93701,93703,93719,93739,93761,93763,93787,93809,93811,93827,93851,93871,93887,93889,93893,93901,93911,93913,93923,93937,93941,93949,93967,93971,93979,93983,93997,94007,94009,94033,94049,94057,94063,94079,94099,94109,94111,94117,94121,94151,94153,94169,94201,94207,94219,94229,94253,94261,94273,94291,94307,94309,94321,94327,94331,94343,94349,94351,94379,94397,94399,94421,94427,94433,94439,94441,94447,94463,94477,94483,94513,94529,94531,94541,94543,94547,94559,94561,94573,94583,94597,94603,94613,94621,94649,94651,94687,94693,94709,94723,94727,94747,94771,94777,94781,94789,94793,94811,94819,94823,94837,94841,94847,94849,94873,94889,94903,94907,94933,94949,94951,94961,94993,94999,95003,95009,95021,95027,95063,95071,95083,95087,95089,95093,95101,95107,95111,95131,95143,95153,95177,95189,95191,95203,95213,95219,95231,95233,95239,95257,95261,95267,95273,95279,95287,95311,95317,95327,95339,95369,95383,95393,95401,95413,95419,95429,95441,95443,95461,95467,95471,95479,95483,95507,95527,95531,95539,95549,95561,95569,95581,95597,95603,95617,95621,95629,95633,95651,95701,95707,95713,95717,95723,95731,95737,95747,95773,95783,95789,95791,95801,95803,95813,95819,95857,95869,95873,95881,95891,95911,95917,95923,95929,95947,95957,95959,95971,95987,95989,96001,96013,96017,96043,96053,96059,96079,96097,96137,96149,96157,96167,96179,96181,96199,96211,96221,96223,96233,96259,96263,96269,96281,96289,96293,96323,96329,96331,96337,96353,96377,96401,96419,96431,96443,96451,96457,96461,96469,96479,96487,96493,96497,96517,96527,96553,96557,96581,96587,96589,96601,96643,96661,96667,96671,96697,96703,96731,96737,96739,96749,96757,96763,96769,96779,96787,96797,96799,96821,96823,96827,96847,96851,96857,96893,96907,96911,96931,96953,96959,96973,96979,96989,96997,97001,97003,97007,97021,97039,97073,97081,97103,97117,97127,97151,97157,97159,97169,97171,97177,97187,97213,97231,97241,97259,97283,97301,97303,97327,97367,97369,97373,97379,97381,97387,97397,97423,97429,97441,97453,97459,97463,97499,97501,97511,97523,97547,97549,97553,97561,97571,97577,97579,97583,97607,97609,97613,97649,97651,97673,97687,97711,97729,97771,97777,97787,97789,97813,97829,97841,97843,97847,97849,97859,97861,97871,97879,97883,97919,97927,97931,97943,97961,97967,97973,97987,98009,98011,98017,98041,98047,98057,98081,98101,98123,98129,98143,98179,98207,98213,98221,98227,98251,98257,98269,98297,98299,98317,98321,98323,98327,98347,98369,98377,98387,98389,98407,98411,98419,98429,98443,98453,98459,98467,98473,98479,98491,98507,98519,98533,98543,98561,98563,98573,98597,98621,98627,98639,98641,98663,98669,98689,98711,98713,98717,98729,98731,98737,98773,98779,98801,98807,98809,98837,98849,98867,98869,98873,98887,98893,98897,98899,98909,98911,98927,98929,98939,98947,98953,98963,98981,98993,98999,99013,99017,99023,99041,99053,99079,99083,99089,99103,99109,99119,99131,99133,99137,99139,99149,99173,99181,99191,99223,99233,99241,99251,99257,99259,99277,99289,99317,99347,99349,99367,99371,99377,99391,99397,99401,99409,99431,99439,99469,99487,99497,99523,99527,99529,99551,99559,99563,99571,99577,99581,99607,99611,99623,99643,99661,99667,99679,99689,99707,99709,99713,99719,99721,99733,99761,99767,99787,99793,99809,99817,99823,99829,99833,99839,99859,99871,99877,99881,99901,99907,99923,99929,99961,99971,99989,99991]  # prime number list
    prime1 = random.choice(prime)  # randomly select random number from list
    byte_length = 16  # byte_length of array to be sent
    p = prime1.to_bytes(byte_length, 'little')  # convert int to bytes to be sent over socket
    connection.send(p)  # send byte

    # Generation of primitive root modulo and share it with client #

    def primRoots(modulo):
        required_set = {num for num in range(1, modulo) if bltin_gcd(num, modulo)}
        return [g for g in range(1, modulo, 5000) if required_set == {pow(g, powers, modulo) for powers in range(1, modulo)}]

    mod = primRoots(99317)  # Generation of list of primitive roots #
    prim_root = random.choice(mod)  # Selecting a random primitive root #
    g = prim_root.to_bytes(byte_length, 'little')  # convert int to bytes to be sent over socket
    connection.send(g)  # send byte

    # Generation of secret key for server #

    ser_sec_key = random.randint(1, prime1)

    # Compute Server public key and exchange with client #

    A = (prim_root**ser_sec_key) % prime1  # Compute session Key
    A_byte = A.to_bytes(byte_length, 'little')  # Convert to bytes
    connection.send(A_byte)  # Send to client
    B_byte = connection.recv(16)  # Recieve client public key in bytes
    B = int.from_bytes(B_byte, 'little')  # Convert client public key to int
    shared_key_ser = B**ser_sec_key % prime1  # Compute server shared key
    digest = hashes.Hash(hashes.SHA256())
    digest.update(str(shared_key_ser).encode())
    key = digest.finalize()
    return key
    

#Send message to client
def sendMsg(msg, connection, encryptObject):

    #Encrypt the message
    msg = encryptObject.encrypt(msg)

    # Prefix each message with a 4-byte length (network byte order)
    msg = struct.pack('>I', len(msg)) + msg
    connection.sendall(msg)

#Receive Message from client. Returns as bytes.
def recvMsg(connection, encryptObject):
    # Read message length and unpack it into an integer
    raw_msglen = recvall(connection, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Read the message data
    cipher = recvall(connection, msglen)
    return(encryptObject.decrypt(cipher))

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
    encryptObject = symEncrypt.symEncrypt(key)
    while True:
        message = recvMsg(connection, encryptObject)
        if message == None:
            removeClient(connection, address)
            break
        else:
            message = message.decode()
            print(str(address) + ": " + message)

        #Run Requested Command
        cmdlst = message.split(" ") #splits commands into arg array
        if cmdlst[0] == "rdir":
            sendDir(connection, encryptObject)
        elif cmdlst[0] == "up":
            receiveFile(connection, encryptObject)
        elif cmdlst[0] == "down":
            sendFile(connection, cmdlst[1], encryptObject)
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