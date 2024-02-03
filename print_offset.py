
class Pretty_print(object):
    def __init__(self):
        self.offset = 0
        self.LINE_SIZE = 16

    def print_space(self, length):
        for i in range(length):
            print(' ', end='')

    def print_offset(self):
        print("%08X" % self.offset, end='')

    def print_ascii(self, buffer):
        print(" |", end='')
        for i in buffer:
            if i < 0x20 or i > 0x7E:
                print('.', end='')
            else:
                print('%c' % i, end='')
        print('|', end='')

    def print_hexdata(self, buffer):
        for i in range(len(buffer)):
            print("%02X" % buffer[i], end=' ')
            if i == 7:
                self.print_space(1)

    def print_buffer(self, buffer):
        buf_length = len(buffer)
        self.print_offset()
        self.print_space(2)
        self.print_hexdata(buffer)
        if len(buffer) < self.LINE_SIZE:
            self.print_space(3 * (16 - buf_length))
            if buf_length < 8:
                self.print_space(1)
        self.print_ascii(buffer)
        print("")

    def printBuf(self, data_list):
        data_length = len(data_list)
        while self.offset + self.LINE_SIZE <= data_length:
            self.print_buffer(data_list[self.offset:self.offset + self.LINE_SIZE])
            self.offset += self.LINE_SIZE
        if self.offset < data_length:
            self.print_buffer(data_list[self.offset:])
            self.offset = data_length
            self.print_offset()
        else:
            self.print_offset()
        print("\n")

    def printString(self, string):
        L = []
        self.offset = 0
        self.LINE_SIZE = 16
        for i in string:
            L.append(ord(i))
        self.printBuf(L)
