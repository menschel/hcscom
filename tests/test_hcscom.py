""" tests for hcscom

(c) Patrick Menschel 2021

"""

from hcscom.hcscom import splitbytes

from .mocks import hcsmock

def test_split_bytes():
    assert splitbytes(data=b"112233",width=3,decimals=1) == (11.2,23.3)
    assert splitbytes(data=b"22221111",width=4,decimals=2) == (22.22,11.11)


def test_sout():
    hcsmock