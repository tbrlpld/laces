#!/usr/bin/env python

import argparse
import os
import shutil
import sys
import warnings

from typing import Optional

from django.core.management import execute_from_command_line


os.environ["DJANGO_SETTINGS_MODULE"] = "laces.test.settings"


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--deprecation",
        choices=["all", "pending", "imminent", "none"],
        default="imminent",
    )
    return parser


def parse_args(
    args: Optional[list[str]] = None,
) -> tuple[argparse.Namespace, list[str]]:
    return make_parser().parse_known_args(args)


def runtests() -> None:
    args, rest = parse_args()

    only_django = r"^django(\.|$)"
    if args.deprecation == "all":
        # Show all deprecation warnings from all packages
        warnings.simplefilter("default", DeprecationWarning)
        warnings.simplefilter("default", PendingDeprecationWarning)
    elif args.deprecation == "pending":
        # Show all deprecation warnings from django
        warnings.filterwarnings(
            "default", category=DeprecationWarning, module=only_django
        )
        warnings.filterwarnings(
            "default", category=PendingDeprecationWarning, module=only_django
        )
    elif args.deprecation == "imminent":
        # Show only imminent deprecation warnings from django
        warnings.filterwarnings(
            "default", category=DeprecationWarning, module=only_django
        )
    elif args.deprecation == "none":
        # Deprecation warnings are ignored by default
        pass

    argv = [sys.argv[0]] + rest

    try:
        execute_from_command_line(argv)
    finally:
        from laces.test.settings import MEDIA_ROOT, STATIC_ROOT

        shutil.rmtree(STATIC_ROOT, ignore_errors=True)
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)


if __name__ == "__main__":
    runtests()
