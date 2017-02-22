import os
from typing import Callable

import vlc


vlc_instance = None
player = None
playback_end_callback = lambda: NotImplemented
current_mrl = None


def init(callback: Callable[[], None]) -> None:

    global vlc_instance
    global player
    global playback_end_callback

    vlc_instance = vlc.Instance("--no-xlib")
    player = vlc_instance.media_player_new()
    playback_end_callback = callback

    player.event_manager().event_attach(
        vlc.EventType.MediaPlayerEndReached,
        callback
    )


def set_mrl(mrl: str) -> None:
    global current_mrl

    current_mrl = mrl
    player.set_mrl(mrl)


def play() -> None:

    player.play()

    if not player.will_play():
        player.stop()
        playback_end_callback()


def stop() -> None:
    player.stop()


def pause() -> None:
    player.pause()


def available() -> bool:
    return os.path.exists(current_mrl)
