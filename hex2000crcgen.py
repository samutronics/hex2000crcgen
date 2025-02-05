import array
import sys
import math 

class HexParser:
    def __init__(self, filename, outputfilename, startaddress, numofblocks, blocksize):
        self.filename = filename
        self.outputfilename = outputfilename
        self.total_data_size = 0
        self.extended_address = 0
        self.start_address = startaddress
        self.end_address = startaddress + (numofblocks * blocksize)
        self.numofblocks = numofblocks
        self.blocksize = blocksize    
        # create a binary buffer to store the data prefill with 0xFF the size is the end address - start address
        self.binary_buffer = array.array('H', [0xFFFF] * (self.numofblocks * self.blocksize))     
        # create a binary buffer for the CRC data; 
        self.crc_buffer = array.array('I', [0xFFFFFFFF] * (self.numofblocks))
        
    
    def parse(self):        
        with open(self.filename, 'r') as file:           
            for line in file:
                if not line.startswith(':'):
                    continue
                # check for the extended segment address record
                if line[7:9] == "02":
                    self.extended_address = int(line[9:13], 16) << 4
                    continue
                # check for the start segment address record
                if line[7:9] == "03":
                    self.start_address = int(line[9:13], 16) << 4
                    continue
                # check for the extended linear address record
                if line[7:9] == "04":
                    self.extended_address = int(line[9:13], 16) << 16
                    continue
                # check for the start linear address record
                if line[7:9] == "05":
                    self.start_address = int(line[9:13], 16)
                    continue
                # check for the data record the address is pointing to 16bit words but the hex record is in 8bit bytes!!!
                if line[7:9] == "00":                  
                    length = int(line[1:3], 16)
                    address = self.extended_address + int(line[3:7], 16)
                    record_type = int(line[7:9], 16)
                    data = line[9:9 + (length * 2)]
                    checksum = int(line[9 + (length * 2):], 16)                
                    #if the data falls withing the start and end address range; add it to the binary buffer
                    #the binary buffer index 0 corresponds to the start address
                    if address >= self.start_address and address < self.end_address:
                        bufferstartindex = address - self.start_address
                        # itearate through the data and add 2 consecutive hex values to the binary buffer
                        # the binary buffer is a 16bit array
                        # the data is stored in little endian format
                        # the first byte is the least significant byte
                        for i in range(0, length*2, 4): #process 4 hex characters at a time
                            word_data = data[i:i + 4] #get 4 hex characters
                            word_value = int(word_data, 16) #convert to integer
                            self.binary_buffer[bufferstartindex] = word_value #store the value in the binary buffer
                            bufferstartindex += 1 
                            #check for the end of the buffer; this can happen if the hex parsded line contains more data than the buffer can hold
                            # if the buffer is full break the loop
                            if bufferstartindex >= len(self.binary_buffer):
                                break                                  
                    self.total_data_size += length
        
    # calculate the CRC32 using the PRIME polynomial 0x04C11DB7
    def crc32_calculate(self, data):     
        table = [ 0x00000000,0x04C11DB7,0x09823B6E,0x0D4326D9,0x130476DC,0x17C56B6B,0x1A864DB2,0x1E475005,0x2608EDB8,0x22C9F00F,0x2F8AD6D6,0x2B4BCB61,0x350C9B64,0x31CD86D3,0x3C8EA00A,0x384FBDBD,0x4C11DB70,0x48D0C6C7,0x4593E01E,0x4152FDA9,0x5F15ADAC,0x5BD4B01B,0x569796C2,0x52568B75,0x6A1936C8,0x6ED82B7F,0x639B0DA6,0x675A1011,0x791D4014,0x7DDC5DA3,0x709F7B7A,0x745E66CD,0x9823B6E0,0x9CE2AB57,0x91A18D8E,0x95609039,0x8B27C03C,0x8FE6DD8B,0x82A5FB52,0x8664E6E5,0xBE2B5B58,0xBAEA46EF,0xB7A96036,0xB3687D81,0xAD2F2D84,0xA9EE3033,0xA4AD16EA,0xA06C0B5D,0xD4326D90,0xD0F37027,0xDDB056FE,0xD9714B49,0xC7361B4C,0xC3F706FB,0xCEB42022,0xCA753D95,0xF23A8028,0xF6FB9D9F,0xFBB8BB46,0xFF79A6F1,0xE13EF6F4,0xE5FFEB43,0xE8BCCD9A,0xEC7DD02D,0x34867077,0x30476DC0,0x3D044B19,0x39C556AE,0x278206AB,0x23431B1C,0x2E003DC5,0x2AC12072,0x128E9DCF,0x164F8078,0x1B0CA6A1,0x1FCDBB16,0x018AEB13,0x054BF6A4,0x0808D07D,0x0CC9CDCA,0x7897AB07,0x7C56B6B0,0x71159069,0x75D48DDE,0x6B93DDDB,0x6F52C06C,0x6211E6B5,0x66D0FB02,0x5E9F46BF,0x5A5E5B08,0x571D7DD1,0x53DC6066,0x4D9B3063,0x495A2DD4,0x44190B0D,0x40D816BA,0xACA5C697,0xA864DB20,0xA527FDF9,0xA1E6E04E,0xBFA1B04B,0xBB60ADFC,0xB6238B25,0xB2E29692,0x8AAD2B2F,0x8E6C3698,0x832F1041,0x87EE0DF6,0x99A95DF3,0x9D684044,0x902B669D,0x94EA7B2A,0xE0B41DE7,0xE4750050,0xE9362689,0xEDF73B3E,0xF3B06B3B,0xF771768C,0xFA325055,0xFEF34DE2,0xC6BCF05F,0xC27DEDE8,0xCF3ECB31,0xCBFFD686,0xD5B88683,0xD1799B34,0xDC3ABDED,0xD8FBA05A,0x690CE0EE,0x6DCDFD59,0x608EDB80,0x644FC637,0x7A089632,0x7EC98B85,0x738AAD5C,0x774BB0EB,0x4F040D56,0x4BC510E1,0x46863638,0x42472B8F,0x5C007B8A,0x58C1663D,0x558240E4,0x51435D53,0x251D3B9E,0x21DC2629,0x2C9F00F0,0x285E1D47,0x36194D42,0x32D850F5,0x3F9B762C,0x3B5A6B9B,0x0315D626,0x07D4CB91,0x0A97ED48,0x0E56F0FF,0x1011A0FA,0x14D0BD4D,0x19939B94,0x1D528623,0xF12F560E,0xF5EE4BB9,0xF8AD6D60,0xFC6C70D7,0xE22B20D2,0xE6EA3D65,0xEBA91BBC,0xEF68060B,0xD727BBB6,0xD3E6A601,0xDEA580D8,0xDA649D6F,0xC423CD6A,0xC0E2D0DD,0xCDA1F604,0xC960EBB3,0xBD3E8D7E,0xB9FF90C9,0xB4BCB610,0xB07DABA7,0xAE3AFBA2,0xAAFBE615,0xA7B8C0CC,0xA379DD7B,0x9B3660C6,0x9FF77D71,0x92B45BA8,0x9675461F,0x8832161A,0x8CF30BAD,0x81B02D74,0x857130C3,0x5D8A9099,0x594B8D2E,0x5408ABF7,0x50C9B640,0x4E8EE645,0x4A4FFBF2,0x470CDD2B,0x43CDC09C,0x7B827D21,0x7F436096,0x7200464F,0x76C15BF8,0x68860BFD,0x6C47164A,0x61043093,0x65C52D24,0x119B4BE9,0x155A565E,0x18197087,0x1CD86D30,0x029F3D35,0x065E2082,0x0B1D065B,0x0FDC1BEC,0x3793A651,0x3352BBE6,0x3E119D3F,0x3AD08088,0x2497D08D,0x2056CD3A,0x2D15EBE3,0x29D4F654,0xC5A92679,0xC1683BCE,0xCC2B1D17,0xC8EA00A0,0xD6AD50A5,0xD26C4D12,0xDF2F6BCB,0xDBEE767C,0xE3A1CBC1,0xE760D676,0xEA23F0AF,0xEEE2ED18,0xF0A5BD1D,0xF464A0AA,0xF9278673,0xFDE69BC4,0x89B8FD09,0x8D79E0BE,0x803AC667,0x84FBDBD0,0x9ABC8BD5,0x9E7D9662,0x933EB0BB,0x97FFAD0C,0xAFB010B1,0xAB710D06,0xA6322BDF,0xA2F33668,0xBCB4666D,0xB8757BDA,0xB5365D03,0xB1F740B4]
        crc = 0xFFFFFFFF
        accumulator = 0x00000000
        parity = 0
        #convert the data to an array of bytes
        data = [byte for word in data for byte in word.to_bytes(2, 'little')]
        # remember a word is 2bytes!        
        for byte in data:        
            accumulator = accumulator & 0xFFFFFFFF
            accumulatorTableIndex = (accumulator >> 24) & 0xFFFFFFFF
            processedByte = data[parity] & 0xFFFFFFFF
            table_index = ((accumulatorTableIndex) ^ (processedByte)) & 0xFFFFFFFF
            accumulatorShifted = (accumulator << 8) & 0xFFFFFFFF
            primefromtable = table[table_index] & 0xFFFFFFFF
            accumulator = ((accumulatorShifted)  ^ (primefromtable)) & 0xFFFFFFFF
            parity += 1            
        return accumulator & 0xFFFFFFFF

    def testcrc32(self):
        # https://downloads.ti.com/docs/esd/SPRU513/##viewer?document=%257B%2522href%2522%253A%2522%252Fdocs%252Fesd%252FSPRU513%2522%257D&url=reference-implementation-of-a-crc-calculation-function-ref-crc-c-spru5138320.html%23SPRU5138320
        # expected CRC_32_PRIME is 0x4BEAB53B
        data1 = [0x0061, 0x0062, 0x0063, 0x0064]
        # expected result 0x202A22E4
        data2 = [0xFFFF] * 0x1A
        # expected result 0x39220EDB
        data3 = [ 0x0001, 0x0002, 0x0001, 0x0002, 0x0001, 0x0002, 0x0001, 0x0002, 0x0001, 0x0002, 0x0001, 0x0002, 0x0001, 0x0002, 0x0001, 0x0002, 0x0001, 0x0002, 0x0001, 0x0002, 0x0001, 0x0002, 0x0001, 0x0002, 0x0001, 0x0002]
        # expected result 0xC06A3CD3
        data4 = [0x0003, 0x0004, 0x0003, 0x0004, 0x0003, 0x0004, 0x0003, 0x0004, 0x0003, 0x0004, 0x0003, 0x0004, 0x0003, 0x0004, 0x0003, 0x0004, 0x0003, 0x0004, 0x0003, 0x0004, 0x0003, 0x0004, 0x0003, 0x0004, 0x0003, 0x0004]
        # expected result 0xEAC1F2EA
        data5 = [0x0005, 0x0006, 0x0005, 0x0006, 0x0005, 0x0006, 0x0005, 0x0006, 0x0005, 0x0006, 0x0005, 0x0006, 0x0005, 0x0006, 0x0005, 0x0006, 0x0005, 0x0006, 0x0005, 0x0006, 0x0005, 0x0006, 0x0005, 0x0006, 0x0005, 0x0006]
        # expected result 0x363B4574
        data6 = [0x0007, 0x0008, 0x0007, 0x0008, 0x0007, 0x0008, 0x0007, 0x0008, 0x0007, 0x0008, 0x0007, 0x0008, 0x0007, 0x0008, 0x0007, 0x0008, 0x0007, 0x0008, 0x0007, 0x0008, 0x0007, 0x0008, 0x0007, 0x0008, 0x0007, 0x0008]
        # expected result 0x9A24EB0E
        data7 = [0x0009, 0x000A, 0x0009, 0x000A, 0x0009, 0x000A, 0x0009, 0x000A, 0x0009, 0x000A, 0x0009, 0x000A, 0x0009, 0x000A, 0x0009, 0x000A, 0x0009, 0x000A, 0x0009, 0x000A, 0x0009, 0x000A, 0x0009, 0x000A, 0x0009, 0x000A]
      
        crc32 = self.crc32_calculate(data1) 
        print(f"\n\nCRC32: 0x{crc32:08X}")
        crc32 = self.crc32_calculate(data2)
        print(f"CRC32: 0x{crc32:08X}")
        crc32 = self.crc32_calculate(data3)
        print(f"CRC32: 0x{crc32:08X}")
        crc32 = self.crc32_calculate(data4)
        print(f"CRC32: 0x{crc32:08X}")
        crc32 = self.crc32_calculate(data5)
        print(f"CRC32: 0x{crc32:08X}")
        crc32 = self.crc32_calculate(data6)
        print(f"CRC32: 0x{crc32:08X}")
        crc32 = self.crc32_calculate(data7)
        print(f"CRC32: 0x{crc32:08X}")



    def calculate_crc32(self):
        # calculate the CRC32 for each block of data
        for i in range(0, self.numofblocks):
            startindex = i * self.blocksize
            endindex = startindex + self.blocksize
            data = self.binary_buffer[startindex:endindex]
            self.crc_buffer[i] = self.crc32_calculate(data)

    def show_summary(self):
        print(f"File: {self.filename}")
        print(f"Start address: 0x{self.start_address:08X}")
        print(f"End address: 0x{self.end_address:08x}")
        print(f"Block size: {self.blocksize}")
        print(f"Golden CRC flash usage: {(self.numofblocks*4):d} bytes")

    
    def create_header_file(self):
        #create a header file with the binary buffer data
        with open(self.outputfilename, 'w') as file:
            file.write("#ifndef __HEX_DATA_H__\n")
            file.write("#define __HEX_DATA_H__\n\n")   
            file.write("#include <stdint.h>\n\n")         
            file.write(f"#define CRC_START_ADDRESS  0x{self.start_address:08X}\n")
            file.write(f"#define CRC_END_ADDRESS    0x{self.end_address:08X}\n")
            file.write(f"#define CRC_DATA_LENGTH    {self.blocksize}\n")
            file.write(f"#define CRC_NUM_OF_ENTRIES {(self.numofblocks):d}\n\n")
            file.write("#pragma DATA_SECTION(goldenCrc, \"CRC_DATA\")\n")
            file.write(f"const uint32_t goldenCrc[] = \n"+"{\n")
                                                          
            for i in range(0, len(self.crc_buffer), 8):                
                for j in range(0, 8):
                    if i+j >= len(self.crc_buffer):
                        #remove the last 2 characters
                        break                    
                    file.write(f"0x{self.crc_buffer[i+j]:08X}U, ")                        

            file.seek(file.tell() - 2) #remove the last comma                                             
            file.write("\n};\n")
            file.write(f"// Total golden CRC flash usage: {self.numofblocks*4} bytes\n")
            file.write("#endif\n")

if __name__ == "__main__":    
    if len(sys.argv) != 6:
        print("Usage: python c2000_hex_parser.py <hexfile> <headerfile> <startaddress> <numberofblocks> <blocksize>")
        print("Example: python c2000_hex_parser.py sample.hex crc_golden.h 0x80000 100 16")
    #parser = HexParser("c:/Users/tomik/git/hex2000crcgen/hex2000crcgen/sample.hex", "crc.golden.h", 0x80000, 1200, 26)
    #parser.testcrc32()
    parser = HexParser(sys.argv[1],sys.argv[2], int(sys.argv[3], 16), int(sys.argv[4]), int(sys.argv[5]))
    parser.parse()   
    parser.calculate_crc32()    
    parser.create_header_file()
    parser.show_summary()
