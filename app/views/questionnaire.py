from datetime import datetime, timedelta

import humanize
import simplejson as json
from dateutil.tz import tzutc
from flask import Blueprint, g, redirect, request, url_for, current_app, jsonify
from flask import session as cookie_session
from flask_login import current_user, login_required, logout_user
from flask_themes2 import render_theme_template
from jwcrypto.common import base64url_decode
from sdc.crypto.encrypter import encrypt
from structlog import get_logger
from werkzeug.exceptions import NotFound

from app.authentication.no_token_exception import NoTokenException
from app.data_model.answer_store import AnswerStore
from app.data_model.app_models import SubmittedResponse
from app.globals import (get_answer_store, get_list_store, get_completed_blocks, get_metadata, get_questionnaire_store,
                         get_collection_metadata)
from app.globals import get_session_store
from app.helpers.form_helper import post_form_for_block
from app.helpers.path_finder_helper import path_finder, full_routing_path_required
from app.helpers.schema_helpers import with_schema
from app.helpers.session_helpers import with_answer_store, with_metadata, with_collection_metadata, with_list_store
from app.helpers.template_helper import (with_session_timeout, with_analytics,
                                         with_legal_basis, render_template, safe_content)
from app.keys import KEY_PURPOSE_SUBMISSION
from app.questionnaire.answer_store_updater import AnswerStoreUpdater
from app.questionnaire.location import Location
from app.questionnaire.router import Router
from app.questionnaire.placeholder_renderer import PlaceholderRenderer
from app.questionnaire.schema_utils import transform_variants
from app.storage.storage_encryption import StorageEncryption
from app.submitter.converter import convert_answers
from app.submitter.submission_failed import SubmissionFailedException
from app.templating.metadata_context import build_metadata_context_for_survey_completed
from app.templating.summary_context import build_summary_rendering_context
from app.templating.view_context import build_view_context
from app.utilities.schema import load_schema_from_session_data

END_BLOCKS = 'Summary', 'Confirmation'

logger = get_logger()

questionnaire_blueprint = Blueprint(name='questionnaire',
                                    import_name=__name__,
                                    url_prefix='/questionnaire/')

post_submission_blueprint = Blueprint(name='post_submission',
                                      import_name=__name__,
                                      url_prefix='/submitted/')


@questionnaire_blueprint.before_request
def before_questionnaire_request():
    metadata = get_metadata(current_user)
    if not metadata:
        raise NoTokenException(401)

    logger.bind(tx_id=metadata['tx_id'], eq_id=metadata['eq_id'],
                metadata=metadata['form_type'], ce_id=metadata['collection_exercise_sid'])

    logger.info('questionnaire request', method=request.method, url_path=request.full_path)

    session_store = get_session_store()
    session_data = session_store.session_data

    language_code = request.args.get('language_code')
    if language_code:
        session_data.language_code = language_code
        session_store.save()

    g.schema = load_schema_from_session_data(session_data)


@post_submission_blueprint.before_request
def before_post_submission_request():
    session_store = get_session_store()
    if not session_store or not session_store.session_data:
        raise NoTokenException(401)

    session_data = session_store.session_data
    g.schema = load_schema_from_session_data(session_data)

    logger.bind(tx_id=session_data.tx_id,
                eq_id=session_data.eq_id,
                form_type=session_data.form_type)

    logger.info('questionnaire request', method=request.method, url_path=request.full_path)


@questionnaire_blueprint.route('<block_id>', methods=['GET'])
@login_required
@with_answer_store
@with_metadata
@with_schema
@full_routing_path_required
def get_block(routing_path, schema, metadata, answer_store, block_id):
    current_location = Location(block_id)
    completed_locations = get_completed_blocks(current_user)
    router = Router(schema, routing_path, current_location, completed_locations)

    if not router.can_access_location():
        next_location = router.get_next_location()
        return _redirect_to_location(next_location)

    block = schema.get_block(current_location.block_id)

    transformed_block = transform_variants(block, schema, metadata, answer_store)

    placeholder_renderer = PlaceholderRenderer(answer_store=answer_store, metadata=metadata)
    rendered_block = placeholder_renderer.render(transformed_block)

    context = _get_context(rendered_block, current_location, schema)

    return _render_page(block['type'], context, current_location, schema)


