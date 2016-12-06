# -*- encoding: utf-8 -*-
#
# Social Network Analysis of Git, Hg, SVN, GitHub, BitBucket repositories
#
# Author: Massimo Menichinelli
# Homepage: http://www.openp2pdesign.org
# License: LGPL v.3
#


import networkx as nx
import datetime
import pandas as pd
import seaborn as sns


def save_graph(graph, filename, self_loops):
    """
    Transform date on a graph to string and save as a graphml file
    """

    for u, v, key, attr in graph.edges(data=True, keys=True):
        if type(attr["start"]) is datetime.datetime:
            attr["start"] = attr["start"].strftime('%Y/%m/%d-%H:%M:%S')
        attr["endopen"] = str(attr["endopen"])

    if self_loops is False:
        self_loops_edges = graph.selfloop_edges(keys=True, data=True)
        graph.remove_edges_from(self_loops_edges)
    else:
        pass

    nx.write_graphml(graph, filename)

    return


def graph_to_pandas_time_series(graph):
    """
    Transform a graph into a pandas time series DataFrame.
    """

    # Empty DataFrame of actions
    time_dataframe = pd.DataFrame(columns=[
        '0',
        '1',
        'node',
        'msg',
        'type',
        'endopen',
        'start',
        'value'
        ])

    # Iterate over edges to create a DataFrame of actions
    for i in graph.edges_iter(data=True):
        if "node" in i[2]:
            node = i[2]["node"]
        else:
            node = "None"
        if "msg" in i[2]:
            msg = i[2]["msg"]
        else:
            msg = "None"
        # Create a new row
        new_row = [
            i[0],
            i[1],
            node,
            msg,
            i[2]["type"],
            i[2]["endopen"],
            i[2]["start"],
            1
            ]
        # Add the new row to the DataFrame of actions
        time_dataframe.loc[len(time_dataframe)] = new_row

        # Convert column strings to datetimes
        time_dataframe['start'] = pd.to_datetime(time_dataframe['start'])
        time_dataframe['endopen'] = pd.to_datetime(time_dataframe['endopen'])

    return time_dataframe


def time_analysis(data, focus, interaction):
    """
    Analyse a pandas time series DataFrame.
    Returns a DataFrame for global status, a dictionary of DataFrames for users stats.

    Plot it with: data.resample('M').sum().plot(kind="bar", figsize=(20,6))
    """

    # Define the DataFrame index as time-based
    data.index = data['start']
    # List of types of interaction
    types = data["type"].value_counts()

    # Users stats
    # Empty dictionary of DataFrames (one for each user)
    users_stats = {}
    # Users maybe starting (0) or receiving (1) the interaction
    # Create a list of users
    if interaction == 0:
        users = data["0"].value_counts()
    elif interaction == 1:
        users = data["1"].value_counts()
    else:
        users = data["0"].value_counts()
    # Add empty DataFrame for each active user
    for i in users.index:
        users_stats[i] = pd.DataFrame(columns=list(types.index))
    # Fill each Dataframe of active users with zeroes, as the default value
    for i in df.iterrows():
        users_stats[i[1]["0"]].loc[i[1]["start"]] = [0] * len(list(type_stats.index))
    # Add a 1 to each timed interaction
    for i in df.iterrows():
        users_stats[i[1]["0"]].ix[i[1]["start"], i[1]["type"]] = 1

    # Global stats
    data_list = []
    for i in users_stats:
        data_list.append(users_stats[i])
    global_stats = pd.concat(data_list)

    # Final output
    if focus.lowercase() == "global":
        return global_stats
    elif focus.lowercase() == "user":
        return users_stats
    else:
        return global_stats


def type_stats(data, focus):
    """
    Return a DataFrame or a dict of DataFrames for global type stats.
    Helper function for speeding up analysis.
    """

    if focus.lowercase() == "global":
        return data.sum(axis=0)
    elif focus.lowercase() == "user":
        users_stats = {}
        for i in data:
            users_stats[i] = data[i].sum(axis=0)
    else:
        return data.sum(axis=0)


if __name__ == "__main__":
    pass
