# -*- encoding: utf-8 -*-
#
# Social Network Analysis of Git, Hg, SVN, GitHub, BitBucket repositories
#
# Author: Massimo Menichinelli
# Homepage: http://www.openp2pdesign.org
# License: LGPL v.3
#

import subprocess
import xmltodict


# Get the information of a svn repository into a dict
def get_log(projectpath):

    # Get the verbose log in xml
    svnlog = subprocess.check_output(
        ['svn log --xml -v'],
        cwd=projectpath, shell=True)

    # Convert to a dict
    all_commits = xmltodict.parse(svnlog)

    # Return the full log with files changed at each commit
    return all_commits


if __name__ == "__main__":
    pass
