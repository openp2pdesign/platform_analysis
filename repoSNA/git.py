# -*- encoding: utf-8 -*-
#
# Social Network Analysis of Git, Hg, SVN, GitHub, BitBucket repositories
#
# Author: Massimo Menichinelli
# Homepage: http://www.openp2pdesign.org
# License: LGPL v.3
#
#

import requests

fablabs_io_api_url = "https://api.fablabs.io/v0/labs.json"


class FabLab(object):

    """Represents a Fab Lab as it is described on fablabs.io."""

    def __init__(self):
        self.address_1 = ""
        self.address_2 = ""
        self.address_notes = ""
        self.avatar = ""
        self.blurb = ""
        self.capabilities = ""
        self.city = ""
        self.country_code = ""
        self.county = ""
        self.description = ""
        self.email = ""
        self.header_image_src = ""
        self.id = ""
        self.kind_name = ""
        self.latitude = ""
        self.longitude = ""
        self.links = ""
        self.name = ""
        self.parent_id = ""
        self.phone = ""
        self.postal_code = ""
        self.slug = ""
        self.url = ""


def data_from_fablabs_io():
    """Gets data from fablabs.io."""

    fablab_list = requests.get(fablabs_io_api_url).json()

    return fablab_list


def get_fablabs():
    """Gets FabLab data from fablabs.io."""

    fablabs_json = data_from_fablabs_io()
    fablabs = {}

    # Load all the FabLabs
    for i in fablabs_json["labs"]:
        current_lab = FabLab()
        current_lab.address_1 = i["address_1"]
        current_lab.address_2 = i["address_2"]
        current_lab.address_notes = i["address_notes"]
        current_lab.avatar = i["avatar"]
        current_lab.blurb = i["blurb"]
        current_lab.capabilities = i["capabilities"]
        current_lab.city = i["city"]
        current_lab.country_code = i["country_code"]
        current_lab.county = i["county"]
        current_lab.description = i["description"]
        current_lab.email = i["email"]
        current_lab.header_image_src = i["header_image_src"]
        current_lab.id = i["id"]
        current_lab.kind_name = i["kind_name"]
        current_lab.latitude = i["latitude"]
        current_lab.longitude = i["longitude"]
        current_lab.links = i["links"]
        current_lab.name = i["name"]
        current_lab.parent_id = i["parent_id"]
        current_lab.phone = i["phone"]
        current_lab.postal_code = i["postal_code"]
        current_lab.slug = i["slug"]
        current_lab.url = i["url"]
        fablabs[i["slug"]] = current_lab

    return fablabs


def get_fablabs_dict():
    """Gets the Fab Labs from fablabs.io as dictionaries instead of FabLab objects."""
    fablab_data = get_fablabs()
    fablabs = {}

    # Load all the FabLabs
    for i in fablab_data:
        fablabs[i] = fablab_data[i].__dict__

    return fablabs


def fablabs_count():
    """Gets the number of current Fab Labs registered on fablabs.io."""

    fablabs = data_from_fablabs_io()

    return len(fablabs["labs"])


if __name__ == "__main__":
    pass
