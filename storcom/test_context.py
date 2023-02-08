import builtins
from contextlib import contextmanager, ExitStack
from unittest.mock import Mock
from typing import Iterator, List, ContextManager, Generator, Dict, Optional

import pytest
from _pytest.monkeypatch import MonkeyPatch

from storcom import context
from storcom.context import Context

@pytest.fixture(name='arrange')
def fixture_arrange(monkeypatch: MonkeyPatch) -> Mock:
    @contextmanager
    def arrange_config_get_or_create_config_directory(expected: str) -> Iterator[None]:
        mock = Mock(return_value=expected)
        monkeypatch.setattr(
            context.config, 'get_or_create_config_directory', mock) # type: ignore
        yield
        mock.assert_called_once()

    @contextmanager
    def arrange_open_context_file(expected: List[str]) -> Iterator[None]:
        mock = Mock(return_value=Mock(__enter__=Mock(return_value=iter(expected)),
                                      __exit__=Mock()))
        monkeypatch.setattr(builtins, 'open', mock)
        yield
        mock.assert_called_once()

    def arrange_shortcuts(expected: Dict[str, str]) -> None:
        monkeypatch.setattr(context, 'shortcuts', expected)

    return Mock(
        config=Mock(get_or_create_config_directory=arrange_config_get_or_create_config_directory),
        context_file=arrange_open_context_file,
        shortcuts=arrange_shortcuts,
    )

def test_load_returns_empty_context_when_no_file(arrange: Mock) -> None:
    config_directory = _build_get_or_create_config_directory_mock(has_config_file=False)
    with arrange.config.get_or_create_config_directory(config_directory):
        actual = context.load()
        _assert_empty_context(actual)

def test_load_returns_empty_context_from_empty_file(arrange: Mock) -> None:
    config_directory = _build_get_or_create_config_directory_mock(has_config_file=True)
    context_file_data: List[str] = []
    with _many(arrange.config.get_or_create_config_directory(config_directory),
               arrange.context_file(context_file_data)):
        actual = context.load()
        _assert_empty_context(actual)

def test_load_returns_context_from_file_lines_out_of_order(arrange: Mock) -> None:
    config_directory = _build_get_or_create_config_directory_mock(has_config_file=True)
    context_file_data = [
        'storage=stor',
        'environment=env',
        'user=usr',
        'service=srv',
    ]
    with _many(arrange.config.get_or_create_config_directory(config_directory),
               arrange.context_file(context_file_data)):
        actual = context.load()
        _assert_context(actual, 'env', 'stor', 'srv', 'usr')

def test_load_with_shortcut_empty_context_from_missing_shortcut(arrange: Mock) -> None:
    arrange.shortcuts({})
    actual = context.load_with_shortcut('missing shortcut')
    _assert_empty_context(actual)

@pytest.mark.parametrize('value', [':', '', None])
def test_load_with_shortcut_empty_context_from_empty_shortcut_value(arrange: Mock,
                                                                    value: Optional[str]) -> None:
    shortcut = 'test_shortcut'
    arrange.shortcuts({
        shortcut: value,
    })
    actual = context.load_with_shortcut(shortcut)
    _assert_empty_context(actual)

@pytest.mark.parametrize('value', ['env:stor:srv:', 'env:stor:srv'])
def test_load_with_shortcut_context_without_user_no_user_in_shortcut_value(arrange: Mock,
                                                                           value: str) -> None:
    shortcut = 'test_shortcut'
    arrange.shortcuts({
        shortcut: value,
    })
    actual = context.load_with_shortcut(shortcut)
    _assert_context(actual, 'env', 'stor', 'srv', '')

@pytest.mark.parametrize('value', ['env:stor:', 'env:stor'])
def test_load_with_shortcut_context_without_service_user_no_service_user_in_shortcut_value(
        arrange:Mock, value: str) -> None:
    shortcut = 'test_shortcut'
    arrange.shortcuts({
        shortcut: value,
    })
    actual = context.load_with_shortcut(shortcut)
    _assert_context(actual, 'env', 'stor', '', '')

@pytest.mark.parametrize('value', ['env:', 'env'])
def test_load_with_shortcut_context_env_only_env_in_shortcut_value(arrange: Mock,
                                                                   value: str) -> None:
    shortcut = 'test_shortcut'
    arrange.shortcuts({
        shortcut: value,
    })
    actual = context.load_with_shortcut(shortcut)
    _assert_context(actual, 'env', '', '', '')

def test_load_with_shortcut_complete_context_complete_shortcut_value(arrange: Mock) -> None:
    shortcut = 'test_shortcut'
    arrange.shortcuts({
        shortcut: 'env:stor:srv:usr',
    })
    actual = context.load_with_shortcut(shortcut)
    _assert_context(actual, 'env', 'stor', 'srv', 'usr')

@contextmanager
def _many(*context_managers: ContextManager[None]) -> Generator[List[None], None, None]:
    with ExitStack() as stack:
        yield [stack.enter_context(c) for c in context_managers]

def _build_get_or_create_config_directory_mock(has_config_file: bool=True) -> Mock:
    return Mock(__truediv__=Mock(return_value=Mock(is_file=Mock(return_value=has_config_file))))

def _assert_context(actual: Context,
                    environment: str,
                    storage: str,
                    service: str,
                    user: str) -> None:
    assert actual.environment == environment
    assert actual.storage == storage
    assert actual.service == service
    assert actual.user == user

def _assert_empty_context(actual: Context) -> None:
    _assert_context(actual, '', '', '', '')
