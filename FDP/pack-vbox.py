#!/usr/bin/env python3
import collections
import pathlib
import shutil
import subprocess
import sys

DIR_VBOX_BUILD = pathlib.Path.home() / "LLDBagility-build-vbox"
DIR_VBOX_OUT = pathlib.Path.home() / "LLDBagility-out-vbox"
DIR_VBOX_OUT_VBOX = DIR_VBOX_OUT / "VirtualBox.app"
DIR_VBOX_OUT_LIBS = DIR_VBOX_OUT / "VirtualBox.app/Contents/libs"


def _exec_cmd(args):
    return subprocess.run(args, check=True, stderr=sys.stderr, stdout=sys.stdout)


def _get_libs(fpath):
    output = subprocess.check_output(["otool", "-L", fpath])
    libs = list()
    for line in output.splitlines()[1:]:
        lpath = pathlib.Path(line[: line.index(b" ")].strip().decode("ascii"))
        if lpath.is_file():
            libs.append(lpath)
    return libs


def _install_name_change(lpath, newlpath, fpath):
    return _exec_cmd(["install_name_tool", "-change", lpath, newlpath, fpath])


def _is_port_lib(fpath):
    return "opt/local/lib" in str(fpath)


if __name__ == "__main__":
    shutil.rmtree(DIR_VBOX_OUT, ignore_errors=True)
    shutil.copytree(DIR_VBOX_BUILD / "darwin.amd64/release/dist", DIR_VBOX_OUT)

    _exec_cmd(["/opt/local/libexec/qt5/bin/macdeployqt", DIR_VBOX_OUT_VBOX])

    print("Fixing macdeployqt...")
    _install_name_change(
        "/opt/local/libexec/qt5/lib/QtGui.framework/Versions/5/QtGui",
        "@rpath/QtGui.framework/Version/5/QtGui",
        DIR_VBOX_OUT_VBOX / "Contents/Frameworks/QtMacExtras.framework/Versions/5/QtMacExtras",
    )
    _install_name_change(
        "/opt/local/libexec/qt5/lib/QtCore.framework/Versions/5/QtCore",
        "@rpath/QtCore.framework/Version/5/QtCore",
        DIR_VBOX_OUT_VBOX / "Contents/Frameworks/QtMacExtras.framework/Versions/5/QtMacExtras",
    )

    _install_name_change(
        "/opt/local/libexec/qt5/lib/QtCore.framework/Versions/5/QtCore",
        "@rpath/QtCore.framework/Version/5/QtCore",
        DIR_VBOX_OUT_VBOX / "Contents/Frameworks/QtGui.framework/Versions/5/QtGui",
    )

    _install_name_change(
        "/opt/local/libexec/qt5/lib/QtGui.framework/Versions/5/QtGui",
        "@rpath/QtGui.framework/Version/5/QtGui",
        DIR_VBOX_OUT_VBOX / "Contents/Frameworks/QtWidgets.framework/Versions/5/QtWidgets",
    )
    _install_name_change(
        "/opt/local/libexec/qt5/lib/QtCore.framework/Versions/5/QtCore",
        "@rpath/QtCore.framework/Version/5/QtCore",
        DIR_VBOX_OUT_VBOX / "Contents/Frameworks/QtWidgets.framework/Versions/5/QtWidgets",
    )

    _install_name_change(
        "/opt/local/libexec/qt5/lib/QtWidgets.framework/Versions/5/QtWidgets",
        "@rpath/QtWidgets.framework/Version/5/QtWidgets",
        DIR_VBOX_OUT_VBOX / "Contents/Frameworks/QtPrintSupport.framework/Versions/5/QtPrintSupport",
    )
    _install_name_change(
        "/opt/local/libexec/qt5/lib/QtGui.framework/Versions/5/QtGui",
        "@rpath/QtGui.framework/Version/5/QtGui",
        DIR_VBOX_OUT_VBOX / "Contents/Frameworks/QtPrintSupport.framework/Versions/5/QtPrintSupport",
    )
    _install_name_change(
        "/opt/local/libexec/qt5/lib/QtCore.framework/Versions/5/QtCore",
        "@rpath/QtCore.framework/Version/5/QtCore",
        DIR_VBOX_OUT_VBOX / "Contents/Frameworks/QtPrintSupport.framework/Versions/5/QtPrintSupport",
    )

    _install_name_change(
        "/opt/local/libexec/qt5/lib/QtWidgets.framework/Versions/5/QtWidgets",
        "@rpath/QtWidgets.framework/Version/5/QtWidgets",
        DIR_VBOX_OUT_VBOX / "Contents/Frameworks/QtOpenGL.framework/Versions/5/QtOpenGL",
    )
    _install_name_change(
        "/opt/local/libexec/qt5/lib/QtGui.framework/Versions/5/QtGui",
        "@rpath/QtGui.framework/Version/5/QtGui",
        DIR_VBOX_OUT_VBOX / "Contents/Frameworks/QtOpenGL.framework/Versions/5/QtOpenGL",
    )
    _install_name_change(
        "/opt/local/libexec/qt5/lib/QtCore.framework/Versions/5/QtCore",
        "@rpath/QtCore.framework/Version/5/QtCore",
        DIR_VBOX_OUT_VBOX / "Contents/Frameworks/QtOpenGL.framework/Versions/5/QtOpenGL",
    )

    print("Finding dependencies...")
    paths_to_process = collections.deque(DIR_VBOX_OUT.rglob("*"))
    paths_already_processed = set()
    deps = set()
    while paths_to_process:
        path = paths_to_process.pop()
        if not path.is_file() or path in paths_already_processed:
            continue
        paths_already_processed.add(path)

        for lpath in _get_libs(path):
            paths_to_process.append(lpath)
            if _is_port_lib(lpath) and "qt5" not in str(lpath):
                deps.add(lpath)

    print("Saving dependencies...")
    shutil.rmtree(DIR_VBOX_OUT_LIBS, ignore_errors=True)
    DIR_VBOX_OUT_LIBS.mkdir(parents=True)
    for lpath in deps:
        srcpath = lpath
        dstpath = DIR_VBOX_OUT_LIBS / lpath.name
        shutil.copyfile(srcpath, dstpath)
        dstpath.chmod(0o644)

    print("Patching references...")
    for path in DIR_VBOX_OUT.rglob("*"):
        if not path.is_file():
            continue

        for lpath in _get_libs(path):
            if _is_port_lib(lpath) and "qt5" not in str(lpath):
                newlpath = "@executable_path/../libs/" + lpath.name
                _install_name_change(lpath, newlpath, path)

    _install_name_change(
        "@executable_path/../libs/libz.1",
        "@executable_path/../libs/libz.dylib",
        DIR_VBOX_OUT_VBOX / "Contents/Frameworks/QtWidgets.framework/Versions/5/QtWidgets",
    )

    print("Done!")
