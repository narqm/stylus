from metadata.utility import RebuildOutline
from pypdf import PdfReader, PdfWriter


def test_rebuild_outline():

    pdf = r'resources\Think Python, sample.pdf'

    reader = PdfReader(pdf)
    writer = PdfWriter()

    rb = RebuildOutline(reader, writer)
    rb.rebuild_outline(reader.outline)
    assert isinstance(writer, PdfWriter)
