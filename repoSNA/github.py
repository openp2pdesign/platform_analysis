# -*- encoding: utf-8 -*-
#
# Social Network Analysis of Git, Hg, SVN, GitHub, BitBucket repositories
#
# Author: Massimo Menichinelli
# Homepage: http://www.openp2pdesign.org
# License: LGPL v.3
#

from github import Github
import networkx as nx
import getpass
import os


issue = {}
issue = {0: {"author": "none", "comments": {}}}
commits = {0: {"commit", "sha"}}
repos = {}


def mine_repo():
    # Clear screen
    os.system('cls' if os.name == 'nt' else 'clear')

    # Variables for the whole program

    graph = nx.MultiDiGraph()
    issue = {}
    issue = {0: {"author": "none", "comments": {}}}
    commits = {0: {"commit", "sha"}}
    repos = {}

    print "Social Network Analisys of a GitHub repository"
    print ""
    userlogin = raw_input("Login: Enter your username: ")
    password = getpass.getpass("Login: Enter yor password: ")
    username = raw_input("Enter the username you want to analyse: ")
    print ""
    g = Github(userlogin, password)

    print username, "has", g.get_user(username).public_repos, "repositories."

    print ""

    for repo in g.get_user(username).get_repos():
        print "-", repo.name

    print ""

    repo_to_mine = raw_input(
        "Enter the name of the repository you want to mine: ")
    b = g.get_user(username).get_repo(repo_to_mine)
    analyse_repo(b, graph)

    # Getting rid of the node "None", it was used to catch the errors of users
    # that are NoneType
    if "None" in graph:
        graph.remove_node('None')

    print ""
    print "NODES..."
    print graph.nodes()
    print ""
    print "EDGES..."
    print graph.edges()
    print ""

    print "Converting multiple edges to weighted edges..."
    print ""

    graph2 = nx.DiGraph()

    for j in list(graph.nodes_iter(data=True)):
        # copying all the nodes with their attributes
        if len(j[1]) > 0:
            graph2.add_node(j[0], collaborator=j[1]["collaborator"], contributor=j[1][
                            "contributor"], owner=j[1]["owner"], watcher=j[1]["watcher"])
        else:
            graph2.add_node(j[0])

    for j in list(graph.edges_iter(data=True)):
        subject_id = j[0]
        object_id = j[1]
        if graph.has_edge(subject_id, object_id) and graph2.has_edge(subject_id, object_id):
            graph2[subject_id][object_id]['weight'] += 1
        elif graph.has_edge(subject_id, object_id) and not graph2.has_edge(subject_id, object_id):
            graph2.add_edge(subject_id, object_id, weight=1)

    print "EDGES..."
    print graph2.edges()
    print ""

    print "Saving the network..."
    nx.write_gexf(graph2, username + "_" + repo_to_mine +
                  "_social_interactions_analysis.gexf")
    print "Done. Saved as " + username + "_" + repo_to_mine + "_social_interactions_analysis.gexf"


