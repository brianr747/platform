"""
Example of a "monkey patch." This file is ignored unless the following config setting is changed.

[Options]
UseMonkeyPatchExample = False # Set this to True

Right now, it has a Windows-specific action: it plays a sound when an external provider is accessed.

Since this is not particularly important, not worth making platform-agnostic.

"""

import datetime
# This is why I can't call my package "platform"!
import platform

try:
    import winsound
except ImportError:
    # Not exactly important
    pass

import econ_platform_core

last_beep: datetime.datetime = None

def beep_on_windows(*args):
    """
    When called, beeps (max every 5 seconds).

    Note: This function overwrites _hook_fetch_external. It ignores the parameters that are passed.
    :return:
    """
    if not platform.system() == 'Windows':
        # I think there's a cross-platform "beep" command, but no idea how annoying it is...
        # A non-Windows user can insert there own beeping code if they want.
        return
    # Don't beep more than once every 5 seconds.
    global last_beep
    nnow = datetime.datetime.now()
    if last_beep is not None:
        if (nnow - last_beep).seconds < 5:
            return
    last_beep = nnow
    try:
        winsound.PlaySound('SystemAsterisk', winsound.SND_ALIAS | winsound.SND_ASYNC)
    except:
        pass


def main():
    """
    Example of plugging in a custom function into the platform.

    Note: probably not a good idea to do have this hook running when running a big batch...
    :return:
    """
    econ_platform_core.update_protocols._hook_fetch_external = beep_on_windows
