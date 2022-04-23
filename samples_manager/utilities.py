"""File used to store all functions without project dependencies."""

import re
import pytz
import math
import logging
import cx_Oracle
import numpy as np
from requests import Session
from django.db.models import Q
from django.urls import reverse
from zeep import Client, Settings
from zeep.exceptions import Fault
from zeep.transports import Transport
from django.db import OperationalError
from django.core.mail import EmailMessage
from django.core.paginator import Paginator
from datetime import datetime as dt, timedelta
from django.core.exceptions import ValidationError


APP_NAME = 'samples_manager'
MIN_ELEMENTS_PER_PAGE_DOUBLE_PAGINATION = 50
MAX_PAGES = 10
FIRST_SET_ID_NUMBER = 3200
SET_ID_NUM_DIGITS = 6
MAX_FILTER_RECURSION_LEVEL = 5
DB_CONNECTION_STRINGS = [
    {
        'key': 'locations',
        'value': 'username/password@'\
            'placeholder.url.com'
    },
    {
        'key': 'sec',
        'value': 'username/password2@'\
            'placeholder.url.com'
    }
]
LIST_VIEW_URL_INFO = [
    {'url_ref': 'samples_manager:experiments_list', 'args': []},
    {'url_ref': 'samples_manager:experiments_shared_list', 'args': []},
    {'url_ref': 'samples_manager:experiment_samples_list', 'args': [1]},
    {'url_ref': 'samples_manager:compounds_list', 'args': []},
    {'url_ref': 'samples_manager:dosimeters_list', 'args': []},
    {'url_ref': 'samples_manager:experiment_users_list', 'args': [1]},
    {'url_ref': 'samples_manager:users_list', 'args': []},
    {'url_ref': 'samples_manager:irradiations_list', 'args': []},
    {'url_ref': 'samples_manager:fluence_factors_list', 'args': []},
    {'url_ref': 'samples_manager:dosimetry_results_list', 'args': []},
    {'url_ref': 'samples_manager:boxes_list', 'args': []},
    {'url_ref': 'samples_manager:box_items_list',  'args': [1]}
]
ALERT_MESSAGES = {
    'invalid_operation_max_number': 'Invalid operation. Maximum number of selected elements exceeded. Limit is ',
    'invalid_operation': 'Invalid operation. Either items with the requested '\
		'IDs don\'t exist in the database or the number of selected items is incorrect.',
}


def is_number(num):
    """Checks if value is number"""
    try:
        float(num)
        return True
    except:
        return False


def get_cern_timezone():
    """Calculate cern timezone"""
    return pytz.timezone('Europe/Zurich')


def get_utc_timezone():
    """Calculate UTC timezone"""
    return pytz.UTC


def datetime_switch_timezone(datetime, tz=None):
    """Switches datetime timezone."""
    if tz is None:
        tz = get_utc_timezone()
    result = datetime_aware_to_naive(datetime)
    result = datetime_naive_to_aware(result, tz)
    return result


def get_aware_datetime(tz=None):
    """Calculates aware datetime using timezone."""
    if tz is None:
        tz = get_utc_timezone()
    result = dt.now(tz)
    return result


def get_aware_cern_datetime():
    """Calculates aware datetime using cern timezone."""
    tz = get_cern_timezone()
    result = dt.now(tz)
    return result


def get_past_aware_datetime(num_days, tz=None):
    """Calculates past aware datetime using timezone."""
    if tz is None:
        tz = get_utc_timezone()
    result = dt.now(tz) - timedelta(num_days)
    return result


def get_naive_datetime():
    """Calculates naive datetime."""
    result = dt.now()
    return result


def datetime_aware_to_naive(datetime):
    """Returns datetime as naive by removing timezone."""
    result = datetime.replace(tzinfo=None)
    return result


def datetime_naive_to_aware(datetime, tz=None):
    """
    Returns datetime as naive by removing timezone. This function uses
    timezone.localize() because datetime.replace doesn't work as expected.
    """
    if tz is None:
        tz = get_utc_timezone()
    fmt = '%Y-%m-%d %H:%M:%S %Z%z'
    result = tz.localize(datetime)
    return result


def datetime_as_timezone(datetime, tz=None):
    """Changes datetime timezone. UTC by default."""
    if tz is None:
        tz = get_utc_timezone()
    result = datetime.astimezone(tz)
    return result


def datetime_as_cern_timezone(datetime):
    """Changes datetime timezone to Geneva timezone."""
    tz = get_cern_timezone()
    result = datetime.astimezone(tz)
    return result


def get_model_classes():
    """Gets model classes."""
    import django
    result = [x for x in django.apps.apps.get_models() if \
        str(x).find(APP_NAME + '.models') > -1]
    return result


def get_model_class_names():
    """Gets model class names."""
    models = get_model_classes()
    result = [get_model_name_from_class(x) for x in models]
    return result


def get_model_name_from_class(model_class):
    """
    Gets model class from model name.
    
    Typical class name "<class 'samples_manager.models.Experiment'>".
    The function extracts the last word after a period. In the case 
    above 'Experiment'.
    """
    result = str(model_class).split('.')[-1][:-2].lower()
    return result


def get_model_class_from_name(name):
    """Gets model class from name."""
    result = None
    name = name.lower()
    models = get_model_classes()
    for model in models:
        is_match = (name in get_model_name_from_class(model))
        if is_match:
            return model
    return None


def get_model_name_from_instance(instance):
    """Gets model name from model instance."""
    result = None
    model = type(instance)
    result = get_model_name_from_class(model)
    return result


def get_model_name_from_url(url):
    """Gets model name from url."""
    result = None
    url = url.lower()
    splitted_url = url.split('/')
    model_names = get_model_class_names()
    for x in splitted_url:
        for name in model_names:
            if name in x:
                result = name
    return result


