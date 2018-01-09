import sys
import common

def print_boot_sector():
    print "BytesPerSector = %d" %common.Blocksize
    print "SectorsPerCluster = %d" %common.NumSecPerCluster
    print "ClusterSize = %d" %(common.NumSecPerCluster*common.Blocksize)
    print "ReservedSectors = %d" %common.ResvSectors
    print "FatCopies = %d" %common.FatCopy
    print "TotalSectors = %d" %common.TotalSectors
    print "SectorsPerFAT = %d" %common.SectorPerFat
    print "RootDirectory = %d" %common.RootDirEntry
    print "FATStartSector = %d" %common.FATStartSector
    print "RootDirStartSector = %d" %common.RootDirStartSector
    print "ClustersInUserArea = %d" %common.ClusterCount
    print "DataAreaStartSector = %d" %common.DataAreaStartSector

def decode_boot_sector():
    common.read_blocks_print(0,1,0)
    #11-12   Number of bytes per sector (512)
    common.Blocksize = 256*ord(common.Block_buf[12])+ord(common.Block_buf[11])

    #13      Number of sectors per cluster (1)
    common.NumSecPerCluster = ord(common.Block_buf[13])

    #14-15   Number of reserved sectors (1)
    common.ResvSectors = 256*ord(common.Block_buf[15])+ord(common.Block_buf[14])

    #16      Number of FAT copies (2)
    common.FatCopy = ord(common.Block_buf[16])

    #17-18   Number of root directory entries (224)
    rootDirEntry = 256*ord(common.Block_buf[18])+ord(common.Block_buf[17])

    #19-20   Total number of sectors in the filesystem
    common.TotalSectors = 256*ord(common.Block_buf[20])+ord(common.Block_buf[19])
    #32-35   Total number of sectors in the filesystem
    if not common.TotalSectors:
        common.TotalSectors = (ord(common.Block_buf[35]) << 24) + (ord(common.Block_buf[34]) << 16) + (ord(common.Block_buf[33]) << 8) + ord(common.Block_buf[32])

    #22-23   Number of sectors per FAT
    common.SectorPerFat = 256*ord(common.Block_buf[23])+ord(common.Block_buf[22])
    if not common.SectorPerFat:
        common.SectorPerFat = (ord(common.Block_buf[39]) << 24) + (ord(common.Block_buf[38]) << 16) + (ord(common.Block_buf[37]) << 8) + ord(common.Block_buf[36])

    #44-47   First cluster of root directory (usually 2)
    common.RootDirEntry = (ord(common.Block_buf[47]) << 24) + (ord(common.Block_buf[46]) << 16) + (ord(common.Block_buf[45]) << 8) + ord(common.Block_buf[44])

    #510-511 Signature 55 aa
    if (0x55 != ord(common.Block_buf[510])) or (0xaa != ord(common.Block_buf[511])):
        print "Error: Boot block signature fails"

    common.FATStartSector = common.ResvSectors
    common.RootDirStartSector = common.FATStartSector + (common.SectorPerFat*common.FatCopy)
    common.DataAreaStartSector = common.RootDirStartSector + (32*rootDirEntry + common.Blocksize-1) / common.Blocksize

    #Number of clusters in the data area = total number of sectors - (space for reserved sectors, FATs and root directory)
    # and dividing, rounding down, by the number of sectors in a cluster
    common.ClusterCount = (common.TotalSectors - common.DataAreaStartSector) / common.NumSecPerCluster
    if common.ClusterCount < 4085:
        common.FatOffset = 1.5
        print "FAT12"
    elif common.ClusterCount < 65525:
        common.FatOffset = 2
        print "FAT16"
    else:
        common.FatOffset = 4
        print "FAT32"
    if common.ClusterCount > 268435445:
        print  "Error: cluster count cannot exceeed 268435445"
