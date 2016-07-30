# -*- encoding: utf-8 -*-
#
# Social Network Analysis of Git, Hg, SVN, GitHub, BitBucket repositories
#
# Author: Massimo Menichinelli
# Homepage: http://www.openp2pdesign.org
# License: LGPL v.3
#

import subprocess
import os
import shutil
import json
from splitstream import splitfile
import StringIO
import unicodedata


def convert_log_to_dict(input_text):
    """
    Convert the git log output to json.
    """

    local_commits = []
    f = StringIO.StringIO(input_text)
    for jsonstr in splitfile(f, format="json"):
        local_commits.append(json.loads(jsonstr))
    return local_commits


def get_log(path):
    """
    Get the information of a git repository into a dict.
    """

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
        cwd=path)

    # Convert to a dict
    all_commits = convert_log_to_dict(gitlog)

    # Do a diff-tree for each commit
    for i in all_commits:

        # Load the current commit id
        current_commit = unicodedata.normalize(
            'NFKD', i["@node"]).encode('ascii', 'ignore')

        # Create the command for diff-tree
        current_command = 'git diff-tree --no-commit-id --name-status -r ' + \
            current_commit

        # Get the log of the files for the current commit
        gitfileslog = subprocess.check_output(
            [current_command], cwd=path, shell=True)

        # Split the output in a list of files
        current_files_list = [
            line for line in gitfileslog.split('\n') if line.strip() != '']

        # Create an empty dict for files for the current commit
        i["paths"] = {}

        # Cycle through each file changed in the current commit
        for k, j in enumerate(current_files_list):
            # Split action and filename, and save them as a dict
            each_file_info = j.split('\t')

            i["paths"][k] = {
                "@action": each_file_info[0], "#text": each_file_info[1]}

    # Format the log like hg and svn
    all_commits = {"log": {"logentry": all_commits}}

    # Return the full log with files changed at each commit
    return all_commits


def git_clone_analysis(url, path):
    """
    Clone, analyse (and then remove the local copy) a remote git repository.
    """

    # If we are on Linux or Mac
    if os.name == "posix":
        tmp_dir = "git.py.tmp"
        where = path + "/" + tmp_dir

        # Remove the temporary directory if it exists
        if os.path.isdir(where):
            try:
                shutil.rmtree(where)
            except subprocess.CalledProcessError as e:
                return e.returncode

        # Git clone to the temporary directory
        try:
            results = subprocess.check_output(
                ["git", "clone", url, where], cwd=path)
        except subprocess.CalledProcessError as e:
            return e.returncode

        # Git log output
        git_log = get_log(where)
        print git_log
        for commit in git_log["log"]["logentry"]:
            print commit
            print "SHA",commit["@node"]
            print "AUTHOR",commit["author"]["#text"]
            print "FILES"
            print commit["paths"]
            for committed_file in commit["paths"]:
                print committed_file
            print "----"
            print ""
        # Git log social network analysis

        # Remove the temporary directory if it exists
        if os.path.isdir(where):
            try:
                shutil.rmtree(where)
            except subprocess.CalledProcessError as e:
                return e.returncode

    return results


if __name__ == "__main__":
    pass
