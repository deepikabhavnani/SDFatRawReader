import common
import boot_sector
import fat_table
from array import array

def set_dummy_values():
    common.HexPrint = 0
    common.Blocksize = 512
    common.NumSecPerCluster = 64
    common.ResvSectors = 32
    common.FatType = 3
    common.FatCopy = 1
    common.TotalSectors = 15644609
    common.SectorPerFat = 1910
    common.RootDirEntry = 2
    common.FATStartSector = 32
    #common.FATStartSector = 150
    common.RootDirStartSector = 1942
    common.ClusterCount = 244416
    common.DataAreaStartSector = 1942

common.Drive = r"\\.\E:"
boot_sector.read_boot_sector()
boot_sector.decode_boot_sector()
boot_sector.print_boot_sector()
#set_dummy_values()
#fat_table.decode_fat_table()
#fat_table.print_fat_table_entries()
#boot_sector.read_boot_sector()
#common.read_blocks_print(80208,1,1)