@questionnaire_blueprint.route('<block_id>', methods=['POST'])
@login_required
@with_answer_store
@with_list_store
@with_collection_metadata
@with_metadata
@with_schema
@full_routing_path_required
# pylint: disable=too-many-locals, too-many-return-statements
def post_block(routing_path, schema, metadata, collection_metadata, list_store, answer_store, block_id):
    current_location = Location(block_id)
    completed_locations = get_completed_blocks(current_user)
    router = Router(schema, routing_path, current_location, completed_locations)

    if not router.can_access_location():
        next_location = router.get_next_location()
        return _redirect_to_location(next_location)

    block = schema.get_block(current_location.block_id)

    transformed_block = transform_variants(block, schema, metadata, answer_store)

    placeholder_renderer = PlaceholderRenderer(answer_store=answer_store, metadata=metadata)
    rendered_block = placeholder_renderer.render(transformed_block)

    form = _generate_wtf_form(request.form, rendered_block, schema)

    if 'action[save_sign_out]' in request.form:
        return _save_sign_out(current_location, rendered_block.get('question'), form, schema)

    if 'action[sign_out]' in request.form:
        return redirect(url_for('session.get_sign_out'))

    if form.validate():
        _set_started_at_metadata_if_required(form, collection_metadata)
        questionnaire_store = get_questionnaire_store(current_user.user_id, current_user.user_ik)
        answer_store_updater = AnswerStoreUpdater(current_location, schema, questionnaire_store,
                                                  rendered_block.get('question'))
        answer_store_updater.save_answers(form)

        if block['type'] == 'ListCollector':
            if list(form.data.values())[0] == block['add_answer_value']:
                add_url = url_for('questionnaire.get_add_list_item', block_id=block_id)
                return redirect(add_url)

        next_location = path_finder.get_next_location(current_location=current_location)

        if _is_end_of_questionnaire(block, next_location):
            return submit_answers(routing_path, schema)

        return redirect(next_location.url())

    context = build_view_context(block['type'], metadata, schema, list_store, answer_store, rendered_block,
                                 current_location, form)

    return _render_page(block['type'], context, current_location, schema)


@post_submission_blueprint.route('thank-you', methods=['GET'])
@login_required
@with_schema
def get_thank_you(schema):
    session_data = get_session_store().session_data

    if session_data.submitted_time:
        metadata_context = build_metadata_context_for_survey_completed(session_data)

        view_submission_url = None
        view_submission_duration = 0
        if _is_submission_viewable(schema.json, session_data.submitted_time):
            view_submission_url = url_for('.get_view_submission')
            view_submission_duration = humanize.naturaldelta(
                timedelta(seconds=schema.json['view_submitted_response']['duration']))

        return render_theme_template(schema.json['theme'],
                                     template_name='thank-you.html',
                                     metadata=metadata_context,
                                     analytics_ua_id=current_app.config['EQ_UA_ID'],
                                     survey_id=schema.json['survey_id'],
                                     survey_title=safe_content(schema.json['title']),
                                     is_view_submitted_response_enabled=is_view_submitted_response_enabled(schema.json),
                                     view_submission_url=view_submission_url,
                                     account_service_url=cookie_session.get('account_service_url'),
                                     account_service_log_out_url=cookie_session.get('account_service_log_out_url'),
                                     view_submission_duration=view_submission_duration)

    routing_path = path_finder.get_full_routing_path()

    completed_locations = get_completed_blocks(current_user)
    router = Router(schema, routing_path, completed_locations=completed_locations)
    next_location = router.get_next_location()

    return _redirect_to_location(next_location)


@post_submission_blueprint.route('thank-you', methods=['POST'])
@login_required
def post_thank_you():
    if 'action[sign_out]' in request.form:
        return redirect(url_for('session.get_sign_out'))

    return redirect(url_for('post_submission.get_thank_you'))


