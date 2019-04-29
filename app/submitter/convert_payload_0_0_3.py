from typing import List, Dict, Optional

from app.data_model.answer import Answer
from app.data_model.answer_store import AnswerStore


def convert_answers_to_payload_0_0_3(answer_store, list_store, schema, routing_path) -> List[Dict]:
    """
    Convert answers into the data format below
    'data': [
        {
            'value': 'Joe',
            'answer_id': 'first-name',
            'list_item_id': 'axkkdh'
        },
        {
            'value': 'Joe',
            'answer_id': 'first-name',
            'list_item_id': 'axkkdh'
        },
        {
            'value': 'No',
            'answer_id': 'do-you-live-here'
        }
    ]

    For list answers, this method will query the list store and get all answers from the
    add list item block. If there are multiple list collectors for one list, they will have
    the same answer_ids, and will not be duplicated.

    Returns:
        A list of answer dictionaries.
    """
    answers = AnswerStore()

    for location in routing_path:
        if schema.get_block(location.block_id)['type'] == 'ListCollector':
            for answer in convert_list_collector_answers(answer_store, list_store, schema, location):
                if answer:
                    answers.add_or_update(answer)

        answer_ids = schema.get_answer_ids_for_block(location.block_id)
        answers_in_block = answer_store.get_answers_by_answer_id(answer_ids, list_item_id=location.list_item_id)
        for answer_in_block in answers_in_block:
            if answer_in_block:
                answers.add_or_update(answer_in_block)

    return list(answers.answer_map.values())


def convert_list_collector_answers(answer_store, list_store, schema, location) -> Optional[List[Answer]]:
    """For the given location, check for list collector and generate submission payload

    Returns:
        A list of answer objects (or None)
    """
    answer_output = []
    block = schema.get_block(location.block_id)
    add_block_answer_ids = schema.get_answer_ids_for_block(block['add_block']['id'])
    list_name = block['populates_list']
    try:
        list_item_ids = list_store[list_name]
    except KeyError:
        return

    for list_item_id in list_item_ids:
        for answer_id in add_block_answer_ids:
            found_answer = answer_store.get_answer(answer_id, list_item_id)
            if found_answer:
                answer_output.append(found_answer)

    return answer_output
