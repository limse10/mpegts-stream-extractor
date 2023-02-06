import subprocess
from threading import Thread
from queue import Queue, Empty
import numpy as np
import cv2 
import klvdata


"""
DISCLAIMER!
This implementation assumes a 16-byte length key and BER length encoding for the KLV packet
If not then I have no idea how to read in the KLV data from a stream without calculating its length using the KLV spec
"""

#TODO: argparse udp stream

def read_into_buffer(src,num_bytes,buffer):
    """
    Reads num_bytes bytes from src and returns the data, as well as the updated buffer
    """
    data = src.read(num_bytes)
    return data, buffer+data

def reader(f,q):
    """
    async reader to get the klv packet and push it to a queue
    assumes 16-byte key length and BER length encoding
    """
    buffer=b'' # empty buffer
    while True:
        header, buffer = read_into_buffer(f,4,buffer) # gets first 4 header bytes 
        if header==b'\x06\x0e+4': # checks sync
            _, buffer = read_into_buffer(f,12,buffer) # reads in rest of header (idc abt the rest)
            length_key, buffer = read_into_buffer(f,1,buffer) # reads BER byte
            if ord(length_key)<128:
                length = ord(length_key)
            else:
                num_len_bytes = ord(length_key)-128
                length, buffer = read_into_buffer(f,num_len_bytes,buffer)
                length = int.from_bytes(length, "big")

            _, buffer = read_into_buffer(f,length,buffer) # reads value packet and stores into buffer
            q.put(buffer)
            buffer=b''
                    
           

video_stream_cmd = ['ffmpeg', '-i', 'udp://@localhost:12345', '-map', '0:0',  '-f', 'image2pipe', '-pix_fmt', 'bgr24', '-codec', 'rawvideo', '-']
vid_proc = subprocess.Popen(video_stream_cmd,stdin=subprocess.PIPE, stdout=subprocess.PIPE)

#TODO obtain stream mappings from the stream somehow
klv_stream_cmd = ['ffmpeg', '-i', 'udp://@localhost:1234?overrun_nonfatal=1&fifo_size=500000', '-map', '0:1',  '-f', 'data', '-codec', 'copy', '-']
klv_proc = subprocess.Popen(klv_stream_cmd,stdin=subprocess.PIPE, stdout=subprocess.PIPE)
q = Queue()
t=Thread(target=reader,args=(klv_proc.stdout,q))
t.daemon = True
t.start()


# TODO: get w and h values from metadata somehow
width = 1280 
height = 720

if __name__=='__main__':
    while True:
        try:
            buffer = q.get_nowait() # gets buffer from queue if any
            for packet in klvdata.StreamParser(buffer): 
                data = packet.MetadataList()
                print(data)  
        except Empty: pass # empty buffer is ok

        raw_frame = vid_proc.stdout.read(width*height*3) # reads raw video stream
        frame = np.frombuffer(raw_frame, np.uint8)
        frame = frame.reshape((height, width, 3))
        cv2.imshow('frame',frame)
        cv2.waitKey(1)
