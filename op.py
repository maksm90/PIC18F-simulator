import picmicro

def addlw(pic, k):
    """  """
    pic.data.wreg.add(k, pic.data.status)
    pic.inc_pc(2)
