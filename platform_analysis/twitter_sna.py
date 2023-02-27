# -*- encoding: utf-8 -*-
#
# Social Network Analysis of Twitter connections (Ego Networks)
#
# Author: Massimo Menichinelli
# Homepage: http://www.openp2pdesign.org
# License: LGPL v.3
#


import twitter
import networkx as nx
from time import sleep
import sys
import os
import unicodedata
import pandas as pd
import json
from ratelimit import limits, sleep_and_retry

# Global variables
errors = 0
protected_accounts = 0
t = "" # Twitter connection

@sleep_and_retry
@limits(calls=900, period=900)
def twitter_accounts_connections(accounts_list, option):
    """
    Get followers or friends of a list of Twitter accounts.

    :param accounts_list: List of Twitter accounts to be looked up
    :param option: Either "followers" or "friends", chooses which kind of interaction to analyze
    :return: returns a dict of connections for each Twitter account
    """

    global errors
    global protected_accounts
    global t
    connections = {}

    for p in accounts_list:
        query = {}
        counting = 0
        cursor = -1
        connections[p] = []

        while cursor != "0":
            # API: https://dev.twitter.com/docs/api/1.1/get/friends/ids
            try:
                if option == "followers":
                    query = t.followers.ids(
                        user_id=p, count=5000, cursor=cursor)
                else:
                    query = t.friends.ids(
                        user_id=p, count=5000, cursor=cursor)
                cursor = query["next_cursor_str"]
                for idtocheck1 in query["ids"]:
                    connections[p].append(idtocheck1)
            except Exception as e:
                if "Rate limit exceeded" in str(e):
                    notworking = False
                    for k in range(1, 60 * 15):
                        remaining = 60 * 15 - k
                        sleep(1)
                    if option == "followers":
                        try:
                            query = t.followers.ids(
                                user_id=p, count=5000, cursor=cursor)
                        except:
                            cursor = "0"
                            errors += 1
                            notworking = True
                    else:
                        try:
                            query = t.friends.ids(
                                user_id=p, count=5000, cursor=cursor)
                        except:
                            cursor = "0"
                            errors += 1
                            notworking = True

                    if notworking is False:
                        cursor = query["next_cursor_str"]
                        for idtocheck2 in query["ids"]:
                            connections[p].append(idtocheck2)
                elif "Not authorized" in str(e):
                    # Unauthorized account
                    cursor = "0"
                    errors += 1
                    protected_accounts += 1
                else:
                    # Some generic errors 
                    cursor = "0"
                    errors += 1

    return connections


