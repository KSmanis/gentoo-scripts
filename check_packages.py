#!/usr/bin/env python3

import argparse
import operator
from functools import partial
from itertools import tee
from pathlib import Path

import portage

DEFAULT_CHECK_KEYWORDS = True
DEFAULT_CHECK_LICENSES = True
DEFAULT_CHECK_SORT_ORDER = True
DEFAULT_CHECK_USE_FLAGS = True
DEFAULT_KEYWORD_PATH = Path('/etc/portage/package.accept_keywords')
DEFAULT_LICENSE_PATH = Path('/etc/portage/package.license')
DEFAULT_USE_PATH = Path('/etc/portage/package.use')


def _is_sorted(iterable, comparator=operator.le):
    a, b = tee(iterable)
    next(b, None)
    return all(map(comparator, a, b))


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
    license_group = parser.add_mutually_exclusive_group()
    license_group.add_argument('-l', '--no-licenses', dest='licenses', action='store_false',
                               help="do not check package licenses")
    license_group.add_argument('-L', '--licenses', dest='licenses', action='store_true',
                               help="check package licenses (default)")
    sort_order_group = parser.add_mutually_exclusive_group()
    sort_order_group.add_argument('-s', '--no-sort-order', dest='sort_order', action='store_false',
                                  help="do not check sort order")
    sort_order_group.add_argument('-S', '--sort-order', dest='sort_order', action='store_true',
                                  help="check sort order (default)")
    use_flag_group = parser.add_mutually_exclusive_group()
    use_flag_group.add_argument('-u', '--no-use-flags', dest='use_flags', action='store_false',
                                help="do not check package USE flags")
    use_flag_group.add_argument('-U', '--use-flags', dest='use_flags', action='store_true',
                                help="check package USE flags (default)")
    parser.add_argument('--keyword-path', metavar='PATH', default=DEFAULT_KEYWORD_PATH,
                        help="the path (file or directory) to check for package keywords (default: %(default)s)")
    parser.add_argument('--license-path', metavar='PATH', default=DEFAULT_LICENSE_PATH,
                        help="the path (file or directory) to check for package licenses (default: %(default)s)")
    parser.add_argument('--use-path', metavar='PATH', default=DEFAULT_USE_PATH,
                        help="the path (file or directory) to check for package USE flags (default: %(default)s)")
    parser.set_defaults(keywords=DEFAULT_CHECK_KEYWORDS, licenses=DEFAULT_CHECK_LICENSES,
                        sort_order=DEFAULT_CHECK_SORT_ORDER, use_flags=DEFAULT_CHECK_USE_FLAGS)
    return parser.parse_args()


def _strip_use_flag(use_flag, prefix=('+', '-')):
    return use_flag[1:] if use_flag.startswith(prefix) else use_flag


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
                keywords = tokens[1:] or ['~{host_arch}'.format(host_arch=portage.settings['ARCH'])]
                installed_packages = portage.db[portage.root]['vartree'].dbapi.match(atom)
                if not installed_packages:
                    print("{file_name}: {atom} is no longer installed!".format(
                        file_name=portage.output.white(f.name),
                        atom=portage.output.red(atom),
                    ))
                    continue
                elif portage.versions.cpv_getversion(atom) is None:
                    continue

                for package in installed_packages:
                    try:
                        package_keywords = portage.db[portage.root]['porttree'].dbapi.aux_get(package, ['KEYWORDS'])[0]
                    except portage.exception.PortageKeyError:
                        print("{file_name}: {atom} is no longer available in the portage tree!".format(
                            file_name=portage.output.white(f.name),
                            atom=portage.output.red(atom),
                        ))
                    else:
                        available_keywords = package_keywords.split()
                        for keyword in keywords:
                            if keyword not in available_keywords:
                                print("{file_name}: {atom} no longer requires the {keyword} keyword!".format(
                                    file_name=portage.output.white(f.name),
                                    atom=portage.output.red(atom),
                                    keyword=portage.output.yellow(keyword),
                                ))


def check_licenses(path=DEFAULT_LICENSE_PATH):
    print("Checking licenses...")
    for p in _get_input_file_paths(Path(path)):
        with open(p) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                atom = line.split(maxsplit=1)[0]
                installed_packages = portage.db[portage.root]['vartree'].dbapi.match(atom)
                if not installed_packages:
                    print("{file_name}: {atom} is no longer installed!".format(
                        file_name=portage.output.white(f.name),
                        atom=portage.output.red(atom),
                    ))


def check_use_flags(path=DEFAULT_USE_PATH, check_sort_order=DEFAULT_CHECK_SORT_ORDER):
    print("Checking USE flags...")
    for p in _get_input_file_paths(Path(path)):
        with open(p) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                tokens = line.split()
                atom = tokens[0]
                use_flags = tokens[1:]
                if check_sort_order and not _is_sorted(map(partial(_strip_use_flag, prefix='+'), use_flags)):
                    print("{file_name}: {atom} has unsorted USE flags!".format(
                        file_name=portage.output.white(f.name),
                        atom=portage.output.red(atom),
                    ))
                installed_packages = portage.db[portage.root]['vartree'].dbapi.match(atom)
                if not installed_packages:
                    print("{file_name}: {atom} is no longer installed!".format(
                        file_name=portage.output.white(f.name),
                        atom=portage.output.red(atom),
                    ))
                    continue

                for package in installed_packages:
                    try:
                        package_iuse = portage.db[portage.root]['porttree'].dbapi.aux_get(package, ['IUSE'])[0]
                    except portage.exception.PortageKeyError:
                        print("{file_name}: {atom} is no longer available in the portage tree!".format(
                            file_name=portage.output.white(f.name),
                            atom=portage.output.red(atom),
                        ))
                    else:
                        available_use_flags = list(map(_strip_use_flag, package_iuse.split()))
                        for use_flag in map(_strip_use_flag, use_flags):
                            if use_flag not in available_use_flags:
                                print("{file_name}: {atom} no longer makes use of the {use_flag} USE flag!".format(
                                    file_name=portage.output.white(f.name),
                                    atom=portage.output.red(atom),
                                    use_flag=portage.output.yellow(use_flag),
                                ))


if __name__ == '__main__':
    args = _parse_args()
    if args.keywords:
        check_keywords(path=args.keyword_path)
    if args.licenses:
        check_licenses(path=args.license_path)
    if args.use_flags:
        check_use_flags(path=args.use_path, check_sort_order=args.sort_order)
