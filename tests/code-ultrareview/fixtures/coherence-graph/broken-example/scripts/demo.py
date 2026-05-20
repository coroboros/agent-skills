#!/usr/bin/env python3
"""Demo script that only accepts --bar (intentionally diverges from README)."""

import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bar", action="store_true")
    args = parser.parse_args()
    print(args)


if __name__ == "__main__":
    main()
