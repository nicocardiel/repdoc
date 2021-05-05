#
# Copyright 2019-2021 Universidad Complutense de Madrid
#
# This file is part of RepDoc
#
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSE.txt
#

from uuid import uuid4


def new_uuid(megalist_uuid):
    """Return new uuid after checking that there is no collision.

    Parameters
    ----------
    megalist_uuid : list
        List of previous uuid. The new value should not be present in
        that list.

    Returns
    -------
    newvalue : str
        New uuid value that does not collide with any previous value.

    """

    loop = True

    while loop:
        newvalue = str(uuid4())
        newlist = megalist_uuid + [newvalue]
        if len(newlist) != len(set(newlist)):
            print('UUID collision with:' + newvalue)
        else:
            return newvalue
