"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""
import enum
from typing import Dict, Optional

from evennia import DefaultCharacter
from typeclasses.objects import CustomObject


class PhysicalPosition(enum.Enum):
    standing = 0
    kneeling = 1
    sitting = 2
    lying = 3


class Hand(enum.Enum):
    left = 0
    right = 1


class Character(DefaultCharacter, CustomObject):
    """
    The Character defaults to reimplementing some of base Object's hook methods with the
    following functionality:

    at_basetype_setup - always assigns the DefaultCmdSet to this object type
                    (important!)sets locks so character cannot be picked up
                    and its commands only be called by itself, not anyone else.
                    (to change things, use at_object_creation() instead).
    at_after_move(source_location) - Launches the "look" command after every move.
    at_post_unpuppet(account) -  when Account disconnects from the Character, we
                    store the current location in the pre_logout_location Attribute and
                    move it to a None-location so the "unpuppeted" character
                    object does not need to stay on grid. Echoes "Account has disconnected"
                    to the room.
    at_pre_puppet - Just before Account re-connects, retrieves the character's
                    pre_logout_location Attribute and move it back on the grid.
    at_post_puppet - Echoes "AccountName has entered the game" to the room.

    """
    equipable_body_parts = ["head", "face", "neck", "right_arm", "left_arm",
                            "right_hand", "left_hand", "torso", "waist", "right_leg", "left_leg", "right_foot", "left_foot"]

    def at_before_move(self, destination, **kwargs):
        if self.db.physical_position != PhysicalPosition.standing:
            self.msg("You must be standing to move.")
            return False

        return super().at_before_move(destination, **kwargs)

    def at_object_creation(self):
        super().at_object_creation()

        if not self.db.dominant_hand:
            self.db.dominant_hand: Hand = Hand.right

        if not self.db.equipment:
            self.db.equipment: Dict = {}
            for part in self.equipable_body_parts:
                self.db.equipment[part] = None

        if not self.db.inventory:
            self.db.inventory: Dict = {}
            self.db.inventory[Hand.left] = None
            self.db.inventory[Hand.right] = None

        if not self.db.physical_position:
            self.db.physical_position: PhysicalPosition = PhysicalPosition.standing

    def at_before_change_position(self, to_position: PhysicalPosition):
        return self.db.physical_position != to_position

    def at_change_position(self, to_position: PhysicalPosition):
        self.db.physical_position = to_position

        self_msg = "You {0}."
        others_msg = "{0} {1}."

        self_position_string = ""
        others_position_string = ""

        if to_position == PhysicalPosition.standing:
            self_position_string = "stand up"
            others_position_string = "stands up"
        elif to_position == PhysicalPosition.kneeling:
            self_position_string = "kneel"
            others_position_string = "kneels"
        elif to_position == PhysicalPosition.sitting:
            self_position_string = "sit"
            others_position_string = "sits"
        elif to_position == PhysicalPosition.lying:
            self_position_string = "lie down"
            others_position_string = "lies down"

        self.msg(self_msg.format(self_position_string))
        self.location.msg_contents(
            others_msg.format(self.name, others_position_string).capitalize(),
            exclude=[self]
        )

    def at_failed_change_position(self, to_position: PhysicalPosition):
        if self.db.physical_position == to_position:
            msg = "You are already {0}."
            position_string = ""
            if to_position == PhysicalPosition.standing:
                position_string = "standing"
            elif to_position == PhysicalPosition.kneeling:
                position_string = "kneeling"
            elif to_position == PhysicalPosition.sitting:
                position_string = "sitting"
            elif to_position == PhysicalPosition.lying:
                position_string = "lying down"

            self.msg(msg.format(position_string))

    def get_equipment_display(self) -> str:
        output = ""
        for part in self.equipable_body_parts:
            part_for_display = part.replace("_", " ").capitalize()
            equipment_name = self.db.equipment[part].name if self.db.equipment[part] is not None else "Nothing"
            output += "{0}: {1}\n".format(part_for_display, equipment_name)

        return output

    def get_nondominant_hand(self) -> Hand:
        return Hand.left if self.db.dominant_hand == Hand.right else Hand.right

    def get_free_hand(self) -> Optional[Hand]:
        other_hand = self.get_nondominant_hand()

        if self.db.inventory[self.db.dominant_hand] is None:
            return self.db.dominant_hand
        elif self.db.inventory[other_hand] is None:
            return other_hand
        else:
            return None

    def get_containing_hand(self, obj_to_search) -> Optional[Hand]:
        other_hand = self.get_nondominant_hand()

        if self.db.inventory[self.db.dominant_hand] is obj_to_search:
            return self.db.dominant_hand
        elif self.db.inventory[other_hand] is obj_to_search:
            return other_hand
        else:
            return None
