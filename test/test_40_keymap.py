'''Test keymaps configuration.'''

import pytest


def _launch(eng):
    eng.feed(":GdbStart ./dummy-gdb.sh\n")


@pytest.fixture(scope='function')
def keymap(eng, post):
    '''Fixture to clear custom keymaps.'''
    yield
    eng.exe('source keymap_cleanup.vim')


def test_hooks(eng, keymap):
    '''Test custom programmable keymaps.'''
    eng.exe("source keymap_hooks.vim")
    _launch(eng)

    assert eng.eval('g:test_tkeymap') == 0
    eng.feed('~tkm')
    assert eng.eval('g:test_tkeymap') == 1
    eng.feed('<esc>')
    assert eng.eval('g:test_keymap') == 0
    eng.feed('~tn')
    assert eng.eval('g:test_keymap') == 1
    eng.exe('let g:test_tkeymap = 0 | let g:test_keymap = 0')
    eng.feed('<c-w>w')
    assert eng.eval('g:test_keymap') == 0
    eng.feed('~tn')
    assert eng.eval('g:test_keymap') == 1
    eng.exe('let g:test_keymap = 0')


def test_conflict(eng, keymap):
    '''Conflicting keymap.'''
    eng.exe("let g:nvimgdb_config = {'key_next': '<f5>', 'key_prev': '<f5>'}")
    _launch(eng)

    count = eng.eval(
        'len(filter(GdbTestPeekConfig(), {k,v -> k =~ "^key_.*"}))')
    assert count == 1
    # Check that the cursor is moving freely without stucking
    eng.feed('<c-\\><c-n>')
    eng.feed('<c-w>w')
    eng.feed('<c-w>w')


def test_override(eng, keymap):
    '''Override a key.'''
    eng.exe("let g:nvimgdb_config_override = {'key_next': '<f2>'}")
    _launch(eng)
    key = eng.eval('get(GdbTestPeekConfig(), "key_next", 0)')
    assert key == '<f2>'


def test_override_priority(eng, keymap):
    '''Check that a config override assumes priority in a conflict.'''
    eng.exe("let g:nvimgdb_config_override = {'key_next': '<f8>'}")
    _launch(eng)
    res = eng.eval('get(GdbTestPeekConfig(), "key_breakpoint", 0)')
    assert res == 0


def test_override_one(eng, keymap):
    '''Override a single key.'''
    eng.exe("let g:nvimgdb_key_next = '<f3>'")
    _launch(eng)
    key = eng.eval('get(GdbTestPeekConfig(), "key_next", 0)')
    assert key == '<f3>'


def test_override_one_priority(eng, keymap):
    '''Override a single key, priority.'''
    eng.exe("let g:nvimgdb_key_next = '<f8>'")
    _launch(eng)
    res = eng.eval('get(GdbTestPeekConfig(), "key_breakpoint", 0)')
    assert res == 0


def test_overall(eng, keymap):
    '''Smoke test.'''
    eng.exe("let g:nvimgdb_config_override = {'key_next': '<f5>'}")
    eng.exe("let g:nvimgdb_key_step = '<f5>'")
    _launch(eng)
    res = eng.eval('get(GdbTestPeekConfig(), "key_continue", 0)')
    assert res == 0
    res = eng.eval('get(GdbTestPeekConfig(), "key_next", 0)')
    assert res == 0
    key = eng.eval('get(GdbTestPeekConfig(), "key_step", 0)')
    assert key == '<f5>'
