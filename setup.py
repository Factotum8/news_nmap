#!/usr/bin/env python3
# coding=utf-8
from setuptools import setup


setup(
    python_requires='~=3.8',

    install_requires=[
        # Production requirements (always need)
        "aiohttp==3.6.2",
        "PyYAML==5.3.1",
        "cacheout==0.11.2",
        "python3-logstash==0.4.80",
        "beautifulsoup4==4.9.0"
        ],

    # tests_require - New in 41.5.0: Deprecated the test command.
    extras_require={
        # test requirements
        'test': [
            "mock==2.0.0",
            "freezegun==0.3.12",
            "asynctest==0.12.2"
        ]
    },
)

