#!/usr/bin/python3.4

# An RFC-6455 implementation (incomplete)
# (c) Dmytro Nikandrov
# July 2016


# standard https://tools.ietf.org/html/rfc6455
# standard values & constants https://www.iana.org/assignments/websocket/websocket.xhtml
# easy RU theory http://learn.javascript.ru/websockets
# polishing TODOs http://stackoverflow.com/a/18371023
# tutorial https://www.fullstackpython.com/websockets.html

# code sample https://github.com/nekudo/php-websocket/blob/master/server/lib/WebSocket/Connection.php
# code sample http://stackoverflow.com/a/18371023
# code sample https://habrahabr.ru/post/179585/
# code sample http://stackoverflow.com/questions/16608296/websocket-javascript-client-and-python-server-retreiving-garbage-in-output


import binascii #only for debug incoming bytes
import array
import time
import socket #https://docs.python.org/3/library/socket.html
import hashlib
import sys
import re
import logging
import signal
from select import select
from threading import Thread
from base64 import b64encode

import serial



class Frame(object):
    def __init__(self, a, b, c, d, e, f, g, h, i, j, k):
        self.rawframe = a
        self.fin = b
        self.rsv1 = c
        self.rsv2 = d
        self.rsv3 = e
        self.opcode = f
        self.isMasked = g
        self.dataLen = h
        self.maskingKey = i
        self.payloadDataRaw = j
        self.payloadDataText = k
        #self. = 
        #self. = 
    
    def print(self):
        logging.info("--- frame data ---")
        print('\nraw frame')
        print(binascii.hexlify(self.rawframe))
        print('\nfin bit')
        print(self.fin)
        print('\nrsv1 bit')
        print(self.rsv1)
        print('\nrsv2 bit')
        print(self.rsv2)
        print('\nrsv3 bit')
        print(self.rsv3)
        print('\nopcode')
        print(self.opcode)
        print('\nmask bit')
        print(self.isMasked)
        print('\nmasking key')
        print(binascii.hexlify(self.maskingKey))
        print('\npayload data length')
        print(self.dataLen)
        print('\npayload raw')
        print(binascii.hexlify(self.payloadDataRaw))
        print('\npayload as utf-8:')
        print(self.payloadDataText)
        
        

class FrameParser(object):
    BYTEORDER = 'little'
    OPCODE_MASK = 0b00001111

    def __init__(self, somebytes):
        self.somebytes = somebytes

    def encode(self):
        logging.info("FrameParser: try encode() frame to bytes")
        # TBD Take Frame object and construct bytes to send

    def decode(self):
        logging.info("FrameParser: try decode() incoming bytes as frame")

        firstbyte = self.somebytes[0:1]   # 1st byte of data
        fin = (0x80 & int.from_bytes(firstbyte, self.BYTEORDER)) != 0
        rsv1 = (0x40 & int.from_bytes(firstbyte, self.BYTEORDER)) != 0
        rsv2 = (0x20 & int.from_bytes(firstbyte, self.BYTEORDER)) != 0
        rsv3 = (0x10 & int.from_bytes(firstbyte, self.BYTEORDER)) != 0
        opcode = self.OPCODE_MASK & int.from_bytes(firstbyte, self.BYTEORDER)

        secondbyte = self.somebytes[1:2]   # 2nd byte of data
        masked =  (0x80 & int.from_bytes(secondbyte, self.BYTEORDER)) != 0
        payloadLength = (0x7F & int.from_bytes(secondbyte, self.BYTEORDER))

        if payloadLength <= 125:
            # payload data length in bytes == the payload length
            dataLength = payloadLength
            payloadOffset = 6
            maskingK = self.somebytes[2:payloadOffset]

        if payloadLength == 126:
            # payload data length is the following 2 bytes interpreted as uint_16
            dataLength = int.from_bytes(self.somebytes[2:4], self.BYTEORDER)
            payloadOffset = 8
            maskingK = self.somebytes[4:payloadOffset]

        if payloadLength == 127:
            # payload data length is the following 8 bytes interpreted as uint_64
            dataLength = int.from_bytes(self.somebytes[2:10], self.BYTEORDER)
            payloadOffset = 14
            maskingK = self.somebytes[10:payloadOffset]

        payloadOffsetEnd = payloadOffset + dataLength

        payloadRaw = self.somebytes[payloadOffset:payloadOffsetEnd]

        if masked:
            unmasked = array.array("B", payloadRaw)
            
            # temporary check - should be removed after tests
            if len(payloadRaw) != dataLength:
                print('incorrect dataLength calculation')
                sys.exit()

            for i in range(len(payloadRaw)):
                unmasked[i] = unmasked[i] ^ maskingK[i % 4]
            print(unmasked)
            payloadText = bytes(unmasked).decode("utf-8", "ignore")

        '''
        TBD: To check for large frames here.
        con.recv(1024) cuts at 1024 bytes, so if websocket-frame is > 1024 bytes we have
        to wait until whole data is transfered.
        '''
        
        return Frame(self.somebytes, fin, rsv1, rsv2, rsv3, opcode, masked, dataLength, maskingK, payloadRaw, payloadText)


    
