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
from io import BytesIO
import unicodedata
from collections import OrderedDict
from dateutil.parser import parse

from . import github_analysis

import networkx as nx
import datetime


def convert_log_to_dict(input_text):
    """
    Convert the git log output to json.
    """

    items = []
    #if type(input_text) != "str":
    #    input_text = input_text.decode('utf-8')
    f = BytesIO(input_text)
    for jsonstr in splitfile(f, format="json"):
        try:
            items.append(json.loads(jsonstr))
        except Exception as e:
            return e

    return items


def get_commits_log(path):
    """
    Get the history of the commits of a git repository into a dict.
    """

    # The pretty format for all the information from the log
    log_pretty_format = '''{%n
    "@node": "%H",%n
    "date": "%aD",%n
    "msg": "%f",%n
    "author": {%n
    "#text": "%aN",%n
    "@email": "%aE"%n
    },%n
    "committer": {%n
    "#text": "%cN",%n
    "@email": "%cE"%n
    }%n},'''

    # Get the verbose log in json
    git_log = subprocess.check_output(
        ['git', 'log', '--pretty=format:' + log_pretty_format], cwd=path)

    # Convert to a dict
    all_commits = convert_log_to_dict(git_log)

    # Do a diff-tree for each commit
    for i in all_commits:

        # Load the current commit id
        current_commit = unicodedata.normalize(
            'NFKD', i["@node"]).encode('ascii', 'ignore')

        # Create the command for diff-tree
        current_command = 'git diff-tree --no-commit-id --name-status -r ' + \
            current_commit

        # Get the log of the files for the current commit
        git_commit_files_log = subprocess.check_output(
            [current_command], cwd=path, shell=True)

        # Split the output in a list of files
        current_files_list = [
            line for line in git_commit_files_log.split('\n')
            if line.strip() != ''
        ]

        # Create an empty dict for files for the current commit
        i["paths"] = {}

        # Cycle through each file changed in the current commit
        for k, j in enumerate(current_files_list):
            # Split action and filename, and save them as a dict
            each_file_info = j.split('\t')

            i["paths"][k] = {
                "@action": each_file_info[0],
                "#text": each_file_info[1]
            }

    # Format the log like hg and svn
    all_commits = {"log": {"logentry": all_commits}}

    # Return the full log with files changed at each commit
    return all_commits


def get_files_log(path):
    """
    Get the history of each edited file in a git repository into a dict.
    """

    # The pretty format for the file log
    log_pretty_format = '''{%n
    "@node": "%H",%n
    "date": "%aD",%n
    "msg": "%f",%n
    "author": {%n
    "#text": "%aN",%n
    "@email": "%aE"%n
    },%n
    "committer": {%n
    "#text": "%cN",%n
    "@email": "%cE"%n
    }%n},'''

    # Get the verbose log in json
    git_log = subprocess.check_output(
        ['git', 'log', '--pretty=format:' + log_pretty_format], cwd=path)

    # Convert to a dict
    all_commits = convert_log_to_dict(git_log)

    # Create a list of edited files
    edited_files = []

    # Do a diff-tree for each commit
    for i in all_commits:

        # Load the current commit id
        current_commit = unicodedata.normalize(
            'NFKD', i["@node"]).encode('ascii', 'ignore')

        # Create the command for diff-tree
        current_command = 'git diff-tree --no-commit-id --name-status -r ' + \
            current_commit.decode('utf-8')

        # Get the log of the files for the current commit
        git_commit_files_log = subprocess.check_output(
            [current_command], cwd=path, shell=True)

        # Split the output in a list of files
        git_commit_files_log = git_commit_files_log.decode('utf-8')
        current_files_list = [
            line for line in git_commit_files_log.split('\n')
            if line.strip() != ''
        ]

        # Cycle through each file changed in the current commit
        for k, j in enumerate(current_files_list):
            # Split action and filename, and save them as a dict
            each_file_info = j.split('\t')
            if each_file_info[1] not in edited_files:
                edited_files.append(each_file_info[1])

    # Get the verbose log for each file in the history in json
    git_all_files_log = {}

    for k, each_file in enumerate(edited_files):
        current_file_log = subprocess.check_output(
            ['git', 'log', '--pretty=format:' + log_pretty_format, '--follow',
             '--', each_file],
            cwd=path)
        git_all_files_log[str(each_file)] = convert_log_to_dict(
            current_file_log)

    # Format the log like hg and svn
    all_files = {"log": {"logentry": git_all_files_log}}

    # Return the full log with the history of each file
    return all_files


