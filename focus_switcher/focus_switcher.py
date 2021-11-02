#!/usr/bin/env python2

from __future__ import print_function
# Use double division by default (as in python3)
from __future__ import division

import Xlib
import Xlib.protocol.event
from Xlib import display, X
import sys

# TODO: Empty win_list after switching workspace
################################################

# https://stackoverflow.com/a/54018620
def getXProp(disp, win, prop):
    """Get X11 property of the specified window
    """
    p = win.get_full_property(disp.intern_atom('_NET_WM_' + prop), 0)
    return [None] if (p is None) else p.value

# https://stackoverflow.com/a/3131644
def getActiveWindow(disp):
    """Get active window on the specified display
    """
    win = disp.get_input_focus().focus
    if win.get_wm_name() is None and win.get_wm_class() is None:
        win = win.query_tree().parent
    return win

def getWinList():
    """Get list of windows found by this script
    """
    global win_list
    return win_list

class XWindow:
    def __init__(self, disp, win):
        self.disp       = disp
        self.win        = win

    def isHidden(self):
        return self.stateHasAtom('HIDDEN')
    def isActive(self):
        # return self.stateHasAtom('FOCUSED')
        # On some WMs, stateHasAtom('FOCUSED') produces incorrect results.
        # Thus, I'm using a different method
        return self.win == getActiveWindow(self.disp)

    def stateHasAtom(self, atom_name):
        atom  = self.disp.intern_atom('_NET_WM_STATE_' + atom_name)
        return atom in self._getState()
    def isViewable(self):
        return self._getMapState() == X.IsViewable
    def getGeometry(self):
        # True window geometry is usually only available from
        # parent window (but I guess it depends on window manager)
        return self.win.query_tree().parent.get_geometry()

    def _getState(self):
        return self.getAtom('STATE')
    def _getMapState(self):
        return self.win.get_attributes().map_state
    def getName(self):
        return self.getAtom('NAME')
    def getAtom(self, atom_name):
        """Get X11 property of the specified window
        """
        return getXProp(self.disp, self.win, atom_name)
    def getWorkspace(self):
        """Returns workspace ID or -1.
        """
        arr = self.getAtom('DESKTOP')
        if arr is None: return -1
        return arr[0]

# Excludes docks, taskbars, popup windows, etc
def isNormalWindow(disp, win):
    if not win.isViewable():
        return False
    if win._getState() == [None]:
        return False
    # https://specifications.freedesktop.org/wm-spec/wm-spec-1.3.html#idm140130317701136
    if win.stateHasAtom('SKIP_TASKBAR') or win.stateHasAtom('HIDDEN'):
        return False
    return True

def printAtoms(disp, prop):
    for atom in prop:
        print('  ', disp.get_atom_name(atom))

def getWindows(disp, parent):
    win_list = []
    children = parent.query_tree().children

    active_win = XWindow(disp, getActiveWindow(disp))
    # Current workspace
    workspace  = active_win.getWorkspace()

    for w in children:
        win = XWindow(disp, w)
        if isNormalWindow(disp, win) and win.getWorkspace() == workspace:
            win_list.append(win)
        # name = w.get_wm_name()
        win_list += getWindows(disp, w)

    return win_list

def getWindowDistance(geom_1, geom_2, direction):
    if direction == 'L':
        return getWindowDistance(geom_2, geom_1, 'R')
    if direction == 'U':
        return getWindowDistance(geom_2, geom_1, 'D')
    x_left   = [0, 0]
    x_right  = [0, 0]
    y_top    = [0, 0]
    y_bottom = [0, 0]
    x_center = [0, 0]
    y_center = [0, 0]
    for i, geom in enumerate((geom_1, geom_2)):
        x_left[i]   = geom.x
        x_right[i]  = geom.x + geom.width
        y_top[i]    = geom.y
        y_bottom[i] = geom.y + geom.height
        x_center[i] = geom.x + geom.width/2
        y_center[i] = geom.y + geom.height/2
    if direction == 'R':
        if y_top[1] >= y_bottom[0]:
            return None
        if y_bottom[1] <= y_top[0]:
            return None
        if x_center[1] <= x_center[0]:
            return None
        intersec = min(y_bottom) - max(y_top)
        if intersec / max( (geom_1.height, geom_2.height) ) < 0.1:
            return None
        return x_center[1] - x_center[0]
    if direction == 'D':
        if x_right[1] <= x_left[0]:
            return None
        if x_left[1] >= x_right[0]:
            return None
        if y_center[1] <= y_center[0]:
            return None
        intersec = min(x_right) - max(x_left)
        if intersec / max( (geom_1.width, geom_2.width) ) < 0.1:
            return None
        return y_center[1] - y_center[0]
    raise ValueError("Direction should be either 'R', 'U', 'L' or 'D'")

disp = display.Display()
root = disp.screen().root
win_list = []
def switchFocus(direction):
    global win_list

    if len(win_list) < 1:
        win_list = getWindows(disp, root)

    current_win = [w for w in win_list if w.isActive()]
    if len(current_win) == 0:
        win_list = getWindows(disp, root)
        current_win = [w for w in win_list if w.isActive()]
    if len(current_win) != 1:
        raise RuntimeError('Unable to find active window')
    geom_1 = current_win[0].getGeometry()
    
    target = None
    min_dist = None

    closed_windows = []

    for i, win in enumerate(win_list):
        if win.isActive() or win.isHidden():
            continue
    
        geom_2 = win.getGeometry()
        dist = getWindowDistance(geom_1, geom_2, direction)
        if dist == None:
            continue
        if min_dist == None or min_dist > dist:
            min_dist = dist
            target   = win

    if target != None:
        # https://xorg.freedesktop.narkive.com/iWck9TMY/xlib-force-raise-map-focus-a-given-window
        ev = Xlib.protocol.event.ClientMessage(
                window=target.win,
                client_type=disp.intern_atom('_NET_ACTIVE_WINDOW'),
                data=(32, [0,0,0,0,0,])
            )
        mask = X.SubstructureRedirectMask | X.SubstructureNotifyMask
        root.send_event(ev, event_mask=mask) # , propagate=True
        disp.sync()

def main(argv):
    if len(argv) < 2:
        print()
        print('%s: Switch window focus to specified direction' % argv[0])
        print('Usage: %s R|U|L|D' % argv[0])
        print()
        return

    switchFocus(argv[1])

if __name__ == '__main__':
    main(sys.argv)

