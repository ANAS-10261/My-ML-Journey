import sys
import ctypes
import win32gui
import win32con
import win32api
import win32process
from PyQt5 import QtWidgets, QtCore, QtGui

# Windows API constants
TB_BUTTONCOUNT = 0x0418
TB_GETITEMRECT = 0x041D


def find_taskbar_toolbar():
    """
    Find the toolbar window that contains taskbar icons.
    """
    taskbar = win32gui.FindWindow("Shell_TrayWnd", None)
    tray = win32gui.FindWindowEx(taskbar, 0, "TrayNotifyWnd", None)

    # Windows 10/11 uses this structure
    rebar = win32gui.FindWindowEx(taskbar, 0, "ReBarWindow32", None)
    taskband = win32gui.FindWindowEx(rebar, 0, "MSTaskSwWClass", None)
    toolbar = win32gui.FindWindowEx(taskband, 0, "ToolbarWindow32", None)

    return toolbar


def get_taskbar_icon_rects():
    """
    Get screen rectangles of taskbar icons.
    """
    toolbar = find_taskbar_toolbar()
    if not toolbar:
        return []

    count = win32gui.SendMessage(toolbar, TB_BUTTONCOUNT, 0, 0)
    rects = []

    for i in range(count):
        rect = ctypes.wintypes.RECT()
        win32gui.SendMessage(
            toolbar,
            TB_GETITEMRECT,
            i,
            ctypes.byref(rect)
        )

        # Convert to screen coordinates
        pt = win32gui.ClientToScreen(toolbar, (rect.left, rect.top))
        left, top = pt
        right = left + (rect.right - rect.left)
        bottom = top + (rect.bottom - rect.top)

        rects.append((left, top, right, bottom))

    return rects


class Overlay(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint
            | QtCore.Qt.WindowStaysOnTopHint
            | QtCore.Qt.Tool
        )

        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)

        self.showFullScreen()

        # Update timer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(500)

    def paintEvent(self, event):
        rects = get_taskbar_icon_rects()

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        font = QtGui.QFont("Segoe UI", 12, QtGui.QFont.Bold)
        painter.setFont(font)
        painter.setPen(QtGui.QColor(255, 255, 255))

        for i, r in enumerate(rects[:9]):
            x = r[0] + 5
            y = r[1] + 5
            painter.drawText(x, y + 15, str(i + 1))


def main():
    app = QtWidgets.QApplication(sys.argv)
    overlay = Overlay()
    overlay.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
