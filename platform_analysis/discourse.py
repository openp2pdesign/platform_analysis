# -*- encoding: utf-8 -*-
#
# Social Network Analysis of Discourse discussions
#
# Author: Massimo Menichinelli
# Homepage: http://www.openp2pdesign.org
# License: LGPL v.3
#


import re
from pydiscourse import DiscourseClient
import networkx as nx
import datetime
from time import sleep


def discourse_topic_discussion_analysis(discussion):
    """
    Analyse the discussion of a single Discourse topic (thread of posts).
    Add edges to the graph and return a graph of the specified discussion.
    """

    # Local graph variable
    local_graph = nx.MultiDiGraph()

    # Check all the posts in the topic
    for j, f in enumerate(discussion):
        # Add an edge when the reply was specific to a post
        if f["reply_to_post_number"] is not None:
            # Find the author of the post replid by post number
            for t in discussion:
                if t["post_number"] == f["reply_to_post_number"]:
                    local_graph.add_edge(
                        f["author"]["#text"], t["author"]["#text"],
                        type="Direct reply to post in a Discourse topic",
                        slug=f["slug"],
                        title=f["title"],
                        category=f["category"],
                        post_number=f["post_number"],
                        reply_to_post_number=f["reply_to_post_number"],
                        node=f["@node"],
                        msg=f["msg"],
                        start=f["date"],
                        endopen=datetime.datetime.now().year)

        # Check if there are any username mentions in the body of each
        # comment, and add an edge if there are any
        message_body = f["msg"]
        message_mention = 'a class="mention" href="/u/'
        for m in re.finditer(message_mention, message_body):
            start_of_mention = message_body.find('">', m.end())+len('">')
            end_of_mention = message_body.find('<', start_of_mention)
            user_mentioned = message_body[start_of_mention:end_of_mention].replace("@","")
            local_graph.add_edge(
                f["author"]["#text"], user_mentioned,
                type="Mention in a Discourse post",
                slug=f["slug"],
                title=f["title"],
                category=f["category"],
                post_number=f["post_number"],
                node=f["@node"],
                start=f["date"],
                msg=f["msg"],
                endopen=datetime.datetime.now().year)

        # Add an edge to all the previous participants in the discussion
        for k in discussion[:j]:
            local_graph.add_edge(
                f["author"]["#text"], k["author"]["#text"],
                type="Joining the discussion with previous posts in a Discourse topic",
                slug=f["slug"],
                title=f["title"],
                category=f["category"],
                post_number=f["post_number"],
                node=f["@node"],
                msg=f["msg"],
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

    categories_data = client.categories()
    categories = {}

    for category in categories_data:
        categories[category[u"id"]] = {"id": category[u"id"], "name": category[u"name"], "slug": category[u"slug"], "description": category[u"description_text"], "topic_count": category[u"topic_count"], "post_count": category[u"post_count"], "url": category[u"topic_url"]}

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
    requests_count = 0
    for page in paginated_content:
        for key in page:
            if key == "topic_list":
                for topic in page[key]["topics"]:
                    # Get the id, slug and title of each topic
                    topic_id = topic["id"]
                    topic_slug = topic["slug"]
                    topic_title = topic["title"]
                    topic_category = topic["category_id"]
                    # Get the data of each topic
                    # But first check the API limit and wait if necessary
                    if requests_count > 50:
                        requests_count = 0
                        sleep(10)
                    topic_content = client.posts(topic_id=topic_id)
                    requests_count += 1
                    topics.append(topic_content)
                    topic_posts = []
                    # Get the posts of each topic
                    for element in topic_content:
                        if element == "post_stream":
                            for post in topic_content[element]["posts"]:
                                this_post = {
                                    '@node': post["id"],
                                    'date': post["created_at"],
                                    'msg': post["cooked"],
                                    'slug': topic_slug,
                                    'title': topic_title,
                                    'category': topic_category,
                                    'post_number': post["post_number"],
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
                                # Add user as a node
                                username = str(this_post["author"]["#text"])
                                local_graph.add_node(username)
                                local_graph.node[username]["#text"] = post["username"]
                                local_graph.node[username]["full_name"] = post["name"]
                                local_graph.node[username]["id"] = post["user_id"]
                                local_graph.node[username]["trust_level"] = post["trust_level"]
                                local_graph.node[username]["moderator"] = post["moderator"]
                                local_graph.node[username]["admin"] = post["admin"]
                                local_graph.node[username]["staff"] = post["staff"]
                                # Avatar url
                                if url[-1] == "/":
                                    avatar_url = url[:-1]
                                else:
                                    avatar_url = url
                                avatar_url = avatar_url + post["avatar_template"].replace('{size}', '90')
                                local_graph.node[username]["avatar_url"] = avatar_url

                    # Analyze each topic and its comments
                    # Order the posts
                    topic_posts_ordered = {}
                    for i in topic_posts:
                        if i['@node'] not in topic_posts_ordered:
                            topic_posts_ordered[i['@node']] = []
                            # Add the commit to the comments, it is part of the discussion
                            topic_posts_index = next(
                                (index for index, d in enumerate(topic_posts)
                                 if d['@node'] == i['@node']))
                            topic_posts_ordered[i['@node']].append(topic_posts[topic_posts_index])
                            topic_posts_ordered[i['@node']].append(i)
                        else:
                            topic_posts_ordered[i['@node']].append(i)

                    # Analyse the posts
                    new_graph = discourse_topic_discussion_analysis(topic_posts)
                    # Join the graphs
                    final_graph = nx.compose(new_graph, local_graph)

                    # Add missing user information
                    for username, data in final_graph.nodes(data=True):
                        if len(data) == 0:
                            user_data = client.user(username=username)
                            final_graph.node[username]["#text"] = username
                            final_graph.node[username]["full_name"] = user_data["name"]
                            final_graph.node[username]["id"] = user_data["id"]
                            final_graph.node[username]["trust_level"] = user_data["trust_level"]
                            final_graph.node[username]["moderator"] = user_data["moderator"]
                            final_graph.node[username]["admin"] = user_data["admin"]
                            # Check if the user is in the staff group
                            is_staff = False
                            for group in user_data["groups"]:
                                if group["display_name"] == "staff":
                                    is_staff = True
                            final_graph.node[username]["staff"] = is_staff
                            # Avatar url
                            if url[-1] == "/":
                                avatar_url = url[:-1]
                            else:
                                avatar_url = url
                            avatar_url = avatar_url + user_data["avatar_template"].replace('{size}', '90')
                            final_graph.node[username]["avatar_url"] = avatar_url


    return final_graph


if __name__ == "__main__":
    pass
