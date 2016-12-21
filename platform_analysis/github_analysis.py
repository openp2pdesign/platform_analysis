# -*- encoding: utf-8 -*-
#
# Social Network Analysis of Git, Hg, SVN, GitHub, BitBucket repositories
#
# Author: Massimo Menichinelli
# Homepage: http://www.openp2pdesign.org
# License: LGPL v.3
#

import re
import string

from github import Github

import networkx as nx
import git
import datetime


# Global variables
# Edge counting
edge_key = 0
# The main graph
graph = nx.MultiDiGraph()
# Log in to GitHub
github_login = Github()


def check_none(value_to_check):
    """
    Helper function that checks for None values from the GitHub APIs.
    """

    return value_to_check if value_to_check is not None else "None"


def github_login(userlogin, username, password):
    """
    Login on GitHub in order to retrieve a dict of repositories
    for a given username.
    """

    # Log in to GitHub
    global github_login
    github_login = Github(userlogin, password)

    results = {}

    # Load the repositories of the username
    for k, repo in enumerate(github_login.get_user(username).get_repos()):
        results[k] = {"name": repo.name, "data": repo}

    return results


def clean_graph(graph):
    """
    Check the missing attributes of every node, and add a "No" when it is not
    present. With this you can, for example, use the attribute for graph
    partitioning in Gephi
    """

    for i in graph.nodes():
        graph.node[i]["Label"] = str(i)
        if "owner" not in graph.node[i]:
            graph.node[i]["owner"] = "No"
        if "committer" not in graph.node[i]:
            graph.node[i]["committer"] = "No"
        if "forker" not in graph.node[i]:
            graph.node[i]["forker"] = "No"
        if "stargazer" not in graph.node[i]:
            graph.node[i]["stargazer"] = "No"
        if "contributor" not in graph.node[i]:
            graph.node[i]["contributor"] = "No"
        if "collaborator" not in graph.node[i]:
            graph.node[i]["collaborator"] = "No"
        if "watcher" not in graph.node[i]:
            graph.node[i]["watcher"] = "No"
        if "subscriber" not in graph.node[i]:
            graph.node[i]["subscriber"] = "No"
        if "issue creator" not in graph.node[i]:
            graph.node[i]["issue creator"] = "No"
        if "issue commenter" not in graph.node[i]:
            graph.node[i]["issue commenter"] = "No"
        if "pull request assignee" not in graph.node[i]:
            graph.node[i]["pull request assignee"] = "No"
        if "issue assignee" not in graph.node[i]:
            graph.node[i]["issue assignee"] = "No"
        if "email" not in graph.node[i]:
            graph.node[i]["email"] = "None"
        if "avatar_url" not in graph.node[i]:
            graph.node[i]["avatar_url"] = "None"

    # Fix None nodes and attributes
    for v in graph.nodes_iter(data=True):
        for attrib in v[1]:
            # Convert nonetype values to string "None"
            if v[1][attrib] is None:
                graph.node[v[0]][attrib] = "None"
        # Remove any None node
        if v[0] == "None" or v[0] is None:
            graph.remove_node(v[0])

    return graph


def github_analysis(repository, username, userlogin, password, path):
    """
    Analyse a specific repository.
    """

    # Log in to GitHub
    global github_login
    github_login = Github(userlogin, password)
    repository_object = github_login.get_user(username).get_repo(repository)

    repo_analysis(repository=repository_object, path=path, graph=graph)

    fork_analysis(repository=repository_object, graph=graph)

    pull_requests_analysis(repository=repository_object, graph=graph)

    clean_graph(graph=graph)

    return graph


