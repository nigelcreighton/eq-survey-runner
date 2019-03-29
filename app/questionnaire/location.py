from flask import url_for


class Location:

    def __init__(self, block_id, list_item_id=None, sub_block=None):
        """
        :param block_id: The id of the current block. This should always match the url
        :param list_item_id: The list_item_id if this location is associated with a list
        :param sub_block: The sub block, either edit, add or remove
        """
        self.block_id = block_id
        self.list_item_id = list_item_id
        self.sub_block = sub_block

    def __eq__(self, other):
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
    def from_dict(cls, location_dict):
        block_id = location_dict['block_id']
        list_item_id = location_dict.get('list_item_id')
        sub_block = location_dict.get('sub_block')
        return cls(block_id, list_item_id, sub_block)

    def to_dict(self):
        attributes = vars(self)
        return {k: v for k, v in attributes.items() if v is not None}

    def url(self):
        """
        Return the survey runner url that this location represents

        :return:
        """
        return url_for('questionnaire.get_block',
                       block_id=self.block_id)