def get_view_list_name_from_model_name(name):
    """Returns view list name from model name."""
    result = None
    if name == 'experiment':
        result = 'experiments_list'
    elif name == 'sample':
        result = 'experiment_samples_list'
    elif name == 'compound':
        result = 'compounds_list'
    elif name == 'dosimeter':
        result = 'dosimeters_list'
    elif name == 'user':
        result = 'users_list'
    elif name == 'irradiation':
        result = 'irradiations_list'
    elif name == 'fluence_factor':
        result = 'fluence_factors_list'
    elif name == 'dosimetry_result':
        result = 'dosimetry_results_list'
    elif name == 'box':
        result = 'boxes_list'
    return result


def get_view_list_name_from_url(url):
    """Returns view list name from url."""
    splitted_url = url.split('/')
    for view in LIST_VIEW_URL_INFO:
        view_url = reverse(view['url_ref'], args=view['args'])
        splitted_view_url = view_url.split('/')
        has_same_length = (len(splitted_url) == len(splitted_view_url))
        if has_same_length:
            is_match_url = True
            for i, e in enumerate(splitted_view_url):
                # Continue only if values match and value isn't a 
                # variable in the url.
                exit_loop = (not is_number(e) and \
                    splitted_url[i] != splitted_view_url[i])
                if exit_loop:
                    is_match_url = False
                    break
            if is_match_url:
                # Return list view name as in urls.py
                result = view['url_ref'].split(':')[1]
                return result
    return None


def extract_ids_from_url(url):
    """Extracts ids from url."""
    result = []
    splitted_url = url.split('/')
    for e in splitted_url:
        if is_number(e):
            result.append(e)
    return result


def get_equipment_id_from_instance(equipment):
    """Gets equipment id from instance."""
    model_name = get_model_name_from_instance(equipment)
    result = ''
    if model_name == 'sample':
        result = equipment.set_id
    elif model_name == 'dosimeter':
        result = equipment.dos_id
    elif model_name == 'box':
        result = equipment.box_id
    else:
        return None
    return result


def generate_number_list(start, end, excluded=[]):
    """
    Generates number list in range excluding 
    specified values.
    """
    result = np.arange(start, end + 1, 1)
    result = list(result[~np.isin(result, excluded)])
    return result


def get_random_values_from_list(array, length, replace=False):
    """Selects n random values from array."""
    if length > len(array):
        length = len(array)
    result = list(np.random.choice(array, size=(length), replace=replace))
    return result


def is_admin(user):
    """Returns if user is admin."""
    result = (user.role == 'Admin')
    return result


def get_checked_elements(request):
    """Get checked elements from HTTP request."""
    result = []
    if request.method == 'POST':
        result = request.POST.getlist('checks[]')
    elif request.method == 'GET':
        result = request.GET.getlist('checks[]')
    return result


def checked_elements_are_valid(checked_elements, action_type, Model, max_num=None):
    """
    Validates if the elements checked are valid for the 
    selected action.
    """
    result = dict()
    result['valid'] = True
    result['msg'] = None
    max_num = len(checked_elements) if max_num is None else max_num
    if action_type == 'single':
        if len(checked_elements) == 1:
            pk = checked_elements[0]
            valid = (Model.objects.filter(pk=pk).count() == 1)
        else:
            result['msg'] = ALERT_MESSAGES['invalid_operation']
            result['valid'] = False
    elif action_type == 'group':
        if (len(checked_elements) >= 1):
            if (len(checked_elements) <= max_num):
                for pk in checked_elements:
                    valid = (Model.objects.filter(pk=pk).count() == 1)
                    if not valid:
                        result['valid'] = False
                        break
            else:
                result['msg'] = ALERT_MESSAGES['invalid_operation_max_number'] \
                    + str(max_num) + '.'
                result['valid'] = False
        else:
            result['msg'] = ALERT_MESSAGES['invalid_operation']
            result['valid'] = False
    return result


def get_experiment_users(experiment):
    """Gets experiment's users including responsible."""
    users = list(experiment.users.all())
    if experiment.responsible not in users:
        users.append(experiment.responsible)
    return users


def get_db_connection_string(connection_str):
    """
    Retrieves database connection string depending on
    connection identifier.
    """
    for connection in DB_CONNECTION_STRINGS:
        if connection_str in connection['key']:
            return connection['value']
    return None


def get_locations_from_db(str=None, num_results=None):
    """Retrieves list of locations at CERN from oracle database."""
    result = ()
    try:
        # Database connection removed from settings to not affect tests.
        connection_str = get_db_connection_string('locations')
        connection = cx_Oracle.connect(connection_str)
        cursor = connection.cursor()
        if str is None:
            query = 'SELECT NOM_LOCAL FROM "AISPUB".'\
                '"LOC_CL_CUR_LOCAL_INFO" ORDER BY NOM_LOCAL'
        else:
            query = 'SELECT NOM_LOCAL FROM "AISPUB".'\
                '"LOC_CL_CUR_LOCAL_INFO" WHERE NOM_LOCAL LIKE '\
                '\'%' + str +  '%\' ORDER BY NOM_LOCAL'
        cursor.execute(query)
    except OperationalError:
        return result

    if type(num_results) is int or type(num_results) is float:
        result = cursor.fetchmany(num_results)
    else:
        result = cursor.fetchall()
    cursor.close()
    connection.close() 
    return result


def get_locations_choices():
    """Retrieves list of locations in choice format for Model fields."""
    result = []
    locations = get_locations_from_db()

    for location in locations:
        tuple_pair = (location[0], location[0])
        result.append(tuple_pair)
    result.append(('unknown', 'Other. Not in list.'))
    
    return tuple(result)