def fork_analysis(repository, graph):
    """
    Analyse the forks of a repository.
    """

    # Global variable
    global edge_key

    # Local graph variable
    local_graph = nx.MultiDiGraph()

    for f, i in enumerate(repository.get_forks()):
        if i.owner is not None and repository.owner is not None:
            # Add edge from the forker to the owner
            if i.owner.login not in graph.nodes():
                get_users(
                    element=i.owner.login, user_type="forker", graph=graph)
                get_users(
                    element=i.owner.login,
                    user_type="forker",
                    graph=local_graph)
            graph.add_edge(
                i.owner.login,
                repository.owner.login,
                key=edge_key,
                node=f,
                msg=i.full_name,
                type="fork",
                start=i.created_at,
                endopen=datetime.datetime.now().year)
            local_graph.add_edge(
                i.owner.login,
                repository.owner.login,
                key=edge_key,
                node=f,
                msg=i.full_name,
                type="fork",
                start=i.created_at,
                endopen=datetime.datetime.now().year)

    return local_graph


def pull_requests_analysis(repository, graph):
    """
    Analyse the discussion of pull requests of a repository.
    """

    # Global variable
    global edge_key

    # Local graph variable
    local_graph = nx.MultiDiGraph()

    # Check both open and closed pull requests
    # Open pull requests are not merged
    pull_request_states = ["closed", "open"]

    for state in pull_request_states:
        for f, i in enumerate(repository.get_pulls(state=state)):
            if i.is_merged() is True:
            # if state == "closed":
                # Add edge from who merged the pull request to who did it
                if i.merged_by is not None and i.user is not None:
                    if i.merged_by.login not in graph.nodes():
                        get_users(
                            element=i.merged_by,
                            user_type="forker",
                            graph=graph)
                        get_users(
                            element=i.merged_by,
                            user_type="forker",
                            graph=local_graph)
                    if i.user.login not in graph.nodes():
                        get_users(
                            element=i.user, user_type="forker", graph=graph)
                        get_users(
                            element=i.user,
                            user_type="forker",
                            graph=local_graph)
                    graph.add_edge(
                        i.merged_by.login,
                        i.user.login,
                        key=edge_key,
                        node=i.merge_commit_sha,
                        msg=i.title,
                        type="merged pull request",
                        start=i.merged_at,
                        endopen=datetime.datetime.now().year)
                    local_graph.add_edge(
                        i.merged_by.login,
                        i.user.login,
                        key=edge_key,
                        node=i.merge_commit_sha,
                        msg=i.title,
                        type="merged pull request",
                        start=i.merged_at,
                        endopen=datetime.datetime.now().year)

            # Add edge from who did the pull requests to the repo owner
            if repository.owner is not None and i.user is not None:
                if repository.owner.login not in graph.nodes():
                    get_users(
                        element=repository.owner,
                        user_type="created a pull request",
                        graph=graph)
                    get_users(
                        element=repository.owner,
                        user_type="created a pull request",
                        graph=local_graph)
                graph.add_edge(
                    i.user.login,
                    repository.owner.login,
                    key=edge_key,
                    node=i.id,
                    msg=i.title,
                    type="merged pull request",
                    start=i.created_at,
                    endopen=datetime.datetime.now().year)
                local_graph.add_edge(
                    i.user.login,
                    repository.owner.login,
                    key=edge_key,
                    node=i.id,
                    msg=i.title,
                    type="created a pull request",
                    start=i.created_at,
                    endopen=datetime.datetime.now().year)

            # Add edge from owner to assignee
            if i.assignee is not None:
                if i.assignee not in graph.nodes():
                    get_users(
                        element=i.assignee,
                        user_type="pull request assignee",
                        graph=graph)
                    get_users(
                        element=i.assignee,
                        user_type="pull request assignee",
                        graph=local_graph)
                graph.add_edge(
                    repository.owner.login,
                    i.assignee,
                    key=edge_key,
                    node=i.id,
                    msg=i.title,
                    type="pull request assignee",
                    start=i.created_at,
                    endopen=datetime.datetime.now().year)

            # Comments
            # for j in i.get_comments():
            #     print j
            # for j in i.get_review_comments():
            #     print j
            # for j in i.get_issue_comments():
            #     print j

            # Check the comments in the pull request
            pull_request_comments = []
            for j in i.get_comments():
                comment = {'@node': j.id,
                           'date': j.created_at,
                           'msg': j.title,
                           'author': {'#text': j.user.login,
                                      '@email': j.user.email,
                                      'avatar_url': j.user.avatar_url}}
                get_users(
                    element=j.user,
                    user_type="pull request commenter",
                    graph=graph)
                pull_request_comments.append(comment)

            comments_analysis(
                pull_request_comments,
                graph,
                comment_type="pull request comment")
            comments_analysis(
                pull_request_comments,
                local_graph,
                comment_type="pull request comment")

    return local_graph


