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
        self_loops_edges = graph.selfloop_edges(keys=True, data=True)
        graph.remove_edges_from(self_loops_edges)
    else:
        pass

    nx.write_graphml(graph, filename)

    return


def graph_to_pandas_time_series(graph):
    """
    Transform a graph into a pandas time series dataframe.
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
    for i in time_dataframe.edges_iter(data=True):
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


if __name__ == "__main__":
    pass