@post_submission_blueprint.route('view-submission', methods=['GET'])
@login_required
@with_schema
def get_view_submission(schema):  # pylint: too-many-locals

    session_data = get_session_store().session_data

    if _is_submission_viewable(schema.json, session_data.submitted_time):
        submitted_data = current_app.eq['storage'].get_by_key(SubmittedResponse, session_data.tx_id)

        if submitted_data:

            metadata_context = build_metadata_context_for_survey_completed(session_data)

            pepper = current_app.eq['secret_store'].get_secret_by_name('EQ_SERVER_SIDE_STORAGE_ENCRYPTION_USER_PEPPER')

            encrypter = StorageEncryption(current_user.user_id, current_user.user_ik, pepper)
            submitted_data = encrypter.decrypt_data(submitted_data.data)

            # for backwards compatibility
            # submitted data used to be base64 encoded before encryption
            try:
                submitted_data = base64url_decode(submitted_data.decode()).decode()
            except ValueError:
                pass

            submitted_data = json.loads(submitted_data)
            answer_store = AnswerStore(submitted_data.get('answers'))

            metadata = submitted_data.get('metadata')

            section_list = schema.json['sections']
            summary_rendered_context = build_summary_rendering_context(schema, section_list, answer_store, metadata)

            context = {
                'summary': {
                    'groups': summary_rendered_context,
                    'answers_are_editable': False,
                    'is_view_submission_response_enabled': is_view_submitted_response_enabled(schema.json),
                },
            }

            return render_theme_template(schema.json['theme'],
                                         template_name='view-submission.html',
                                         metadata=metadata_context,
                                         analytics_ua_id=current_app.config['EQ_UA_ID'],
                                         survey_id=schema.json['survey_id'],
                                         survey_title=safe_content(schema.json['title']),
                                         account_service_url=cookie_session.get('account_service_url'),
                                         account_service_log_out_url=cookie_session.get('account_service_log_out_url'),
                                         content=context)

    return redirect(url_for('post_submission.get_thank_you'))


@post_submission_blueprint.route('view-submission', methods=['POST'])
@login_required
def post_view_submission():
    if 'action[sign_out]' in request.form:
        return redirect(url_for('session.get_sign_out'))

    return redirect(url_for('post_submission.get_view_submission'))


def _set_started_at_metadata_if_required(form, collection_metadata):
    if not collection_metadata.get('started_at') and form.data:
        started_at = datetime.utcnow().isoformat()

        logger.info('Survey started. Writing started_at time to collection metadata',
                    started_at=started_at)

        collection_metadata['started_at'] = started_at


def _render_page(block_type, context, current_location, schema):
    if request_wants_json():
        return jsonify(context)

    return _build_template(current_location, context, block_type, schema)


def _generate_wtf_form(form, block, schema):
    disable_mandatory = 'action[save_sign_out]' in form

    wtf_form = post_form_for_block(
        schema,
        block,
        get_answer_store(current_user),
        get_metadata(current_user),
        request.form,
        disable_mandatory)

    return wtf_form


def _is_end_of_questionnaire(block, next_location):
    return (
        block['type'] in END_BLOCKS and next_location is None
    )


def submit_answers(routing_path, schema):
    metadata = get_metadata(current_user)
    collection_metadata = get_collection_metadata(current_user)
    answer_store = get_answer_store(current_user)

    message = json.dumps(convert_answers(
        metadata,
        collection_metadata,
        schema,
        answer_store,
        routing_path,
    ))

    encrypted_message = encrypt(message, current_app.eq['key_store'], KEY_PURPOSE_SUBMISSION)
    sent = current_app.eq['submitter'].send_message(encrypted_message, case_id=metadata.get('case_id'),
                                                    tx_id=metadata.get('tx_id'))

    if not sent:
        raise SubmissionFailedException()

    submitted_time = datetime.utcnow()

    _store_submitted_time_in_session(submitted_time)

    if is_view_submitted_response_enabled(schema.json):
        _store_viewable_submission(list(answer_store), metadata, submitted_time)

    get_questionnaire_store(current_user.user_id, current_user.user_ik).delete()

    return redirect(url_for('post_submission.get_thank_you'))


def _store_submitted_time_in_session(submitted_time):
    session_store = get_session_store()
    session_data = session_store.session_data
    session_data.submitted_time = submitted_time.isoformat()
    session_store.save()


def _store_viewable_submission(answers, metadata, submitted_time):
    pepper = current_app.eq['secret_store'].get_secret_by_name('EQ_SERVER_SIDE_STORAGE_ENCRYPTION_USER_PEPPER')
    encrypter = StorageEncryption(current_user.user_id, current_user.user_ik, pepper)
    encrypted_data = encrypter.encrypt_data(
        {
            'answers': answers,
            'metadata': metadata.copy(),
        },
    )

    valid_until = submitted_time + timedelta(seconds=g.schema.json['view_submitted_response']['duration'])

    item = SubmittedResponse(
        tx_id=metadata['tx_id'],
        data=encrypted_data,
        valid_until=valid_until.replace(tzinfo=tzutc()),
    )

    current_app.eq['storage'].put(item)


def is_view_submitted_response_enabled(schema):
    view_submitted_response = schema.get('view_submitted_response')
    if view_submitted_response:
        return view_submitted_response['enabled']

    return False