def issue_analysis(issue, graph):
    """
    Analyse the discussion of a single issue.
    """

    # Global variable
    global edge_key

    # Local graph variable
    local_graph = nx.MultiDiGraph()

    if issue.user is not None:
        # Issue creator
        get_users(element=issue.user, user_type="issue creator", graph=graph)

    # Issue assignee
    if issue.assignee is not None:
        edge_key += 1
        get_users(
            element=issue.assignee, user_type="issue assignee", graph=graph)
        graph.add_edge(
            issue.user.login,
            issue.assignee.login,
            key=edge_key,
            node=issue.id,
            msg=issue.title,
            type="issue assignation",
            start=issue.created_at,
            endopen=datetime.datetime.now().year)
        local_graph.add_edge(
            issue.user.login,
            issue.assignee.login,
            key=edge_key,
            node=issue.id,
            msg=issue.title,
            type="issue assignation",
            start=issue.created_at,
            endopen=datetime.datetime.now().year)

    # Check the comments in the issue
    issues_comments = []
    first_issue_comment = {
        '@node': issue.id,
        'date': issue.created_at,
        'msg': issue.title,  # Use f.body for the comment content
        'author': {'#text': issue.user.login,
                   '@email': issue.user.email,
                   'avatar_url': issue.user.avatar_url}}
    issues_comments.append(first_issue_comment)
    for j, f in enumerate(issue.get_comments()):
        comment = {'@node': f.id,
                   'date': f.created_at,
                   'msg': issue.title,  # Use f.body for the comment content
                   'author': {'#text': f.user.login,
                              '@email': f.user.email,
                              'avatar_url': f.user.avatar_url}}
        get_users(element=f.user, user_type="issue commenter", graph=graph)
        issues_comments.append(comment)

    comments_analysis(
        issues_comments,
        graph,
        comment_type="issue comment")
    comments_analysis(
        issues_comments,
        local_graph,
        comment_type="issue comment")

    return local_graph


def comments_analysis(discussion, graph, comment_type):
    """
    Analyse the discussion of a GitHub discussion.
    Add edges to the graph and return a graph of the specified discussion.
    """

    # Global variable
    global edge_key

    # Local graph variable
    local_graph = nx.MultiDiGraph()

    # Check all the comments in the commit
    for j, f in enumerate(discussion):
        # Add an edge to all the previous participants in the discussion
        for k in discussion[:j]:
            edge_key += 1
            graph.add_edge(
                f["author"]["#text"], k["author"]["#text"], key=edge_key,
                node=f["@node"], type=comment_type, msg=f["msg"],
                start=f["date"], endopen=datetime.datetime.now().year)
            local_graph.add_edge(
                f["author"]["#text"], k["author"]["#text"], key=edge_key,
                type=comment_type, node=f["@node"], date=f["date"],
                msg=f["msg"], start=f["date"],
                endopen=datetime.datetime.now().year)

            # Check if there are any username mentions in the body of each
            # comment, and add an edge if there are any
            message_body = f["msg"]
            message_body_split = message_body.split()
            for word in message_body_split:
                # If the word is an username...
                if "@" in word:
                    # Check that it is a username and not an e-mail address
                    email_check = re.findall(r'[\w\.-]+@[\w\.-]+', word)
                    # If it is not an e-mail address but an username, add an
                    # edge
                    if len(email_check) == 0:
                        # Remove the @ mention char
                        word = re.sub(r'@', "", word)
                        # If the username is a word longer than 0 chars, then
                        # create an edge from the issue comment author to the
                        # mentioned username
                        if len(word) != 0:
                            # Remove strange punctuation at the end, if any
                            if word[-1] in string.punctuation:
                                word = word[:-1]
                                edge_key += 1
                                graph.add_edge(
                                    f["author"]["#text"], word, key=edge_key,
                                    type="comment mention", start=f["date"],
                                    endopen=datetime.datetime.now().year)
                                local_graph.add_edge(
                                    f["author"]["#text"], word, key=edge_key,
                                    type="comment mention", start=f["date"],
                                    endopen=datetime.datetime.now().year)

    return local_graph


