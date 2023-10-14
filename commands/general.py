from evennia import default_cmds
from typeclasses.characters import Hand, PhysicalPosition
from typeclasses.objects import CustomObject, WearableObject
from typeclasses.characters import Character


class CmdEcho(default_cmds.MuxCommand):
    """
    Simple command example

    Usage:
        echo [text]

    This command simply echoes text back to the caller.
    """
    key = "echo"

    def func(self):
        if not self.args:
            self.caller.msg("You didn't enter anything!")
        else:
            self.caller.msg("You gave the string {0}".format(self.args))


class CmdEquipment(default_cmds.MuxCommand):
    """
    Show all worn equipment for a character. 
    """
    key = "equipment"
    aliases = ["eq"]

    def func(self):
        caller: Character = self.caller
        caller.msg("|wYou are wearing the following equipment:|n")
        caller.msg(caller.get_equipment_display())


class CmdOpen(default_cmds.MuxCommand):
    """
    Attempts to open an object.

    Usage:
        open <obj>
    """
    key = "open"
    aliases = ["op"]

    def func(self):
        opener = self.caller
        if not self.args:
            opener.msg("Open what?")
            return

        target: CustomObject = opener.search(self.arglist[0])
        if not target:
            return

        if target.at_before_open(opener):
            target.at_open(opener)
        else:
            target.at_failed_open(opener)

        return


class CmdClose(default_cmds.MuxCommand):
    """
    Attempts to close an object.

    Usage:
        close <obj>
    """
    key = "close"
    aliases = ["cl"]

    def func(self):
        closer = self.caller
        if not self.args:
            closer.msg("Close what?")
            return

        target: CustomObject = closer.search(self.arglist[0])
        if not target:
            return

        if target.at_before_close(closer):
            target.at_close(closer)
        else:
            target.at_failed_close(closer)


class CmdStand(default_cmds.MuxCommand):
    """
    Attempts to stand up.

    Usage:
        stand
    """
    key = "stand"

    def func(self):
        caller: Character = self.caller

        if caller.at_before_change_position(PhysicalPosition.standing):
            caller.at_change_position(PhysicalPosition.standing)
        else:
            caller.at_failed_change_position(PhysicalPosition.standing)


class CmdKneel(default_cmds.MuxCommand):
    """
    Attempts to kneel.

    Usage:
        kneel
    """
    key = "kneel"

    def func(self):
        caller: Character = self.caller

        if caller.at_before_change_position(PhysicalPosition.kneeling):
            caller.at_change_position(PhysicalPosition.kneeling)
        else:
            caller.at_failed_change_position(PhysicalPosition.kneeling)


class CmdSit(default_cmds.MuxCommand):
    """
    Attempts to sit.

    Usage:
        sit
    """
    key = "sit"

    def func(self):
        caller: Character = self.caller

        if caller.at_before_change_position(PhysicalPosition.sitting):
            caller.at_change_position(PhysicalPosition.sitting)
        else:
            caller.at_failed_change_position(PhysicalPosition.sitting)


class CmdLie(default_cmds.MuxCommand):
    """
    Attempts to lie down.

    Usage:
        lie
    """
    key = "lie"

    def func(self):
        caller: Character = self.caller

        if caller.at_before_change_position(PhysicalPosition.lying):
            caller.at_change_position(PhysicalPosition.lying)
        else:
            caller.at_failed_change_position(PhysicalPosition.lying)


class CmdWear(default_cmds.MuxCommand):
    """
    Wear an object.

    Usage:
        wear <object>
    """
    key = "wear"

    def func(self):
        caller: Character = self.caller

        if not self.args:
            caller.msg("Wear what?")
            return

        target = caller.search(self.arglist[0])
        if not target:
            return

        if not isinstance(target, WearableObject):
            caller.msg("You can't wear that.")
            return

        if target not in caller.db.inventory.values():
            caller.msg("You have to be holding something to wear it.")
            return

        wearable_location = target.db.wearable_location
        if caller.db.equipment[wearable_location] is target:
            caller.msg("You're already wearing that.")
        elif caller.db.equipment[wearable_location] is not None:
            caller.msg("You're already wearing something else there.")
        else:
            caller.db.equipment[wearable_location] = target
            held_in_hand = caller.get_containing_hand(target)
            caller.db.inventory[held_in_hand] = None
            target.db.is_worn = True
            caller.msg("You wear {0}.".format(target.name))


class CmdRemove(default_cmds.MuxCommand):
    """
    Remove an object.

    Usage:
        remove <object>
    """
    key = "remove"
    aliases = ["rem", "rm"]

    def func(self):
        caller: Character = self.caller

        if not self.args:
            caller.msg("Remove what?")
            return

        target = caller.search(self.arglist[0])
        if not target:
            return

        if target not in caller.contents:
            caller.msg("You aren't wearing that.")
            return

        if not isinstance(target, WearableObject):
            caller.msg("That isn't a wearable object.")
            return

        wearable_location = target.db.wearable_location
        free_hand = caller.get_free_hand()
        if caller.db.equipment[wearable_location] is not target:
            caller.msg("You aren't wearing that.")
        elif free_hand is None:
            caller.msg("You don't have a free hand to hold it in.")
        else:
            caller.db.equipment[wearable_location] = None
            caller.db.inventory[free_hand] = target
            target.db.is_worn = False
            caller.msg("You remove {0}.".format(target.name))


class CmdInventory(default_cmds.MuxCommand):
    """
    view inventory

    Usage:
      inventory
      inv

    Shows your inventory.
    """

    key = "inventory"
    aliases = ["inv", "i"]
    locks = "cmd:all()"
    arg_regex = r"$"

    def func(self):
        """check inventory"""
        left_hand_item = self.caller.db.inventory[Hand.left]
        right_hand_item = self.caller.db.inventory[Hand.right]

        if not left_hand_item and not right_hand_item:
            self.caller.msg("You aren't carrying anything.")
            return

        message = "You are holding "
        if left_hand_item:
            message += "{0} in your left hand".format(left_hand_item.name)

        if left_hand_item and right_hand_item:
            message += " and "
        else:
            message += "."

        if right_hand_item:
            message += "{0} in your right hand.".format(
                right_hand_item.name)

        self.caller.msg(message)