@sleep_and_retry
@limits(calls=900, period=900)
def twitter_accounts_graph(ACCESS_TOKEN, ACCESS_TOKEN_SECRET, API_KEY, API_KEY_SECRET, first_perspective_accounts, second_perspective_accounts, keywords):
    """
    Create a graph of connections among Twitter accounts focusing on first-person, second-person, third-person perspective in the social network. Get the Twitter API credentials from https://developer.twitter.com/.

    :param ACCESS_TOKEN: Twitter API access token
    :param ACCESS_TOKEN_SECRET: Twitter API access token secret
    :param API_KEY: Twitter API api key
    :param API_KEY_SECRET: Twitter API api key secret
    :param first_perspective_accounts: List of Twitter accounts of first person perspective
    :param second_perspective_accounts: List of Twitter accounts of second person perspective
    :param keywords: List of keywords for searching for Twitter accounts - this is the third person perspective
    :return: returns a dict with a graph of connections among Twitter accounts and overall statics of the results of the search
    """

    global t
    graph = nx.DiGraph()

    # Log in
    # TODO Move to API v2 when they will port user search
    t = twitter.Twitter(auth=twitter.OAuth(ACCESS_TOKEN, ACCESS_TOKEN_SECRET,
                      API_KEY, API_KEY_SECRET), api_version="1.1")
    # Result variables
    search_results = []
    search_results_stats = {}
    accounts = []
    accounts_data = {}

    # Search (directly) for first_perspective_accountss account
    search_results_word = []
    for user in first_perspective_accounts:
        try:
            search = t.users.lookup(screen_name=user)
            search_results.append(search[0])
            accounts_data[search[0]["id"]] = search[0]
            search_results_word.append(search[0])
        except:
            pass
    search_results_stats["first_perspective_accounts"] = search_results_word
    # Search (directly) for second_perspective_accounts accounts
    search_results_word = []
    for user in second_perspective_accounts:
        try:
            search = t.users.lookup(screen_name=user)
            search_results.append(search[0])
            accounts_data[search[0]["id"]] = search[0]
            search_results_word.append(search[0])
        except:
            pass
    search_results_stats["second_perspective_accounts"] = search_results_word
    # Search (indirectly) accounts by keywords
    for word in keywords:
        search_results_word = []
        # Pagination issue https://twittercommunity.com/t/odd-pagination-behavior-with-get-users-search/148502
        # Only the first 1,000 matching results are available for API v1.1.
        # https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-users-search
        for i in range(50):
            try:
                search = t.users.search(q=word, page=i, count=20)
                for k in search:
                    search_results.append(k)
                    search_results_word.append(k)
            except Exception as e:
                break
        # Remove duplicates
        cleaned_search_results_word = []
        for item in search_results_word:
            if item not in cleaned_search_results_word:
                cleaned_search_results_word.append(item)
        search_results_stats[word] = cleaned_search_results_word
    # Remove duplicates
    cleaned_search_results = []
    for item in search_results:
        if item not in cleaned_search_results:
            cleaned_search_results.append(item)
    search_results = cleaned_search_results
    # Create dict of accounts
    for result in search_results:
        accounts_data[result["id"]] = result
        accounts.append(result["id"])
    # Remove duplicates in dict of accounts, if any
    accounts = list(dict.fromkeys(accounts))

    # Load connections of account
    for k, l in enumerate(accounts):
        followers = twitter_accounts_connections([l], "followers")
        friends = twitter_accounts_connections([l], "friends")
        # Add edges...
        for f in followers:
            for k in followers[f]:
                graph.add_edge(k, f)
        for o in friends:
            for p in friends[o]:
                graph.add_edge(o, p)

    # Clean from nodes who are not accounts, in order to get a 1.5 level network
    nodes_to_remove = []
    for v in graph.nodes(data=True):
        if v[0] not in accounts:
            nodes_to_remove.append(v[0])
        else:
            for j in accounts_data[v[0]]:
                try:
                    if accounts_data[v[0]][j] == None:
                        graph.nodes[v[0]][j] = "None"
                    else:
                        graph.nodes[v[0]][j] = accounts_data[v[0]][j]
                except:
                    pass
    graph.remove_nodes_from(nodes_to_remove)

    # Associate accounts to search keywords
    for key in keywords:
        keyword_accounts = []
        for x in search_results_stats[key]:
            keyword_accounts.append(x["screen_name"])
        for v in graph.nodes(data=True):
            if graph.nodes[v[0]]['screen_name'] in keyword_accounts:
                graph.nodes[v[0]]['keyword_' + key] = True
            else:
                graph.nodes[v[0]]['keyword_' + key] = False

    # Adding the first_perspective_accounts attribute
    for v in graph.nodes(data=True):
        if graph.nodes[v[0]]['screen_name'] in first_perspective_accounts:
            graph.nodes[v[0]]['first_perspective_accounts'] = True
            graph.nodes[v[0]]['second_perspective_accounts'] = False
        else:
            graph.nodes[v[0]]['first_perspective_accounts'] = False
    # Adding the second_perspective_accounts attribute
    for v in graph.nodes(data=True):
        if graph.nodes[v[0]]['screen_name'] in second_perspective_accounts:
            graph.nodes[v[0]]['second_perspective_accounts'] = True
        else:
            graph.nodes[v[0]]['second_perspective_accounts'] = False
    # Adding the general first_perspective_accounts, second_perspective_accounts, community (1-2-3 person perspectives) attribute
    for v in graph.nodes(data=True):
        graph.nodes[v[0]]['perspective'] = "third-person"
    for v in graph.nodes(data=True):
        if graph.nodes[v[0]]['screen_name'] in second_perspective_accounts:
            graph.nodes[v[0]]['perspective'] = "second-person"
        if graph.nodes[v[0]]['screen_name'] in first_perspective_accounts:
            graph.nodes[v[0]]['perspective'] = "first-person"

    # Save the graph, only accounts of the chosen lists and the connections
    # among them

    # TODO Save full stats for each keyword

    returning_results = {"stats": search_results_stats, "errors": errors,
                         "protected_accounts": protected_accounts, "graph": graph}

    return returning_results


if __name__ == "__main__":
    pass