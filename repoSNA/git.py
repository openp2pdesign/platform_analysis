# -*- encoding: utf-8 -*-
#
# Social Network Analysis of Git, Hg, SVN, GitHub, BitBucket repositories
#
# Author: Massimo Menichinelli
# Homepage: http://www.openp2pdesign.org
# License: LGPL v.3
#

import subprocess
import json
from splitstream import splitfile
import StringIO
import unicodedata


# Convert the log output to json
def convert_log_to_dict(input_text):
    local_commits = []
    f = StringIO.StringIO(input_text)
    for jsonstr in splitfile(f, format="json"):
        local_commits.append(json.loads(jsonstr))
    return local_commits


# Get the information of a git repository into a dict
def get_log(projectpath):
    # The pretty format for all the information from the log
    log_pretty_format = '''{%n
    "@node": "%H",%n
    "date": "%aD",%n
    "msg": {%n
    "#text": "%s"%n
    },%n
    "author": {%n
    "#text": "%aN",%n
    "@email": "%aE"%n
    },%n
    "commiter": {%n
    "#text": "%cN",%n
    "@email": "%cE"%n
    }%n},'''

    # Get the verbose log in json
    gitlog = subprocess.check_output(
        ['git', 'log', '--pretty=format:' + log_pretty_format],
        cwd=projectpath)

    # Convert to a dict
    all_commits = convert_log_to_dict(gitlog)

    # Do a diff-tree for each commit
    for i in all_commits:

        # Load the current commit id
        current_commit = unicodedata.normalize(
            'NFKD', i["@node"]).encode('ascii', 'ignore')

        # Create the command for diff-tree
        current_command = 'git diff-tree --no-commit-id --name-status -r ' + \
            current_commit

        # Get the log of the files for the current commit
        gitfileslog = subprocess.check_output(
            [current_command], cwd=projectpath, shell=True)

        # Split the output in a list of files
        current_files_list = [
            line for line in gitfileslog.split('\n') if line.strip() != '']

        # Create an empty dict for files for the current commit
        i["paths"] = {}

        # Cycle through each file changed in the current commit
        for k, j in enumerate(current_files_list):
            # Split action and filename, and save them as a dict
            each_file_info = j.split('\t')
            i["paths"]["path"] = {
                "@action": each_file_info[0], "#text": each_file_info[1]}

    # Format the log like hg and svn
    all_commits = {"log": {"logentry": all_commits}}
    # Return the full log with files changed at each commit
    return all_commits

if __name__ == "__main__":
    pass
