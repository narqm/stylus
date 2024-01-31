from stylus.api_call import GoogleBooksAPICall

def test_normal_build_api_request():
    gbac = GoogleBooksAPICall(r'.\resources\Think Python, sample.pdf')
    url = gbac.build_api_request(author='Allen Downey')
    baseline = 'https://www.googleapis.com/books/v1/volumes?' \
        'q=think+python+inauthor:allen+downey'
    assert url == baseline