def get_sec_dates_from_irradiation(irradiation):
    """
    Returns dates for first and last positive sec measurement
    in date range.
    """
    connection_str = get_db_connection_string('sec')
    connection_db = cx_Oracle.connect(connection_str)
    cursor = connection_db.cursor()
    result = dict()
    # From UTC to CERN timezone because SEC database has times 
    # stored in CERN timezone.
    local_date_in = get_aware_cern_datetime() if irradiation.date_in \
        is None else datetime_as_cern_timezone(irradiation.date_in)
    local_date_out = get_aware_cern_datetime() if irradiation.date_out \
        is None else datetime_as_cern_timezone(irradiation.date_out)
    local_date_in = local_date_in.strftime('%Y-%m-%d %H:%M:%S')
    local_date_out = local_date_out.strftime('%Y-%m-%d %H:%M:%S')
    partial_query = 'SELECT TIMESTAMP FROM PS_IRRAD_USER.SEC_DATA WHERE '\
        'SEC_ID = \'SEC_01\' AND SEC_VALUE > 0 AND TIMESTAMP > TO_DATE(\'' \
        + str(local_date_in) + '\', \'YYYY-MM-DD HH24:MI:SS\') AND '\
        'TIMESTAMP < TO_DATE(\''+ str(local_date_out) + '\', \''\
        'YYYY-MM-DD HH24:MI:SS\') ORDER BY TIMESTAMP'
    asc_query = partial_query + ' ASC FETCH FIRST 1 ROWS ONLY'
    desc_query = partial_query + ' DESC FETCH FIRST 1 ROWS ONLY'
    try:
        cursor.execute(asc_query)
        asc_rows = cursor.fetchall()
        cursor.execute(desc_query)
        desc_rows = cursor.fetchall()
        # Database returns naive timezone
        local_tz = get_cern_timezone()
        # Add local timezone before turning to UTC
        cond = (len(asc_rows) > 0 and len(desc_rows) > 0)
        date_first_sec = None
        date_last_sec = None
        if cond:
            date_first_sec = datetime_naive_to_aware(asc_rows[0][0], local_tz)
            date_last_sec = datetime_naive_to_aware(desc_rows[0][0], local_tz)
            date_first_sec = datetime_as_timezone(date_first_sec)
            date_last_sec = datetime_as_timezone(date_last_sec)
    except OperationalError:
        logging.error('Error calculating sec_dates.')
    result['date_first_sec'] = date_first_sec
    result['date_last_sec'] = date_last_sec
    return result


def is_in_infoream_db(equipment_id):
    """Checks if equipment is in the inforEAM database."""
    infoream_id = get_infoream_id(equipment_id)
    result = (read_equipment({'infoream_id': infoream_id})['response'] is not None)


def search_re_in_string(regex, str):
    """Looks for pattern in string using regular expression."""
    return (re.search(regex, str) is not None)


def get_equipment_type(equipment_id, case=0):
    """Checks if equipment id is box, dosimeter or sample."""
    if case < 1:
        regex = r'^((SET|BOX)-[\d]{6}|DOS-[\d]{6}(\.(\d{1,3})){0,5})$'
    elif case < 2:
        regex = r'^((SET|BOX)-[\d]{6}|DOS-[\d]{6}(\.(\d{1,3})){1,5})$'
    else:
        regex = r'^(SET|BOX|DOS)-[\d]{6}$'

    is_valid = search_re_in_string(regex, str(equipment_id))

    if is_valid:
        prefix = equipment_id.split('-')[0]
        if prefix == 'SET':
            result = 'sample'
        elif prefix == 'DOS':
            result = 'dosimeter'
        elif prefix == 'BOX':
            result = 'box'
        else:
            result = None
    else:
        result = None

    return result


def get_set_id_from_number(id_num):
    """Builds SET ID from number."""
    result = 'SET-' + ('0'*(SET_ID_NUM_DIGITS - \
        (math.floor(math.log10(id_num)) + 1))) + str(id_num)
    return result


def get_ids_from_checked_equipments(checked_pks, equipment_type):
    """Returns ids from checked equipments html."""
    result = []
    for pk in checked_pks:
        equipment_id = None
        model = get_model_class_from_name(equipment_type)
        if equipment_type == 'sample':
            equipment_id = model.objects.get(pk=pk).set_id
        elif equipment_type == 'dosimeter':
            equipment_id = model.objects.get(pk=pk).dos_id
        elif equipment_type == 'box':
            equipment_id = model.objects.get(pk=pk).box_id
        result.append(equipment_id)
    return result


def equipment_ids_are_correct_type(pk_list, equipment_type):
    """Checks if equipment ids are the same as equipment_type."""
    result = True
    has_items = (len(pk_list) > 0)
    if has_items:
        equipment_id_list = \
            get_ids_from_checked_equipments(pk_list, equipment_type)
        for equipment_id in equipment_id_list:
            not_same_type = (get_equipment_type(equipment_id) != \
                equipment_type)
            if not_same_type:
                result = False
                break
    else:
        result = False
    return result


def get_infoream_id(equipment_id):
    """Generates infoream id format."""
    equipment_type = get_equipment_type(equipment_id)
    result = ''
    if equipment_type is not None:
        if equipment_type == 'sample':
            prefix = 'PXXISET001-CR'
        elif equipment_type == 'dosimeter':
            prefix = 'PXXIDOS001-CR'
        elif equipment_type == 'box':
            prefix = 'HCPWPDI002-CR'
        else:
            result = None
        code = equipment_id.split('-')[1]
    else:
        result = None

    if result is not None:
        result = prefix + code

    return result


def apply_infoream_actions(actions):
    """Applies inforEAM actions passed as argument."""
    for item in actions:
        if item['action'] == 'create_equipment':
            response = create_equipment(item)
        elif item['action'] == 'update_equipment':
            response = update_equipment(item)
        elif item['action'] == 'detach_parent':
            response = detach_parent(item)
        elif item['action'] == 'attach_parent':
            response = attach_parent(item)
        elif item['action'] == 'create_comment':
            response = create_comment(item)
        elif item['action'] == 'update_comment':
            response = update_comment(item)
        elif item['action'] == 'print_label_equipment':
            response = print_label_equipment(item)
        else:
            response = None

        is_unrecognized = (response is None)
        if is_unrecognized:
            logging.info('Action ' + item['action'] + ' isn\'t a '\
                'recognized inforEAM action.')
        is_infoream_error = ('response' not in response or (response['response'] \
            is None and response['response'] == 500))
        if is_infoream_error:
            logging.info(str(item['action']) + ' ' + \
                str(response['status_code']) + ' No response. inforEAM error.')
            return response
        else :
            logging.info(str(item['action']) + '; ' + \
                str(response['status_code']) + '; ' + \
                str(response['response']) + '; ')

    return response


