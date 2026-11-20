import ctypes


class MONITORINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.c_ulong),
        ("rcMonitor", ctypes.c_ulong * 4),
        ("rcWork", ctypes.c_ulong * 4),
        ("dwFlags", ctypes.c_ulong),
    ]


class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_ulong)]


SHELL_CLASSES = {"Progman", "WorkerW", "Shell_TrayWnd", "Shell_SecondaryTrayWnd"}


def winapi():
    u = ctypes.windll.user32
    from ctypes import wintypes

    u.GetForegroundWindow.restype = wintypes.HWND
    u.GetParent.argtypes = [wintypes.HWND]
    u.GetParent.restype = wintypes.HWND
    u.GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    u.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
    u.MonitorFromWindow.argtypes = [wintypes.HWND, wintypes.DWORD]
    u.MonitorFromWindow.restype = wintypes.HANDLE
    u.GetMonitorInfoW.argtypes = [wintypes.HANDLE, ctypes.POINTER(MONITORINFO)]
    u.GetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int]
    u.GetWindowLongW.restype = ctypes.c_long
    u.IsWindowVisible.argtypes = [wintypes.HWND]
    u.IsIconic.argtypes = [wintypes.HWND]
    u.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
    u.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND, ctypes.c_int, ctypes.c_int,
                               ctypes.c_int, ctypes.c_int, wintypes.UINT]
    u.GetLastInputInfo.argtypes = [ctypes.POINTER(LASTINPUTINFO)]
    u.SystemParametersInfoW.argtypes = [ctypes.c_uint, ctypes.c_uint, ctypes.c_void_p, ctypes.c_uint]
    u.GetDpiForSystem.restype = ctypes.c_uint
    return u


def make_dpi_aware():
    for fn in (lambda: ctypes.windll.shcore.SetProcessDpiAwareness(2),
               lambda: ctypes.windll.user32.SetProcessDPIAware()):
        try:
            fn()
            break
        except Exception:
            pass


def work_area(u):
    from ctypes import wintypes
    wa = wintypes.RECT()
    u.SystemParametersInfoW(0x30, 0, ctypes.byref(wa), 0)
    return wa


def fullscreen_active(u):
    from ctypes import wintypes
    try:
        hwnd = u.GetForegroundWindow()
        if not hwnd or not u.IsWindowVisible(hwnd) or u.IsIconic(hwnd):
            return False
        pid = wintypes.DWORD()
        u.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value == ctypes.windll.kernel32.GetCurrentProcessId():
            return False
        buf = ctypes.create_unicode_buffer(64)
        u.GetClassNameW(hwnd, buf, 64)
        if buf.value in SHELL_CLASSES:
            return False
        rc = wintypes.RECT()
        u.GetWindowRect(hwnd, ctypes.byref(rc))
        mi = MONITORINFO()
        mi.cbSize = ctypes.sizeof(MONITORINFO)
        u.GetMonitorInfoW(u.MonitorFromWindow(hwnd, 2), ctypes.byref(mi))
        mleft, mtop, mright, mbottom = mi.rcMonitor
        covers = rc.left <= mleft and rc.top <= mtop and rc.right >= mright and rc.bottom >= mbottom
        exact = (rc.left, rc.top, rc.right, rc.bottom) == (mleft, mtop, mright, mbottom)
        captioned = (u.GetWindowLongW(hwnd, -16) & 0x00C00000) == 0x00C00000
        return covers and (exact or not captioned)
    except Exception:
        return False


def system_idle_seconds(u):
    try:
        li = LASTINPUTINFO()
        li.cbSize = ctypes.sizeof(li)
        if u.GetLastInputInfo(ctypes.byref(li)):
            return ((ctypes.windll.kernel32.GetTickCount() - li.dwTime) & 0xFFFFFFFF) / 1000
    except Exception:
        pass
    return 0.0


def set_topmost(u, hwnd):
    from ctypes import wintypes
    u.SetWindowPos(hwnd, wintypes.HWND(-1), 0, 0, 0, 0, 0x13)