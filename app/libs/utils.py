import uuid
import copy

def convert_tx_id(tx_id):
    """
    Converts the guid tx_id to string of 16 characters with a dash between every 4 characters
    :param tx_id: tx_id to be converted
    :return: String in the form of xxxx-xxxx-xxxx-xxxx
    """
    return (tx_id[:4] + '-' + tx_id[4:])[:19]


def convert_tx_id_for_boxes(tx_id):
    """
    Converts the guid tx_id to string of 16 characters with a space between every 4 characters
    :param tx_id: tx_id to be converted
    :return: String in the form of xxxx xxxx xxxx xxxx
    """
    tx_id = uuid.UUID(tx_id)
    tx_id = tx_id.hex
    tx_id = tx_id.upper()
    displayable_tx_id = (tx_id[i:i + 4] for i in range(0, 16, 4))
    return displayable_tx_id


# Converts a dict into an object with the key names as property names
class ObjectFromDict:
    def __init__(self, properties):
        self.__dict__ = properties


def make_hash(o):
    """
    Makes a hash from a dictionary, list, tuple or set to any level, that contains
    only other hashable types (including any lists, tuples, sets, and
    dictionaries).
    https://stackoverflow.com/questions/5884066/hashing-a-dictionary/22003440#22003440
    """

    if isinstance(o, (set, tuple, list)):

        return tuple([make_hash(e) for e in o])

    elif not isinstance(o, dict):

        return hash(o)

    new_o = copy.deepcopy(o)
    for k, v in new_o.items():
        new_o[k] = make_hash(v)

    return hash(tuple(frozenset(sorted(new_o.items()))))
