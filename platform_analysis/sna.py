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


def save_graph(graph, filename, self_loops):
    """
    Transform date on a graph to string and save as a graphml file
    """

    for u, v, key, attr in graph.edges(data=True, keys=True):
        if type(attr["start"]) is datetime.datetime:
            attr["start"] = attr["start"].strftime('%Y/%m/%d-%H:%M:%S')
        attr["endopen"] = str(attr["endopen"])

    if self_loops is False:
        self_loops_edges = nx.selfloop_edges(graph, keys=True, data=True)
        graph.remove_edges_from(list(self_loops_edges))
    else:
        pass

    nx.write_graphml(graph, filename)

    return


def graph_to_pandas_time_series(graph):
    """
    Transform a graph into a pandas time series DataFrame.
    """

    # List of rows
    rows_list = []

    # Empty DataFrame of interactions
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

    # Iterate over edges to create a DataFrame of interactions
    for u, v, d in graph.edges(data=True):
        if "node" in d:
            node = d["node"]
        else:
            node = "None"
        if "msg" in d:
            msg = d["msg"]
        else:
            msg = "None"
        # Create a new row
        new_row = [
            u,
            v,
            node,
            msg,
            d["type"],
            d["endopen"],
            d["start"],
            1
            ]
        # Add the new row to the DataFrame of interactions
        #time_dataframe.loc[len(time_dataframe)] = new_row
        row_df = pd.DataFrame([new_row])
        rows_list.append(row_df)

    # Convert list to full dataframe
    time_dataframe = pd.concat(rows_list, axis=0)
    time_dataframe.rename(columns={0: "0", 1: "1", 2: 'node', 3: 'msg',
                      4: 'type', 5: 'endopen', 6: 'start',
                      7: 'value'}, inplace=True)

    # Convert column strings to datetimes
    time_dataframe['start'] = pd.to_datetime(time_dataframe['start'])
    time_dataframe['endopen'] = pd.to_datetime(time_dataframe['endopen'])

    return time_dataframe


def time_analysis(data, focus, interaction, structure):
    """
    Analyse a pandas time series DataFrame.
    Returns a time-series DataFrame. If structure == "combined".
    Returns a Series with all the interactions merged.
    """

    # Define the DataFrame index as time-based
    data.index = data['start']
    # List of types of interaction
    interaction_types = data["type"].value_counts()

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
        users_stats[i] = pd.DataFrame(columns=list(interaction_types.index))
    # Fill each Dataframe of active users with zeroes, as the default value
    for i in data.iterrows():
        users_stats[i[1]["0"]].loc[i[1]["start"]] = [0] * len(list(interaction_types.index))
    # Add a 1 to each timed interaction
    for i in data.iterrows():
        users_stats[i[1]["0"]].loc[i[1]["start"], i[1]["type"]] = 1

    # Global stats
    data_list = []
    index_list = []
    for i in users_stats:
        users_stats[i].index = pd.to_datetime(users_stats[i].index)
        data_list.append(users_stats[i])
        index_list.append(i)
    global_stats = pd.concat(data_list)
    global_stats.index = pd.to_datetime(global_stats.index)

    # Merge interactions if required by the user
    if structure.lower() == "combined":
        global_stats = global_stats.sum(axis=1)
        for i in users_stats:
            users_stats[i] = users_stats[i].sum(axis=1)

    # Transform users_stats into a multi index DataFrame
    users_stats = pd.concat(data_list, keys=index_list)
    users_stats.index.names = ['users', 'time']

    # Final output
    if focus.lower() == "global":
        return global_stats
    elif focus.lower() == "user":
        return users_stats
    else:
        return global_stats


def type_stats(data, focus):
    """
    Return a DataFrame or a dict of DataFrames for global type stats.
    Helper function for speeding up analysis.
    """

    if focus.lower() == "global":
        return data.sum(axis=0)
    elif focus.lower() == "user":
        users_stats = {}
        for i in data:
            users_stats[i] = data[i].sum(axis=0)
    else:
        return data.sum(axis=0)


if __name__ == "__main__":
    pass
