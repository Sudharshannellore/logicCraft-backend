"""Downloads portable compilers for the code runner into backend/.toolchains (Windows, no admin needed).

    python scripts/install_toolchains.py [gcc go php kotlin dotnet rust]

Official builds only, checksums verified where the publisher provides them. Python, Node.js (which
also runs TypeScript) and a JDK (for Java and Kotlin) are expected to be installed already.
Swift isn't covered: on Windows it needs Visual Studio Build Tools (admin); install it on Linux servers.
On Linux, install the distro packages instead (gcc g++ golang php-cli dotnet-sdk rustc kotlin swift).
"""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / ".toolchains"
UA = {"User-Agent": "Logicraft-toolchain-installer"}


def get_json(url: str):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return json.load(r)


def download(url: str, dest: Path, sha256: str | None = None) -> Path:
    print(f"  downloading {url}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=600) as r, dest.open("wb") as f:
        while chunk := r.read(1 << 20):
            f.write(chunk)
            digest.update(chunk)
    if sha256 and digest.hexdigest().lower() != sha256.lower():
        dest.unlink()
        raise SystemExit(f"checksum mismatch for {url}")
    print(f"  {dest.stat().st_size // 2**20} MB{' (sha256 ok)' if sha256 else ''}")
    return dest


def unzip(archive: Path, target: Path) -> None:
    if target.exists():
        shutil.rmtree(target)
    with zipfile.ZipFile(archive) as z:
        z.extractall(target)
    archive.unlink()


def unzip_top_folder(archive: Path, folder: str) -> None:
    """For archives whose single top-level folder is already the name we want (go/, kotlinc/).

    Extracting in place avoids renaming a just-unpacked folder, which antivirus scanners often lock.
    """
    shutil.rmtree(ROOT / folder, ignore_errors=True)
    with zipfile.ZipFile(archive) as z:
        z.extractall(ROOT)
    archive.unlink()


def github_asset(repo: str, predicate):
    release = get_json(f"https://api.github.com/repos/{repo}/releases/latest")
    asset = next(a for a in release["assets"] if predicate(a["name"]))
    digest = (asset.get("digest") or "").removeprefix("sha256:") or None
    return asset["browser_download_url"], asset["name"], digest


def gcc() -> None:
    """C and C++: WinLibs GCC (MinGW-w64, UCRT), without the optional LLVM tools."""
    url, name, digest = github_asset(
        "brechtsanders/winlibs_mingw",
        lambda n: n.startswith("winlibs-x86_64-posix-seh-gcc") and "llvm" not in n and n.endswith(".zip"),
    )
    unzip(download(url, ROOT / name, digest), ROOT / "gcc")


def go() -> None:
    release = get_json("https://go.dev/dl/?mode=json")[0]
    f = next(x for x in release["files"] if x["os"] == "windows" and x["arch"] == "amd64" and x["kind"] == "archive")
    unzip_top_folder(download(f"https://go.dev/dl/{f['filename']}", ROOT / f["filename"], f["sha256"]), "go")


def php() -> None:
    releases = get_json("https://windows.php.net/downloads/releases/releases.json")
    version = max(releases, key=lambda v: [int(p) for p in v.split(".")])
    build = next(v for k, v in releases[version].items() if "nts" in k and "x64" in k)["zip"]
    unzip(download(f"https://windows.php.net/downloads/releases/{build['path']}", ROOT / build["path"], build.get("sha256")), ROOT / "php")


def kotlin() -> None:
    url, name, _ = github_asset("JetBrains/kotlin", lambda n: n.startswith("kotlin-compiler-") and n.endswith(".zip") and "embeddable" not in n)
    with urllib.request.urlopen(urllib.request.Request(url + ".sha256", headers=UA), timeout=60) as r:
        digest = r.read().decode().split()[0]
    unzip_top_folder(download(url, ROOT / name, digest), "kotlinc")


def dotnet() -> None:
    """C#: the .NET SDK (current LTS) via Microsoft's official install script, into the toolchains folder."""
    script = download("https://dot.net/v1/dotnet-install.ps1", ROOT / "dotnet-install.ps1")
    subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script),
         "-Channel", "LTS", "-InstallDir", str(ROOT / "dotnet"), "-NoPath"],
        check=True,
    )  # fmt: skip
    script.unlink()


def rust() -> None:
    """Rust with the GNU host toolchain: it ships its own linker, so no Visual Studio is needed."""
    url = "https://static.rust-lang.org/rustup/dist/x86_64-pc-windows-gnu/rustup-init.exe"
    with urllib.request.urlopen(urllib.request.Request(url + ".sha256", headers=UA), timeout=60) as r:
        digest = r.read().decode().split()[0]
    installer = download(url, ROOT / "rustup-init.exe", digest)
    env = {**os.environ, "RUSTUP_HOME": str(ROOT / "rust" / "rustup"), "CARGO_HOME": str(ROOT / "rust" / "cargo")}
    subprocess.run(
        [str(installer), "-y", "--no-modify-path", "--profile", "minimal",
         "--default-host", "x86_64-pc-windows-gnu", "--default-toolchain", "stable"],
        check=True,
        env=env,
    )  # fmt: skip
    installer.unlink()


STEPS = {"gcc": gcc, "go": go, "php": php, "kotlin": kotlin, "dotnet": dotnet, "rust": rust}

if __name__ == "__main__":
    if sys.platform != "win32":
        raise SystemExit("This installer is for Windows. On Linux, install the distro packages (see the docstring).")
    ROOT.mkdir(exist_ok=True)
    for name in sys.argv[1:] or STEPS:
        print(f"[{name}]")
        STEPS[name]()
    print("Done. Restart the API so it picks up the new toolchains.")