def get_infoream_credentials(**kwargs):
    """Centralized function to access inforEAM credentials."""
    settings = kwargs.get('settings', None)
    wsdl = 'placeholder.url.com'
    session = Session()
    # Set to True in production
    session.verify = False
    transport = Transport(session=session)
    if settings is None:
        client = Client(wsdl=wsdl, transport=transport)
    else:
        client = Client(wsdl=wsdl, transport=transport, settings=settings)
    credetials_type = client.get_type('ns0:credentials')
    cred = credetials_type(password= 'password', username='username')
    return cred, client


def get_query(query_string, search_fields):
    """
    Returns a query, that is a combination of Q objects. 
    That combination aims to match all keywords on all fields
    contained in search_fields.
    """
    query = None  # Query to search for every search term
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None  # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{'%s__icontains' % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query


def filter_model_objects_by_str(query_str, Model, recursion_level=0, instance_list=None):
    """
    Filters model object by string. It compares string with all comparable 
    model attributes. If instance_list is provided, it ony returns from 
    instance_list. It also maintains the order of elements from instace_list.
    """
    search_field_types = ['CharField', 'TextField', 'PositiveIntegerField', \
        'DecimalField', 'EmailField', 'DateTimeField']
    model_names = get_model_class_names()
    model_name = get_model_name_from_class(Model)
    recursion_level = recursion_level + 1
    if model_name not in model_names:
        return None
    if query_str.strip():
        fields = Model._meta.fields
        query_result = []
        # Check if maximum recursion level has met
        if recursion_level < MAX_FILTER_RECURSION_LEVEL:
            # Find foreign keys and run filter recursively 
            for field in fields:
                field_type = str(type(field)) 
                if 'ForeignKey' in field_type:
                    foreign_model = get_model_class_from_name(\
                        field.deconstruct()[3]['to'].split('.')[1])
                    # Recursive call
                    foreign_matches = \
                        filter_model_objects_by_str(query_str, foreign_model, 
                            recursion_level)
                    foreign_matches_ids = [e.pk for e in foreign_matches]
                    entry_query = Q(**{
                        '%s__id__in' % field.name: foreign_matches_ids})
                    matches = Model.objects.filter(entry_query)
                    query_result = query_result + list(matches)
        fields = [field.name for field in fields 
            if any(x in str(type(field)) for x in search_field_types)]
        entry_query = get_query(query_str,fields)
        query_result = query_result + list(Model.objects.filter(entry_query))
        # Remove duplicates
        query_result = list(set(query_result))
    else:
        query_result = Model.objects.all()

    # If a list is provided only return items from list.
    result = query_result
    if instance_list is not None:
        result = []
        for e in instance_list:
            if e in query_result:
                result.append(e)

    return result


def read_equipment(data):
    """Reads equipment information in inforEAM."""
    result = dict()
    cred, client = get_infoream_credentials()
    try:
        result['response'] = client.service.readEquipment(data['infoream_id'], cred)
        result['status_code'] = 200

        if result['response'].code:
            result['code'] =  result['response'].code
        else:
            result['code'] =  ' - '

        if result['response'].description:
            result['description'] = result['response'].description
        else:
            result['description'] =  ' - '

        if result['response'].hierarchyLocationCode:
            result['hierarchyLocationCode'] = result['response']\
                .hierarchyLocationCode
        else:
            data['hierarchyLocationCode'] =  ' - '
    
        if result['response'].equipmentValue:
            result['equipmentValue'] = result['response'].equipmentValue
        else:
            result['equipmentValue'] = ' - '

        if result['response'].serialNumber:
            result['serialNumber'] = result['response'].serialNumber
        else:
            result['serialNumber'] =  ' - '

        if result['response'].hierarchyLocationCode:
            result['hierarchyLocationCode'] = result['response'].hierarchyLocationCode
        else:
            result['hierarchyLocationCode'] =  ' - '

        if result['response'].userDefinedFields.udfnum07:
            result['udfnum07'] = result['response'].userDefinedFields.udfnum07
        else:
            result['udfnum07'] =  ' - '

        if result['response'].userDefinedFields.udfnum08:
            result['udfnum08'] = result['response'].userDefinedFields.udfnum08
        else:
            result['udfnum08'] =  ' - '

        if result['response'].userDefinedFields.udfnum09:
            result['udfnum09'] = result['response'].userDefinedFields.udfnum09
        else:
            result['udfnum09'] =  ' - '

        if result['response'].userDefinedFields.udfnum10:
            result['udfnum10'] = result['response'].userDefinedFields.udfnum10
        else:
            result['udfnum10'] =  ' - '

        if result['response'].userDefinedFields.udfchar21:
            result['udfchar21'] = result['response'].userDefinedFields.udfchar21
        else:
            result['udfchar21'] =  ' - '

        if result['response'].userDefinedFields.udfchar22:
            result['udfchar22'] = result['response'].userDefinedFields.udfchar22
        else:
            result['udfchar22'] =  ' - '
    except:
        result['status_code'] = 500
        result['response'] = None

    return result


def read_equipment_list(data):
    """Reads multiple equipment information in inforEAM."""
    result = dict()
    cred, client = get_infoream_credentials()
    try:
        result['response'] = client.service.readEquipmentBatch(data['infoream_ids'], cred)
        result['status_code'] = 200
    except Fault as fault:
        result['status_code'] = 500
        result['response'] = None

    return result


def read_equipment_list(data):
    """Reads multiple equipment information in inforEAM."""
    result = dict()
    cred, client = get_infoream_credentials()
    try:
        result['response'] = client.service.readEquipmentBatch(data['infoream_ids'], cred)
        result['status_code'] = 200
    except Fault as fault:
        result['status_code'] = 500
        result['response'] = None

    return result


def read_equipment_list_simulated(data):
    """Simulate reading multiple equipment information from inforEAM."""
    result = {
        'response':[],
        'status_code': 200
        }
    for requested_id in data['infoream_ids']:
            if requested_id in data['stored_infoream_ids']:
                result['response'].append({
                    'response': {
                        'code': requested_id
                    }
                })
            else:
                result['response'].append({
                    'response': None,
                    'errorMessage': 'equipment record couldn\'t be found'
                })

    return result


