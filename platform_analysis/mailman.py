# -*- encoding: utf-8 -*-
#
# Social Network Analysis of Mailman discussions
#
# Author: Massimo Menichinelli
# Homepage: http://www.openp2pdesign.org
# License: LGPL v.3
#


import networkx as nx
import datetime
import email
from email.utils import getaddresses, parseaddr, parsedate_tz, mktime_tz
# from email.Parser import Parser as EmailParser
import mailbox
import sys
import urllib
import os
import uuid

# TODO Update with https://networkx.org/documentation/stable/auto_examples/drawing/plot_unix_email.html?highlight=mbox

def mailman_analysis(url, list_name, username, password):
    """
    Analyse the discussion of a Mailman discussion list. Download and parse an .mbox from a Mailman archive with:

    http://www.example.com/mailman/private/LIST.mbox/LIST.mbox?username=U&password=P

    This function is based on the NetworkX example plot_unix_email available at: https://github.com/networkx/networkx/blob/master/examples/drawing/plot_unix_email.py

    The plot_unix_email example is released under a 3-clause BSD:
    Author: Aric Hagberg (hagberg@lanl.gov)

    Copyright (C) 2005-2017 by
    Aric Hagberg <hagberg@lanl.gov>
    Dan Schult <dschult@colgate.edu>
    Pieter Swart <swart@lanl.gov>
    All rights reserved.
    BSD license.
    """

    # Buil the full url for downloading the .mbox file
    if url[-1] != "/":
        url = url + "/"
    full_url = url + "mailman/private/" + list_name + ".mbox/"+list_name+".mbox?username="+username+"&password="+password

    # Download the .mbox file with a random filename
    filename = "/tmp/"+uuid.uuid4().hex  +".mbox"
    urllib.urlretrieve(full_url, filename)

    # Open the file
    try:
        fh = open(filename, 'rb')
    except IOError:
        print(".mbox file not found")
        raise

    mbox = mailbox.UnixMailbox(fh, email.message_from_file)  # parse unix mailbox

    G = nx.MultiDiGraph()  # create empty graph

    # parse each messages and build graph
    for msg in mbox:  # msg is python email.Message.Message object
        (source_name, source_addr) = parseaddr(msg['From'])  # sender
        # get all recipients
        # see https://docs.python.org/2/library/email.html
        tos = msg.get_all('to', [])
        ccs = msg.get_all('cc', [])
        resent_tos = msg.get_all('resent-to', [])
        resent_ccs = msg.get_all('resent-cc', [])
        all_recipients = getaddresses(tos + ccs + resent_tos + resent_ccs)

        # Get the date of the message
        parsed_date = parsedate_tz(msg.get('Date'))
        timestamp = mktime_tz(parsed_date)
        date = datetime.datetime.fromtimestamp(timestamp)

        # now add the edges for this mail message
        for (target_name, target_addr) in all_recipients:
            G.add_edge(source_addr, target_addr, message=msg)

    # Delete file
    os.remove(filename)

    # Return the graph
    return G


if __name__ == "__main__":
    pass
