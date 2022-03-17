# from __future__ import print_function
#
import platform
import re
import sys

import cpuinfo

from src.deployment.flow import cmd

# from .characters import CHARS
CHARS = {
    "tux": r'''
     \
      \
       \
        .--.
       |o_o |
       |:_/ |
      //   \ \
     (|     | )
    /'\_   _/`\
    \___)=(___/
'''
}

__version__ = '4.0'
__name__ = 'jina-now'

char_names = CHARS.keys()


def main():
    if '--version' in sys.argv[1:]:
        print(__version__)
        exit(0)

    os_type = platform.system().lower()
    arch = 'x86_64'
    if os_type == 'darwin':
        if 'm1' in cpuinfo.get_cpu_info().get('brand_raw').lower():
            arch = 'arm64'
        else:
            arch = platform.machine()
    elif os_type == 'linux':
        arch = platform.machine()
    # kubectl needs `intel` or `m1` for apple os
    # for linux no need of architecture type
    output, _ = cmd(
        f'/bin/bash ./scripts/install_kubectl.sh {os_type} {arch}',
        output=False,
        error=False,
    )

    # kind needs no distinction of architecture type
    cmd(
        f'/bin/bash ./scripts/install_kind.sh {os_type}',
        output=False,
        error=False,
    )

    # gcloud needs `x86_64`, `arm64` and `x86_64` for mac os
    # for linux it needs `x86_64` and `x86`
    cmd(
        f'/bin/bash ./scripts/install_kind.sh {os_type} {arch}',
        output=False,
        error=False,
    )


if __name__ == '__main__':
    print(' Iam here')
    cli()
    print('done')