def analyse_repo(repository, graph):
    print "-----"
    print "DESCRIPTION:", repository.description
    print "-----"
    print "OWNER:", repository.owner.login
    graph.add_node(str(unicode(repository.owner.login)), owner="Yes")
    print "-----"
    print "WATCHERS:", repository.watchers
    print ""
    for i in repository.get_stargazers():
        if i not None:
            print "-", i.login
            if i.login not in graph:
                graph.add_node(str(unicode(i.login)), watcher="Yes")
            else:
                graph.node[i.login]["watcher"] = "Yes"
        else:
            graph.node["None"]["watcher"] = "Yes"
    print "-----"
    print "COLLABORATORS"
    print ""
    for i in repository.get_collaborators():
        if i not None:
            print "-", i.login
            if i.login not in graph:
                graph.add_node(str(unicode(i.login)), collaborator="Yes")
            else:
                graph.node[i.login]["collaborator"] = "Yes"
        else:
            graph.node["None"]["collaborator"] = "Yes"
    print "-----"
    print "HAS ISSUES=", repository.has_issues
    if repository.has_issues is True:
        print "-----"
        print "ISSUES: Open ones"
        print ""
        for i in repository.get_issues(state="open"):
            print "Issue number:", i.number
            if i.user not None:
                print "- Created by", i.user.login
                issue[i.number] = {}
                issue[i.number]["comments"] = {}
                issue[i.number]["author"] = i.user.login
            else:
                print "- Created by None"
                issue[i.number] = {}
                issue[i.number]["comments"] = {}
                issue[i.number]["author"] = "None"
            print "--", i.title
            if i.assignee not None:
                print "-- Assigned to", i.assignee.login
                graph.add_edge(str(i.user.login), str(i.assignee.login))
            else:
                print "-- Assigned to None"
                graph.add_edge(str(i.user.login), "None")
            print "--", i.comments, "comments"
            for j, f in enumerate(i.get_comments()):
                if f.user not None:
                    print "--- With a comment by", f.user.login
                    issue[i.number]["comments"][j] = f.user.login
                else:
                    print "--- With a comment by None"
                    issue[i.number]["comments"][j] = "None"
            print ""

        print "ISSUES: Closed ones"
        print ""
        for i in repository.get_issues(state="closed"):
            print "Issue number:", i.number
            if i.user not None:
                print "- Created by", i.user.login
                issue[i.number] = {}
                issue[i.number]["comments"] = {}
                issue[i.number]["author"] = i.user.login
            else:
                print "- Created by None"
                issue[i.number] = {}
                issue[i.number]["comments"] = {}
                issue[i.number]["author"] = "None"
            print "--", i.title
            if i.assignee not None:
                print "-- Assigned to", i.assignee.login
                graph.add_edge(str(i.user.login), str(i.assignee.login))
            else:
                print "-- Assigned to None"
                graph.add_edge(str(i.user.login), "None")
            print "--", i.comments, "comments"
            for j, f in enumerate(i.get_comments()):
                if f.user not None:
                    print "--- With a comment by", f.user.login
                    issue[i.number]["comments"][j] = f.user.login
                else:
                    print "--- With a comment by None"
                    issue[i.number]["comments"][j] = "None"
            print ""

    print "-----"
    print "CONTRIBUTORS"
    print ""
    for i in repository.get_contributors():
        if i.login not None:
            print "-", i.login
            if i.login not in graph:
                graph.add_node(str(unicode(i.login)), contributor="Yes")
            else:
                graph.node[i.login]["contributor"] = "Yes"
        else:
            graph.node["None"]["contributor"] = "Yes"
    print "-----"
    print "COMMITS"
    print ""

    repos[0] = {0: ""}
    for k, i in enumerate(repository.get_commits()):
        print "-", i.sha
        if i.committer not None:
            print "-- by", i.committer.login
            repos[0][k] = i.committer.login
        else:
            print "-- by None"
            repos[0][k] = "None"
    print "-----"

    # Check the attributes of every node, and add a "No" when it is not
    # present, in order to let Gephi use the attribute for graph partitioning
    for i in graph.nodes():
        if "owner" not in graph.node[i]:
            graph.node[i]["owner"] = "No"
        if "contributor" not in graph.node[i]:
            graph.node[i]["contributor"] = "No"
        if "collaborator" not in graph.node[i]:
            graph.node[i]["collaborator"] = "No"
        if "watcher" not in graph.node[i]:
            graph.node[i]["watcher"] = "No"

    # Add an edge from a commiter to a previous one,
    # i.e. if you are committing after somebody has commited,
    # you are interacting with him/her
    print "ADDING EDGES FROM COMMITS"
    print ""
    for h in repos[0]:
        if h < len(repos[0]) - 1:
            print "-"
            print "Committer:", repos[0][h]
            print "Adding an edge from:", repos[0][h], "to previous committer:", repos[0][h + 1]
            graph.add_edge(str(repos[0][h]), str(repos[0][h + 1]))

    # Creating the edges from the commits and their comments.
    # Each comment interacts with the previous ones,
    # so each user interacts with the previous ones that have been creating
    # the issue or commented it
    print ""
    print "-----"
    print "ADDING EDGES FROM COMMENTS IN COMMITS"
    print ""

    comm = {}

    for k, i in enumerate(repository.get_commits()):
        if i.author not None:
            print "Commit by: ", i.author.login
        comm[k] = {}
        comm[k]["comments"] = {}

        for m, f in enumerate(i.get_comments()):
            print "- Commented by: ", f.user.login
            comm[k]["comments"][m] = f.user.login
            graph.add_edge(str(f.user.login), str(i.author.login))
            print "- Adding an edge from ", f.user.login, "to", i.author.login

            for l in range(m):
                print "- Adding an edge from ", f.user.login, "to", comm[k]["comments"][l]
                graph.add_edge(str(f.user.login), str(comm[k]["comments"][l]))

    print "-----"

    # Creating the edges from the issues and their comments.
    # Each comment interacts with the previous ones,
    # so each user interacts with the previous ones that have been creating
    # the issue or commented it
    print ""
    print "-----"
    print "ADDING EDGES FROM ISSUES COMMENTING"
    print ""

    for a, b in enumerate(issue):
        print "-----"
        print "Issue author:", issue[a]["author"]
        print ""
        for k, j in enumerate(issue[a]["comments"]):
            print "Comment author:", issue[a]["comments"][k]
            print "Adding an edge from:", issue[a]["comments"][k], "to:", issue[a]["author"]
            graph.add_edge(str(issue[a]["comments"][k]),
                           str(issue[a]["author"]))

            for l in range(k):
                print "Adding an edge from:", issue[a]["comments"][k], "to:", issue[a]["comments"][l]
                graph.add_edge(str(issue[a]["comments"][l]), str(
                    issue[a]["comments"][l]))
    print ""

    # print "FORKS"
    # print ""
    # for f,i in enumerate(repository.get_forks()):
    #    print i.name
    #    print "ANALYSING A FORK, number",f
    #    print ""
    #    analyse_repo(i,f+1)
    #    print ""
    # print "-----"

    print "-----"
    print "PULL REQUESTS"
    print ""

    for i in repository.get_pulls():
        print i.id
        if i.assignee not None:
            print "Assignee:", i.assignee.login
            one = i.assignee.login
        else:
            one = "None"
        if i.user not None:
            print "User:", i.user.login
            two = i.user.login
        else:
            two = "None"

        print "Adding an edge from:", one, "to:", two
        graph.add_edge(str(one), str(two))

        # We should look at the comments on the pull request, but a pull request is automatically translated
        # as an issue, so we are already looking at the issue comments

    print "-----"

    return


if __name__ == "__main__":
    pass