def _is_submission_viewable(schema, submitted_time):
    if is_view_submitted_response_enabled(schema) and submitted_time:
        submitted_time = datetime.strptime(submitted_time, '%Y-%m-%dT%H:%M:%S.%f')
        submission_valid_until = submitted_time + timedelta(seconds=schema['view_submitted_response']['duration'])
        return submission_valid_until > datetime.utcnow()

    return False


def _save_sign_out(current_location, current_question, form, schema):
    questionnaire_store = get_questionnaire_store(current_user.user_id, current_user.user_ik)

    block = schema.get_block(current_location.block_id)

    if form.validate():
        answer_store_updater = AnswerStoreUpdater(current_location, schema, questionnaire_store, current_question)
        answer_store_updater.save_answers(form)

        questionnaire_store.remove_completed_blocks(location=current_location)
        questionnaire_store.add_or_update()

        logout_user()

        return redirect(url_for('session.get_sign_out'))

    context = _get_context(block, current_location, schema, form)
    return _render_page(block['type'], context, current_location, schema)


def _redirect_to_location(location):
    return redirect(url_for('questionnaire.get_block', block_id=location.block_id))


def _get_context(block, current_location, schema, form=None):
    metadata = get_metadata(current_user)

    answer_store = get_answer_store(current_user)

    list_store = get_list_store(current_user)

    return build_view_context(block['type'], metadata, schema, list_store, answer_store, block, current_location,
                              form=form)


def get_page_title_for_location(schema, current_location, context):
    block = schema.get_block(current_location.block_id)
    if block['type'] == 'Interstitial':
        group = schema.get_group(schema.get_group_by_block_id(block['id'])['id'])
        page_title = '{group_title} - {survey_title}'.format(group_title=group['title'],
                                                             survey_title=schema.json['title'])
    elif block['type'] == 'Question':
        question_title = context['block']['question'].get('title')

        page_title = '{question_title} - {survey_title}'.format(question_title=question_title,
                                                                survey_title=schema.json['title'])
    else:
        page_title = schema.json['title']

    return safe_content(page_title)


def _build_template(current_location, context, template, schema):
    previous_location = path_finder.get_previous_location(current_location)
    previous_url = previous_location.url() if previous_location is not None else None

    return _render_template(context, current_location, template, previous_url, schema)


@with_session_timeout
@with_analytics
@with_legal_basis
def _render_template(context, current_location, template, previous_url, schema,
                     **kwargs):
    page_title = get_page_title_for_location(schema, current_location, context)

    session_store = get_session_store()
    session_data = session_store.session_data

    return render_template(
        template,
        content=context,
        current_location=current_location,
        previous_location=previous_url,
        page_title=page_title,
        language_code=session_data.language_code,
        **kwargs
    )


def request_wants_json():
    best = request.accept_mimetypes \
        .best_match(['application/json', 'text/html'])
    return best == 'application/json' and request.accept_mimetypes[best] > request.accept_mimetypes['text/html']


class InvalidListItemId(Exception):
    pass


@with_list_store
def validate_list_collector_route(list_store, schema, block_id, list_item_id=None):
    block = schema.get_block(block_id)

    if not block:
        raise NotFound()

    if block['type'] != 'ListCollector':
        raise NotFound()

    if list_item_id and list_item_id not in list_store[block['populates_list']]:
        raise InvalidListItemId(f'List item id: {list_item_id} not found for block {block_id}')


@questionnaire_blueprint.route('<block_id>/add', methods=['POST'])
@login_required
@with_answer_store
@with_list_store
@with_collection_metadata
@with_metadata
@with_schema
def post_add_list_item(schema, metadata, collection_metadata, list_store, answer_store, block_id):

    return list_collector_post_handler(schema, metadata, collection_metadata, list_store, answer_store, block_id,
                                       None, 'add')


@questionnaire_blueprint.route('<block_id>/<list_item_id>/remove', methods=['POST'])
@login_required
@with_answer_store
@with_list_store
@with_collection_metadata
@with_metadata
@with_schema
def post_remove_list_item(schema, metadata, collection_metadata, list_store, answer_store, block_id,
                          list_item_id):

    return list_collector_post_handler(schema, metadata, collection_metadata, list_store, answer_store, block_id,
                                       list_item_id, 'remove')


@questionnaire_blueprint.route('<block_id>/<list_item_id>/edit', methods=['POST'])
@login_required
@with_answer_store
@with_list_store
@with_collection_metadata
@with_metadata
@with_schema
def post_edit_list_item(schema, metadata, collection_metadata, list_store, answer_store, block_id,
                        list_item_id):

    return list_collector_post_handler(schema, metadata, collection_metadata, list_store, answer_store, block_id,
                                       list_item_id, 'edit')


