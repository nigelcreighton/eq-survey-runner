from __future__ import annotations

from flask import url_for


class Location:

    def __init__(self, block_id: str, list_name: str=None, list_item_id: str=None):
        """
        Args:
            block_id: The id of the current block. This could be a block inside a list collector
            list_item_id: The list_item_id if this location is associated with a list
            list_name: The list name
        """
        self.block_id = block_id
        self.list_name = list_name
        self.list_item_id = list_item_id

    def __eq__(self, other: Location):
        """
        Check to see if two locations are equal.
        Two answers are considered to be equal if their dictionary representations equal one another.

        :param other: An answer to compare
        :return: True if both answers match, otherwise False.
        """
        return isinstance(other, Location) and self.__dict__ == other.__dict__

    def __hash__(self):
        return hash(frozenset(self.__dict__.values()))

    def __str__(self):
        """
        String representation of the location, handy for debug messages

        :return:
        """
        return '{}'.format(self.block_id)

    def __repr__(self):
        """
        String representation of the location, handy for debug messages

        :return:
        """
        return str(self)

    @classmethod
    def from_dict(cls, location_dict: dict):
        block_id = location_dict['block_id']
        list_item_id = location_dict.get('list_item_id')
        list_name = location_dict.get('list_name')
        return cls(block_id, list_item_id, list_name)

    def to_dict(self) -> dict:
        attributes = vars(self)
        return {k: v for k, v in attributes.items() if v is not None}

    def url(self) -> str:
        """
        Return the survey runner url that this location represents

        The structure

        :return:
        """
        return url_for('questionnaire.get_block',
                       block_id=self.block_id)
