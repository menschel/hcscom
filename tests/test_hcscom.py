""" tests for hcscom

(c) Patrick Menschel 2021

"""
import pytest

from hcscom.hcscom import split_data_to_values, HcsCom, OutputStatus, FORMAT_FOUR_DIGITS, format_to_width_and_decimals
from .mocks import HcsMock,HcsDefectMock


def test_split_bytes():
    assert split_data_to_values(data="112233", width=3, decimals=1) == (11.2, 23.3)
    assert split_data_to_values(data="22221111", width=4, decimals=2) == (22.22, 11.11)


@pytest.mark.xfail
def test_obj_creation_should_fail_wrong_port_string():
    hcs = HcsCom(port="some_port")

@pytest.mark.xfail
def test_obj_creation_should_fail_wrong_port_type():
    hcs = HcsCom(port=None)


@pytest.mark.xfail
def test_obj_creation_should_fail_wrong_response():
    mock = HcsDefectMock()
    hcs = HcsCom(port=mock)


def test_sout():
    mock = HcsMock()
    hcs = HcsCom(port=mock)
    hcs.switch_output(OutputStatus.on)
    assert mock.output_status == OutputStatus.on
    hcs.switch_output(OutputStatus.off)
    assert mock.output_status == OutputStatus.off


def test_display_set():
    mock = HcsMock()
    hcs = HcsCom(port=mock)
    volt = 12
    hcs.set_voltage(volt)
    assert mock.display_values[0] == volt
    curr = 5
    hcs.set_current(curr)
    assert mock.display_values[1] == curr


def test_display_set_format_four_digits():
    mock = HcsMock()
    mock.value_format = FORMAT_FOUR_DIGITS
    mock.width, mock.decimals = format_to_width_and_decimals(mock.value_format)
    hcs = HcsCom(port=mock)
    volt = 12
    hcs.set_voltage(volt)
    assert mock.display_values[0] == volt
    curr = 5
    hcs.set_current(curr)
    assert mock.display_values[1] == curr


def test_active_preset_set():
    mock = HcsMock()
    hcs = HcsCom(port=mock)
    curr = 10
    hcs.set_output_current_preset(curr)
    assert mock.active_preset[1] == curr
    volt = 24
    hcs.set_output_voltage_preset(volt)
    assert mock.active_preset[0] == volt


def test_preset_selection():
    mock = HcsMock()
    hcs = HcsCom(port=mock)
    test_preset = (11.0, 22.0)
    mock.presets[1] = test_preset
    hcs.load_preset(1)
    assert mock.display_values == test_preset
    assert hcs.get_presets() == test_preset
    assert hcs.get_display_status()[:-1] == test_preset
    assert hcs.get_output_voltage_preset() == test_preset[0]
    assert hcs.get_output_current_preset() == test_preset[1]
    presets = hcs.get_presets_from_memory()
    for idx, preset in enumerate(mock.presets):
        for num1, num2 in zip(preset, presets.get(idx)):
            assert num1 == num2
    hcs.set_presets_to_memory()
    presets = hcs.get_presets_from_memory()
    for idx, preset in enumerate(mock.presets):
        for num1, num2 in zip(preset, presets.get(idx)):
            assert num1 == num2


def test_print():
    mock = HcsMock()
    hcs = HcsCom(port=mock)
    print(hcs)
