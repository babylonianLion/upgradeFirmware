# Author: Hussain Al Zerjawi
# Organization: Radiator Labs
# Assignment: IoT Firmware upgrade
# Date: 04/25/2021

import requests
import math
from base64 import b64encode, b64decode
import sys

def upload_firmware(file):
    with open(file, 'r') as firmware:
        # This code segmant is part of the alternative solution (wrong checksum) in which only the data field of the hex was sent
        #data = firmware.readlines()

        # Removing EOL
        data = firmware.read().replace('\n', '')

    # Removing colons
    data = data.replace(':', '')

    # Converting the HEX into base64
    data = b64encode(bytes.fromhex(data)).decode()

    iterations = math.ceil(len(data) / 20)

    # start and end index for slicing data into chunks
    start = 0
    end = 20
    
    for x in range(iterations):
        # In case the last iteration doesn't have 20 elements we just send over the last remaining elements
        if(x==iterations -1):
            status = post_chunk(data[start])
            # In case the node server didn't favour me, it will resend the latest missing package
            while status == False:
                status = post_chunk(data[start])
        else:
            status = post_chunk(data[start:end])
            while status == False:
                status = post_chunk(data[start:end])
        # Here I increment for the next chunk
        start += 20
        end += 20

# This code segmant is part of the alternative solution (wrong checksum though) in which only the data field of the hex was sent
"""
    for line in data:
        if(line[7:9] == '01'):
            break
        elif(line[7:9] == '00'):
            status = post_chunk(b64encode(bytes.fromhex(line[1:-1])).decode())
            while status == False:
                status = post_chunk(b64encode(bytes.fromhex(line[1:-1])).decode())
"""
# POST Request Chunk
def post_chunk(chunk):
    data = "CHUNK: " + str(chunk)
    resp = requests.post('http://localhost:3000/', data=data)
    print(resp.status_code)
    if resp.status_code == 200:
        if(resp.text == "OK\n"):
            return True
        elif(resp.text == "ERROR PROCESSING CONTENTS\n"):
            return False
    elif resp.status_code == 500:
        print(resp.text)

# POST Request Checksum
def post_checksum():
    data = "CHECKSUM"
    resp = requests.post('http://localhost:3000/', data=data)
    print(resp.status_code)
    if resp.status_code == 200:
        print(resp.text)

def main(argv):
    upload_firmware(argv)
    post_checksum()

if __name__ == "__main__":
    main(sys.argv[1])
