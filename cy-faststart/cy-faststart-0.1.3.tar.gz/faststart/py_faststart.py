import os
import struct
import humanfriendly
from collections import namedtuple
import tempfile
import io

from faststart.exceptions import AlreadyMoved, FileIsCorrupt, \
                                        FileIsUnsupported, FastStartError


# Atom storage namedtuple
Atom = namedtuple('Atom', 'name position size')
REQUIRED_ATOMS = {'moov', 'mdat'}
ATOMS = {'ftyp', 'moov', 'moof', 'mdat', 'free', 'fourcc', 'mfra'}
CHILD_ANCESTORS = {"trak", "mdia", "minf", "stbl"}
DESIRED_CHILDREN = {"stco", "co64"}


class FastStart(object):
    __slots__ = ('cache', 'stream', 'indexes', '_stream_pos', 'BUFFER_SIZE')

    def __init__(self, buffer_size=50 * 1024 * 1024):
        """ @buffer_size: (#int) size of each stream chunk in bytes, defaults
                to 50M. The buffer size also must be a multiple of 16.
        """
        self.reset()
        self.BUFFER_SIZE = buffer_size
        if buffer_size < 16 or \
           float(buffer_size / 16) != float(buffer_size // 16):
            raise FastStartError('Buffer size must be at least 16 bytes and '
                                 'must be a multiple of 16. The recommended '
                                 'size is at least 10M.')

    def __repr__(self):
        return '<FastStart: -buffer_size=%s>' % \
               humanfriendly.format_size(self.BUFFER_SIZE)

    def get_indexes(self, chunk, chunk_size):
        """ Yields an index of top level atoms, their absolute byte-position in
            the file and their size
        """
        while(chunk):
            try:
                # Reads the next atom in the chunk
                atom = self.read_atom(chunk, self._stream_pos)
            except struct.error as e:
                break

            if atom.size == 0:
                if atom.name == "mdat":
                    # Some files may end in mdat with no size set, which
                    # generally means to seek to the end of the file
                    break
                else:
                    # Not necessarily malformed nor signaling anything,
                    # so just continue
                    continue
            # The next top-level atom will be found immediately after the end
            # of this atom, so that's where we will skip to
            skip_to = atom.position + atom.size
            chunk_end = self._stream_pos + chunk_size
            # Yield the newly discovered atom
            yield atom
            # If the next atom position is available within this chunk,
            # find it, otherwise break the loop and move on to the next chunk
            if skip_to < chunk_end:
                # We need at least 16 available bytes to unpack properly
                # so we fetch any extras we need from the stream
                if chunk_end - skip_to < 16:
                    # Read the required bytes from the stream
                    stream = self.stream.read(chunk_end - skip_to)
                    # Write the new bytes to the chunk AND the cached data
                    chunk.seek(0, os.SEEK_END)
                    chunk.write(stream)
                    self.cache.write(stream)
                # Seek the chunk to the next atom location
                chunk.seek(skip_to - self._stream_pos)
            else:
                break

    def read_atom(self, chunk, padding=0):
        """ Read an atom and return a tuple of (size, type) where size is the
            size in bytes (including the 8 bytes already read) and type is a
            "fourcc" like "ftyp" or "moov".
        """
        pos = chunk.tell()
        read = chunk.read(8)
        atom_size, atom_type = struct.unpack(">L4s", read)

        if atom_size == 1:
            atom = Atom(atom_type.decode('ascii', 'ignore'),
                        padding + pos,
                        struct.unpack(">Q", chunk.read(8))[0])
        else:
            atom = Atom(atom_type.decode('ascii', 'ignore'),
                        padding + pos,
                        atom_size)
        return atom


    def _check_compressed(self, moov_atom):
        is_compressed = self._moov_is_compressed(moov_atom)
        if is_compressed:
            raise FileIsUnsupported("Files with compressed headers are not "
                                    "supported")

    def _moov_is_compressed(self, moov_atom):
        """ Scan the atoms under the moov atom and detect whether or not the
            atom data is compressed.
        """
        # Seek to the beginning of the moov atom contents (8 skips the atom
        # type identifier)
        self.cache.seek(moov_atom.position + 8)

        # Step through the moov atom children to see if a cmov atom is
        # among them
        stop = moov_atom.position + moov_atom.size
        while self.cache.tell() < stop:
            child_atom = self.read_atom(self.cache)
            self.cache.seek(self.cache.tell() + child_atom.size - 8)
            # cmov means there is a compressed moov header
            if child_atom.name == 'cmov':
                return True
        return False

    def _patch_moov(self, atom, offset):
        # Seek to the beginning of the moov atom within the cache
        self.cache.seek(atom.position)
        # Wrap the moov in BytesIO for independent seeking
        moov = io.BytesIO(self.cache.read(atom.size))

        # reload the atom from the fixed stream
        atom = self.read_atom(moov)
        for atom in self._find_atoms_ex(atom, moov):
            # Read either 32-bit or 64-bit offsets
            ctype, csize = ('L', 4) if atom.name == 'stco' else ('Q', 8)

            # Get number of entries
            version, entry_count = struct.unpack(">2L", moov.read(8))
            entries_pos = moov.tell()
            struct_fmt = ">%s%s" % (entry_count, ctype)

            # Read entries
            entries = struct.unpack(struct_fmt, moov.read(csize * entry_count))

            # Patch and write entries
            offset_entries = map(lambda entry: entry + offset, entries)
            moov.seek(entries_pos)
            moov.write(struct.pack(struct_fmt, *offset_entries))
        return moov



    def _find_atoms_ex(self, parent_atom, datastream):
        """
            Yield either "stco" or "co64" Atoms from datastream.
            datastream will be 8 bytes into the stco or co64 atom when the value
            is yielded.
            It is assumed that datastream will be at the end of the atom after
            the value has been yielded and processed.
            parent_atom is the parent atom, a 'moov' or other ancestor of CO
            atoms in the datastream.
        """
        stop = parent_atom.position + parent_atom.size

        while datastream.tell() < stop:
            try:
                atom = self.read_atom(datastream)
            except:
                raise FileIsCorrupt("Error reading next atom!")

            if atom.name in CHILD_ANCESTORS:
                # Known ancestor atom of stco or co64, search within it
                for res in self._find_atoms_ex(atom, datastream):
                    yield res
            elif atom.name in DESIRED_CHILDREN:
                yield atom
            else:
                # Ignore this atom, seek to the end of it.
                datastream.seek(atom.position + atom.size)

    def reset(self, stream=None):
        self.stream = stream
        self._stream_pos = 0
        self.cache = tempfile.TemporaryFile()
        self.indexes = []

    def iter_stream(self):
        CHUNK_SIZE = -1
        while CHUNK_SIZE:
            chk = self.stream.read(self.BUFFER_SIZE)
            CHUNK_SIZE = len(chk)
            if CHUNK_SIZE:
                yield chk

    def iter_atom_data(self, blacklist=None, whitelist=None):
        blacklist = set(blacklist or {})
        whitelist = set(whitelist or {})
        if len(blacklist):
            filter_ = lambda x: x.name not in blacklist
        else:
            filter_ = lambda x: x.name in whitelist
        for atom in filter(filter_, self.indexes):
            self.cache.seek(atom.position)
            chunk_size = atom.size if atom.size < self.BUFFER_SIZE else\
                         self.BUFFER_SIZE
            chunk = -1
            while(chunk):
                chunk = self.cache.read(chunk_size)
                yield chunk

    def from_file(self, input_file, output_file=None):
        """ @input_file: (#str) the input filename relative to the current
                working directory
            @output_file: (#str) optional file to output to. If no filename is
                provided, this method will yield :class:io.BytesIO chunks.
        """
        with open(humanfriendly.parse_path(input_file), 'rb') as f:
            for output in self.from_stream(f):
                yield output

    def from_stream(self, stream, output_file=None):
        """ @stream: An object with a 'read' attribute which returns a
                bytes-like object, 'seek' is NOT required
            @output_file: (#str) optional file to output to. If no filename is
                provided, this method will yield :class:io.BytesIO chunks.
        """
        self.reset(stream)
        CHUNK_SIZE = -1
        SKIP_TO = 0
        top_level_atoms = set()
        ccount = 0
        while CHUNK_SIZE:
            # Read the chunk from the stream
            chk = self.stream.read(self.BUFFER_SIZE)
            # Write chunk to io.BytesIO object so it is guaranteed to be
            # seekable
            CHUNK_SIZE = len(chk)
            CHUNK = io.BytesIO(chk)
            # Write the chunk to cached data, necessary for seeking outside of
            # the stream (which may or may not be seekable)
            self.cache.write(chk)
            # Skip bytes we don't need to process because we know they are part
            # of existing atoms
            chunk_skip_to = 0
            if self.cache.tell() < SKIP_TO:
                self._stream_pos = self.cache.tell()
                continue
            else:
                chunk_skip_to = SKIP_TO - self._stream_pos
            # Patch bytes in order to make sure we have at least 16 to pass to
            # the index finder
            if 0 < chunk_skip_to < 16:
                chk = self.stream.read(16 - chunk_skip_to)
                CHUNK.seek(0, os.SEEK_END)
                CHUNK.write(chk)
                CHUNK_SIZE += len(chk)
                self.cache.write(chk)
            # Seek the chunk to its proper starting point, that is, where the
            # next atom is supposed to begin
            CHUNK.seek(chunk_skip_to)
            # Find the indexes within this chunk
            for index in self.get_indexes(CHUNK, CHUNK_SIZE):
                self.indexes.append(index)
                SKIP_TO = index.position + index.size
            self._stream_pos = self.cache.tell()
            # Quit searching if we've already found the indexes that we care
            # about.
            top_level_atoms = set(item.name for item in self.indexes)
            if REQUIRED_ATOMS.issuperset(top_level_atoms) or \
               top_level_atoms.issuperset(REQUIRED_ATOMS):
                break
            elif not bool(ATOMS & top_level_atoms) and \
                 self._stream_pos >= 5 * 1024 * 1024:
                raise FileIsUnsupported('This file does not appear to be '
                                        'atom-based.')

        if not REQUIRED_ATOMS.issubset(top_level_atoms):
            raise FileIsCorrupt("A required atom was not found.")

        mdat_pos = float('inf')
        free_size = 0

        for atom in self.indexes:
            if atom.name == "moov":
                moov_atom = atom
                # If we haven't read the full atom yet, do so
                if atom.size + atom.position > self._stream_pos:
                    stream = self.stream.read(atom.size + atom.position -
                                              self._stream_pos)
                    self.cache.write(stream)
                    self._stream_pos = self.cache.tell()
            elif atom.name == "mdat":
                mdat_pos = atom.position
            elif atom.name == "free" and atom.position < mdat_pos:
                # This free atom is before the mdat!
                free_size += atom.size
            elif atom.name == "\x00\x00\x00\x00" and atom.position < mdat_pos:
                # This is some strange zero atom with incorrect size
                free_size += 8

        # Offset to shift positions
        offset =- free_size
        if moov_atom.position > mdat_pos:
            # moov is in the wrong place, shift by moov size
            offset += moov_atom.size

        if offset <= 0:
            # No free atoms to process and moov is correct, we are done so
            # just yield the file contents
            self.cache.seek(0)
            yield self.cache.read()
            # Yield the rest of the stream
            for data in self.iter_stream():
                yield data
        else:
            # Check for compressed moov atom
            self._check_compressed(moov_atom)

            # Yield ftype
            for data in self.iter_atom_data(whitelist={"ftyp"}):
                yield data

            # Read and fix moov
            moov = self._patch_moov(moov_atom, offset)
            moov = moov.getvalue()
            # Yield the moov
            yield moov

            # Yield the rest of the atoms
            for data in self.iter_atom_data(blacklist={"ftyp", "moov", "free"}):
                yield data

            # Yield the rest of the stream
            for data in self.iter_stream():
                yield data

        self.cache.close()
