# -*- encoding: utf-8 -*-
#
# Social Network Analysis of Git, Hg, SVN, GitHub, BitBucket repositories
#
# Author: Massimo Menichinelli
# Homepage: http://www.openp2pdesign.org
# License: LGPL v.3
#

import re
import subprocess
import os
import shutil
import json
from splitstream import splitfile
import StringIO
import unicodedata
from collections import OrderedDict
from dateutil.parser import parse

import github_analysis

import networkx as nx
import datetime


def convert_log_to_dict(input_text):
    """
    Convert the git log output to json.
    """

    items = []
    f = StringIO.StringIO(input_text)
    for jsonstr in splitfile(f, format="json"):
        try:
            items.append(json.loads(jsonstr))
        except Exception as e:
            return e

    return items


if __name__ == "__main__":
    pass
