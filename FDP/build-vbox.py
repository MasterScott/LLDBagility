#!/usr/bin/env python3
import pathlib
import shutil
import subprocess
import sys

DIR_VBOX_BUILD = pathlib.Path.home() / "LLDBagility-build-vbox"


def _exec_cmd(args):
    return subprocess.run(args, check=True, stderr=sys.stderr, stdout=sys.stdout)


if __name__ == "__main__":
    shutil.rmtree(DIR_VBOX_BUILD, ignore_errors=True)
    DIR_VBOX_BUILD.mkdir(parents=True)

    BUILD_VBOX_SCRIPT = DIR_VBOX_BUILD / "build.sh"
    with open(BUILD_VBOX_SCRIPT, "w") as f:
        f.write(
            f"""\
cat > "{DIR_VBOX_BUILD}/LocalConfig.kmk" <<EOF
VBOX_WITH_TESTSUITE             :=
VBOX_WITH_TESTCASES             :=

kBuildGlobalDefaults_LD_DEBUG   :=
EOF

export PATH="/usr/local/opt/ccache/libexec:$PATH"

./configure\
    --disable-hardening\
    --disable-extpack\
    --disable-java\
    --disable-python\
    --disable-docs\
    --with-openssl-dir="/usr/local/opt/openssl"\
    --with-xcode-dir="tools/darwin.amd64/xcode/v6.2/x.app"\
    --out-path="{DIR_VBOX_BUILD}"

source "{DIR_VBOX_BUILD}/env.sh"
kmk

find "{DIR_VBOX_BUILD}" -type d -name ".dSYM" -delete
"""
        )
    _exec_cmd(["bash", BUILD_VBOX_SCRIPT])

    print("Done!")
