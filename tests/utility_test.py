from metadata.utility import Utilities

def test_missing_first_line():
    func = Utilities.unpack_text_file('resources\\missing_first_line.txt')
    assert isinstance(func, list)
    assert func[0] is ''

def test_empty_file():
    func = Utilities.unpack_text_file('resources\\empty_file.txt')
    assert isinstance(func, list)

def test_normal_file():
    func = Utilities.unpack_text_file('resources\\normal_file.txt')
    assert isinstance(func, list)