class WebSocket(object):
    GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

    handshake = (
        "HTTP/1.1 101 Web Socket Protocol Handshake\r\n"
        "Upgrade: WebSocket\r\n"
        "Connection: Upgrade\r\n"
        "WebSocket-Origin: %(origin)s\r\n"
        "WebSocket-Location: ws://%(host)s:%(port)s/\r\n"
        "Sec-Websocket-Accept: %(accept)s\r\n"
        "Sec-Websocket-Origin: %(origin)s\r\n"
        "Sec-Websocket-Location: ws://%(host)s:%(port)s/\r\n"
        "\r\n"
    )
    
    def __init__(self, client, server):
        self.conn = client
        self.server = server
        self.handshaken = False
        self.header = ""
#        self.data = ""



    def feed(self, data):
        if not self.handshaken:
            print('---')
            print(data.decode("utf-8"))
            print('---')
            self.header += str(data)
            if self.header.find('\\r\\n\\r\\n') != -1:
                parts = self.header.split('\\r\\n\\r\\n', 1)
                self.header = parts[0]
                if self.dohandshake(self.header, parts[1]):
                    logging.info("Handshake successful")
                    self.handshaken = True
        else:
            self.onmessage(data)

    def dohandshake(self, header, key=None):
        logging.debug("Begin handshake: %s" % header)
        digitRe = re.compile(r'[^0-9]')
        spacesRe = re.compile(r'\s')
        part = part_1 = part_2 = origin = None
        for line in header.split('\\r\\n')[1:]:
            name, value = line.split(': ', 1)
            if name.lower() == "sec-websocket-key1":
                key_number_1 = int(digitRe.sub('', value))
                spaces_1 = len(spacesRe.findall(value))
                if spaces_1 == 0:
                    return False
                if key_number_1 % spaces_1 != 0:
                    return False
                part_1 = key_number_1 / spaces_1
            elif name.lower() == "sec-websocket-key2":
                key_number_2 = int(digitRe.sub('', value))
                spaces_2 = len(spacesRe.findall(value))
                if spaces_2 == 0:
                    return False
                if key_number_2 % spaces_2 != 0:
                    return False
                part_2 = key_number_2 / spaces_2
            elif name.lower() == "sec-websocket-key":
                part = bytes(value, 'UTF-8')
            elif name.lower() == "origin":
                origin = value
        if part:
            logging.debug("Using challenge + response")
            #challenge = struct.pack('!I', part_1) + struct.pack('!I', part_2) + key
            #response = hashlib.md5(challenge).digest()
            sha1 = hashlib.sha1()
            sha1.update(part)
            sha1.update(self.GUID.encode('utf-8'))
            accept = (b64encode(sha1.digest())).decode("utf-8", "ignore")
            handshake = WebSocket.handshake % {
                'accept': accept,
                'origin': origin,
                'port': self.server.port,
                'host': self.server.host
            }
            #handshake += response
        else:
            logging.warning("Not using challenge + response")
            handshake = WebSocket.handshake % {
                'origin': origin,
                'port': self.server.port,
                'host': self.server.host
            }
        logging.debug("Sending handshake\n\n%s" % handshake)
        self.conn.send(bytes(handshake, 'UTF-8'))
        return True

    def onmessage(self, data):
        logging.info("Got new frame")
        f = FrameParser(data).decode()
        self.analyzeFrame(f)
        

    def send(self, data):
        logging.info("Sent message: %s" % data)
        self.conn.send("\x00%s\xff" % data)

    def closingHandshake(self, opcode):
        logging.debug("Closing handshake %s" % opcode)
        frame_Close = bytes.fromhex('88 02 03 e8')    # close frame with status code 1000 CLOSE_NORMAL
        #(138).to_bytes(2, 'big')
        print('\control frame as hex:')
        print(binascii.hexlify(frame_Close))
        print(frame_Close)
        self.conn.sendall(frame_Close)

    def analyzeFrame(self, frame):
        frame.print()
        
        #TODO: add control frame fin validation here
        
        if frame.rsv1 or frame.rsv2 or frame.rsv1:
            print('error: some of RSV bits are non-zero')
            # TBD terminate the connection with 1002 error code

        if frame.opcode == 0:
            print('opcode: Continuation Frame')
        elif frame.opcode == 1:
            print('opcode: Text Frame')
        elif frame.opcode == 2:
            print('opcode: Binary Frame')
        elif frame.opcode == 8:
            print('opcode: Connection Close Frame')
            self.closingHandshake(frame.opcode)
        elif frame.opcode == 9:
            print('opcode: Ping Frame')
        elif frame.opcode == 10:
            print('opcode: Pong Frame ')
        elif frame.opcode in set([3, 4, 5, 6, 7, 11, 12, 13, 14, 15]):
            print('error: undefined opcode - protocol violation')
            # TBD terminate the connection with 1002 error code

        if not frame.isMasked:
            print('error: mask is not set by client - protocol violation')
            # TBD terminate the connection with 1002 error code

        #TODO: add control frame payload length validation here
        
        
        print('\nREADY TO ARDU:')
        print(frame.payloadDataText.encode('ascii'))
        ser.write(frame.payloadDataText.encode('ascii'))



    def close(self):
        self.conn.close()
        


