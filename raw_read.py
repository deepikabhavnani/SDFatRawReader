import sys

drive = r"\\.\E:"
Blocksize = 512
Block_buf = ""
ClusterCount = 0
NumSecPerCluster = 0
ResvSectors = 0
FATStartSector = 0
RootDirStartSector = 0
DataAreaStartSector = 0

def check_and_print(block_num):
    if all(ord(i) == 0 for i in Block_buf):
        print 'Skipping all zero block %d' %block_num
    else :
        print_block_data(0)
    
def print_block_data(inhex):
    str = ""
    count = 0
    if inhex:
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
    disk = file(drive,'rb')
    disk.seek(physical_num*Blocksize)
    Block_buf = disk.read(Blocksize)    
    disk.close()
    
def decode_boot_sector():
    global Blocksize, ClusterCount, NumSecPerCluster, ResvSectors, FATStartSector, RootDirStartSector

    read_blocks_print(0,1,0)
    #11-12   Number of bytes per sector (512)
    Blocksize = 256*ord(Block_buf[12])+ord(Block_buf[11])
    print "BytesPerSector = %d" %Blocksize

    #13      Number of sectors per cluster (1)
    NumSecPerCluster = ord(Block_buf[13])
    print "SectorsPerCluster = %d" %NumSecPerCluster
    clusterSize = NumSecPerCluster*Blocksize
    print "ClusterSize = %d" %clusterSize
    
    #14-15   Number of reserved sectors (1)
    ResvSectors = 256*ord(Block_buf[15])+ord(Block_buf[14])
    print "ReservedSectors = %d" %ResvSectors

    #16      Number of FAT copies (2)
    fatCopy = ord(Block_buf[16])
    print "FatCopies = %d" %fatCopy

    #17-18   Number of root directory entries (224)
    rootDirEntry = 256*ord(Block_buf[18])+ord(Block_buf[17])
    print "RootDirectoryEntries = %d - Note 0 for FAT32" %rootDirEntry

    #19-20   Total number of sectors in the filesystem
    totalSectors = 256*ord(Block_buf[20])+ord(Block_buf[19])
    #32-35   Total number of sectors in the filesystem
    if not totalSectors:
        totalSectors = (ord(Block_buf[35]) << 24) + (ord(Block_buf[34]) << 16) + (ord(Block_buf[33]) << 8) + ord(Block_buf[32])
    print "TotalSectors = %d" %totalSectors
    
    #22-23   Number of sectors per FAT
    secPerFat = 256*ord(Block_buf[23])+ord(Block_buf[22])
    if not secPerFat:
        secPerFat = (ord(Block_buf[39]) << 24) + (ord(Block_buf[38]) << 16) + (ord(Block_buf[37]) << 8) + ord(Block_buf[36])
    print "SectorsPerFAT = %d" %secPerFat

    #44-47   First cluster of root directory (usually 2)
    rootDir = (ord(Block_buf[47]) << 24) + (ord(Block_buf[46]) << 16) + (ord(Block_buf[45]) << 8) + ord(Block_buf[44])
    print "RootDirectory = %d" %rootDir

    #Number of clusters in the data area = total number of sectors - (space for reserved sectors, FATs and root directory)
    # and dividing, rounding down, by the number of sectors in a cluster
    ClusterCount = (totalSectors - (ResvSectors)) / NumSecPerCluster
    print "ClustersInUserArea = %d" %ClusterCount
    if ClusterCount < 4085:
        print "FAT12"
    elif ClusterCount < 65525:
        print "FAT16"
    else:
        print "FAT32"        
    
    #510-511 Signature 55 aa
    if (0x55 == ord(Block_buf[510])) and (0xaa == ord(Block_buf[511])):
        print "Signature matches 55 AA"

    FATStartSector = ResvSectors
    print "FATStartSector = %d" %FATStartSector

    RootDirStartSector = FATStartSector + (secPerFat*fatCopy);
    print "RootDirStartSector = %d" %RootDirStartSector

    
def decode_root_dir():
    read_blocks_print(RootDirStartSector,2,1)
    
decode_boot_sector()
read_blocks_print(FATStartSector,1,1)
decode_root_dir()

