Simple module to jump between adjacent windows in X11 window manager.

Requirements:
  * Python version >= 2.6
  * Xlib (`pip install Xlib` or `pip install --user Xlib` if you don't have sudo rights)

You can edit `win_navigator.py` to change the hotkeys, by default
the module uses `Alt+H, Alt+J, Alt+K, Alt+L` to move left, down, up and right
respectively.

(it's necessary to edit both `keycodes` dictionary and hotkey handling code near the end of the file)

