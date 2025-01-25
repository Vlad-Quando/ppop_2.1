import socket
import struct
import sys


IP: str = '80.87.106.12'
PORT: int = 28026

try:
    
    sct = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sct.connect((IP, PORT))
    sct.settimeout(5)

except OSError:
    print('Station is unactive')
    sys.exit(1)


byte_header: bytes = struct.pack('iii', 1, 0, 0)

sct.sendall(byte_header)

responce: bytes = sct.recv(24)
print(responce)

count = 0
for i in range(len(responce)):
    print(responce[i], end='  ')
    count += 1
    if count == 15:
        count = 0
        print()
print()
# for i in range(0, 20, 4):
#     print(struct.unpack('i', responce[i:i+4])[0], end='\t')
# print()

# for i in range(20, 148):
#     if responce[i] == 0:
#         post_name_end = i
#         break
#     print(chr(responce[i]), end='')
# print()

# count = 0
# for i in range(post_name_end + 1, 148, 4):
#     count += 1
#     print(struct.unpack('i', responce[i:i+4])[0], end='\t')

#     if count == 15:
#         print()
#         count = 0
# print()
sct.close()

