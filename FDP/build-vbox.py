#!/usr/bin/env python3
import datetime
import pathlib
import shutil
import subprocess
import sys

DIRPATH_VBOX_BUILD = pathlib.Path.home() / "LLDBagility-vbox-build"


if __name__ == "__main__":
    shutil.rmtree(DIRPATH_VBOX_BUILD, ignore_errors=True)
    DIRPATH_VBOX_BUILD.mkdir(parents=True)

    starttime = datetime.datetime.now()
    SCRIPT_VBOX_BUILD = DIRPATH_VBOX_BUILD / "build.sh"
    with open(SCRIPT_VBOX_BUILD, "w") as f:
        f.write(
            f"""\
cat > "{DIRPATH_VBOX_BUILD}/LocalConfig.kmk" <<EOF
VBOX_WITH_DARWIN_R0_DARWIN_IMAGE_VERIFICATION =
VBOX_WITH_TESTSUITE =
VBOX_WITH_TESTCASES =
kBuildGlobalDefaults_LD_DEBUG =
EOF

./configure\
    --disable-hardening\
    --disable-java\
    --disable-python\
    --disable-docs\
    --with-qt-dir="/opt/local/libexec/qt5"\
    --with-openssl-dir="/usr/local/opt/openssl"\
    --with-xcode-dir="tools/darwin.amd64/xcode/v6.2/x.app"\
    --out-path="{DIRPATH_VBOX_BUILD}"

source "{DIRPATH_VBOX_BUILD}/env.sh"
kmk
"""
        )
    subprocess.check_output(["/usr/bin/env", "bash", SCRIPT_VBOX_BUILD])
    print("Done in {}".format(datetime.datetime.now() - starttime))