def generate_set_id_simulated(samples_numbers, sim_infoream, min_idm):
    """Simulation. Generates a set_id for a sample."""
    samples_numbers.sort(reverse=False)
    is_empty = (len(samples_numbers) > 0)
    max_in_idm = samples_numbers[-1] if is_empty else min_idm
    last_id_num = int('9'*6)
    id_nums = generate_number_list(min_idm, max_in_idm, samples_numbers)
    id_nums = get_random_values_from_list(id_nums, 10)
    end_num = max_in_idm
    while (True):
        start_num = end_num + 1
        end_num = (start_num + 20 - len(id_nums))
        over_max_number = (end_num > last_id_num)
        if over_max_number:
            end_num = last_id_num
        id_nums = id_nums + generate_number_list(start_num, end_num)
        print('selection: ', id_nums)
        set_ids = [get_set_id_from_number(num) for num in id_nums]
        infoream_ids = [get_infoream_id(set_id) for set_id in set_ids]
        if len(infoream_ids) == 0:
            return None

        stored_set_ids = [get_set_id_from_number(num) for num in sim_infoream]
        stored_infoream_ids = [get_infoream_id(set_id) for set_id in stored_set_ids]
        data = {
            'infoream_ids': infoream_ids,
            'stored_infoream_ids': stored_infoream_ids
        }
        response = read_equipment_list_simulated(data)
        if response['status_code'] == 500:
            return None
        response = response['response']
        for i, item in enumerate(response):
            if item['response'] is None:
                if 'errorMessage' in item:
                    error_substr = 'Connection refused'
                    not_found_substr = 'equipment record couldn\'t be found'
                    if not_found_substr in item['errorMessage']:
                        return set_ids[i]
                    elif error_substr in item['errorMessage']:
                        return None
        id_nums = []


def run_assign_set_id_simulation():
    """Simulation of set id assignment"""
    #Parameters
    num_idm_missing = 30
    min_idm = 3200
    max_idm = 4001
    num_infroeam_missing = 30
    min_infoream = 2000
    max_infoream = 3990
    #Simulated values
    complete_idm = generate_number_list(min_idm, max_idm)
    complete_infoream = generate_number_list(min_infoream, max_infoream)
    old_spots_idm = get_random_values_from_list(complete_idm, num_idm_missing)
    old_spots_infoream = get_random_values_from_list(complete_infoream, \
        num_infroeam_missing)
    sim_idm = generate_number_list(min_idm, max_idm, old_spots_idm)
    sim_infoream = generate_number_list(min_infoream, max_infoream, \
        old_spots_infoream)
    old_spots = list(filter(lambda num: (num not in sim_infoream), old_spots_idm))
    #Simulation execution
    continue_loop = True
    i = 0
    id_num = None
    while(continue_loop):
        print('\n\n###ITERATION-' + str(i) + '###')
        set_id = generate_set_id_simulated(sim_idm, sim_infoream, min_idm)
        id_num = int(set_id[4:])
        print('min_idm: ', min_idm)
        print('max_idm: ', max_idm)
        print('min_infoream: ', min_infoream)
        print('min_infoream: ', max_infoream)
        print('oldspots_idm: ', old_spots_idm)
        print('oldspots_infoream: ', old_spots_infoream)
        print('old spots: ', old_spots)
        print('length idm: ', len(sim_idm))
        print('length infoream: ', len(sim_infoream))
        print('id_num: ', id_num)
        print('id_num_not_in_idm: ', (id_num not in sim_idm))
        print('id_num_not_in_infoream: ', (id_num not in sim_infoream))
        print('id_num_over_max_idm: ', (id_num > max_idm))
        print('id_num_over_max_infoream: ', (id_num > max_infoream))

        if id_num not in sim_idm and id_num not in sim_infoream and id_num in old_spots_idm:
            if id_num in old_spots:
                old_spots.remove(id_num)
            old_spots_idm.remove(id_num)
            sim_idm.append(id_num)
            sim_idm.sort(reverse=False)
        elif id_num not in sim_idm and id_num not in sim_infoream and id_num not in old_spots_idm:
            sim_idm.append(id_num)
            sim_idm.sort(reverse=False)
        else:
            print('ERROR. Simulation stopped.')
            return
        continue_loop = False
        for n in old_spots_idm:
            if n not in sim_infoream:
                continue_loop = True
        i += 1


def create_equipment(data):
    """Creates equipment in inforEAM."""
    result = dict()
    settings = Settings(strict=False, xml_huge_tree=True)
    cred, client = get_infoream_credentials(settings=settings)
    equipment_type = client.get_type('ns0:equipment')
    current_date = get_aware_datetime().strftime('%d-%b-%Y')
    udf = {}
    udf['udfnum08'] = data['width']
    udf['udfnum09'] = data['height']
    udf['udfnum10'] = data['weight']
    udf['udfchar21'] = 'ACC_COMPONENT'
    udf['udfchar22'] = data['material']
    if 'length' in data:
        udf['udfnum07'] = data['length']
    else:
        udf['udfnum07'] = 0
    equipment = equipment_type(
        code= data['infoream_id'],
        serialNumber= data['equipment_id'],
        categoryDesc= data['category_desc'],
        comissionDate= current_date,
        departmentCode= 'XI01',
        departmentDesc = 'Experiments - IRRAD',
        stateCode= 'GOOD',
        stateDesc= 'Bonn',
        statusCode = 'I',
        statusDesc= 'En fabrication',
        typeCode= 'A',
        typeDesc= 'Equipment',
        description= data['category_desc'],
        hierarchyLocationCode= data['location'],
        userDefinedList= [],
        userDefinedFields= udf
    )
    with client.settings(raw_response=True):
        try:
            result['response'] = client.service.createEquipment(equipment, cred, '')
            if result['response'].ok:
                result['status_code'] = 200
            else:
                result['status_code'] = 500
                result['response'] = None
        except Fault as fault:
            result['status_code'] = 500
            result['response'] = None
    return result


