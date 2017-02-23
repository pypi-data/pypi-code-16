"""Basic tests for collections."""

from byte import Collection, Model, Property


def test_simple_dynamic():
    """Test collections with dynamic models."""
    class Artist(Model):
        class Options:
            collection = Collection()

        id = Property(int, primary_key=True)

        name = Property(str)

    class Album(Model):
        class Options:
            collection = Collection()

        id = Property(int, primary_key=True)
        artist = Property(Artist)

        title = Property(str)

    class Track(Model):
        class Options:
            collection = Collection()

        id = Property(int, primary_key=True)
        artist = Property(Artist)
        album = Property(Album)

        name = Property(str)

    # Create objects
    Artist.create(
        id=1,
        name='Daft Punk'
    )

    Album.create(
        id=1,
        artist_id=1,

        title='Discovery'
    )

    Track.create(
        id=1,
        artist_id=1,
        album_id=1,

        name='One More Time'
    )

    # Fetch track, and ensure relations can be resolved
    track = Track.Objects.get(1)

    assert track.id == 1

    assert track.artist.id == 1

    assert track.album.id == 1
    assert track.album.artist.id == 1