@questionnaire_blueprint.route('<block_id>/<list_item_id>/remove', methods=['GET'])
@login_required
@with_answer_store
@with_metadata
@with_schema
def get_remove_list_item(schema, metadata, answer_store, block_id, list_item_id):
    return list_collector_get_handler(schema, metadata, answer_store, block_id, 'remove', list_item_id)


@questionnaire_blueprint.route('<block_id>/<list_item_id>/edit', methods=['GET'])
@login_required
@with_answer_store
@with_metadata
@with_schema
def get_edit_list_item(schema, metadata, answer_store, block_id, list_item_id):
    return list_collector_get_handler(schema, metadata, answer_store, block_id, 'edit', list_item_id)


@questionnaire_blueprint.route('<block_id>/add', methods=['GET'])
@login_required
@with_answer_store
@with_metadata
@with_schema
def get_add_list_item(schema, metadata, answer_store, block_id):
    return list_collector_get_handler(schema, metadata, answer_store, block_id, 'add')


def list_collector_get_handler(schema, metadata, answer_store, block_id, list_operation, list_item_id=None):
    try:
        validate_list_collector_route(schema, block_id, list_item_id)
    except InvalidListItemId:
        return redirect(url_for('questionnaire.get_block', block_id=block_id))

    parent_block = schema.get_block(block_id)
    sub_block = parent_block[f'{list_operation}_block']

    current_location = Location(block_id, list_item_id, sub_block=list_operation)

    transformed_block = transform_variants(sub_block, schema, metadata, answer_store)

    placeholder_renderer = PlaceholderRenderer(answer_store=answer_store, metadata=metadata)
    rendered_block = placeholder_renderer.render(transformed_block)

    context = _get_context(rendered_block, current_location, schema)

    return _render_page(rendered_block['type'], context, current_location, schema)


# pylint: disable=too-many-locals
def list_collector_post_handler(schema, metadata, collection_metadata, list_store, answer_store, block_id, list_item_id, list_operation):
    try:
        validate_list_collector_route(schema, block_id, list_item_id)
    except InvalidListItemId:
        return redirect(url_for('questionnaire.get_block', block_id=block_id))

    parent_block = schema.get_block(block_id)
    block = parent_block[f'{list_operation}_block']

    current_location = Location(parent_block['id'], list_item_id, sub_block=list_operation)

    transformed_block = transform_variants(block, schema, metadata, answer_store)

    placeholder_renderer = PlaceholderRenderer(answer_store=answer_store, metadata=metadata)
    rendered_block = placeholder_renderer.render(transformed_block)

    form = _generate_wtf_form(request.form, rendered_block, schema)

    if 'action[save_sign_out]' in request.form:
        return _save_sign_out(current_location, rendered_block.get('question'), form, schema)

    if 'action[sign_out]' in request.form:
        return redirect(url_for('session.get_sign_out'))

    if form.validate():
        _set_started_at_metadata_if_required(form, collection_metadata)
        questionnaire_store = get_questionnaire_store(current_user.user_id, current_user.user_ik)
        answer_store_updater = AnswerStoreUpdater(current_location, schema,
                                                  questionnaire_store, rendered_block.get('question'))

        if list_operation == 'remove':
            if list(form.data.values())[0] == parent_block['remove_answer_value']:
                list_store.delete_list_item_id(parent_block['populates_list'], list_item_id)
                answer_store_updater.remove_all_answers_with_list_item_id(list_item_id)
            else:
                redirect(
                    url_for('questionnaire.get_edit_list_item',
                            block_id=parent_block['id'], list_item_id=list_item_id))
        elif list_operation == 'add':
            new_list_item_id = list_store.add_list_item(parent_block['populates_list'])
            current_location = Location(current_location.block_id, new_list_item_id, sub_block='add')
            answer_store_updater = AnswerStoreUpdater(current_location, schema,
                                                      questionnaire_store, rendered_block.get('question'))

            answer_store_updater.save_answers(form)
        else:
            answer_store_updater.save_answers(form)

        list_collector_url = url_for('questionnaire.get_block', block_id=parent_block['id'])

        return redirect(list_collector_url)

    context = build_view_context(block['type'], metadata, schema, list_store, answer_store, rendered_block,
                                 current_location, form)

    return _render_page(block['type'], context, current_location, schema)
