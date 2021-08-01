import sys
import numpy as np
import struct

# Low level reading functions: int32, float, and string [until null is reached, null not included in returned string]
def readInt32(f):
    return struct.unpack('<i', f.read(4))[0]
def readUInt32(f):
    return struct.unpack('<I', f.read(4))[0]
#Read int16
def readInt16(f):
    return struct.unpack('<h', f.read(2))[0]
def readUInt16(f):
    return struct.unpack('<H', f.read(2))[0]
#Read int8	
def readInt8(f):
    return struct.unpack('<b', f.read(1))[0]
def readUInt8(f):
    return struct.unpack('<B', f.read(1))[0]
#Read float (4 bytes)
def readFloat(f):
    return struct.unpack('<f', f.read(4))[0]
    
def readString(f,mxRead,jump=False):
    mystr = ''
    c = ' '
    cnt = 0
    while ((c[0] != 0)and(cnt<mxRead)):
        c = struct.unpack('c', f.read(1))[0]
        if(c[0] != 0):
            b = c[0].to_bytes(1, sys.byteorder)
            mystr += b.decode('utf-8', 'backslashreplace')

        cnt+=1
    
    #There is a possiblity that the string has a dedicated amount of space, like 64 bytes
    #   Which would have been passed in via the parameter mxRead. If jump = true
    #   This following code will jump the file pointer to where the string would have ended
    if(jump == True):
        f.seek(f.tell()+((mxRead-1) - len(mystr)))
    return mystr
    
# Low level writing functions:
def writeInt32(f,val):
    f.write(struct.pack('<i',val))
    
def writeUInt32(f,val):
    f.write(struct.pack('<I',val))
#Write int16	
def writeInt16(f,val):
    f.write(struct.pack('<h',val))
    
def writeUInt16(f,val):
    f.write(struct.pack('<H',val))
#Write int8
def writeInt8(f,val):
    f.write(struct.pack('<b',val))
    
def writeUInt8(f,val):
    f.write(struct.pack('<B',val))
#Write float (4 bytes)
def writeFloat(f,val):
    f.write(struct.pack('<f',val))
#Write String
def writeString(f,val,num=64):
    for c in val:
        f.write(struct.pack('<c',bytes(c,'utf-8')))
    #Write zeros for the rest of the string
    if(len(val) < num):
        for x in range(len(val),num):
            writeInt8(f,0)

		
#numpy data type
#	'<': little endian
#	'>': big endian
#	Variable Type
#	'b': Boolean
#	'i': integer
#	'u': unsigned integer
#	'f': float
#	'c': complex-floating point
#	'm': timedelta
#	'M': Datetime
#	'O': Python Object
#	'S','a': (byte-) String
#	'U': Unicode
#	'V': Raw Data
#	Number of Bytes
#		Following the variable type a number is used to intidate the number of bytes to read
#	Example
#		'<i4': Little endian 32bit integer