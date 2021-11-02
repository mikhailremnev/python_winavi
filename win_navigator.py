#!/usr/bin/env python2

# The code for hotkey handling and searching in the window tree is based on
# Quicktile implementations.
# (https://github.com/ssokolow/quicktile)
#
# Also, this script was heavily inspired by Quicktile, with the idea to
# (partially?) integrate with it (quicktile provides the tiling, winavi
#                                 provides the navigation)

from Xlib import display, X
import subprocess
from focus_switcher import switchFocus, getWinList

d = display.Display()
root = d.screen().root

# Xlib programming manual:
#   https://tronche.com/gui/x/xlib/
# Explanation of all event masks (like X.Mod1Mask):
#   https://tronche.com/gui/x/xlib/events/keyboard-pointer/keyboard-pointer.html
# Same, but for python-xlib
#   http://python-xlib.sourceforge.net/doc/html/python-xlib_12.html#SEC11
# Reference for Display class (pending_events() is an interesting method)
#   http://python-xlib.sourceforge.net/doc/html/python-xlib_16.html#SEC15

# Use `xev` to determine keycodes
keycodes = {
    'h': 43,
    'j': 44,
    'k': 45,
    'l': 46,
  }

###
# Alt
###
mask = X.Mod1Mask
print('Hotkeys: Alt+H, Alt+J, Alt+K, Alt+L')

###
# Win
###
# mask = X.Mod4Mask
# print('Hotkeys: Win+H, Win+J, Win+K, Win+L')

event_mask = 0
# Monitor key events for hotkeys
event_mask |= X.KeyPressMask
# Monitor window creation events
event_mask |= X.SubstructureNotifyMask
root.change_attributes(event_mask=event_mask)

for code in keycodes.values():
    # Set hotkeys to work even with Caps/Num/Scroll Lock
    additional_masks = [0,
            X.LockMask, # Caps Lock
            X.Mod2Mask, # Num Lock
            X.Mod3Mask, # Scroll Lock
            ]
    for add_mask in additional_masks:
        root.grab_key(code, mask | add_mask, 1, X.GrabModeAsync, X.GrabModeAsync)
d.sync()

while True:
    evt = root.display.next_event()
    # Unfortunately I wasn't able to mask key press events (I only need key releases),
    # so checking here manually.
    KEY_PRESS   = 2
    KEY_RELEASE = 3
    CREATE_NOTIFY  = 16
    DESTROY_NOTIFY = 17
    UNMAP_NOTIFY   = 18
    MAP_NOTIFY     = 19
    if evt.type in [MAP_NOTIFY, UNMAP_NOTIFY]:
        # If window is closed/opened/minimized/restored, force to rebuild
        # the list of current windows on the screen (by emptying it)
        del getWinList()[:]
    if evt.type != KEY_PRESS: continue
    evt_key = evt.detail

    key = ''
    for k in keycodes:
        if keycodes[k] == evt_key:
            key = k
            break
    if key == '': continue

    try:
        if key == 'h': switchFocus('L')
        if key == 'j': switchFocus('D')
        if key == 'k': switchFocus('U')
        if key == 'l': switchFocus('R')
    except RuntimeError:
        pass

