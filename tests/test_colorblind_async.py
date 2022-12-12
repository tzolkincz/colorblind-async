import pytest

from src.colorblind_async import ColorblindAsync

ColorblindAsync.init()


def test_basic():
    from cases.basic import await_from_sync
    from cases.basic import call_nested_functions

    assert await_from_sync() == "ok"
    assert call_nested_functions() == 6


def test_exception():
    with pytest.raises(Exception) as e_info:
        from cases.exception import raise_exception
