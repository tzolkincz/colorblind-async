import pytest

from src.colorblind_async import ColorblindAsync

ColorblindAsync.init()


def test_basic():
    from cases.basic import await_from_sync
    from cases.basic import call_nested_functions
    from cases.basic import test_async_with
    from cases.basic import test_async_for

    assert await_from_sync() == "ok"
    assert call_nested_functions() == 6
    assert test_async_with()
    assert test_async_for() == [0, 1]


def test_exception():
    with pytest.raises(Exception) as e_info:
        from cases.exception import raise_exception


def test_multiimport():
    from cases.multiimport import foo, bar

    assert foo()
    assert bar()