def update_equipment(data):
    """Updates information of equipment in inforEAM."""
    result = dict()
    cred, client = get_infoream_credentials()
    equipment_type = client.get_type('ns0:equipment')
    current_date = get_aware_datetime().strftime('%d-%b-%Y')
    udf = {}
    udf['udfnum08'] = data['width']
    udf['udfnum09'] = data['height']
    udf['udfnum10'] = data['weight']
    udf['udfchar21'] = 'ACC_COMPONENT'
    udf['udfchar22'] = data['material']
    if 'length' in data:
        udf['udfnum07'] = data['length']
    else:
        udf['udfnum07'] = 0
    equipment = equipment_type(
        code= data['infoream_id'],
        serialNumber= data['equipment_id'],
        categoryDesc= data['category_desc'],
        comissionDate= current_date,
        departmentCode= 'XI01',
        departmentDesc = 'Experiments - IRRAD',
        stateCode= 'GOOD',
        stateDesc= 'Bonn',
        statusCode = 'I',
        statusDesc= 'En fabrication',
        typeCode= 'A',
        typeDesc= 'Equipment',
        description= data['category_desc'],
        hierarchyLocationCode= data['location'],
        userDefinedList= [],
        userDefinedFields= udf
    )
    try:
        result['response'] = client.service.updateEquipment(equipment, cred)
        result['status_code'] = 200
    except Fault as fault:
        logging.error(fault)
        result['status_code'] = 500
        result['response'] = None
    return result


def delete_equipment(data):
    """Deletes equipment in inforEAM."""
    result = dict()
    cred, client = get_infoream_credentials()
    equipment_type = client.get_type('ns0:equipment')
    equipment = equipment_type(
        code = data['infoream_id'],
        userDefinedList=[]
    )
    try:
        result['response'] = client.service.deleteEquipment(equipment, cred)
        result['status_code'] = result['response'].status_code
    except Fault as fault:
        result['status_code'] = 500
        result['response'] = None
    return result


def attach_parent(data):
    """
    Creates parent child relationship between equipments 
    in inforEAM.
    """
    result = dict()
    cred, client = get_infoream_credentials()
    equipment_type = client.get_type('ns0:equipment')
    equipment = equipment_type(
        code = data['infoream_id_child'], 
        hierarchyAssetCode = data['infoream_id_parent'], 
        hierarchyAssetCostRollUp = 'true', 
        hierarchyAssetDependent = 'true', 
        userDefinedList= [])
    try:
        result['response'] = client.service.updateEquipment(equipment, cred)
        result['status_code'] = 200
    except Fault as fault:
        result['status_code'] = 500
        result['response'] = None
    return result


def detach_parent(data):
    """
    Deletes parent child relationship between equipments 
    in inforEAM.
    """
    result = dict()
    cred, client = get_infoream_credentials()
    equipment_type = client.get_type('ns0:equipment')
    equipment = equipment_type(
        code = data['infoream_id'] , 
        hierarchyAssetCode = '', 
        hierarchyAssetCostRollUp = 'true', 
        hierarchyAssetDependent = 'true', 
        userDefinedList= [])
    try:
        result['response'] = client.service.updateEquipment(equipment, cred)
        result['status_code'] = 200
    except Fault as fault:
        result['status_code'] = 500
        result['response'] = None
    return result


def read_comment(data):
    """Reads equipment comment from inforEAM."""
    result = dict()
    cred, client = get_infoream_credentials()
    comment_type = client.get_type('ns0:comment')
    comment = comment_type(
        entityCode = 'OBJ',
        entityKeyCode= data['infoream_id'], 
        created = 'false', 
        updated = 'false')
    try:
        result['response'] = client.service.readComments(comment, cred)
        result['status_code'] = 200
        if len(result['response']) > 0:
            result['status_code'] = 200
        else:
            result['status_code'] = 500
            result['response'] = None
    except Fault as fault:
        result['status_code'] = 500
        result['response'] = None
    return result

def create_comment(data):
    """
    Creates equipment comment in inforEAM. This call with create comment 
    independently if the entityKeyCode previously exists or not.
    """
    result = dict()
    cred, client = get_infoream_credentials()
    comment_type = client.get_type('ns0:comment')
    comment = comment_type(
        entityCode = 'OBJ',
        entityKeyCode= data['infoream_id'],
        lineNumber= data['line_number'],
        text = data['text'],
        typeCode = '*',
        created = 'false',
        updated = 'false')
    try:
        result['response'] = client.service.createComment(comment, cred)
        result['status_code'] = 200
    except Fault as fault:
        result['status_code'] = 500
        response = None
    return result


def update_comment(data):
    """
    Updates equipment comment in inforEAM. LineNumber determines 
    which comment to update.
    """
    result = dict()
    cred, client = get_infoream_credentials()
    comment_type = client.get_type('ns0:comment')
    comment = comment_type(
        entityCode = 'OBJ',
        entityKeyCode= data['infoream_id'],
        lineNumber= data['line_number'],
        text = data['text'],
        typeCode = '*',
        created = 'false',
        updated = 'false')
    try:
        result['response'] = client.service.updateComment(comment, cred)
        result['status_code'] = 200
    except Fault as fault:
        result['status_code'] = 500
        response = None
    return result


def get_category_desc_from_serial_number(serial_number):
    """
    Returns equipment's category description corresponding 
    to serial number. The values are based on previous records 
    from the inforEAM database.
    """
    equipment_type = get_equipment_type(serial_number)
    result = None
    if equipment_type == 'sample':
        result = 'Sample Set'
    elif equipment_type == 'dosimeter':
        result = 'IRRAD Dosimeters'
    elif equipment_type == 'box':
        result = 'IRRAD Container'
    return result


def clear_equipment_serial_number(serial_number):
    """
    Clears equiipment's serial number leaving the 
    rest of the data intact. If the equipment doesn't 
    exist in inforEAM, then it doesn't perform any action.
    """
    result = None
    equipment_id = get_infoream_id(serial_number)
    category_desc = get_category_desc_from_serial_number(serial_number)
    is_in_infoream = is_equipment_in_db(equipment_id)
    if is_in_infoream:
        data = dict()
        data['infoream_id'] = equipment_id
        response = read_equipment(data)['response']
        data['infoream_id'] = equipment_id
        data['width'] = response['userDefinedFields']['udfnum08']
        data['height'] = response['userDefinedFields']['udfnum09']
        data['weight'] = response['userDefinedFields']['udfnum10']
        data['equipment_id'] = ''
        data['category_desc'] = category_desc
        update_equipment(data)
        result = equipment_id 
    return result

