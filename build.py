from __future__ import annotations

import platform
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SYSTEM = platform.system()

SEP = ";" if SYSTEM == "Windows" else ":"


def compile_bundled_driver() -> Path:
    """Compile the Fortran driver that will be bundled with CubatureApp."""

    compiler = shutil.which("gfortran")

    if compiler is None:
        raise RuntimeError(
            "gfortran is required on the build machine "
            "to compile the bundled Fortran driver."
        )

    runtime_dir = ROOT / "build" / "bundled_driver"
    module_dir = runtime_dir / "mod"

    runtime_dir.mkdir(parents=True, exist_ok=True)
    module_dir.mkdir(parents=True, exist_ok=True)

    executable_name = (
        "driverCLI.exe"
        if SYSTEM == "Windows"
        else "driverCLI"
    )

    executable = runtime_dir / executable_name

    sources = [
        ROOT / "fortran" / "src" / name
        for name in (
            "TypesDef.f90",
            "PrepCheap.f90",
            "PolyhedronMesh.f90",
            "triangleQuadratureGJ.f90",
            "CubaCheap.f90",
            "OptimalPolyCuba3D.f90",
            "driverCLI.f90",
        )
    ]

    subprocess.run(
        [
            compiler,
            "-O2",
            "-ffree-line-length-none",
            "-J",
            str(module_dir),
            *map(str, sources),
            "-o",
            str(executable),
        ],
        cwd=ROOT,
        check=True,
    )

    return executable


def build_application() -> None:
    if SYSTEM not in {"Darwin", "Windows"}:
        raise RuntimeError(
            f"Unsupported operating system: {SYSTEM}. "
            "Build CubatureApp on macOS or Windows."
        )

    print()
    print("*" * 70)
    print(f"Building CubatureApp for {SYSTEM}")
    print("*" * 70)
    print()

    if SYSTEM == "Darwin":
        icon = ROOT / "app" / "assets" / "CubatureApp.icns"
        output_dir = ROOT / "dist" / "macOS"
    else:
        icon = ROOT / "app" / "assets" / "cubature_icon.ico"
        output_dir = ROOT / "dist" / "Windows"

    output_dir.mkdir(parents=True, exist_ok=True)

    bundled_driver = compile_bundled_driver()

    command = [
    sys.executable,
    "-m",
    "PyInstaller",

    "--noconfirm",
    "--clean",

    "--onedir",
    "--windowed",

    "--name",
    "CubatureApp",

    "--distpath",
    str(output_dir),

    "--workpath",
    str(ROOT / "build" / "pyinstaller"),

    "--paths",
    str(ROOT),

    "--add-data",
    f"{ROOT / 'app' / 'assets'}{SEP}app/assets",

    "--add-data",
    f"{ROOT / 'fortran' / 'src'}{SEP}fortran/src",

    "--add-binary",
    f"{bundled_driver}{SEP}app/assets",

    "--exclude-module",
    "pytest",

    "--exclude-module",
    "IPython",

    "--exclude-module",
    "jupyter",

    "--exclude-module",
    "notebook",

    "--exclude-module",
    "sphinx",

    str(ROOT / "app" / "main.py"),
    ]

    if icon.is_file():
        command.extend([
            "--icon",
            str(icon),
        ])
    else:
        print(f"WARNING: icon not found: {icon}")

    print("Running PyInstaller...")
    print()

    subprocess.run(
        command,
        cwd=ROOT,
        check=True,
    )

    print()
    print("*" * 70)
    print("Build completed successfully.")
    print("*" * 70)
    print()

    if SYSTEM == "Darwin":
        print(f"Application: {output_dir / 'CubatureApp.app'}")
    else:
        print(
            f"Application: "
            f"{output_dir / 'CubatureApp' / 'CubatureApp.exe'}"
        )

    print()


def main() -> None:
    build_application()


if __name__ == "__main__":
    main()