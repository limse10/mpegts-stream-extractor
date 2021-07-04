import klvdata
import sys 

for packet in klvdata.StreamParser(sys.stdin.buffer.read()): 
    data = packet.MetadataList()
    print(data)