def is_equipment_in_db(equipment_id):
    """Checks if equipment is in the inforEAM database."""
    data = dict()
    data['infoream_id'] = equipment_id
    response = read_equipment(data)
    result = (response['response'] is not None and \
        response['response']['serialNumber'] is not None)
    return result


def print_label_equipment(data):
    """Sends SOAP request to print equipment label remotely."""
    result = dict()
    cred, client = get_infoream_credentials()
    data['print_variables'] = {
        'code': data['infoream_id'],
        'fields': [{
            'entry': {
                'key': 'serialNumber',
                'value': data['equipment_id'],
            }
        }]
    }
    request_data = {
        'barcodingSoftware': 'NiceLabel',
        'batch': '0',
        'printQty': data['print_quantity'],
        'printVariables': data['print_variables'],
        'printerPath': data['printer_path'],
        'templateCode': data['template_code'],
        'type': 'E',
    }
    try:
        result['response'] = client.service.createPrintRequest(
            request_data, cred)
        result['status_code'] = 200
    except Fault as fault:
        logging.error(fault)
        result['status_code'] = 500
        result['response'] = None
    return result


def calc_acc_sec_in_range(utc_date_in, utc_date_out=None):
    """
    Calculates accumulated SEC for date range. If date_out is None, it uses
    current timestamp. Expects dates in UTC timezone. 
    """
    connection_str = get_db_connection_string('sec')
    connection_db = cx_Oracle.connect(connection_str)
    cursor = connection_db.cursor()

    if utc_date_in is None:
        return 0
    elif utc_date_out is None:
        utc_date_out = get_aware_datetime()
    local_date_in = datetime_as_cern_timezone(utc_date_in)
    local_date_out = datetime_as_cern_timezone(utc_date_out)
    local_date_in = local_date_in.strftime('%Y-%m-%d %H:%M:%S')
    local_date_out = local_date_out.strftime('%Y-%m-%d %H:%M:%S')
    if 'pdbr' in connection_str:
        query = 'SELECT SUM(SEC_VALUE) FROM PS_IRRAD_USER.SEC_DATA WHERE '\
            'SEC_ID = \'SEC_01\' AND TIMESTAMP > TO_DATE(\''\
            + str(local_date_in) + '\', \'YYYY-MM-DD HH24:MI:SS\') AND ' \
            'TIMESTAMP < TO_DATE(\'' + str(local_date_out) + '\', \''\
            'YYYY-MM-DD HH24:MI:SS\')'
    else:
        #Option included for automated Selenium tests. 
        query = 'SELECT SUM(SEC_VALUE) FROM SEC_DATA WHERE '\
            'SEC_ID = "SEC_01" AND TIMESTAMP>"' + str(local_date_in) + \
            '" AND TIMESTAMP<"' + str(local_date_out) + ';'
    table_not_present = True
    while(table_not_present):
        try:
            cursor.execute(query)
            table_not_present = False
        except OperationalError:
            cursor.execute('CREATE TABLE SEC_DATA (SEC_ID CHAR(10), '\
                'SEC_VALUE FLOAT(20, 17), TIMESTAMP TIMESTAMP);')

    sec_sum = cursor.fetchall()[0][0]
    if sec_sum is None:
        sec_sum = 0
    return sec_sum


def update_previous_irradiations_sec(irradiations):
    """Updates sec of irradiaitons and their children relations."""
    connection_str = get_db_connection_string('sec')
    connection_db = cx_Oracle.connect(connection_str)
    cursor = connection_db.cursor()
    data = dict()
    data['sec_data'] = []

    for irradiation in irradiations:
        if 'inbeam' in irradiation.status.lower():
            has_no_date = (irradiation.date_in is None)
            if has_no_date:
                irradiation.date_in = get_aware_datetime()
            # To Geneva time because SEC database has times stored in local timezone
            local_date_in = datetime_as_cern_timezone(irradiation.date_in)
            timestamp = local_date_in.strftime('%Y-%m-%d %H:%M:%S')
            if 'pdbr' in connection_str:
                query = 'SELECT SUM(SEC_VALUE) FROM PS_IRRAD_USER.SEC_DATA WHERE '\
                    'SEC_ID = \'SEC_01\' AND TIMESTAMP > TO_DATE(\''\
                    + str(timestamp) + '\', \'YYYY-MM-DD HH24:MI:SS\')'
            else:
                #Option included for automated Selenium tests. 
                query = 'SELECT SEC_VALUE FROM SEC_DATA WHERE '\
                    'SEC_ID = "SEC_01" AND TIMESTAMP>"' + str(timestamp) + '";'
            table_not_present = True
            while(table_not_present):
                try:
                    cursor.execute(query)
                    table_not_present = False
                except OperationalError:
                    cursor.execute('CREATE TABLE SEC_DATA (SEC_ID CHAR(10), '\
                        'SEC_VALUE FLOAT(20, 17), TIMESTAMP TIMESTAMP);')

            sec_sum = cursor.fetchall()[0][0]
            if sec_sum is None:
                sec_sum = 0
            if irradiation.previous_irradiation is not None:
                sec_sum = sec_sum + irradiation.previous_irradiation.sec
            irradiation.sec = sec_sum
            irradiation.save()
            data['sec_data'].append({
                'pk': irradiation.id,
                'sec': irradiation.sec
            })
    return data


def send_mail_notification(title, message, from_mail, to_mail):
    """Sends an email."""
    headers = {'Reply-To': 'placeholder@cern.ch'}
    from_mail = 'placeholder@cern.ch'
    msg = EmailMessage(title, message, from_mail, to=[to_mail], headers=headers)
    #msg.send()