def git_repo_analysis(git_files_log, graph):
    """
    The main function of SNA for a git repo.
    """

    # For each file, check its history and connect committers based on
    # commit order: connect each committer with the previous ones for the
    # same file (path dependency)
    for k, each_file in enumerate(git_files_log):
        file_history = {}
        for l, each_commit in enumerate(git_files_log[each_file]):
            file_history[l] = {
                "author": each_commit["author"]["#text"],
                "email": each_commit["author"]["@email"],
                "date": each_commit["date"],
                "@node": each_commit["@node"],
                "msg": re.sub(r'-', " ", each_commit["msg"])
            }

        # Sort the dict in order to be sure about the chronological order
        # of the file history
        sorted_file_history = OrderedDict(
            sorted(
                file_history.items(), key=lambda x: x[1]['date']))

        # Add an edge from a committer to the previous ones
        # since there are interactions on the same file
        for j in sorted_file_history:

            # Add the committers in case they are not in the graph
            if sorted_file_history[j]["author"] not in graph:
                graph.add_node(
                    sorted_file_history[j]["author"], committer="Yes",
                    email=sorted_file_history[j]["email"])
            else:
                graph.nodes[sorted_file_history[j]["author"]]["committer"] = "Yes"

            # Look for the interactions
            following_committers = {}
            for m in range(j):
                following_committers[m] = (sorted_file_history[m])
            #following_committers[j] = sorted_file_history[j]["author"]
            reversed_following_committers = OrderedDict(
                sorted(
                    following_committers.items(), reverse=True))

            for t in following_committers:
                if t < len(reversed_following_committers) - 1:
                    first_actor = reversed_following_committers[t]["author"]
                    second_actor = sorted_file_history[j]["author"]
                    # Add the nodes of the edge
                    graph.add_node(first_actor, Label=first_actor)
                    graph.add_node(first_actor, Label=second_actor)
                    # Add the edge
                    github_analysis.edge_key += 1
                    graph.add_edge(
                        first_actor,
                        second_actor,
                        key=github_analysis.edge_key,
                        node=sorted_file_history[j]["@node"], type="commit",
                        msg=re.sub(r'-', " ", sorted_file_history[j]["msg"]),
                        start=parse(reversed_following_committers[t]["date"]),
                        endopen=datetime.datetime.now().year)
                    # start=parse(sorted_file_history[j]["date"]),

    return graph


def git_remote_repo_log(url, path, log_type):
    """
    Clone, retrieve the log of (and then remove the local copy) a remote git repository.
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
            subprocess.check_output(["git", "clone", url, where], cwd=path)
        except subprocess.CalledProcessError as e:
            return e.returncode

        # Load the log output
        if log_type.lower() == "files" or log_type.lower() == "file":
            git_log = get_files_log(where)["log"]["logentry"]
        else:
            git_log = get_commits_log(where)["log"]["logentry"]

        # Remove the temporary directory if it exists
        if os.path.isdir(where):
            try:
                shutil.rmtree(where)
            except subprocess.CalledProcessError as e:
                return e.returncode

    return git_log


def git_remote_repo_analysis(url, path, graph):
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
            subprocess.check_output(["git", "clone", url, where], cwd=path)
        except subprocess.CalledProcessError as e:
            return e.returncode

        # Load the log output for each file
        git_files_log = get_files_log(where)["log"]["logentry"]

        # Analyse the repo
        git_repo_analysis(git_files_log=git_files_log, graph=graph)

        # Remove the temporary directory if it exists
        if os.path.isdir(where):
            try:
                shutil.rmtree(where)
            except subprocess.CalledProcessError as e:
                return e.returncode

    return graph


def git_local_repo_analysis(path, graph):
    """
    Analyse a local git repository.
    """

    # If we are on Linux or Mac
    if os.name == "posix":

        # Load the log output for each file
        git_files_log = get_files_log(path)["log"]["logentry"]

        # Analyse the repo
        git_repo_analysis(git_files_log=git_files_log, graph=graph)

    return graph


if __name__ == "__main__":
    pass
