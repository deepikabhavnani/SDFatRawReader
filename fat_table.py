import sys
import common
import boot_sector
from array import array

AvailClus = array('L')
ResvClus = array('L')
BadClus = array('L')
UserClus = array('L')
EndMarkers = array('L')

def getFatSectorNum(entry_num):
    if common.FatType == 1:
        return (common.FATStartSector + ((entry_num+(entry_num/2)) / common.Blocksize))
    elif common.FatType == 2:
        return (common.FATStartSector + (entry_num*2) / common.Blocksize)
    elif common.FatType == 3:
        return (common.FATStartSector + (entry_num*4) / common.Blocksize)
    else:
        print"Error: Incorrect Fat type"
        sys.exit()

def getFatEntryOffset(entry_num):
    if common.FatType == 1:
        return ((entry_num+(entry_num/2)) % common.Blocksize)
    elif common.FatType == 2:
        return ((entry_num*2) % common.Blocksize)
    elif common.FatType == 3:
        return ((entry_num*4) % common.Blocksize)
    else:
        print"Error: Incorrect Fat type"
        sys.exit()

def getFatValue(off):
    if common.FatType == 1:
        fatValue = 0
        '''TODO'''
    elif common.FatType == 2:
        fatValue = (ord(common.Block_buf[off+1]) << 8) + ord(common.Block_buf[off])
    elif common.FatType == 3:
        fatValue = (ord(common.Block_buf[off+3]) << 24) + (ord(common.Block_buf[off+2]) << 16) + (ord(common.Block_buf[off+1]) << 8) + ord(common.Block_buf[off])
    return fatValue

def decodeFatErrors(value, entry):
    if value == 0:
        AvailClus.append(entry)
        print ", ".join('%02d'%x for x in AvailClus)
        return
    elif value == 1:
        ResvClus.append(entry)
        print ", ".join('%02d'%x for x in ResvClus)
        return 
    if common.FatType == 1:
        if value == 0xFF7:
            BadClus.append(entry)
        elif value >= 0xFF8:
            EndMarkers.append(entry)
        else:
            UserClus.append(entry)
    elif common.FatType == 2:
        if value == 0xFFF7:
            BadClus.append(entry)
        elif value >= 0xFFF8:
            EndMarkers.append(entry)
        else:
            UserClus.append(entry)
    elif common.FatType == 3:
        if (value & 0xF0000000):
            print "Error: FAT Entry error (Last 4bits not masked) at FAT[%d]" %entry
        elif value == 0xFFFFFF7:
            BadClus.append(entry)
        elif value >= 0xFFFFFF8:
            EndMarkers.append(entry)            
        else:
            UserClus.append(entry)

def decodeFatValue(value, entry):
    if value == 0:
        print "Available Cluster at FAT[%d]" %entry
        return
    elif value == 1:
        print "Reserved cluster at FAT[%d]" %entry
        return 
    if common.FatType == 1:
        if value == 0xFF7:
            print "Bad Cluster at FAT[%d]" %entry
        elif value >= 0xFF8:
            print "End Marker: FAT at FAT[%d]" %entry
        else:
            print "User data %x at FAT[%d]" %(value, entry)
    elif common.FatType == 2:
        if value == 0xFFF7:
            print "Bad Cluster at FAT[%d]" %entry
        elif value >= 0xFFF8:
            print "End Marker: FAT at FAT[%d]" %entry
        else:
            print "User data %x at FAT[%d]" %(value, entry)
    elif common.FatType == 3:
        if (value & 0xF0000000):
            print "Error: FAT Entry error (Last 4bits not masked) at FAT[%d]" %off
        elif value == 0xFFFFFF7:
            print "Bad Cluster at FAT[%d]" %entry
        elif value >= 0xFFFFFF8:
            print "End Marker: FAT at FAT[%d]" %entry
        else:
            print "User data %x at FAT[%d]" %(value, entry)

def read_fat_entry(entry_num):
    if not common.FatType:
        boot_sector.decode_boot_sector()
    fatSectorNum = getFatSectorNum(entry_num)
    common.read_blocks_print(fatSectorNum,1,0)
    fatEntryOffset = getFatEntryOffset(entry_num)
    value = getFatValue(fatEntryOffset)
    decodeFatValue(value, entry_num)
    return value

def decode_fat_table():
    if not common.FATStartSector:
        boot_sector.decode_boot_sector()

    entry_num = 2
    prev_block_num = 0
    block_num = getFatSectorNum(entry_num)    
    while (block_num <= common.FATStartSector+2):
        if (prev_block_num != block_num):
            common.read_blocks_print(block_num,1,0)
            prev_block_num = block_num
        fatEntryOffset = getFatEntryOffset(entry_num)
        value = getFatValue(fatEntryOffset)
        decodeFatErrors(value, entry_num)
        entry_num += 1
        block_num = getFatSectorNum(entry_num)

def print_array_elements(a):
    limit_in_line = len(a) if (len(a) < 16) else 16
    count = limit_in_line    
    for x in a:
        sys.stdout.write(str(x))
        sys.stdout.write(' ')
        count -= 1
        if (0 == count):
            sys.stdout.flush()
            print ''
            count = limit_in_line
    print ''
    
def print_fat_table_entries():
    print "Available Cluster list:"
    print_array_elements(AvailClus)
    print "Reserved Cluster list:"
    print_array_elements(ResvClus)
    print "Bad Cluster list:"
    print_array_elements(BadClus)
    print "User Cluster list:"
    print_array_elements(UserClus)
    print "End Markers Cluster list:"
    print_array_elements(EndMarkers)

def decode_root_dir():
    common.read_blocks_print(common.RootDirStartSector,2,1)