def get_users(element, user_type, graph):
    """
    Get users of a specific type from the GitHub repo.
    """

    try:
        if element is not None:
            if str(element.login) not in graph:
                graph.add_node(str(element.login))
                # graph.node[str(element.login)]["Label"] = str(element.login)
                graph.node[str(element.login)][user_type] = "Yes"
                graph.node[str(element.login)]["email"] = check_none(element.email)
                graph.node[str(element.login)]["avatar_url"] = check_none(
                    element.avatar_url)
            else:
                graph.node[str(element.login)][user_type] = "Yes"
    except:
        try:
            new_element = github_login.get_user(element)
            if new_element is not None:
                if str(new_element.login) not in graph:
                    graph.add_node(str(new_element.login))
                    # graph.node[str(new_element.login)]["Label"] = check_none(new_element.login)
                    graph.node[str(new_element.login)][user_type] = "Yes"
                    graph.node[str(new_element.login)]["email"] = check_none(new_element.email)
                    graph.node[str(new_element.login)]["avatar_url"] = check_none(new_element.avatar_url)
                else:
                    graph.node[str(new_element.login)][user_type] = "Yes"
        except:
            print("There was an error with", element, "which is of type",
                  type(element))


def repo_analysis(repository, path, graph):
    """
    Analyse a specific GitHub repo.
    """

    # Global variable
    global edge_key

    # Local graph variable
    local_graph = nx.MultiDiGraph()

    # Add the repo owner to the graph
    get_users(element=repository.owner, user_type="owner", graph=graph)
    get_users(element=repository.owner, user_type="owner", graph=local_graph)

    # Add an edge from the owner to the repo, to mark the creation of the repo
    graph.add_edge(
        repository.owner.login,
        repository.full_name,
        key=edge_key,
        type="repository creation",
        start=repository.created_at,
        endopen=datetime.datetime.now().year)
    edge_key += 1

    # Add the repo watchers to the graph
    for i in repository.get_stargazers():
        get_users(element=i, user_type="stargazer", graph=graph)
        get_users(element=i, user_type="stargazer", graph=local_graph)

    # Add the repo collaborators to the graph
    for i in repository.get_collaborators():
        get_users(element=i, user_type="collaborator", graph=graph)
        get_users(element=i, user_type="collaborator", graph=local_graph)

    # Add the repo contributors to the graph
    for i in repository.get_contributors():
        get_users(element=i, user_type="contributor", graph=graph)
        get_users(element=i, user_type="contributor", graph=local_graph)

    # Add the repo watchers to the graph
    for i in repository.get_watchers():
        get_users(element=i, user_type="watcher", graph=graph)
        get_users(element=i, user_type="watcher", graph=local_graph)

    # Add the repo subscribers to the graph
    for i in repository.get_subscribers():
        get_users(element=i, user_type="subscriber", graph=graph)
        get_users(element=i, user_type="subscriber", graph=local_graph)

    # Analyse issues of the repo
    if repository.has_issues is True:
        for i in repository.get_issues(state="open"):
            issue_analysis(i, graph)
            issue_analysis(i, local_graph)
        for i in repository.get_issues(state="closed"):
            issue_analysis(i, graph)
            issue_analysis(i, local_graph)

    # Analyse the commits of the repo

    # Get the log from GitHub, we want the GitHub username
    github_commits = []
    for i in repository.get_commits():
        if i is not None:
            commit = {
                "@node": check_none(i.sha),
                "date": check_none(i.commit.author.date),
                "msg": check_none(i.commit.message),
                "author": {
                    "#text": check_none(i.author.login)
                    if i.author is not None else 'None',
                    "@email": check_none(i.author.email)
                    if i.author is not None else 'None',
                    "avatar_url": check_none(i.author.avatar_url)
                    if i.author is not None else 'None'
                },
                "committer": {
                    "#text": check_none(i.committer.login)
                    if i.committer is not None else 'None',
                    "@email": check_none(i.committer.email)
                    if i.committer is not None else 'None',
                    "avatar_url": check_none(i.committer.avatar_url)
                    if i.committer is not None else 'None'
                },
            }
        github_commits.append(commit)

    # Unfortunately, it's hard to understand the work on files from GitHub
    # And sometimes the same person uses different names on GitHub and git.
    # So we merge the GitHub log with the git log.

    # Get the files log from cloning the repo
    git_commits = git.git_remote_repo_log(
        repository.clone_url, path, log_type="files")

    # Add GitHub user details from the GitHub log to the git log of files
    # By checking the commit sha
    github_files_log = {}
    for k, each_git_file in enumerate(git_commits):
        # Collect the log of the files from git
        github_files_log[each_git_file] = git_commits[each_git_file]

    # Check with the log from GitHub, and add username details from it
    for k in github_files_log:
        for l, j in enumerate(github_files_log[k]):
            current_sha = github_files_log[k][l]["@node"]
            for g in github_commits:
                if g["@node"] == current_sha:
                    if g["author"]["#text"] != "None":
                        github_files_log[k][l]["author"]["#text"] = g[
                            "author"]["#text"]
                    if g["author"]["@email"] != "None":
                        github_files_log[k][l]["author"]["@email"] = g[
                            "author"]["@email"]
                    if g["author"]["avatar_url"] != "None":
                        github_files_log[k][l]["author"]["avatar_url"] = g[
                            "author"]["avatar_url"]
                    github_files_log[k][l]["author"]["committer"] = "Yes"

    # Update the main graph from the git + GitHub log
    git.git_repo_analysis(github_files_log, graph)
    git.git_repo_analysis(github_files_log, local_graph)

    # Get interactions from comments in commits on GitHub
    github_commits_comments = []
    github_commits_comments_ordered = {}
    for i in repository.get_comments():
        comment = {'@node': i.commit_id,
                   'date': i.created_at,
                   'msg': i.body,
                   'author': {'#text': i.user.login,
                              '@email': i.user.email,
                              'avatar_url': i.user.avatar_url}}
        github_commits_comments.append(comment)
    for i in github_commits_comments:
        if i['@node'] not in github_commits_comments_ordered:
            github_commits_comments_ordered[i['@node']] = []
            # Add the commit to the comments, it is part of the discussion
            commit_index = next((index
                                 for index, d in enumerate(github_commits)
                                 if d['@node'] == i['@node']))
            github_commits_comments_ordered[i['@node']].append(github_commits[
                commit_index])
            github_commits_comments_ordered[i['@node']].append(i)
        else:
            github_commits_comments_ordered[i['@node']].append(i)

    # Analyse each commit and its comments
    for each_commit in github_commits_comments_ordered:
        comments_analysis(
            github_commits_comments_ordered[each_commit],
            graph,
            comment_type="commit comment")
        comments_analysis(
            github_commits_comments_ordered[each_commit],
            local_graph,
            comment_type="commit comment")

    return local_graph


if __name__ == "__main__":
    pass