#        self.data += data.decode("utf-8", "ignore")



class WebSocketServer(object):
    def __init__(self, ser, host, port, cls):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((host, port))
        self.ser = ser
        self.host = host
        self.port = port
        self.cls = cls
        self.connections = {}
        self.listeners = [self.socket]
        #self.ser.open()

    def listen(self, backlog=5):
        self.socket.listen(backlog)
        logging.info("Listening on port %s" % self.port)
        self.running = True
        while self.running:
            '''
            https://docs.python.org/3/library/select.html
            straightforward interface to the Unix select() system call
            rlist: wait until ready for reading
            wlist: wait until ready for writing
            xlist: wait for an “exceptional" condition
            1 sec timeout
            '''
            rList, wList, xList = select(self.listeners, [], self.listeners, 1)
            for ready in rList:
                logging.debug("ready = %s" % ready)
                if ready == self.socket:
                    logging.debug("New client connection")
                    con, address = self.socket.accept()
                    fileno = con.fileno()
                    self.listeners.append(fileno)
                    self.connections[fileno] = self.cls(con, self)
                else:
                    logging.debug("Client ready for reading %s" % ready)
                    con = self.connections[ready].conn
                    data = con.recv(1024)
                    fileno = con.fileno()
                    if data:
                        self.connections[fileno].feed(data)
                    else:
                        logging.debug("Closing client %s" % ready)
                        self.connections[fileno].close()
                        del self.connections[fileno]
                        self.listeners.remove(ready)
            for failed in xList:
                if failed == self.socket:
                    logging.error("Socket broke")
                    for fileno, conn in self.connections:
                        conn.close()
                    self.running = False




if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
    
    ser = serial.Serial('/dev/ttyACM0', 9600)

    # empty host "" means i want receive connection from ANY host
    server = WebSocketServer(ser, "", 12345, WebSocket)
    server_thread = Thread(target=server.listen, args=[5])
    server_thread.start()
    # add SIGINT handler for killing the threads
    def signal_handler(signal, frame):
        logging.info("Caught Ctrl+C, shutting down...")
        server.running = False
        sys.exit()
    signal.signal(signal.SIGINT, signal_handler)
    while True:
        time.sleep(100)
