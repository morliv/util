from tests.googl.test_map import assert_mapped

def test_upload(paths, monkeypatch):
    assert_mapped(paths, lambda p: monkeypatch.setattr('sys.argv', ['-l', p]).file)