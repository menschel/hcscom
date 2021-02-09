from hcscom.hcscom import splitbytes

def test_split_bytes():
    assert splitbytes(data=b"112233",width=3,decimals=1) == (11.2,23.3)
    assert splitbytes(data=b"22221111",width=4,decimals=2) == (22.22,11.11)


