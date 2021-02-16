""" tests for hcscom

(c) Patrick Menschel 2021

"""

from hcscom.hcscom import split_data_to_values, HcsCom, OutputStatus

from .mocks import HcsMock


def test_split_bytes():
    assert split_data_to_values(data="112233", width=3, decimals=1) == (11.2, 23.3)
    assert split_data_to_values(data="22221111", width=4, decimals=2) == (22.22, 11.11)


def test_sout():
    mock = HcsMock()
    hcs = HcsCom(port=mock)
    hcs.switch_output(OutputStatus.on)
    assert mock.output_status == OutputStatus.on
    hcs.switch_output(OutputStatus.off)
    assert mock.output_status == OutputStatus.off
