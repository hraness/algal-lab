"""Local access to an installed CaDiCaL C API; no package download."""

import argparse
import ctypes
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build(static_library, output):
    static_library = static_library.resolve(strict=True)
    if output.exists():
        raise ValueError("output directory must be new")
    compiler = shutil.which("c++")
    if compiler is None:
        raise ValueError("an installed C++ compiler is required")
    output.mkdir(parents=True)
    if sys.platform == "darwin":
        library = output / "libcadical.dylib"
        command = [compiler, "-dynamiclib", "-Wl,-force_load," + str(static_library), "-o", str(library)]
    elif sys.platform.startswith("linux"):
        library = output / "libcadical.so"
        command = [compiler, "-shared", "-Wl,--whole-archive", str(static_library),
                   "-Wl,--no-whole-archive", "-o", str(library)]
    else:
        raise ValueError("unsupported shared-library platform")
    result = subprocess.run(command, capture_output=True, text=True, timeout=30)
    (output / "build.log").write_text(result.stdout + result.stderr)
    if result.returncode:
        raise ValueError("local shared-library link failed; see build.log")
    receipt = {"source": str(static_library), "source_sha256": digest(static_library),
               "command": command, "library": str(library), "library_sha256": digest(library),
               "network_used": False}
    (output / "build.json").write_text(json.dumps(receipt, indent=2) + "\n")
    return receipt


class Solver:
    def __init__(self, library, variables, *, seed=0, terminate=None, freeze=()):
        if type(variables) is not int or not 1 <= variables <= 100_000:
            raise ValueError("solver variable limit")
        if type(seed) is not int or not 0 <= seed <= 2**31 - 1:
            raise ValueError("solver seed range")
        self.variables = variables
        self.api = ctypes.CDLL(str(Path(library).resolve(strict=True)))
        pointer, integer = ctypes.c_void_p, ctypes.c_int
        for name, arguments, result in (
            ("ccadical_signature", [], ctypes.c_char_p),
            ("ccadical_init", [], pointer),
            ("ccadical_release", [pointer], None),
            ("ccadical_add", [pointer, integer], None),
            ("ccadical_solve", [pointer], integer),
            ("ccadical_val", [pointer, integer], integer),
            ("ccadical_set_option", [pointer, ctypes.c_char_p, integer], None),
            ("ccadical_declare_more_variables", [pointer, integer], integer),
            ("ccadical_freeze", [pointer, integer], None),
        ):
            function = getattr(self.api, name)
            function.argtypes, function.restype = arguments, result
        self.callback_type = ctypes.CFUNCTYPE(integer, pointer)
        self.api.ccadical_set_terminate.argtypes = [pointer, pointer, self.callback_type]
        self.api.ccadical_set_terminate.restype = None
        self.handle = self.api.ccadical_init()
        if not self.handle:
            raise RuntimeError("CaDiCaL initialization failed")
        self.signature = self.api.ccadical_signature().decode("ascii")
        self.api.ccadical_set_option(self.handle, b"quiet", 1)
        self.api.ccadical_set_option(self.handle, b"seed", seed)
        self.api.ccadical_declare_more_variables(self.handle, variables)
        for variable in freeze:
            self._literal(variable)
            self.api.ccadical_freeze(self.handle, variable)
        self.callback_failed = False

        def callback(_):
            try:
                return int(bool(terminate and terminate()))
            except BaseException:
                # A Python callback exception must fail closed, never turn into
                # a continued native search with a missing resource check.
                self.callback_failed = True
                return 1

        self.callback = self.callback_type(callback)
        self.api.ccadical_set_terminate(self.handle, None, self.callback)

    def _literal(self, literal):
        if type(literal) is not int or not 1 <= abs(literal) <= self.variables:
            raise ValueError("invalid solver literal")

    def add(self, clause):
        for literal in clause:
            self._literal(literal)
        for literal in clause:
            self.api.ccadical_add(self.handle, literal)
        self.api.ccadical_add(self.handle, 0)

    def solve(self):
        result = self.api.ccadical_solve(self.handle)
        if self.callback_failed:
            raise RuntimeError("native termination callback failed")
        if result not in (0, 10, 20):
            raise RuntimeError("unexpected SAT solver status")
        return result

    def value(self, variable):
        self._literal(variable)
        value = self.api.ccadical_val(self.handle, variable)
        if value not in (-variable, 0, variable):
            raise RuntimeError("invalid solver model value")
        return value > 0

    def close(self):
        if self.handle:
            self.api.ccadical_release(self.handle)
            self.handle = None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("static_library", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.static_library, args.output), indent=2))
