import picmicro

def addlw(pic, k):
    """
    pre: k & 0xff == k
    """
    pic.data.wreg.add(k, pic.data.status)

addlw.num_words = 1
addlw.num_cycles = 1
