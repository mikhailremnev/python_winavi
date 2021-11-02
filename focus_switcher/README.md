Simple python module to switch between X11 windows on screen.

    import focus_switcher
    # Select window to the left of the active window
    focus_switcher.switchFocus('L')
    # Select window to the right of the active window
    focus_switcher.switchFocus('R')
    # Select window above the active window
    focus_switcher.switchFocus('U')
    # Select window below the active window
    focus_switcher.switchFocus('D')

First call to `switchFocus` is slow since the module needs to build
a list of active windows.

You can delete the list of windows by running
`del focus_switcher.getWinList()[:]`, so focus_switcher will
rebuild it on the next call of `switchFocus`.

