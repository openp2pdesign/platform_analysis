# -*- encoding: utf-8 -*-
#
# Social Network Analysis of Discourse discussions
#
# Author: Massimo Menichinelli
# Homepage: http://www.openp2pdesign.org
# License: LGPL v.3
#


import re
import string

from pydiscourse import DiscourseClient
import networkx as nx
import datetime


# Global variables
# Edge counting
edge_key = 0
# The main graph
graph = nx.MultiDiGraph()


def topic_analysis(discussion, graph, comment_type):
    """
    Analyse the discussion of a single Discourse topic (thread of posts).
    Add edges to the graph and return a graph of the specified discussion.
    """

    # Global variable
    global edge_key

    # Local graph variable
    local_graph = nx.MultiDiGraph()

    # Check all the posts in the topic
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
                                    type="mention in a discourse post",
                                    start=f["date"],
                                    endopen=datetime.datetime.now().year)
                                local_graph.add_edge(
                                    f["author"]["#text"], word, key=edge_key,
                                    type="mention in a discourse post",
                                    start=f["date"],
                                    endopen=datetime.datetime.now().year)

    return local_graph


def get_discourse_content(url, api_username, api_key):
    """
    Get the data from a Discourse instance.
    """

    # Connect with the Discourse API
    client = DiscourseClient(url, api_username=api_username, api_key=api_key)

    # Get all the topics
    pagination = True
    paginated_content = []
    page_count = 0

    # Get the data of the paginated topics
    topics_request = client.latest_topics()
    while pagination:
        topics_request = client._get(topics_request["topic_list"][
            "more_topics_url"])
        paginated_content.append(topics_request)
        # Check if there is still pagination or it's the last page
        try:
            value = topics_request["topic_list"]["more_topics_url"]
            pagination = True
            page_count += 1
        except:
            pagination = False

    # Return results
    return paginated_content


def discourse_analysis(url, api_username, api_key):
    """
    Analyse a Discourse instance.
    """

    # Get data
    paginated_content = get_discourse_content(url, api_username, api_key)

    # Local graph variable
    local_graph = nx.MultiDiGraph()

    # Connect with the Discourse API
    client = DiscourseClient(url, api_username=api_username, api_key=api_key)

    # Browse the paginated topics
    topics = []
    for page in paginated_content:
        for key in page:
            if key == "topic_list":
                for topic in page[key]["topics"]:
                    # Get the id, slug and title of each topic
                    topic_id = topic["id"]
                    topic_slug = topic["slug"]
                    topic_title = topic["title"]
                    topic_content = client.posts(topic_id=topic_id)
                    topic_posts = []
                    topics.append(topic_content)
                    # Get the posts of each topic
                    for element in topic_content:
                        if element == "post_stream":
                            for post in topic_content[element]["posts"]:
                                this_post = {
                                    '@node': post["id"],
                                    'date': post["created_at"],
                                    'msg': post["cooked"],
                                    'reply_to_post_number':
                                    post["reply_to_post_number"],
                                    'reply_count': post["reply_count"],
                                    'quote_count': post["quote_count"],
                                    'author':
                                    {'#text': post["username"],
                                     'full_name': post["name"],
                                     'id': post["user_id"],
                                     'avatar_url': post["avatar_template"],
                                     'trust_level': post["trust_level"],
                                     'moderator': post["moderator"],
                                     'admin': post["admin"],
                                     'staff': post["staff"]}
                                }
                                topic_posts.append(this_post)

                    # Analyse each commit and its comments
                    topic_posts_ordered = {}
                    for i in topic_posts:
                        if i['@node'] not in topic_posts_ordered:
                            topic_posts_ordered[i['@node']] = []
                            # Add the commit to the comments, it is part of the discussion
                            topic_posts_index = next(
                                (index for index, d in enumerate(topic_posts)
                                 if d['@node'] == i['@node']))
                            topic_posts_ordered[i['@node']].append(topic_posts[
                                topic_posts_index])
                            topic_posts_ordered[i['@node']].append(i)
                        else:
                            topic_posts_ordered[i['@node']].append(i)
                    for each_post in topic_posts_ordered:
                        topic_analysis(topic_posts_ordered[each_post],
                                       graph,
                                       comment_type="discourse post")
                        topic_analysis(topic_posts_ordered[each_post],
                                       local_graph,
                                       comment_type="discourse post")

        return local_graph


if __name__ == "__main__":
    pass
