#!/usr/bin/env python3
# coding=utf-8

import os
from collections import ChainMap

import yaml

__all__ = ('load_config', )


def load_config(path_to_config=None):
    if path_to_config:
        with open(path_to_config) as f:
            return ChainMap(os.environ, yaml.safe_load(f))
    return ChainMap(os.environ)


if __name__ == '__main__':
    pass
