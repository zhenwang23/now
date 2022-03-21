import argparse

from src import __version__


def set_base_parser():
    """Set the base parser
    :return: the parser
    """

    # create the top-level parser
    urls = {
        'Code': ('💻', 'https://github.com/jina-ai/now'),
        'Jina Docs': ('📖', 'https://docs.jina.ai'),
        'Help': ('💬', 'https://slack.jina.ai'),
        'Hiring!': ('🙌', 'https://career.jina.ai'),
    }
    url_str = '\n'.join(f'- {v[0]:<10} {k:10.10}\t{v[1]}' for k, v in urls.items())

    parser = argparse.ArgumentParser(
        epilog=f'''
        Jina NOW allows one to tune the weights of any deep neural network for better embedding on search tasks.
        
        {url_str}
        
        ''',
        description='Command Line Interface of `%(prog)s`',
    )
    parser.add_argument(
        '-v',
        '--version',
        action='version',
        version=__version__,
        help='Show Jina version',
    )

    return parser


def set_help_parser(parser=None):
    """Set the parser for the jina help lookup
    :param parser: an optional existing parser to build upon
    :return: the parser
    """

    if not parser:
        from jina.parsers.base import set_base_parser

        parser = set_base_parser()

    parser.add_argument(
        'query',
        type=str,
        help='Lookup the usage & mention of the argument name in Jina NOW',
    )
    return parser


def set_now_parser(parser=None):
    """Add the arguments for the jina now to the parser
    :param parser: an optional existing parser to build upon
    :return: the parser
    """

    if not parser:
        from jina.parsers.base import set_base_parser

        parser = set_base_parser()
    parser.add_argument(
        '--name',
        help='the name of the Executor',
        type=str,
    )

    parser.add_argument(
        '--data',
        help='Select one of the provided datasets or set it to custom to use your own dataset',
        type=str,
    )

    parser.add_argument(
        '--data_path',
        help='The path to the custom dataset if you want to load from local filepath',
        type=str,
    )

    parser.add_argument(
        '--data_url',
        help='If your docarray is hosted on a remote server, then provide the url to pull',
        type=str,
    )

    parser.add_argument(
        '--data_secret',
        help='If you want to pull custom docarray from the Hub, then provide the secret',
        type=str,
    )

    parser.add_argument(
        '--quality',
        help='Choose the qulaity of the model that you would like to finetune',
        type=str,
    )


def get_main_parser():
    """The main parser for Jina NOW
    :return: the parser
    """
    # create the top-level parser
    parser = set_base_parser()
    # sp = parser.add_subparsers(
    #     dest='cli',
    #     description='''.
    #         To show all commands, run `jina-now commands`.
    #         ''',
    #     required=True,
    # )
    # set_help_parser(
    #     sp.add_parser(
    #         'help',
    #         help='Show help text of a CLI argument',
    #         description='Show help text of a CLI argument',
    #     )
    # )
    set_now_parser(parser)

    return parser
