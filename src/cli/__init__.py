import os
import platform
import sys

import cpuinfo
from rich import box
from rich.table import Table
from src.deployment.flow import cmd
from src.run_all_k8s import run_k8s
from src.utils import get_rich_console


def _get_run_args(print_args: bool = True):
    from src.cli.parser import get_main_parser

    console = get_rich_console()
    parser = get_main_parser()

    if len(sys.argv) > 1:
        from argparse import _StoreAction, _StoreTrueAction

        args, unknown = parser.parse_known_args()

        if unknown:
            # Need to handle the unwanted arg parse
            pass

        if print_args:
            from src import __resources_path__

            p = parser._actions[-1].choices[sys.argv[1]]
            default_args = {
                a.dest: a.default
                for a in p._actions
                if isinstance(a, (_StoreAction, _StoreTrueAction))
            }

            with open(os.path.join(__resources_path__, 'jina.logo')) as fp:
                logo_str = fp.read()

            param_str = Table(title=None, box=box.ROUNDED, highlight=True)
            param_str.add_column('')
            param_str.add_column('Parameters', justify='right')
            param_str.add_column('Value', justify='left')

            for k, v in sorted(vars(args).items()):
                sign = ' ' if default_args.get(k, None) == v else '🔧️'
                param = f'{k.replace("_", "-"): >30.30}'
                value = f'=  {str(v):30.30}'

                style = None if default_args.get(k, None) == v else 'blue on yellow'

                param_str.add_row(sign, param, value, style=style)

            print(f'\n{logo_str}\n')
            console.print(f'▶️  {" ".join(sys.argv)}')
            console.print(param_str)
        return args


def _quick_ac_lookup():
    from src.cli.autocomplete import ac_table

    if len(sys.argv) > 1:
        if sys.argv[1] == 'commands':
            for k in ac_table['commands']:
                print(k)
            exit()


def _is_latest_version(suppress_on_error=True):
    try:
        import json
        from urllib.request import Request, urlopen

        from jina import __version__

        req = Request(
            'https://api.jina.ai/latest', headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urlopen(
            req, timeout=5
        ) as resp:  # 'with' is important to close the resource after use
            latest_ver = json.load(resp)['version']
            from packaging.version import Version

            latest_ver = Version(latest_ver)
            cur_ver = Version(__version__)
            if cur_ver < latest_ver:
                from jina.logging.predefined import default_logger

                default_logger.warning(
                    f'You are using Jina version {cur_ver}, however version {latest_ver} is available. '
                    f'You should consider upgrading via the "pip install --upgrade jina" command.'
                )
                return False
        return True
    except Exception:
        if not suppress_on_error:
            raise


def cli():
    """The main entrypoint of the CLI"""
    _quick_ac_lookup()
    args = _get_run_args()

    if '--version' in sys.argv[1:]:
        # print(__version__)
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
    if not args:
        args = {}  # Empty arguments
    # kubectl needs `intel` or `m1` for apple os
    # for linux no need of architecture type
    if not os.path.isfile('/usr/local/bin/kubectl'):
        print('kubectl not found. Installing kubectl as it is required to run Jina Now')
        cmd(
            f'/bin/bash ./src/scripts/install_kubectl.sh {os_type} {arch}',
            output=False,
            error=False,
        )

    # kind needs no distinction of architecture type
    if not os.path.isfile('/usr/local/bin/kind'):
        print('kind not found. Installing kind')
        cmd(
            f'/bin/bash ./src/scripts/install_kind.sh {os_type}',
            output=False,
            error=False,
        )
    run_k8s(os_type=os, arch=arch, **args)
    print('done')


if __name__ == '__main__':
    print('I am here')
    cli()
    print('done')
