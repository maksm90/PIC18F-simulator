import picmicro

def addlw(pic, k):
    """implementation 'addlw' operation
    
    pre: 0 <= k <= 255
    post: pic.data[WREG] == (__old__.pic.data[WREG] + k) & 0x100
    """

    assert(0 <= k <= 255)
    result = pic.wreg + k
    pic.wreg = result & 0xff

addlw.num_words = 1
addlw.num_cycles = 1

def test_addlw():
    pic = picmicro.PICmicro()
    pic.wreg = 0x10
    addlw(pic, 0x15)
    assert(pic.wreg == 0x25)
