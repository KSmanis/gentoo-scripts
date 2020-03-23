#!/usr/bin/env python3

import argparse
from pathlib import Path

import portage

DEFAULT_CHECK_KEYWORDS = True
DEFAULT_CHECK_USE_FLAGS = True
DEFAULT_KEYWORD_PATH = Path('/etc/portage/package.accept_keywords')
DEFAULT_USE_PATH = Path('/etc/portage/package.use')


def _get_input_file_paths(path):
    if path.is_dir():
        return sorted(filter(lambda x: x.is_file() and not x.is_symlink(), path.iterdir()))
    else:
        return [path]


def _parse_args():
    parser = argparse.ArgumentParser(description="Check package configuration.")
    keyword_group = parser.add_mutually_exclusive_group()
    keyword_group.add_argument('-k', '--no-keywords', dest='keywords', action='store_false',
                               help="do not check package keywords")
    keyword_group.add_argument('-K', '--keywords', dest='keywords', action='store_true',
                               help="check package keywords (default)")
    use_flag_group = parser.add_mutually_exclusive_group()
    use_flag_group.add_argument('-u', '--no-use-flags', dest='useflags', action='store_false',
                                help="do not check package USE flags")
    use_flag_group.add_argument('-U', '--use-flags', dest='useflags', action='store_true',
                                help="check package USE flags (default)")
    parser.add_argument('--keyword-path', metavar='PATH', default=DEFAULT_KEYWORD_PATH,
                        help="the path (file or directory) to check for package keywords (default: %(default)s)")
    parser.add_argument('--use-path', metavar='PATH', default=DEFAULT_USE_PATH,
                        help="the path (file or directory) to check for package USE flags (default: %(default)s)")
    parser.set_defaults(keywords=DEFAULT_CHECK_KEYWORDS, useflags=DEFAULT_CHECK_USE_FLAGS)
    return parser.parse_args()


def _strip_use_flag(use_flag):
    return use_flag[1:] if use_flag.startswith(('+', '-')) else use_flag


def check_keywords(path=DEFAULT_KEYWORD_PATH):
    print("Checking keywords...")
    for p in _get_input_file_paths(Path(path)):
        with open(p) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                tokens = line.split()
                atom = tokens[0]
                keywords = tokens[1:] or ['~{host_arch}'.format(host_arch=portage.settings["ARCH"])]
                installed_packages = portage.db[portage.root]['vartree'].dbapi.match(atom)
                if not installed_packages:
                    print("{file_name}: {atom} is missing!".format(
                        file_name=portage.output.white(f.name),
                        atom=portage.output.red(atom),
                    ))
                    continue
                elif portage.versions.cpv_getversion(atom) is None:
                    continue

                for package in installed_packages:
                    package_keywords = portage.db[portage.root]['porttree'].dbapi.aux_get(package, ['KEYWORDS'])[0]
                    available_keywords = package_keywords.split()
                    for keyword in keywords:
                        if keyword not in available_keywords:
                            print("{file_name}: {atom} is missing the {keyword} keyword!".format(
                                file_name=portage.output.white(f.name),
                                atom=portage.output.red(atom),
                                keyword=portage.output.yellow(keyword),
                            ))


def check_use_flags(path=DEFAULT_USE_PATH):
    print("Checking USE flags...")
    for p in _get_input_file_paths(Path(path)):
        with open(p) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                tokens = line.split()
                atom = tokens[0]
                use_flags = list(map(_strip_use_flag, tokens[1:]))
                installed_packages = portage.db[portage.root]['vartree'].dbapi.match(atom)
                if not installed_packages:
                    print("{file_name}: {atom} is missing!".format(
                        file_name=portage.output.white(f.name),
                        atom=portage.output.red(atom),
                    ))
                    continue

                for package in installed_packages:
                    package_iuse = portage.db[portage.root]['porttree'].dbapi.aux_get(package, ['IUSE'])[0]
                    available_use_flags = list(map(_strip_use_flag, package_iuse.split()))
                    for use_flag in use_flags:
                        if use_flag not in available_use_flags:
                            print("{file_name}: {atom} is missing the {use_flag} USE flag!".format(
                                file_name=portage.output.white(f.name),
                                atom=portage.output.red(atom),
                                use_flag=portage.output.yellow(use_flag),
                            ))


if __name__ == '__main__':
    args = _parse_args()
    if args.keywords:
        check_keywords(path=args.keyword_path)
    if args.useflags:
        check_use_flags(path=args.use_path)
