"""Windows Job Objects: OS-enforced limits for a child process (memory, CPU time, no child processes).

The child is created suspended, placed in the job, and only then resumed, so it never runs a single
instruction outside the limits. Closing the job kills everything still inside it.
"""

import ctypes
import subprocess
from ctypes import wintypes

CREATE_SUSPENDED = 0x00000004
BELOW_NORMAL_PRIORITY_CLASS = 0x00004000
CREATE_NO_WINDOW = 0x08000000

_JOB_OBJECT_EXTENDED_LIMIT_INFORMATION = 9
_LIMIT_JOB_TIME = 0x00000004
_LIMIT_ACTIVE_PROCESS = 0x00000008
_LIMIT_PROCESS_MEMORY = 0x00000100
_LIMIT_DIE_ON_UNHANDLED_EXCEPTION = 0x00000400
_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000


class _IoCounters(ctypes.Structure):
    _fields_ = [
        (name, ctypes.c_ulonglong)
        for name in (
            "ReadOperationCount",
            "WriteOperationCount",
            "OtherOperationCount",
            "ReadTransferCount",
            "WriteTransferCount",
            "OtherTransferCount",
        )
    ]


class _BasicLimits(ctypes.Structure):
    _fields_ = [
        ("PerProcessUserTimeLimit", ctypes.c_int64),
        ("PerJobUserTimeLimit", ctypes.c_int64),
        ("LimitFlags", wintypes.DWORD),
        ("MinimumWorkingSetSize", ctypes.c_size_t),
        ("MaximumWorkingSetSize", ctypes.c_size_t),
        ("ActiveProcessLimit", wintypes.DWORD),
        ("Affinity", ctypes.c_size_t),
        ("PriorityClass", wintypes.DWORD),
        ("SchedulingClass", wintypes.DWORD),
    ]


class _ExtendedLimits(ctypes.Structure):
    _fields_ = [
        ("BasicLimitInformation", _BasicLimits),
        ("IoInfo", _IoCounters),
        ("ProcessMemoryLimit", ctypes.c_size_t),
        ("JobMemoryLimit", ctypes.c_size_t),
        ("PeakProcessMemoryUsed", ctypes.c_size_t),
        ("PeakJobMemoryUsed", ctypes.c_size_t),
    ]


def _kernel32():
    k = ctypes.WinDLL("kernel32", use_last_error=True)
    k.CreateJobObjectW.restype = wintypes.HANDLE
    k.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
    k.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
    k.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    k.TerminateJobObject.argtypes = [wintypes.HANDLE, wintypes.UINT]
    k.CloseHandle.argtypes = [wintypes.HANDLE]
    return k


class JobLimitError(OSError):
    pass


class WindowsJob:
    def __init__(self, *, memory_bytes: int, cpu_seconds: float):
        self._k = _kernel32()
        self._ntdll = ctypes.WinDLL("ntdll")
        self._ntdll.NtResumeProcess.argtypes = [wintypes.HANDLE]
        self.handle = self._k.CreateJobObjectW(None, None)
        if not self.handle:
            raise JobLimitError(ctypes.get_last_error(), "CreateJobObject failed")
        info = _ExtendedLimits()
        info.BasicLimitInformation.LimitFlags = (
            _LIMIT_JOB_TIME
            | _LIMIT_ACTIVE_PROCESS
            | _LIMIT_PROCESS_MEMORY
            | _LIMIT_DIE_ON_UNHANDLED_EXCEPTION
            | _LIMIT_KILL_ON_JOB_CLOSE
        )
        info.BasicLimitInformation.PerJobUserTimeLimit = int(cpu_seconds * 10_000_000)  # 100 ns units
        info.BasicLimitInformation.ActiveProcessLimit = 1
        info.ProcessMemoryLimit = memory_bytes
        if not self._k.SetInformationJobObject(
            self.handle, _JOB_OBJECT_EXTENDED_LIMIT_INFORMATION, ctypes.byref(info), ctypes.sizeof(info)
        ):
            error = ctypes.get_last_error()
            self.close()
            raise JobLimitError(error, "SetInformationJobObject failed")

    def adopt_and_resume(self, proc: subprocess.Popen) -> None:
        """Puts a CREATE_SUSPENDED process into the job, then lets it run."""
        handle = int(proc._handle)  # type: ignore[attr-defined]
        if not self._k.AssignProcessToJobObject(self.handle, handle):
            raise JobLimitError(ctypes.get_last_error(), "AssignProcessToJobObject failed")
        if self._ntdll.NtResumeProcess(handle) != 0:
            raise JobLimitError(0, "NtResumeProcess failed")

    def terminate(self) -> None:
        self._k.TerminateJobObject(self.handle, 1)

    def close(self) -> None:
        if self.handle:
            self._k.CloseHandle(self.handle)  # KILL_ON_JOB_CLOSE ends anything left inside
            self.handle = None
