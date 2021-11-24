from cryptography.hazmat.primitives import hashes

class symEncrypt:
    def __init__(self, key):
        self.key = str(key).encode()

    def encrypt(self, msg):
        # Add hashed signature to beginning msg.
        digest = hashes.Hash(hashes.SHA256())
        digest.update(self.key + msg)
        signature = digest.finalize()
        msg = signature + msg
        
        #Get requested size of bit stream.
        size = len(msg)

        stream = self._genStream(size)
        cipher = self._byte_xor(msg, stream)
        return cipher

    def decrypt(self, cipher):
        #Get requested size of bit stream.
        size = len(cipher)

        #Generate Stream and xor cipher w/ it.
        stream = self._genStream(size)
        msg = self._byte_xor(cipher, stream)

        #Confirm message matches signature.
        signature = msg[:32]
        msg = msg[32:]
        
        digest = hashes.Hash(hashes.SHA256())
        digest.update(self.key + msg)
        recvSig = digest.finalize()

        if signature != recvSig:
            print("UH OH, THIS MESSAGE HAS BEEN TAMPERED! DO NOT TRUST")

        return msg
    
    def _byte_xor(self, ba1, ba2):
        return bytes([_a ^ _b for _a, _b in zip(ba1, ba2)])

    #View Privacy Portion of Report to see how the bit stream is generated.
    def _genStream(self, size):

        #Get number of runs for bit stream based on file size.
        runs = size/32
        if size % 32 > 0:        #account for trailing bits.
            runs = runs + 1

        #Do the First Run
        digest = hashes.Hash(hashes.SHA256())
        digest.update(self.key)
        prevChunk = digest.finalize()
        bitStream = prevChunk
        
        #Do any additional runs and append to stream.
        for x in range(0, int(runs)-1):
            digest = hashes.Hash(hashes.SHA256())
            digest.update(self.key + prevChunk)
            prevChunk = digest.finalize()
            bitStream = bitStream + prevChunk

        return bitStream