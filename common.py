Drive = r"\\.\E:"
Blocksize = 512
Block_buf = ""
ClusterCount = 0
NumSecPerCluster = 0
FatCopy = 0
TotalSectors = 0
SectorPerFat = 0
RootDirEntry = 0
ResvSectors = 0
FATStartSector = 0
RootDirStartSector = 0
DataAreaStartSector = 0
#FatType - 1 FAT12, 2 - FAT16, 3 - FAT32
FatType = 0
HexPrint = 1


def check_and_print(block_num):
    if all(ord(i) == 0 for i in Block_buf):
        print 'Skipping all zero block %d' %block_num
    else :
        print_block_data()

def print_block_data():
    str = ""
    count = 0
    if HexPrint:
        for ch in Block_buf:
            str += hex(ord(ch)) + " "
            count += 1
            if (16 == count):
                print str
                str = ""
                count = 0
    else:
        str = Block_buf
    print str

def read_blocks_print(physical_num, count, ifprint):
    for i in range(count):
        read_block(physical_num)
        if ifprint:
            check_and_print(physical_num)
        physical_num += 1


def read_block(physical_num):
    global Block_buf
    disk = file(Drive,'rb')
    disk.seek(physical_num*Blocksize)
    Block_buf = disk.read(Blocksize)
    disk.close()
