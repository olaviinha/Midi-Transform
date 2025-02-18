def read_varlen(data):
    NEXTBYTE = 1
    value = 0
    while NEXTBYTE:
        chr = next(data)  # Updated this line
        # is the hi-bit set?
        if not (chr & 0x80):
            # no next BYTE
            NEXTBYTE = 0
        # mask out the 8th bit
        chr = chr & 0x7f
        # shift last value up 7 bits
        value = value << 7
        # add new value
        value += chr
    return value

def write_varlen(value):
    chr1 = value & 0x7F
    value >>= 7
    if value:
        chr2 = (value & 0x7F) | 0x80
        value >>= 7
        if value:
            chr3 = (value & 0x7F) | 0x80
            value >>= 7
            if value:
                chr4 = (value & 0x7F) | 0x80
                res = bytes([chr4, chr3, chr2, chr1])
            else:
                res = bytes([chr3, chr2, chr1])
        else:
            res = bytes([chr2, chr1])
    else:
        res = bytes([chr1])
    return res
