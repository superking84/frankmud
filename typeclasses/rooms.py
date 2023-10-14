"""
Room

Rooms are simple containers that has no location of their own.

"""

from collections import defaultdict

from evennia import DefaultRoom
from evennia.utils.utils import list_to_string
from typeclasses.objects import CustomObject


class Room(DefaultRoom, CustomObject):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See examples/object.py for a list of
    properties and methods available on all Objects.
    """

    def return_appearance(self, looker, **kwargs):
        """
        This formats a description. It is the hook a 'look' command
        should call.

        Args:
            looker (Object): Object doing the looking.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).
        """
        if not looker:
            return ""

        # get and identify all objects
        visible = (con for con in self.contents if con !=
                   looker and con.access(looker, "view"))
        exits, users, things = [], [], defaultdict(list)

        for con in visible:
            key = con.get_display_name(looker)
            if con.destination:
                exits.append(key)
            elif con.has_account:
                users.append("|c%s|n" % key)
            else:
                # things can be pluralized
                things[key].append(con)

        # get description, build string
        string = "\n|c%s|n\n" % self.get_display_name(looker)
        desc = self.db.desc
        if desc:
            string += "%s" % desc

        if exits:
            string += "  |wExits:|n " + list_to_string(exits)
        else:
            string += "\n|wThere are no visible exits.|n"

        if users or things:
            # handle pluralization of things (never pluralize users)
            thing_strings = []
            for key, itemlist in sorted(things.items()):
                item_count = len(itemlist)
                if item_count == 1:
                    key, _ = itemlist[0].get_numbered_name(
                        item_count, looker, key=key)
                else:
                    key = [item.get_numbered_name(item_count, looker, key=key)[
                        1] for item in itemlist][0]
                thing_strings.append(key)

            string += "\n|wYou see:|n " + \
                list_to_string(users + thing_strings)

        return string
