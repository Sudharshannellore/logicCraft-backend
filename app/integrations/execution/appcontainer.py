"""Windows AppContainer sandbox: the isolation browsers use for their renderer processes.

A process in an AppContainer runs with a special low-privilege token. It can't read the user's
files, other apps' data or anything not explicitly granted to its container SID, and it has no
network access unless given the internetClient capability (we never grant it). No admin rights
are needed to create one. Combined with a Job Object (memory/CPU/process limits) this lets
compilers and compiled programs run without seeing the server's files or secrets.

Two containers are used: one for compilers (may read the toolchains and use a build cache) and one
for running learner programs (sees only its own run folder and read-only runtimes).
"""

import ctypes
import os
import subprocess
import time
from ctypes import wintypes
from pathlib import Path

_userenv = ctypes.WinDLL("userenv")
_kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
_advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)

_E_ALREADY_EXISTS = ctypes.c_long(0x800700B7).value
_PROC_THREAD_ATTRIBUTE_HANDLE_LIST = 0x00020002
_PROC_THREAD_ATTRIBUTE_SECURITY_CAPABILITIES = 0x00020009
_EXTENDED_STARTUPINFO_PRESENT = 0x00080000
_CREATE_UNICODE_ENVIRONMENT = 0x00000400
_STARTF_USESTDHANDLES = 0x00000100
_WAIT_TIMEOUT = 0x102
_INFINITE = 0xFFFFFFFF


class _SecurityCapabilities(ctypes.Structure):
    _fields_ = [
        ("AppContainerSid", ctypes.c_void_p),
        ("Capabilities", ctypes.c_void_p),
        ("CapabilityCount", wintypes.DWORD),
        ("Reserved", wintypes.DWORD),
    ]


