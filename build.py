from __future__ import annotations

import platform
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SEP = ";" if platform.system() == "Windows" else ":"


def compile_bundled_driver() -> Path:
    compiler = shutil.which("gfortran")
    if compiler is None:
        raise RuntimeError("gfortran is required on the build machine to package the Fortran driver.")

    runtime_dir = ROOT / "build" / "bundled_driver"
    module_dir = runtime_dir / "mod"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    module_dir.mkdir(parents=True, exist_ok=True)
    executable_name = "driverCLI.exe" if platform.system() == "Windows" else "driverCLI"
    executable = runtime_dir / executable_name
    sources = [ROOT / "fortran" / "src" / name for name in (
        "TypesDef.f90",
        "PrepCheap.f90",
        "PolyhedronMesh.f90",
        "triangleQuadratureGJ.f90",
        "CubaCheap.f90",
        "OptimalPolyCuba3D.f90",
        "driverCLI.f90",
    )]
    subprocess.run(
        [compiler, "-O2", "-ffree-line-length-none", "-J", str(module_dir), *map(str, sources), "-o", str(executable)],
        cwd=ROOT,
        check=True,
    )
    return executable


def main() -> None:
    system = platform.system()
    icon = None
    if system == "Darwin":
        icon = ROOT / "app" / "assets" / "CubatureApp.icns"
    elif system == "Windows":
        icon = ROOT / "app" / "assets" / "cubature_icon.ico"

    # Keep the package focused on the modules used by the desktop application.
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
        "--paths",
        str(ROOT),
        "--add-data",
        f"{ROOT / 'app' / 'assets'}{SEP}app/assets",
        "--add-data",
        f"{ROOT / 'fortran' / 'src'}{SEP}fortran/src",
        "--add-binary",
        f"{bundled_driver}{SEP}app/assets",
        "--collect-all",
        "pyvista",
        "--collect-all",
        "pyvistaqt",
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
    if icon is not None and icon.is_file():
        command[7:7] = ["--icon", str(icon)]

    subprocess.run(command, cwd=ROOT, check=True)
    print(f"Build completed for {system}. See: {ROOT / 'dist'}")


if __name__ == "__main__":
    main()
