import sys
import numpy as np
import struct

#Reading a single point
def readLHPoint(f):
    pt = {}
    pt['X'] = readFloat(f)
    pt['Y'] = readFloat(f)
    pt['Z'] = readFloat(f)
    return pt

#Writing a single point
def writeLHPoint(f,val):
    writeFloat(f,val['X'])
    writeFloat(f,val['Y'])
    writeFloat(f,val['Z'])

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
    
def readString(f,mxRead):
    mystr = ''
    c = ' '
    cnt = 0
    while ((c[0] != 0)and(cnt<mxRead)):
        c = struct.unpack('c', f.read(1))[0]
        if(c[0] != 0):
            b = c[0].to_bytes(1, sys.byteorder)
            mystr += b.decode('utf-8', 'backslashreplace')

        cnt+=1
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
def writeString(f,val):
    for c in val:
        f.write(struct.pack('<c',bytes(c,'utf-8')))
		
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