def get_registered_samples_number(experiments):
    """Calculates data regarding a set of experiments."""
    data = dict()
    experiment_data = []
    total_registered_samples = 0
    total_declared_samples = 0
    total_experiments_radiation_length_occupancy = 0
    total_experiments_nu_coll_length_occupancy = 0
    total_experiments_int_length_occupancy = 0
    row = 0
    for experiment in experiments:
        total_registered_samples += experiment.number_registered_samples
        total_declared_samples += experiment.number_samples
        total_experiments_radiation_length_occupancy += experiment.radiation_length_occupancy
        total_experiments_nu_coll_length_occupancy += experiment.nu_coll_length_occupancy
        total_experiments_int_length_occupancy += experiment.nu_int_length_occupancy
    data = {
        'experiments':
        experiments,
        'total_registered_samples':
        total_registered_samples,
        'total_declared_samples':
        total_declared_samples,
        'total_experiments_radiation_length_occupancy':
        total_experiments_radiation_length_occupancy,
        'total_experiments_nu_coll_length_occupancy':
        total_experiments_nu_coll_length_occupancy,
        'total_experiments_int_length_occupancy':
        total_experiments_int_length_occupancy
    }
    return data


def normalize_query(query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    """
    Parses query and returns List containing all groups of characters quoted 
    in double quotes or separated by white spaces.

    Args:
        query_string (String): query.
        findterms (Regular Expression, optional): Regular expression. Defaults 
            to re.compile(r'"([^"]+)"|(\S+)').findall. Default function matches 
            all quoted characters in double quotes except quoted characters 
            containing double quotes, and also concatenations of non-whitespace 
            characters.
        normspace (Regular Expression, optional): Regular expression. Defaults 
            to re.compile(r'\s{2,}').sub. Default function substitutes multiple 
            white spaces for single white spaces.
    """
    return [
        normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)
    ]


def get_mail_to_string_from_emails(emails):
    """Returns mail to string with emails list."""
    result = 'mailto:'
    for email in emails:
        result += email + '; '
    result = result[:-2]
    return result


def get_page_url_parameters_as_string(request):
    """Extracts parmeters from url without including 'page='"""
    params = request.get_full_path().split('/')[-1]
    params = params.split('?')[-1].split('&')
    result = '?'
    for param in params:
        condition = ('page=' not in param and param != '')
        if condition:
            result += param + '&'
    return result


def clean_number_in_range(value, var_type, ranges):
    """
    Clean number using ranges. Either integer or float. In case of error 
    raises ValidationError.
    """
    result = value
    is_empty = (result == '' or result == None)
    if not is_empty:
        invalid = False
        try:
            result = var_type(result)

            for i, threshold in enumerate(ranges):
                if i%2 == 0:
                    if result < threshold:
                        invalid = True
                        break
                else:
                    if result > threshold:
                        invalid = True
                        break
        except ValueError:
            invalid = True
        
        if invalid:
            msg = 'Number is invalid. Must be '

            for i, threshold in enumerate(ranges):
                even_index = (i%2 == 0)
                
                if even_index:
                    msg += 'larger than ' + str(threshold)
                else:
                    msg += 'lower than ' + str(threshold)
                
                not_done = (i < (len(ranges) - 1))

                if not_done:
                    msg += ' and '
                else:
                    msg += '.'

            raise ValidationError(
                (msg),
                code='invalid_number',
            )
        result = str(result)
    else:
        result = None

    return result


def get_pagination_data(request, elements):
    """Calculates pagination data."""
    elements_per_page = None
    if 'elements_per_page' in request.COOKIES:
        if request.COOKIES['elements_per_page'] == 'all':
            length = len(elements)
            elements_per_page =  len(elements) if length > 0 else 1
        else:
            elements_per_page =  int(request.COOKIES['elements_per_page'])
    ELEMENTS_PER_PAGE = 10 if elements_per_page is None else elements_per_page
    paginator = Paginator(elements, ELEMENTS_PER_PAGE)
    page_num = None
    if request.method == 'GET':
        page_num = 1 if request.GET.get('page') is None else int(request.GET.get('page'))
    elif request.method == 'POST':
        page_num = 1 if request.POST.get('page') is None else int(request.POST.get('page'))

    too_high = (page_num > paginator.num_pages)
    too_low =  (page_num < 1)
    # If page is off margins return closest page.
    if too_high:
        page_num = paginator.num_pages
    elif too_low:
        page_num = 1

    page_obj = paginator.page(page_num)
    prev_params = get_page_url_parameters_as_string(request)
    current_page = {
        'active': True,
        'obj': page_obj,
        'href': prev_params + 'page=' + str(page_obj.number)
    }
    pages = [current_page]
    free_slots = MAX_PAGES - 1
    # Fill pages from top and bottom simultaneously
    while free_slots > 0:
        low_full = pages[0]['obj'].number == 1
        high_full = pages[len(pages) - 1]['obj'].number == paginator.num_pages
        no_slots = free_slots == 0

        if (high_full and low_full) or no_slots:
            break

        if not high_full and not no_slots:
            i = len(pages) - 1
            new_item = [{
                'active': False,
                'obj': paginator.page(pages[i]['obj'].next_page_number()),
                'href': prev_params + 'page=' + \
                    str(pages[i]['obj'].next_page_number())
            }]
            pages = pages + new_item
            free_slots -= 1
            no_slots = free_slots == 0

        if not low_full and not no_slots:
            i = 0
            new_item = [{
                'active': False,
                'obj': paginator.page(pages[i]['obj'].previous_page_number()),
                'href': prev_params + 'page=' + \
                    str(pages[i]['obj'].previous_page_number())
            }]
            pages = new_item + pages
            free_slots -= 1

    curr_index = pages.index(current_page)
    prev_index = 0 if curr_index == 0 else curr_index - 1
    next_index = \
        curr_index if curr_index == len(pages) - 1 else curr_index + 1
    data = {
        'double_pagination': (MIN_ELEMENTS_PER_PAGE_DOUBLE_PAGINATION \
            <= len(pages[curr_index]['obj'].object_list)),
        'page_obj': pages[curr_index]['obj'],
        'previous_href': pages[prev_index]['href'],
        'next_href': pages[next_index]['href'],
        'first_href': prev_params + 'page=1',
        'last_href': prev_params + 'page=' + str(paginator.num_pages),
        'pages': pages
    }
    return data