class _StartupInfo(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("lpReserved", wintypes.LPWSTR),
        ("lpDesktop", wintypes.LPWSTR),
        ("lpTitle", wintypes.LPWSTR),
        ("dwX", wintypes.DWORD),
        ("dwY", wintypes.DWORD),
        ("dwXSize", wintypes.DWORD),
        ("dwYSize", wintypes.DWORD),
        ("dwXCountChars", wintypes.DWORD),
        ("dwYCountChars", wintypes.DWORD),
        ("dwFillAttribute", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("wShowWindow", wintypes.WORD),
        ("cbReserved2", wintypes.WORD),
        ("lpReserved2", ctypes.c_void_p),
        ("hStdInput", wintypes.HANDLE),
        ("hStdOutput", wintypes.HANDLE),
        ("hStdError", wintypes.HANDLE),
    ]


class _StartupInfoEx(ctypes.Structure):
    _fields_ = [("StartupInfo", _StartupInfo), ("lpAttributeList", ctypes.c_void_p)]


class _ProcessInformation(ctypes.Structure):
    _fields_ = [
        ("hProcess", wintypes.HANDLE),
        ("hThread", wintypes.HANDLE),
        ("dwProcessId", wintypes.DWORD),
        ("dwThreadId", wintypes.DWORD),
    ]


_userenv.CreateAppContainerProfile.argtypes = [
    wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.LPCWSTR, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(ctypes.c_void_p)
]  # fmt: skip
_userenv.CreateAppContainerProfile.restype = ctypes.c_long
_userenv.DeriveAppContainerSidFromAppContainerName.argtypes = [wintypes.LPCWSTR, ctypes.POINTER(ctypes.c_void_p)]
_userenv.DeriveAppContainerSidFromAppContainerName.restype = ctypes.c_long
_advapi32.ConvertSidToStringSidW.argtypes = [ctypes.c_void_p, ctypes.POINTER(wintypes.LPWSTR)]
_kernel32.InitializeProcThreadAttributeList.argtypes = [
    ctypes.c_void_p,
    wintypes.DWORD,
    wintypes.DWORD,
    ctypes.POINTER(ctypes.c_size_t),
]
_kernel32.UpdateProcThreadAttribute.argtypes = [
    ctypes.c_void_p, wintypes.DWORD, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_void_p
]  # fmt: skip
_kernel32.DeleteProcThreadAttributeList.argtypes = [ctypes.c_void_p]
_kernel32.CreateProcessW.argtypes = [
    wintypes.LPCWSTR, wintypes.LPWSTR, ctypes.c_void_p, ctypes.c_void_p, wintypes.BOOL, wintypes.DWORD,
    ctypes.c_void_p, wintypes.LPCWSTR, ctypes.POINTER(_StartupInfoEx), ctypes.POINTER(_ProcessInformation),
]  # fmt: skip
_kernel32.ResumeThread.argtypes = [wintypes.HANDLE]
_kernel32.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
_kernel32.WaitForSingleObject.restype = wintypes.DWORD
_kernel32.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
_kernel32.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
_kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
_kernel32.LocalFree.argtypes = [ctypes.c_void_p]


class AppContainer:
    """A named AppContainer profile (created on first use; persists per user)."""

    def __init__(self, name: str, display_name: str):
        self.name = name
        sid = ctypes.c_void_p()
        hr = _userenv.CreateAppContainerProfile(name, display_name, display_name, None, 0, ctypes.byref(sid))
        if hr == _E_ALREADY_EXISTS:
            hr = _userenv.DeriveAppContainerSidFromAppContainerName(name, ctypes.byref(sid))
        if hr != 0:
            raise OSError(f"Couldn't create AppContainer {name!r} (HRESULT {hr & 0xFFFFFFFF:#x})")
        self._sid = sid  # freed with the process — profiles are long-lived
        text = wintypes.LPWSTR()
        if not _advapi32.ConvertSidToStringSidW(sid, ctypes.byref(text)):
            raise ctypes.WinError(ctypes.get_last_error())
        self.sid = text.value
        _kernel32.LocalFree(text)

    def grant(self, path: Path, rights: str = "RX", *, low_integrity: bool = False) -> None:
        """Lets this container access `path` (and everything below it). Only for folders we own."""
        subprocess.run(
            ["icacls", str(path), "/grant", f"*{self.sid}:(OI)(CI){rights}", "/Q"],
            check=True,
            capture_output=True,
        )
        if low_integrity:  # AppContainer tokens are low integrity: they can't write to medium-labelled folders
            subprocess.run(
                ["icacls", str(path), "/setintegritylevel", "(OI)(CI)low", "/Q"], check=True, capture_output=True
            )

    def spawn(
        self,
        command: list[str],
        *,
        cwd: str,
        env: dict[str, str],
        stdout,
        stderr,
        creationflags: int = 0,
    ) -> "ContainedProcess":
        """Starts `command` suspended inside the container. Call `.resume()` once it's in a job."""
        caps = _SecurityCapabilities(AppContainerSid=self._sid.value, Capabilities=None, CapabilityCount=0)
        devnull = open(os.devnull, "rb")  # noqa: SIM115 — closed after CreateProcess
        import msvcrt

        handles = [msvcrt.get_osfhandle(f.fileno()) for f in (devnull, stdout, stderr)]
        for h in set(handles):
            os.set_handle_inheritable(h, True)
        handle_array = (wintypes.HANDLE * len(set(handles)))(*set(handles))

        size = ctypes.c_size_t()
        _kernel32.InitializeProcThreadAttributeList(None, 2, 0, ctypes.byref(size))
        attrs = ctypes.create_string_buffer(size.value)
        if not _kernel32.InitializeProcThreadAttributeList(attrs, 2, 0, ctypes.byref(size)):
            raise ctypes.WinError(ctypes.get_last_error())
        try:
            for attribute, value, length in (
                (_PROC_THREAD_ATTRIBUTE_SECURITY_CAPABILITIES, ctypes.byref(caps), ctypes.sizeof(caps)),
                (_PROC_THREAD_ATTRIBUTE_HANDLE_LIST, handle_array, ctypes.sizeof(handle_array)),
            ):
                if not _kernel32.UpdateProcThreadAttribute(attrs, 0, attribute, value, length, None, None):
                    raise ctypes.WinError(ctypes.get_last_error())

            info = _StartupInfoEx()
            info.StartupInfo.cb = ctypes.sizeof(_StartupInfoEx)
            info.StartupInfo.dwFlags = _STARTF_USESTDHANDLES
            info.StartupInfo.hStdInput, info.StartupInfo.hStdOutput, info.StartupInfo.hStdError = handles
            info.lpAttributeList = ctypes.cast(attrs, ctypes.c_void_p)

            block = "".join(f"{k}={v}\0" for k, v in env.items()) + "\0"
            env_buffer = ctypes.create_unicode_buffer(block, len(block))
            cmdline = ctypes.create_unicode_buffer(subprocess.list2cmdline(command))
            pi = _ProcessInformation()
            flags = creationflags | _EXTENDED_STARTUPINFO_PRESENT | _CREATE_UNICODE_ENVIRONMENT
            if not _kernel32.CreateProcessW(
                None, cmdline, None, None, True, flags, env_buffer, cwd, ctypes.byref(info), ctypes.byref(pi)
            ):
                raise ctypes.WinError(ctypes.get_last_error())
        finally:
            _kernel32.DeleteProcThreadAttributeList(attrs)
            devnull.close()
        return ContainedProcess(pi)


class ContainedProcess:
    """The small part of `subprocess.Popen` the executor uses: wait / returncode / kill / _handle."""

    def __init__(self, pi: _ProcessInformation):
        self._handle = pi.hProcess
        self._thread = pi.hThread
        self.pid = pi.dwProcessId
        self.returncode: int | None = None

    def resume(self) -> None:
        if _kernel32.ResumeThread(self._thread) == 0xFFFFFFFF:
            raise ctypes.WinError(ctypes.get_last_error())

    def wait(self, timeout: float | None = None) -> int:
        if self.returncode is not None:
            return self.returncode
        ms = _INFINITE if timeout is None else max(0, int(timeout * 1000))
        started = time.perf_counter()
        if _kernel32.WaitForSingleObject(self._handle, ms) == _WAIT_TIMEOUT:
            raise subprocess.TimeoutExpired("contained process", time.perf_counter() - started)
        code = wintypes.DWORD()
        _kernel32.GetExitCodeProcess(self._handle, ctypes.byref(code))
        self.returncode = ctypes.c_int32(code.value).value
        self._close()
        return self.returncode

    def kill(self) -> None:
        if self.returncode is None and self._handle:
            _kernel32.TerminateProcess(self._handle, 1)

    def _close(self) -> None:
        for name in ("_thread", "_handle"):
            if getattr(self, name):
                _kernel32.CloseHandle(getattr(self, name))
                setattr(self, name, None)
