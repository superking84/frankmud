"""
Exits

Exits are connectors between Rooms. An exit always has a destination property
set and has a single command defined on itself with the same name as its key,
for allowing Characters to traverse the exit to its destination.

"""
import enum

from django.conf import settings

from evennia import DefaultExit
from evennia.utils.utils import class_from_module

from typeclasses.objects import CustomObject


_COMMAND_DEFAULT_CLASS = class_from_module(settings.COMMAND_DEFAULT_CLASS)


class DoorState(enum.Enum):
    open = 0
    closed = 1
    locked = 2


class Exit(DefaultExit, CustomObject):
    """
    Exits are connectors between rooms. Exits are normal Objects except
    they defines the `destination` property. It also does work in the
    following methods:

     basetype_setup() - sets default exit locks (to change, use `at_object_creation` instead).
     at_cmdset_get(**kwargs) - this is called when the cmdset is accessed and should
                              rebuild the Exit cmdset along with a command matching the name
                              of the Exit object. Conventionally, a kwarg `force_init`
                              should force a rebuild of the cmdset, this is triggered
                              by the `@alias` command when aliases are changed.
     at_failed_traverse() - gives a default error message ("You cannot
                            go there") if exit traversal fails and an
                            attribute `err_traverse` is not defined.

    Relevant hooks to overload (compared to other types of Objects):
        at_traverse(traveller, target_loc) - called to do the actual traversal and calling of the other hooks.
                                            If overloading this, consider using super() to use the default
                                            movement implementation (and hook-calling).
        at_after_traverse(traveller, source_loc) - called by at_traverse just after traversing.
        at_failed_traverse(traveller) - called by at_traverse if traversal failed for some reason. Will
                                        not be called if the attribute `err_traverse` is
                                        defined, in which case that will simply be echoed.
    """
    pass


class DoorCommand(_COMMAND_DEFAULT_CLASS):
    """
    This is a command that simply cause the caller to traverse
    the door it is attached to.
    """

    obj = None

    def func(self):
        """
        Exit traversal command for doors.
        """
        door: Door = self.obj

        if door.db.door_state != DoorState.open:
            door.at_failed_traverse(self.caller)
            return

        if not door.access(self.caller, "traverse"):
            # exit is locked
            if door.db.err_traverse:
                # if exit has a better error message, let's use it.
                self.caller.msg(door.db.err_traverse)
            else:
                # No shorthand error message. Call hook.
                door.at_failed_traverse(self.caller)
        else:
            # we may traverse the exit.
            door.at_traverse(self.caller, door.destination)

    def get_extra_info(self, caller, **kwargs):
        """
        Shows a bit of information on where the exit leads.

        Args:
            caller (Object): The object (usually a character) that entered an ambiguous command.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).

        Returns:
            A string with identifying information to disambiguate the command, conventionally with a preceding space.
        """
        if self.obj.destination:
            return " (exit to %s)" % self.obj.destination.get_display_name(caller)
        else:
            return " (%s)" % self.obj.get_display_name(caller)


class Door(Exit):
    exit_command = DoorCommand

    def at_object_creation(self):
        self.db.door_state = DoorState.closed
        self.db.pair: Door = None

    def at_failed_traverse(self, traversing_object, **kwargs):
        if self.db.door_state != DoorState.open:
            traversing_object.msg(
                "{0} is closed.".format(self.name).capitalize())
            return

        super().at_failed_traverse(traversing_object, **kwargs)

    def at_before_open(self, opener):
        return self.db.door_state == DoorState.closed

    def at_before_close(self, closer):
        return self.db.door_state == DoorState.open

    def at_open(self, opener):
        self.db.door_state = DoorState.open
        self.db.pair.db.door_state = DoorState.open

        opener.msg("You open {0}.".format(self.name))
        self.location.msg_contents(
            "{0} opens {1}.".format(opener.name, self.name).capitalize(),
            exclude=[opener]
        )

        self.db.pair.location.msg_contents(
            "{0} opens.".format(self.db.pair.name).capitalize())

    def at_close(self, closer):
        self.db.door_state = DoorState.closed
        self.db.pair.db.door_state = DoorState.closed

        closer.msg("You close {0}.".format(self.name))
        self.location.msg_contents(
            "{0} closes {1}".format(closer.name, self.name).capitalize(),
            exclude=[closer]
        )

        self.db.pair.location.msg_contents(
            "{0} closes.".format(self.db.pair.name).capitalize())

    def at_failed_open(self, opener):
        if self.db.door_state == DoorState.open:
            opener.msg("It's already open.")
        elif self.db.door_state == DoorState.locked:
            opener.msg("You can't open it, because it's locked.")
        else:
            super().at_failed_open(opener)

    def at_failed_close(self, closer):
        if self.db.door_state in [DoorState.closed, DoorState.locked]:
            closer.msg("It's already closed.")
        else:
            super().at_failed_close(closer)
