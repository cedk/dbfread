"""
Reads data from FPT (memo) files.

FPT files are used to varying lenght text or binary data which is too
large to fit in a DBF field.
"""

from collections import namedtuple
from .struct_parser import StructParser


Header = StructParser(
    'FPTHeader',
    '>LHH504s',
    ['nextblock',
     'reserved1',
     'blocksize',
     'reserved2'])

BlockHeader = StructParser(
    'FPTBlock',
    '>LL',
    ['type',
     'length'])

# Record type
RECORD_TYPES = {
    0x0: 'picture',
    0x1: 'memo',
    0x2: 'object',
}

Record = namedtuple('Record', ['type', 'data'])


class FakeMemoFile(object):
    def __getitem__(self, i):
        return Record(type=None, data=None)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        return False


class MemoFile(object):
    """
    This class implement read access to a FPT files.

    FPT files are used to store varying-length data (strings or
    binary) that is too large to fit in a DBF field.

    
    Documentation of the FPT file format:
    http://www.clicketyclick.dk/databases/xbase/format/fpt.html
    """
    def __init__(self, filename):
        # Todo: detect file type by extension.
        self.filename = filename
        self.file = open(filename, 'rb')
        self.header = Header.read(self.file)

    def __getitem__(self, index):
        """Get a memo from the file.
        
        Returns a Record with attributes.
        Memos are returned as byte strings.
        """

        # Todo: Handle reading block header in middle of a memo?
        # Todo: Handle n > end of file and n < 0 and n inside header
        # Todo: Handle wrong sized memo

        if index <= 0:
            raise IndexError('memo file got index {}'.format(index))

        self.file.seek(index * self.header.blocksize)
        block_header = BlockHeader.read(self.file)

        data = self.file.read(block_header.length)
        if len(data) != block_header.length:
            raise IOError('EOF reached while reading memo')
        
        record_type = RECORD_TYPES.get(block_header.type)
        return Record(type=record_type, data=data)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.file.close()
        return False