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
    g = Github(userlogin, password)

    results = {}

    # Load the repositories of the username
    for k, repo in enumerate(g.get_user(username).get_repos()):
        results[k] = {"name": repo.name, "data": repo}

    return results


def github_analysis(repository, username, userlogin, password, path):
    """
    Analyse a specific repository.
    """

    # Log in to GitHub
    g = Github(userlogin, password)
    starting_repository_object = g.get_user(username).get_repo(repository)

    repo_analysis(repository=starting_repository_object, path=path)

    # Then we analyse forks of the starting repo
    # for f, i in enumerate(b.get_forks()):
    #     testing = i.__dict__
    #     print(testing["_rawData"]["full_name"])
    #     print(testing["_rawData"]["name"])
    #     print(testing["_rawData"]["clone_url"])
    #     print(testing["_rawData"]["owner"]["avatar_url"])
    #     print(testing["_rawData"]["owner"]["login"])
    #     print("...")

    # TODO do repo_analysis( for each fork, checking the starting point
    # TODO every pull request is an issue

    # Get rid of the node "None", it was used to catch the errors of users
    # that are NoneType
    if "None" in graph:
        graph.remove_node('None')

    # TODO Get rid of self-loops

    # Converting multiple edges to weighted edges
    graph2 = nx.DiGraph()
    for j in list(graph.nodes_iter(data=True)):
        # Copying all the nodes with their attributes
        if len(j[1]) > 0:
            graph2.add_node(
                j[0],
                collaborator=j[1]["collaborator"],
                contributor=j[1]["contributor"], owner=j[1]["owner"],
                watcher=j[1]["watcher"])
        else:
            graph2.add_node(j[0])
    for j in list(graph.edges_iter(data=True)):
        subject_id = j[0]
        object_id = j[1]
        if (graph.has_edge(subject_id, object_id) and
                graph2.has_edge(subject_id, object_id)):
            graph2[subject_id][object_id]['weight'] += 1
        elif (graph.has_edge(subject_id, object_id) and
              not graph2.has_edge(subject_id, object_id)):
            graph2.add_edge(subject_id, object_id, weight=1)
    # Return the resulting weighted graph
    return graph2


def issue_analysis(issue, graph):
    """
    Analyse the discussion of a single issue.
    """

    # Local graph variable
    local_graph = nx.MultiDiGraph()

    if issue.user is not None:
        # Issue creator
        get_users(element=issue.user, user_type="issue creator", graph=graph)

    # Issue assignee
    if issue.assignee is not None:
        get_users(
            element=issue.assignee, user_type="issue assignee", graph=graph)
        graph.add_edge(issue.user.login, issue.assignee.login)
        local_graph.add_edge(issue.user.login, issue.assignee.login)
    else:
        # No assignee
        graph.add_edge(issue.user.login, "None")
        local_graph.add_edge(issue.user.login, "None")

    # Check the comments in the issue
    issues_comments = []
    for j, f in enumerate(issue.get_comments()):
        comment = {'@node': f.id,
                   'date': f.created_at,
                   'msg': f.body,
                   'author': {'#text': f.user.login,
                              '@email': f.user.email,
                              'avatar_url': f.user.avatar_url}}
        get_users(element=f.user, user_type="issue commenter", graph=graph)
        issues_comments.append(comment)

    comments_analysis(issues_comments, local_graph)

    return local_graph


def comments_analysis(discussion, graph):
    """
    Analyse the discussion of a GitHub discussion.
    Add edges to the graph and return a graph of the specified discussion.
    """

    # Local graph variable
    local_graph = nx.MultiDiGraph()

    # Check all the comments in the commit
    for j, f in enumerate(discussion):

        # Add an edge to all the previous participants in the discussion
        for k in discussion[:j]:
            graph.add_edge(
                f["author"]["#text"], k["author"]["#text"], node=f["@node"],
                date=f["date"], msg=f["msg"])

            local_graph.add_edge(
                f["author"]["#text"], k["author"]["#text"], node=f["@node"],
                date=f["date"], msg=f["msg"])

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
                                graph.add_edge(f["author"]["#text"], word)
                                local_graph.add_edge(f["author"]["#text"],
                                                     word)

    return local_graph


