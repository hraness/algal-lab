"""Bounded custody of one exact child, with durable per-stage receipts.

The terminate/wait/kill/wait sequence follows degree_six/run.py; that frozen
module is not imported because its top-level imports use generic module names.
No other holder, process group, scheduler lease, or process tree is signalled.
"""

import math
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

from shared import digest, write_json


def terminate_owned_worker(process):
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def resident_bytes(pid):
    """Read only the owned child's RSS; a failed live sample fails closed."""
    ps = Path("/bin/ps")
    if not ps.exists():
        ps = Path("/usr/bin/ps")
    result = subprocess.run([str(ps), "-o", "rss=", "-p", str(pid)],
                            stdin=subprocess.DEVNULL, capture_output=True,
                            text=True, timeout=2, check=False)
    value = result.stdout.strip()
    if result.returncode or not value.isdigit() or len(value) > 20:
        raise ValueError("owned child RSS sample unavailable")
    return int(value) * 1024


def run_process(argv, log_path, receipt_path, *, cpu_seconds, wall_seconds,
                memory_mib=1024, file_bytes=256 * 1024**2):
    if (not argv or not 0 < cpu_seconds <= 300 or not 0 < wall_seconds <= cpu_seconds + 30
            or not 64 <= memory_mib <= 1024 or not 1 <= file_bytes <= 256 * 1024**2):
        raise ValueError("unsupported process limits")
    executable = Path(argv[0]).resolve(strict=True)
    command = [str(executable), *map(str, argv[1:])]
    log_path, receipt_path = Path(log_path), Path(receipt_path)
    if log_path.exists() or receipt_path.exists():
        raise ValueError("stage outputs must be new")
    hard_cpu = math.ceil(cpu_seconds)
    report = {"schema_version": 1, "argv": command, "executable_sha256": digest(executable),
              "status": "not_started", "cpu_limit_seconds": hard_cpu,
              "wall_limit_seconds": wall_seconds, "memory_threshold_mib": memory_mib,
              "rss_sampling_interval_seconds": 0.1, "rss_sample_timeout_seconds": 2,
              "memory_limit_is_cooperative": sys.platform == "darwin",
              "linux_address_space_limit": sys.platform.startswith("linux"),
              "per_file_limit_bytes": file_bytes, "pid": None, "returncode": None,
              "external_stop": None, "supervisor_signal": None}
    write_json(receipt_path, report)

    def limits():
        resource.setrlimit(resource.RLIMIT_CPU, (hard_cpu, hard_cpu))
        resource.setrlimit(resource.RLIMIT_FSIZE, (file_bytes, file_bytes))
        if sys.platform.startswith("linux"):
            memory_bytes = memory_mib * 1024**2
            resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))

    watched = (signal.SIGINT, signal.SIGTERM)
    previous = {sig: signal.getsignal(sig) for sig in watched}

    def interrupted(signum, _frame):
        report["supervisor_signal"] = signum
        raise KeyboardInterrupt

    process = None
    start = time.monotonic()
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    peak_rss = 0
    try:
        for sig in watched:
            signal.signal(sig, interrupted)
        with log_path.open("x") as log:
            process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=log,
                                       stderr=subprocess.STDOUT, preexec_fn=limits)
            report.update({"pid": process.pid, "status": "running"})
            write_json(receipt_path, report)
            try:
                while process.poll() is None:
                    remaining = wall_seconds - (time.monotonic() - start)
                    if remaining <= 0:
                        report["external_stop"] = "wall_limit"
                        break
                    try:
                        process.wait(timeout=min(0.1, remaining))
                    except subprocess.TimeoutExpired:
                        try:
                            peak_rss = max(peak_rss, resident_bytes(process.pid))
                        except (OSError, ValueError, subprocess.TimeoutExpired):
                            if process.poll() is None:
                                report["external_stop"] = "memory_monitor_failed"
                                break
                        if peak_rss >= memory_mib * 1024**2:
                            report["external_stop"] = "memory_threshold"
                            break
            except KeyboardInterrupt:
                report["external_stop"] = "supervisor_interrupted"
                report["supervisor_signal"] = report["supervisor_signal"] or int(signal.SIGINT)
    except (OSError, subprocess.SubprocessError) as error:
        report["external_stop"] = "launch_or_supervision_error"
        report["error"] = str(error)
    except KeyboardInterrupt:
        report["external_stop"] = "supervisor_interrupted"
        report["supervisor_signal"] = report["supervisor_signal"] or int(signal.SIGINT)
    finally:
        # Repeated interrupts cannot abandon the child during collection.
        for sig in watched:
            signal.signal(sig, signal.SIG_IGN)
        try:
            if process is not None:
                terminate_owned_worker(process)
                report["returncode"] = process.returncode
        finally:
            for sig, handler in previous.items():
                signal.signal(sig, handler)
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    report.update({"status": "complete" if report["external_stop"] is None else "incomplete",
                   "wall_seconds": time.monotonic() - start,
                   "children_cpu_seconds_including_rss_sampler":
                   after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime,
                   "maximum_sampled_rss_bytes": peak_rss,
                   "log_sha256": digest(log_path) if log_path.exists() else None,
                   "owned_child_collected": process is not None and process.returncode is not None})
    write_json(receipt_path, report)
    return report
