"""Run media subprocesses in an OS-owned process group.

On Windows, a Job Object with KILL_ON_JOB_CLOSE ensures FFmpeg children do not
outlive the worker if the worker is terminated unexpectedly.
"""
from __future__ import annotations

import ctypes
import os
import subprocess
from ctypes import wintypes
from typing import Any


class _BasicLimitInformation(ctypes.Structure):
    _fields_ = [
        ("PerProcessUserTimeLimit", ctypes.c_longlong),
        ("PerJobUserTimeLimit", ctypes.c_longlong),
        ("LimitFlags", wintypes.DWORD),
        ("MinimumWorkingSetSize", ctypes.c_size_t),
        ("MaximumWorkingSetSize", ctypes.c_size_t),
        ("ActiveProcessLimit", wintypes.DWORD),
        ("Affinity", ctypes.c_size_t),
        ("PriorityClass", wintypes.DWORD),
        ("SchedulingClass", wintypes.DWORD),
    ]


class _IoCounters(ctypes.Structure):
    _fields_ = [
        ("ReadOperationCount", ctypes.c_ulonglong),
        ("WriteOperationCount", ctypes.c_ulonglong),
        ("OtherOperationCount", ctypes.c_ulonglong),
        ("ReadTransferCount", ctypes.c_ulonglong),
        ("WriteTransferCount", ctypes.c_ulonglong),
        ("OtherTransferCount", ctypes.c_ulonglong),
    ]


class _ExtendedLimitInformation(ctypes.Structure):
    _fields_ = [
        ("BasicLimitInformation", _BasicLimitInformation),
        ("IoInfo", _IoCounters),
        ("ProcessMemoryLimit", ctypes.c_size_t),
        ("JobMemoryLimit", ctypes.c_size_t),
        ("PeakProcessMemoryUsed", ctypes.c_size_t),
        ("PeakJobMemoryUsed", ctypes.c_size_t),
    ]


def _create_kill_on_close_job() -> int | None:
    if os.name != "nt":
        return None

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
    kernel32.CreateJobObjectW.restype = wintypes.HANDLE
    kernel32.SetInformationJobObject.argtypes = [
        wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD
    ]
    kernel32.SetInformationJobObject.restype = wintypes.BOOL

    handle = kernel32.CreateJobObjectW(None, None)
    if not handle:
        raise ctypes.WinError(ctypes.get_last_error())

    info = _ExtendedLimitInformation()
    info.BasicLimitInformation.LimitFlags = 0x00002000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
    if not kernel32.SetInformationJobObject(
        handle, 9, ctypes.byref(info), ctypes.sizeof(info)
    ):
        error = ctypes.get_last_error()
        kernel32.CloseHandle(handle)
        raise ctypes.WinError(error)
    return int(handle)


def _assign_to_job(job_handle: int | None, process: subprocess.Popen[Any]) -> None:
    if job_handle is None:
        return
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    kernel32.AssignProcessToJobObject.restype = wintypes.BOOL
    if not kernel32.AssignProcessToJobObject(
        wintypes.HANDLE(job_handle), wintypes.HANDLE(int(process._handle))
    ):
        error = ctypes.get_last_error()
        process.kill()
        process.wait()
        raise ctypes.WinError(error)


def _close_job(job_handle: int | None) -> None:
    if job_handle is None:
        return
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL
    kernel32.CloseHandle(wintypes.HANDLE(job_handle))


def run_media_process(
    args: list[str],
    *,
    capture_output: bool = False,
    check: bool = False,
    timeout: float | None = None,
    input: str | bytes | None = None,
    text: bool = False,
    encoding: str | None = None,
    errors: str | None = None,
    cwd: str | os.PathLike[str] | None = None,
    env: dict[str, str] | None = None,
    stdout: int | Any | None = None,
    stderr: int | Any | None = None,
) -> subprocess.CompletedProcess[Any]:
    """Run a media command and tie its lifetime to this worker process."""
    if capture_output:
        if stdout is not None or stderr is not None:
            raise ValueError("stdout/stderr cannot be used with capture_output=True")
        stdout = subprocess.PIPE
        stderr = subprocess.PIPE
    if input is not None and stdout is not None:
        raise ValueError("stdin input cannot be combined with explicit stdout redirection")

    job_handle = _create_kill_on_close_job()
    process: subprocess.Popen[Any] | None = None
    try:
        process = subprocess.Popen(
            args,
            stdin=subprocess.PIPE if input is not None else None,
            stdout=stdout,
            stderr=stderr,
            cwd=cwd,
            env=env,
            text=text,
            encoding=encoding,
            errors=errors,
        )
        _assign_to_job(job_handle, process)
        try:
            out, err = process.communicate(input=input, timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            out, err = process.communicate()
            raise
        completed = subprocess.CompletedProcess(args, process.returncode, out, err)
        if check and completed.returncode:
            raise subprocess.CalledProcessError(
                completed.returncode, args, output=out, stderr=err
            )
        return completed
    finally:
        if process is not None and process.poll() is None:
            process.kill()
            process.wait()
        _close_job(job_handle)