def get_users(element, user_type, graph):
    """
    Get users of a specific type from the GitHub repo.
    """

    if element is not None:
        if element.login not in graph:
            graph.add_node(element.login)
            graph.node[element.login][user_type] = "Yes"
            graph.node[element.login]["email"] = element.email
            graph.node[element.login]["avatar_url"] = element.avatar_url
        else:
            graph.node[element.login][user_type] = "Yes"
    else:
        graph.node["None"][user_type] = "No"


def repo_analysis(repository, path):
    """
    Analyse a specific GitHub repo.
    """

    # The main graph
    graph = nx.MultiDiGraph()

    # Add the repo owner to the graph
    get_users(element=repository.owner, user_type="owner", graph=graph)

    # Add the repo watchers to the graph
    for i in repository.get_stargazers():
        get_users(element=i, user_type="stargazers", graph=graph)

    # Add the repo collaborators to the graph
    for i in repository.get_collaborators():
        get_users(element=i, user_type="collaborators", graph=graph)

    # Add the repo contributors to the graph
    for i in repository.get_contributors():
        get_users(element=i, user_type="contributors", graph=graph)

    # Add the repo watchers to the graph
    for i in repository.get_watchers():
        get_users(element=i, user_type="watchers", graph=graph)

    # Add the repo subscribers to the graph
    for i in repository.get_subscribers():
        get_users(element=i, user_type="subscribers", graph=graph)

    # Check the attributes of every node, and add a "No" when it is not
    # present. With this you can, for example, use the attribute for graph
    # partitioning in Gephi
    for i in graph.nodes():
        if "owner" not in graph.node[i]:
            graph.node[i]["owner"] = "No"
        if "contributor" not in graph.node[i]:
            graph.node[i]["contributor"] = "No"
        if "collaborator" not in graph.node[i]:
            graph.node[i]["collaborator"] = "No"
        if "watcher" not in graph.node[i]:
            graph.node[i]["watcher"] = "No"

    # Analyse issues of the repo
    if repository.has_issues is True:
        # Check the open issues
        for i in repository.get_issues(state="open"):
            issue_analysis(i, graph)
        # Check the closed issues
        for i in repository.get_issues(state="closed"):
            issue_analysis(i, graph)

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
        github_files_log[each_git_file] = git_commits[each_git_file]

    # Update the main graph from the git + GitHub log
    git.git_repo_analysis(github_files_log, graph)

    # Get interactions from comments in commits on GitHub
    git.git_repo_analysis(github_files_log, graph)
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

    # Analyse each commit
    for each_commit in github_commits_comments_ordered:
        comments_analysis(github_commits_comments_ordered[each_commit], graph)

    exit()
    # Debug
    for v in graph.nodes_iter(data=True):
        print '..........'
        print v

    nx.write_gexf(graph, 'test.gexf')
    exit()

    print "-----"
    print "PULL REQUESTS"
    print ""

    for i in repository.get_pulls():
        print i.id
        if i.assignee is not None:
            print "Assignee:", i.assignee.login
            one = i.assignee.login
        else:
            one = "None"
        if i.user is not None:
            print "User:", i.user.login
            two = i.user.login
        else:
            two = "None"

        print "Adding an edge from:", one, "to:", two
        graph.add_edge(str(one), str(two))

        # TODO We should look at the comments on the pull request, but a pull request is automatically translated
        # as an issue, so we are already looking at the issue comments

        # TODO FORKS. make an option to recursively analyse forks with this script and with git.py, but by removing the already existing work done
        # for example: if repository.fork is True...
        # from the main repo: get_forks() (paginated list)
        # We can get the starting point with "created_at": "2016-07-23T05:22:58Z",

    return graph


if __name__ == "__main__":
    pass
