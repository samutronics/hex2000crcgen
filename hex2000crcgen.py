import array
import sys

class HexParser:
    def __init__(self, filename, startaddress, endaddress, blocksize):
        self.filename = filename
        self.total_data_size = 0
        self.extended_address = 0
        self.start_address = startaddress
        self.end_address = endaddress
        self.blocksize = blocksize    
        # ord array to store the data
        #self.binary_buffer = bytearray([0xFF] * (endaddress - startaddress + 1))
        self.binary_buffer = array.array('H', [0xFFFF] * (endaddress - startaddress + 1))
        # create a binary buffer to store the data prefill with 0xFF the size is the end address - start address
        
    
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
                    if address >= self.start_address and address <= self.end_address:
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
    
    def show_summary(self):
        print(f"File: {self.filename}")
        print(f"Total data size: {self.total_data_size} bytes")
        print(f"Start address: {self.start_address}")
        print(f"End address: {self.end_address}")
        # print a dump of the binary buffer in hex format 16bit with 8 words per line
        for i in range(0, len(self.binary_buffer), 8):
            print(' '.join(f"{word:04X}" for word in self.binary_buffer[i:i + 8]))
             

if __name__ == "__main__":
    #if len(sys.argv) != 2:
    #    print("Usage: python c2000_hex_parser.py <hexfile>")
    #    sys.exit(1)
    
    #parser = HexParser(sys.argv[1], 0x7FFE8, 0x80600, 100)    
    parser = HexParser("./sample1.hex", 0x7FFE8, 0x80600, 100)
    parser.parse()
    parser.show_summary()
