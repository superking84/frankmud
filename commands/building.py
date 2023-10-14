from evennia import default_cmds


class CmdDesc(default_cmds.MuxCommand):
    """
    describe an object or the current room.

    Usage:
      desc [<object> [= <description>]]

    Switches:
      edit - Open up a line editor for more advanced editing.

    Gets or sets the "desc" attribute on an object.
    If neither parameter is given, display the caller's description.
    If object is provided without description, display the object's description.
    If both are provided, set the object's description.
    """

    key = "desc"
    aliases = "describe"
    locks = "cmd:perm(desc) or perm(Builder)"
    help_category = "Building"

    def func(self):
        """Define command"""

        caller = self.caller
        if not self.args:
            caller.msg(caller.db.desc)
            return

        if len(self.arglist) == 1:
            obj = caller.search(self.arglist[0])
            if not obj:
                return

            desc: str = obj.db.desc
            if not desc or len(desc) == 0 or desc.isspace():
                caller.msg(
                    'Object does not have a description.  Set with "desc <object> = <description>".')
            else:
                caller.msg(desc)
        elif self.arglist[1] != "=":
            caller.msg("Usage: desc [<object> [= <description>]]")
        else:
            # We have an =
            obj = caller.search(self.lhs)
            if not obj:
                return
            if not self.rhs or len(self.rhs) == 0:
                caller.msg("You must provide a description.")
                return
            desc = self.rhs or ""

            if obj.access(self.caller, "control") or obj.access(self.caller, "edit"):
                obj.db.desc = desc
                caller.msg("The description was set on {0}.".format(
                    obj.get_display_name(caller)))
                caller.msg("New description: \n{0}".format(desc))
            else:
                caller.msg(
                    "You don't have permission to edit the description of {0}.".format(obj.key))
