# -*- encoding: utf-8 -*-
#
# Social Network Analysis of Git, Hg, SVN, GitHub, BitBucket repositories
#
# Author: Massimo Menichinelli
# Homepage: http://www.openp2pdesign.org
# License: LGPL v.3
#

import requests
import os
import subprocess
import json
from splitstream import splitfile
import StringIO


def convert_log_to_dict(input_text):
    local_commits = []
    f = StringIO.StringIO(input_text)
    for jsonstr in splitfile(f, format="json"):
        local_commits.append(json.loads(jsonstr))
    return local_commits


if __name__ == "__main__":
    # Configure the path of the git project
    projectpath = ""
    gitpath = os.path.join(projectpath, '.git')

    # Get the authors from the git log
    gitlog = subprocess.check_output(
        ['git', 'log', '--pretty=format:%ae|%an'], cwd=projectpath)

    log_pretty_format = '{%n  "commit": "%H",%n  "abbreviated_commit": "%h",%n  "tree": "%T",%n  "abbreviated_tree": "%t",%n  "parent": "%P",%n  "abbreviated_parent": "%p",%n  "refs": "%D",%n  "encoding": "%e",%n  "subject": "%s",%n  "sanitized_subject_line": "%f",%n  "body": "%b",%n  "commit_notes": "%N",%n  "verification_flag": "%G?",%n  "signer": "%GS",%n  "signer_key": "%GK",%n  "author": {%n    "name": "%aN",%n    "email": "%aE",%n    "date": "%aD"%n  },%n  "commiter": {%n    "name": "%cN",%n    "email": "%cE",%n    "date": "%cD"%n  }%n},'

    # only commits
    # log_pretty_format = '{%n  "commit": "%H",%n}'

    # Get the verbose log in json
    gitlog = subprocess.check_output(
        ['git', 'log', '--pretty=format:' + log_pretty_format], cwd=projectpath)

    testing = convert_log_to_dict(gitlog)
    print testing
    print type(testing)
