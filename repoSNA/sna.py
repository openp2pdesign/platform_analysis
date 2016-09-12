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

    nx.write_graphml(graph, filename)

    return


def graph_to_pandas_time_series(graph):
    """
    Transform a graph into a pandas time series dataframe.
    """

    time_dataframe = nx.to_pandas_dataframe(graph)

    return


if __name__ == "__main__":
    pass
