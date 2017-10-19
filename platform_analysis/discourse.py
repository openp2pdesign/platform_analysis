# -*- encoding: utf-8 -*-
#
# Social Network Analysis of Discourse discussions
#
# Author: Massimo Menichinelli
# Homepage: http://www.openp2pdesign.org
# License: LGPL v.3
#

from pydiscourse import DiscourseClient

import networkx as nx
import datetime


def discourse_analysis(url, api_username, api_key):
    """
    Get the data from a Discourse instance.
    """

    client = DiscourseClient(url, api_username=api_username, api_key=api_key)

    # Get categories
    categories = client.categories()

    # Get all the topics
    pagination = True
    paginated_content = []
    page_count = 0
    topics = []
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

    # Browse the paginated topics
    for page in paginated_content:
        for key in page:
            if key == "topic_list":
                for topic in page[key]["topics"]:
                    # Get the id of each topic
                    topic_id = topic["id"]
                    topic_content = client.posts(topic_id=topic_id)
                    topics.append(topic_content)
                    for element in topic_content:
                        if element == "post_stream":
                            for post in topic_content[element]["posts"]:
                                print post
                    exit()


if __name__ == "__main__":
    pass
