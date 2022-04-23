"""Django app principal views. It also includes auxiliary functions."""
import json
import yaml
import logging
from .forms import *
from .models import *
from .utilities import *
from django.db.models import Q
from django.utils.safestring import mark_safe
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404, render
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import PermissionDenied, ViewDoesNotExist


APP_NAME = 'samples_manager'
ELEMENTS_PER_PAGE = 10
CERNBOX_UPLOAD_URL = 'placeholder.url.com'
NUM_RESULTS_LOCATION_QUERY = 20


ALERT_MESSAGES = {
    'success': 'Operation executed successfully.',
    'invalid': 'Form is invalid. Please review the data.',
    'equipment_no_id': 'Equipment is missing an ID.',
    'default': 'Something went wrong.',
    'infoream_write_success': 'Information registered in inforEAM successfully.',
    'box_not_in_infoream': 'Box equivalent inforEAM ID doesn\'t exist. Please use ID '\
        'within valid range.',
    'invalid_operation_page_origin': 'This operation can\'t be prformed from '\
        'the requested page isn\'t allowed.',
    'print_experiment_status_invalid': 'One of the selected equipment is associated to an '\
        'experiment with an invalid status. Status should be \'In Preparation\'.',
    'invalid_equipment_id': 'One of the selected equipments has an invalid id.' 
}

# Lines needed to disable InsecureRequestWarning for requests to databse 
# hosted at placeholder.url.com. These warnings aren't relevant in the 
# production environment because they only happen in the test database. 
# In the production database, as of 24/03/21, secure connections to 
# placeholder.url.com are possible and no warning is present. In production set 
# session.verify = True in the function get_infoream_credentials to a ensure 
# secure connection to the database hosted at placeholder.url.com.
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_logged_user(request):
    """Returns user instance of CERN database user. 
    
    If user from CERN database exists in IDM database returns existing 
    user instance, if it doesn't exist it creates and returns new 
    instance."""
    '''
    username =  request.META['HTTP_X_REMOTE_USER']
    first_name = request.META['HTTP_X_REMOTE_USER_FIRSTNAME']
    last_name = request.META['HTTP_X_REMOTE_USER_LASTNAME']
    telephone = request.META['HTTP_X_REMOTE_USER_PHONENUMBER']
    email =  request.META['HTTP_X_REMOTE_USER_EMAIL']
    mobile = request.META['HTTP_X_REMOTE_USER_MOBILENUMBER']
    department = request.META['HTTP_X_REMOTE_USER_DEPARTMENT'] 
    home_institute = request.META['HTTP_X_REMOTE_USER_HOMEINSTITUTE']
    '''
    # Used during development
    user = 1

    if user == 0:
        username =  'test-user'
        first_name =  'Test'
        last_name = 'User'
        telephone = '1234'
        email =  'test-user@gmail.com'
        mobile = '1234'
        department = 'EP/DT'
        home_institute = 'TU'
    elif user == 1:
        username =  'test-admin'
        first_name =  'Test'
        last_name = 'Admin'
        telephone = '1234'
        email =  'test-admin@gmail.com'
        mobile = '1234'
        department = 'EP/DT'
        home_institute = 'TU'
    elif user == 2:
        return None
    else:
        raise ViewDoesNotExist

    if 'username' in request.COOKIES:
        username =  request.COOKIES['username']
        first_name =  request.COOKIES['first_name']
        last_name = request.COOKIES['last_name']
        telephone = request.COOKIES['telephone']
        email =  request.COOKIES['email']
        mobile = request.COOKIES['mobile']
        department = request.COOKIES['department']
        home_institute = request.COOKIES['home_institute']

    email = email.lower()
    users = User.objects.all()
    emails = []
    for item in users:
        emails.append(item.email)
    if not email in emails:
        new_user = User()
        if first_name is not None:
            new_user.name = first_name
        if last_name is not None:
            new_user.surname = last_name
        if mobile:
            new_user.telephone = mobile
            new_user.db_telephone = mobile
        else:
            new_user.telephone = telephone
            new_user.db_telephone = telephone
        if email is not None:
            new_user.email = email
        logged_user = new_user
    else:
        logged_user = User.objects.get(email=email)

    if mobile:
        logged_user.db_telephone = mobile
    else:
        logged_user.db_telephone = telephone
    if department:
        logged_user.department = department

    if home_institute:
        logged_user.home_institute = home_institute
    logged_user.last_login = get_aware_datetime()
    logged_user.save()
    return logged_user


def has_permission_or_403(request, perm, pk_list = None):
    """Verifies if logged user has access to resource. If not access is denied."""
    user = get_logged_user(request)
    allowed = True

    if isinstance(pk_list,str):
        pk_list = int(pk_list)

    if isinstance(pk_list,int):
        pk_list = [pk_list]

    if user:
        if perm == 'admin':
            allowed = is_admin(user)
        elif perm == 'login':
            pass
        else:
            if user.role != 'Admin':
                for pk in pk_list:
                    if perm == 'experiment':
                        experiment = get_object_or_404(Experiment, pk=pk)
                        allowed = (user == experiment.responsible
                            or user in experiment.users.all())
                    elif perm == 'experiment_samples':
                        experiment = get_object_or_404(Experiment, pk=pk)
                        allowed = ((user == experiment.responsible
                            or user in experiment.users.all())
                            and experiment.status.lower() != 'registered') 
                    elif perm == 'sample':
                        sample = get_object_or_404(Sample, pk=pk)
                        experiment = sample.experiment
                        allowed = (user == experiment.responsible
                            or user in experiment.users.all())
                    elif perm == 'experiment_details':
                        experiments = read_authorised_experiments(user)
                        experiment = get_object_or_404(Experiment, pk=pk)
                        allowed = (experiment in experiments)
                    elif perm == 'box_details':
                        box = Box.objects.get(pk=pk)
                        samples = Sample.objects.filter(box=box)
                        experiments = write_authorised_experiments(user)
                        allowed = False
                        for sample in samples:
                            if sample.experiment in experiments:
                                allowed = True
                                break
                    else:
                        allowed = False
                    if not allowed:
                        break
    else:
        allowed = False

    if not allowed:
        raise PermissionDenied


def read_authorised_experiments(logged_user):
    """Retrieves experiments logged user can read."""
    experiments = Experiment.objects.none()

    if is_admin(logged_user):
        experiments = Experiment.objects.order_by('-updated_at')
    else:
        has_private_experiments = (len(Experiment.objects.filter(
            Q(users=logged_user)
            | Q(responsible=logged_user)
            , Q(public_experiment=False))) > 0)

        if has_private_experiments:
            experiments = Experiment.objects.filter(
                Q(users=logged_user)
                | Q(responsible=logged_user))
        else :
            experiments = Experiment.objects.filter(
                Q(public_experiment=True) | Q(users=logged_user)
                | Q(responsible=logged_user))

    return experiments


def shared_experiments(logged_user):
    """Retrieves experiments shared with user."""
    experiments = Experiment.objects.none()

    if is_admin(logged_user):
        experiments = Experiment.objects.order_by('-updated_at')
    else:
        has_private_experiments = (len(Experiment.objects.filter(
            Q(users=logged_user)
            | Q(responsible=logged_user)
            , Q(public_experiment=False))) > 0)

        if not has_private_experiments:
            experiments = Experiment.objects.filter(
                Q(public_experiment=True) | Q(users=logged_user)
                | Q(responsible=logged_user))

    return experiments


def write_authorised_experiments(logged_user):
    """Retrieves experiments logged user can modify."""
    experiments = []

    if is_admin(logged_user):
        experiments = Experiment.objects.order_by('-updated_at')
    else:
        experiments = Experiment.objects.filter(
            Q(users=logged_user)
            | Q(responsible=logged_user)).order_by('-updated_at')

    return experiments


def index(request):
    """Renders index page"""
    logged_user = get_logged_user(request)
    context = {
        'logged_user': logged_user,
    }
    return render(request, 'samples_manager/index.html', context)


def authorised_samples(logged_user):
    """Retrieves authorized samples for user."""
    samples = []
    if is_admin(logged_user):
        experiments = Experiment.objects.order_by('-updated_at')
    else:
        experiment_values = Experiment.objects.filter(
            Q(users=logged_user)
            | Q(responsible=logged_user)).values('title').distinct()
        experiments = []
        for value in experiment_values:
            experiment = Experiment.objects.get(title=value['title'])
            experiments.append(experiment)
    for experiment in experiments:
        experiment_samples = Sample.objects.filter(experiment=experiment)
        for sample in experiment_samples:
            samples.append(sample)
    return samples


def regulations(request):
    """Renders terms and conditions page."""
    logged_user = get_logged_user(request)
    return render(request, 'samples_manager/terms_conditions.html',
                  {'logged_user': logged_user})


def fluence_conversion(request):
    """Renders fluence conversion page."""
    logged_user = get_logged_user(request)
    return render(request, 'samples_manager/fluence_conversion.html',
                  {'logged_user': logged_user})


def save_occupancies(sample, status):
    """Saves sample occupancies in DB."""
    layers = Layer.objects.filter(sample=sample)
    occupancies = []
    radiation_length_occupancy = 0
    nu_coll_length_occupancy = 0
    nu_int_length_occupancy = 0
    for layer in layers:
        compound_elements = CompoundElement.objects.filter(
            compound=layer.compound_type)
        if len(compound_elements) != 0:
            layer_radiation_length = 0
            layer_nu_coll_length = 0
            layer_nu_int_length = 0
            for compound_element in compound_elements:
                layer_radiation_length = layer_radiation_length + compound_element.percentage * compound_element.element_type.radiation_length
                layer_nu_coll_length = layer_nu_coll_length + compound_element.percentage * compound_element.element_type.nu_coll_length
                layer_nu_int_length = layer_nu_int_length + compound_element.percentage * compound_element.element_type.nu_int_length
            layer_radiation_length = layer_radiation_length / 100
            layer_nu_coll_length = layer_nu_coll_length / 100
            layer_nu_int_length = layer_nu_int_length / 100
            if layer.compound_type.density != 0:
                layer_linear_radiation_length = layer_radiation_length / layer.compound_type.density
                layer_linear_nu_coll_length = layer_nu_coll_length / layer.compound_type.density
                layer_linear_nu_int_length = layer_nu_int_length / layer.compound_type.density
            else:
                layer_linear_radiation_length = 0
                layer_linear_nu_coll_length = 0
                layer_linear_nu_int_length = 0
            if layer_linear_radiation_length != 0:
                radiation_length_occupancy = radiation_length_occupancy + layer.length / (
                    10 * layer_linear_radiation_length)
            if layer_linear_nu_coll_length != 0:
                nu_coll_length_occupancy = nu_coll_length_occupancy + layer.length / (
                    10 * layer_linear_nu_coll_length)
            if layer_linear_nu_int_length != 0:
                nu_int_length_occupancy = nu_int_length_occupancy + layer.length / (
                    10 * layer_linear_nu_int_length)
    radiation_length_occupancy = radiation_length_occupancy * 100
    nu_coll_length_occupancy = nu_coll_length_occupancy * 100
    nu_int_length_occupancy = nu_int_length_occupancy * 100
    if status == 'new' or status == 'clone':
        sample_occupancy = Occupancy()
        sample_occupancy.sample = sample
    else:
        sample_occupancies = Occupancy.objects.filter(sample=sample)
        if len(sample_occupancies) != 0:
            sample_occupancy = sample_occupancies[0]
        else:
            sample_occupancy = Occupancy()
            sample_occupancy.sample = sample
    sample_occupancy.radiation_length_occupancy = \
        round(radiation_length_occupancy, 3)
    sample_occupancy.nu_coll_length_occupancy = \
        round(nu_coll_length_occupancy, 3)
    sample_occupancy.nu_int_length_occupancy = \
        round(nu_int_length_occupancy, 3)
    sample_occupancy.save()


def get_samples_occupancies(samples):
    """Calculates the occupancies of a set of samples."""
    samples_data = []
    for sample in samples:
        if 'passive standard' in sample.experiment.category.lower():
            sample_category = sample.category.split('standard', 1)[1]
        else:
            sample_category = sample.category.split(':', 1)[1]
        occupancy = Occupancy.objects.filter(sample=sample)
        if len(occupancy) == 0:
            save_occupancies(sample, 'new')
        occupancy1 = Occupancy.objects.filter(sample=sample.id)[0]
        samples_data.append({
            'sample': sample,
            'sample_category': sample_category,
            'occupancy': occupancy1,
        })
    return samples_data


def get_sample_fluences(sample):
    """Calculates fluence of a sample."""
    fluences = []
    irradiations = Irradiation.objects.filter(sample=sample)
    result = 0
    tuple_list = []
    for irradiation in irradiations:
        if irradiation.estimated_fluence:
            if '.' in str(irradiation.dosimeter):
                logging.info('no calculation')
            else:
                logging.info('size:' + str(irradiation.dosimeter.width) + ' x ' +
                      str(irradiation.dosimeter.height))
                dosimeter_area = irradiation.dosimeter.width * irradiation.dosimeter.height
                dos_position = irradiation.dos_position
                dos_tuple = (dosimeter_area, irradiation.dosimeter,
                             irradiation.estimated_fluence,
                             irradiation.sample, irradiation.dos_position)
                tuple_list.append(dos_tuple)
    tuple_list.sort(key=lambda tup: (tup[0], tup[4]))
    if tuple_list:
        sum_fluence = tuple_list[0][2]
        tuple_list_length = len(tuple_list)
        if tuple_list_length > 1:
            for i in range(1, tuple_list_length):
                if tuple_list[i - 1][0] == tuple_list[i][0]:
                    if tuple_list[i - 1][4] == tuple_list[i][4]:
                        sum_fluence = sum_fluence + tuple_list[i][2]
                    else:
                        fluences.append({
                            'Sample': sample,
                            'Fluence_data': {
                                'width': tuple_list[i - 1][1].width,
                                'height': tuple_list[i - 1][1].height,
                                'estimated_fluence': sum_fluence
                            }
                        })
                        sum_fluence = 0
                else:
                    fluences.append({
                        'Sample': sample,
                        'Fluence_data': {
                            'width': tuple_list[i - 1][1].width,
                            'height': tuple_list[i - 1][1].height,
                            'estimated_fluence': sum_fluence
                        }
                    })
                    sum_fluence = 0

            if tuple_list[tuple_list_length -
                          2][0] == tuple_list[tuple_list_length - 1][0]:
                if tuple_list[i - 1][4] == tuple_list[i][4]:
                    fluences.append({
                        'Sample': sample,
                        'Fluence_data': {
                            'width': tuple_list[tuple_list_length - 1][1].width,
                            'height':
                            tuple_list[tuple_list_length - 1][1].height,
                            'estimated_fluence': sum_fluence
                        }
                    })
                else:
                    fluences.append({
                        'Sample': sample,
                        'Fluence_data': {
                            'width':
                            tuple_list[tuple_list_length - 1][1].width,
                            'height':
                            tuple_list[tuple_list_length - 1][1].height,
                            'estimated_fluence':
                            tuple_list[tuple_list_length - 1][2]
                        }
                    })
            else:
                fluences.append({
                    'Sample': sample,
                    'Fluence_data': {
                        'width': tuple_list[tuple_list_length - 1][1].width,
                        'height': tuple_list[tuple_list_length - 1][1].height,
                        'estimated_fluence':
                        tuple_list[tuple_list_length - 1][2]
                    }
                })
        else:
            fluences.append({
                'Sample': sample,
                'Fluence_data': {
                    'width': tuple_list[tuple_list_length - 1][1].width,
                    'height': tuple_list[tuple_list_length - 1][1].height,
                    'estimated_fluence': tuple_list[tuple_list_length - 1][2]
                }
            })
    return fluences


def equipment_print(request):
    """Prints equipment label."""
    data = dict()
    actions = []
    form = None
    collapsible_text = ''
    data['form_is_valid'] = True
    logged_user = get_logged_user(request)
    checked_elements = get_checked_elements(request)
    prev_url = request.META.get('HTTP_REFERER')
    model_name = get_model_name_from_url(prev_url)
    model = get_model_class_from_name(model_name)
    validation_data = checked_elements_are_valid(checked_elements, 'group', model, 5)

    if validation_data['valid']:
        collapsible_text = get_collapsible_text_checked_elements(
            checked_elements, model)
        if request.method == 'POST':
            form = PrintLabelForm(request.POST)
            if form.is_valid():
                data_render = dict()
                if model_name == 'sample':
                    data_render['experiment'] = Sample.objects.get(\
                        pk=checked_elements[0]).experiment
                    data_render['ids'] = [data_render['experiment'].id]
                for pk in checked_elements:
                    equipment = model.objects.get(pk=pk)
                    has_permission_or_403(request, model_name, pk)
                    equipment_id = get_equipment_id_from_instance(equipment)
                    print_data = dict()
                    print_data['action'] = 'print_label_equipment'
                    print_data['equipment_id'] = equipment_id
                    print_data['infoream_id'] = get_infoream_id(equipment_id)
                    print_data['printer_path'] = form.cleaned_data['printer']
                    print_data['template_code'] = form.cleaned_data['template']
                    print_data['print_quantity'] = form.cleaned_data['num_copies']
                    actions.append(print_data)
                data['alert_message'] = ALERT_MESSAGES['success']
                data_render['list_name'] = \
                    get_view_list_name_from_model_name(model_name)
                data['html_list'] = \
                    render_partial_list_to_string(request, data_render)
                apply_infoream_actions(actions)
            else:
                data['form_is_valid'] = False
                data['alert_message'] = ALERT_MESSAGES['invalid']
        else:
            experiment_status_valid = True
            valid_equipment_id = True
            for pk in checked_elements:
                equipment = model.objects.get(pk=pk)
                equipment_id = get_equipment_id_from_instance(equipment)
                if valid_equipment_id:
                    valid_equipment_id = (get_equipment_type(equipment_id) is not None)
            if model_name == 'sample':
                for pk in checked_elements:
                    sample = Sample.objects.get(pk=pk)
                    experiment_status_valid = \
                        (sample.experiment.status == 'In Preparation')
                    if not experiment_status_valid:
                        break
            if experiment_status_valid:
                if valid_equipment_id:
                    form = PrintLabelForm()
                else:
                    data['form_is_valid'] = False
                    data['alert_message'] = ALERT_MESSAGES['invalid_equipment_id']
            else:
                data['form_is_valid'] = False
                data['alert_message'] = ALERT_MESSAGES['print_experiment_status_invalid']
    else:
        data['form_is_valid'] = False
        data['alert_message'] = validation_data['msg']

    context = dict()
    context['form'] = form
    context['render_with_errors'] = True
    context['additional_text'] = collapsible_text
    context['equipment_model_name'] = model_name
    data['html_form'] = render_to_string(
        'samples_manager/partial_equipment_print.html',
        context,
        request=request,
    )
    return  JsonResponse(data)


def list_filter(request):
    """View for all filter queries in IDM."""
    data = dict()
    url = request.GET['url']
    list_name = get_view_list_name_from_url(url)
    data['list_name'] = list_name
    data['ids'] = extract_ids_from_url(url)
    data['html_list'] = render_partial_list_to_string(request, data)
    query_string = request.GET['search_box'] \
        if 'search_box' in request.GET else ''
    data['query_str'] = query_string
    return JsonResponse(data)

def get_locations(request):
    """Collects data for list of users."""
    data = dict()
    data['success'] = True
    locations = []
    results = []
    if request.method == 'GET':
        filter_str = request.GET.get('q')
        data['q'] = filter_str
        locations = get_locations_from_db(filter_str, \
            NUM_RESULTS_LOCATION_QUERY)
        for location in locations:
            results.append({
                'name': location[0],
                'value': location[0],
            })
        if len(locations) == 0:
            results.append({
                'name': 'Other. Not in list.',
                'value': 'other',
            })

    else:
        data['success'] = False
    data['results'] = results
    data['length'] = len(locations)
    return JsonResponse(data)


def get_users_data(users):
    """Collects data for list of users."""
    users_data=[]
    row = 0
    for user in users:
        row = row + 1
        experiment_values = Experiment.objects.filter(
            Q(users=user)
            | Q(responsible=user)).values('title').distinct()
        experiment_number = 0
        if experiment_values:
            experiments_number = experiment_values.count()
        else:
            experiments_number = 0
        users_data.append({
            'user': user,
            'experiments_number': experiments_number,
            'row': row,
        })

    return users_data


def read_equipment_from_infoream(request, equipment_id):
    """Reads equipment information from inforEAM."""
    type = get_equipment_type(equipment_id)
    if type == 'sample':
        sample = Sample.objects.get(set_id=equipment_id)
        has_permission_or_403(request, 'sample', sample.id)
    else:
        has_permission_or_403(request, 'admin')
    previous_page = 'None' if request.META.get('HTTP_REFERER') is None else \
        request.META.get('HTTP_REFERER')
    is_sample = 'samples' in previous_page.split('/')
    is_dosimeter = 'dosimeters' in previous_page.split('/')
    is_box = 'boxes' in previous_page.split('/')
    context = {
        'equipment_id': equipment_id,
        'exists': True,
        'logged_user': get_logged_user(request)
    }

    if get_equipment_type(equipment_id) is not None:
        try:
            data =dict()
            data['infoream_id'] = get_infoream_id(equipment_id)
            context['data'] = read_equipment(data)
            if context['data']['response'] is None:
                context['exists'] = False
        except:
            context['exists'] = False
    else:
        context['exists'] = False
    return render(request, 'samples_manager/equipment_infoream_details.html', context)


def get_infoream_dimensions_from_equipment(equipment_id):
    """Calculates dimensions of equipment with converted units."""
    result = dict()
    equipment_type = get_equipment_type(equipment_id) 
    is_sample = 'sample' in equipment_type
    is_dosimeter = 'dosimeter' in equipment_type
    is_box = 'box' in equipment_type
    if is_sample:
        sample = Sample.objects.get(set_id=equipment_id)
        result['height'] = 0 if sample.height == 0 or sample.height is None else sample.height / 10
        result['width'] = 0 if sample.width == 0 or sample.width is None else sample.width / 10
        result['weight'] = 0 if sample.weight == 0 or sample.weight is None else sample.weight
        result['length'] = 0
        layers = Layer.objects.filter(sample=sample)
        for layer in layers:
            increment = 0 if layer.length == 0 or layer.length is None else layer.length / 10
            result['length'] += increment
    elif is_dosimeter:
        dosimeter = Dosimeter.objects.get(dos_id=equipment_id)
        result['height'] = 0 if dosimeter.height == 0 or dosimeter.height is None else dosimeter.height / 10
        result['width'] = 0 if dosimeter.width == 0 or dosimeter.width is None else dosimeter.width / 10
        result['length'] = 0 if dosimeter.length == 0 or dosimeter.length is None else dosimeter.length / 10
        result['weight'] = 0 if dosimeter.weight == 0 or dosimeter.weight is None else dosimeter.weight / 1000
    elif is_box:
        box = Box.objects.get(box_id=equipment_id)
        result['height'] = 0 if box.height == 0 or box.height is None else box.height
        result['width'] = 0 if box.width == 0 or box.width is None else box.width
        result['length'] = 0 if box.length == 0 or box.length is None else box.length
        result['weight'] = 0 if box.weight == 0 or box.weight is None else box.weight
    return result


def get_actions_from_equipment_list(equipment_id_list):
    """Returns infoream actions from equipment list."""
    result = dict()
    actions = []
    for equipment_id in equipment_id_list:
        dimensions = get_infoream_dimensions_from_equipment(equipment_id)
        equipment_type = get_equipment_type(equipment_id)
        is_sample = 'sample' in equipment_type
        is_dosimeter = 'dosimeter' in equipment_type
        is_box = 'box' in equipment_type
        if is_sample:
            sample = Sample.objects.get(set_id=equipment_id)
            infoream_id = get_infoream_id(sample.set_id)
            text = get_sample_infoream_comment(sample)
            category_desc = \
                get_category_desc_from_serial_number(equipment_id)
            exists_equipment_in_infoream = \
                (read_equipment({'infoream_id': infoream_id})['response'] is not None)
            exists_comment_in_infoream = \
                (read_comment({'infoream_id': infoream_id})['response'] is not None)
            
            if exists_equipment_in_infoream:
                actions.append({
                    'action': 'update_equipment',
                    'width': dimensions['width'],
                    'height': dimensions['height'],
                    'length': dimensions['length'],
                    'weight': dimensions['weight'],
                    'material': 'OTHER',
                    'equipment_id': sample.set_id,
                    'infoream_id': infoream_id,
                    'category_desc': category_desc,
                    'location': sample.last_location,
                    'category_code': 'PXXISET001',
                    'class_code': 'XISET'
                })
                if exists_comment_in_infoream:
                    actions.append({
                        'action': 'update_comment',
                        'equipment_id': sample.set_id,
                        'infoream_id': infoream_id,
                        'line_number': 5,
                        'text': text
                    })
                else:
                    actions.append({
                        'action': 'create_comment',
                        'equipment_id': sample.set_id,
                        'infoream_id': infoream_id,
                        'line_number': 5,
                        'text': text
                    })
            else:
                actions.append({
                    'action': 'create_equipment',
                    'width': dimensions['width'],
                    'height': dimensions['height'],
                    'weight': dimensions['weight'],
                    'length': dimensions['length'],
                    'material': 'OTHER',
                    'equipment_id': sample.set_id,
                    'infoream_id': infoream_id,
                    'category_desc': category_desc,
                    'location': sample.last_location
                })
                actions.append({
                    'action': 'create_comment',
                    'equipment_id': sample.set_id,
                    'infoream_id': infoream_id,
                    'line_number': 5,
                    'text': text
                })
        elif is_dosimeter:
            dosimeter = Dosimeter.objects.get(dos_id=equipment_id)
            infoream_id = get_infoream_id(dosimeter.dos_id)
            category_desc = \
                get_category_desc_from_serial_number(equipment_id)
            exists_in_infoream = \
                (read_equipment({'infoream_id': infoream_id})['response'] is not None)
            
            if exists_in_infoream:
                actions.append({
                    'action': 'update_equipment',
                    'width': dimensions['width'],
                    'height': dimensions['height'],
                    'weight': dimensions['weight'],
                    'length': dimensions['length'],
                    'material': 'ALUMINIUM',
                    'equipment_id': dosimeter.dos_id,
                    'infoream_id': infoream_id,
                    'category_desc': category_desc,
                    'location': dosimeter.last_location
                })
            else:
                actions.append({
                    'action': 'create_equipment',
                    'width': dimensions['width'],
                    'height': dimensions['height'],
                    'weight': dimensions['weight'],
                    'length': dimensions['length'],
                    'material': 'ALUMINIUM',
                    'equipment_id': dosimeter.dos_id,
                    'infoream_id': infoream_id,
                    'category_desc': category_desc,
                    'location': dosimeter.last_location
                })
        elif is_box:
            box = Box.objects.get(box_id=equipment_id)
            infoream_id = get_infoream_id(box.box_id)
            category_desc = \
                get_category_desc_from_serial_number(equipment_id)
            exists_in_infoream = \
                (read_equipment({'infoream_id': infoream_id})['response'] is not None)
            if exists_in_infoream:
                actions.append({
                    'action': 'update_equipment',
                    'width': dimensions['width'],
                    'height': dimensions['height'],
                    'weight': dimensions['weight'],
                    'length': dimensions['length'],
                    'material': 'OTHER',
                    'equipment_id': box.box_id,
                    'infoream_id': infoream_id,
                    'category_desc': category_desc,
                    'location': box.last_location
                })
            else:
                result['form_is_valid'] = False
                result['alert_message'] = ALERT_MESSAGES['box_not_in_infoream']
                break

            items = get_box_items(box)
            for item in items:
                dimensions = get_infoream_dimensions_from_equipment(item['id'])
                infoream_id_child = get_infoream_id(item['id'])
                infoream_id_parent = get_infoream_id(box.box_id)
                category_desc = \
                    get_category_desc_from_serial_number(item['id'])
                
                exists_child_in_infoream = \
                    (read_equipment({'infoream_id': infoream_id_child})['response']\
                    is not None)
                if infoream_id_child is not None and infoream_id_parent is not None:
                    equipment_type = get_equipment_type(item['id'])
                    if exists_child_in_infoream:
                        if equipment_type == 'sample':
                            actions.append({
                                'action': 'update_equipment',
                                'width': dimensions['width'],
                                'height': dimensions['height'],
                                'weight': dimensions['weight'],
                                'length': dimensions['length'],
                                'material': 'OTHER',
                                'equipment_id': item['id'],
                                'infoream_id': infoream_id_child,
                                'category_desc': category_desc,
                                'location': item['object'].last_location
                            })
                        else:
                            actions.append({
                                'action': 'update_equipment',
                                'width': dimensions['width'],
                                'height': dimensions['height'],
                                'weight': dimensions['weight'],
                                'length': dimensions['length'],
                                'material': 'ALUMINIUM',
                                'equipment_id': item['id'],
                                'infoream_id': infoream_id_child,
                                'category_desc': category_desc,
                                'location': item['object'].last_location
                            })
                        actions.append({
                            'action': 'detach_parent',
                            'infoream_id': infoream_id_child
                        })
                        actions.append({
                            'action': 'attach_parent',
                            'infoream_id_child': infoream_id_child,
                            'infoream_id_parent': infoream_id_parent
                        })
                    else:
                        if equipment_type == 'sample':
                            actions.append({
                                'action': 'create_equipment',
                                'width': dimensions['width'],
                                'height': dimensions['height'],
                                'weight': dimensions['weight'],
                                'length': dimensions['length'],
                                'material': 'OTHER',
                                'equipment_id': item['id'],
                                'infoream_id': infoream_id_child,
                                'category_desc': category_desc,
                                'location': item['object'].last_location
                            })
                        else:
                            actions.append({
                                'action': 'create_equipment',
                                'width': dimensions['width'],
                                'height': dimensions['height'],
                                'weight': dimensions['weight'],
                                'length': dimensions['length'],
                                'material': 'ALUMINIUM',
                                'equipment_id': item['id'],
                                'infoream_id': infoream_id_child,
                                'category_desc': category_desc,
                                'location': item['object'].last_location
                            })
                        actions.append({
                            'action': 'attach_parent',
                            'infoream_id_child': infoream_id_child,
                            'infoream_id_parent': infoream_id_parent
                        })

                else:
                    logging.error('inforEAM parent or child id is invalid.')
                    result['form_is_valid'] = False
                    result['alert_message'] = ALERT_MESSAGES['default']
                    break
    result['actions'] = actions
    return result


def write_equipment_in_infoream(equipment_id_list):
    """Writes equipment information in inforEAM."""
    data = dict()
    data['form_is_valid'] = True
    data['alert_message'] = ALERT_MESSAGES['infoream_write_success']

    if 'None' not in equipment_id_list and '' not in equipment_id_list:
        data_actions = get_actions_from_equipment_list(equipment_id_list)
        if 'alert_message' not in data_actions:
            response = apply_infoream_actions(data_actions['actions'])
            if response['response'] is None:
                logging.error('inforEAM reponse is None.')
                data['form_is_valid'] = False
                data['alert_message'] = ALERT_MESSAGES['default']
        else:
            data['form_is_valid'] = data_actions['form_is_valid']
            data['alert_message'] = data_actions['alert_message']
    else:
        data['form_is_valid'] = False
        data['alert_message'] = ALERT_MESSAGES['equipment_no_id']
    
    return data


def get_box_items(box):
    """Retrieves box items."""
    result = []
    samples = list(Sample.objects.filter(box=box))
    dosimeters = list(Dosimeter.objects.filter(box=box))

    for sample in samples:
        result.append({
            'object': sample,
            'type': 'sample',
            'id': sample.set_id,
            'infoream_id': get_infoream_id(sample.set_id)
        })
    for dosimeter in dosimeters:
        result.append({
            'object': dosimeter,
            'type': 'dosimeter',
            'id': dosimeter.dos_id,
            'infoream_id': get_infoream_id(dosimeter.dos_id)
        })

    return result


def get_sample_infoream_comment(sample):
    """Generates sample comment to be written in inforEAM. Comment
    contains information regarding sample's composition."""
    data = dict()
    if not isinstance(sample, Sample):
        return ''
    layers = Layer.objects.filter(sample=sample)
    data['layers'] = []
    for i in range(0, len(layers)):
        data['layers'].append({
            'name': layers[i].name,
            'length': num_notation(layers[i].length, '2e') + 'mm',
            'compound': {
                'name': layers[i].compound_type.name,
                'density': num_notation(layers[i].compound_type.density, '4e') + ' g/cm2',
                'elements': []
            }
        })
        elements = CompoundElement.objects.filter(compound=layers[i].compound_type)
        compound_data = data['layers'][i]['compound']
        for element in elements:
            compound_data['elements'].append({
                'name': str(element.element_type),
                'percentage': num_notation(element.percentage, '2d') + '%'
            })
    
    result = yaml.dump(yaml.load(json.dumps(data), Loader=yaml.Loader), \
        Dumper=yaml.Dumper, default_flow_style=False)
    return result


def get_items_from_item_ids(items_ids):
    """Returns objects containing ids."""
    result = []
    for item_id in items_ids:
        item_type = get_equipment_type(item_id)
        if item_type == 'sample':
            result.append(Sample.objects.get(set_id=item_id))
        elif item_type == 'dosimeter':
            result.append(Dosimeter.objects.get(dos_id=item_id))
    return result


def get_num_samples_compound(compound):
    """Counts the number of samples where a compound is used."""
    layers = Layer.objects.filter(compound_type=compound)

    compound_samples = []
    for layer in layers:
        if layer.sample not in compound_samples:
            compound_samples.append(layer.sample)

    return len(compound_samples)


def get_compounds_data(compounds):
    """Retrieves all compounds and number of samples where each compound
    appears."""
    compounds_data = []
    for compound in compounds:
        samples_sum = get_num_samples_compound(compound)
        compounds_data.append({
            "compound": compound,
            "samples_sum": samples_sum,
        })
    return compounds_data


def render_partial_list_to_string(request, data):
    """Renders partial list as string."""
    result = None
    query_string = request.GET['search_box'] \
        if 'search_box' in request.GET else ''
    logged_user = get_logged_user(request)
    if data['list_name'] == 'experiments_list':
        elements = experiments_search(logged_user, query_string)
        result = render_partial_experiments_list_to_string(request, elements)
    elif data['list_name'] == 'experiments_shared_list':
        elements = experiments_shared_search(logged_user, query_string)
        result = render_partial_shared_experiments_list_to_string(\
            request, elements)
    elif data['list_name'] == 'experiment_samples_list':
        experiment = Experiment.objects.get(pk=data['ids'][0])
        elements = samples_search(experiment, query_string)
        result = render_partial_samples_list_to_string(\
            request, experiment, elements)
    elif data['list_name'] == 'compounds_list':
        elements = compounds_search(query_string)
        result = render_partial_compounds_list_to_string(request, elements)
    elif data['list_name'] == 'dosimeters_list':
        elements = dosimeters_search(query_string)
        result = render_partial_dosimeters_list_to_string(request, elements)
    elif data['list_name'] == 'experiment_users_list':
        experiment = Experiment.objects.get(pk=data['ids'][0])
        elements = experiment_users_search(experiment, query_string)
        result = render_partial_experiment_users_list_to_string(\
            request, experiment, elements)
    elif data['list_name'] == 'users_list':
        elements = users_search(query_string)
        result = render_partial_users_list_to_string(request, elements)
    elif data['list_name'] == 'irradiations_list':
        elements = irradiations_search(query_string)
        result = render_partial_irradiations_list_to_string(request, elements)
    elif data['list_name'] == 'fluence_factors_list':
        elements = fluence_factors_search(query_string)
        result = render_partial_fluence_factors_list_to_string(request, elements)
    elif data['list_name'] == 'dosimetry_results_list':
        elements = dosimetry_results_search(query_string)
        result = render_partial_dosimetry_results_list_to_string(request, elements)
    elif data['list_name'] == 'boxes_list':
        elements = boxes_search(query_string)
        result = render_partial_boxes_list_to_string(request, elements)
    elif data['list_name'] == 'box_items_list':
        box = Box.objects.get(pk=data['ids'][0])
        elements = box_items_search(box, query_string)
        result = render_partial_box_items_list_to_string(request, box, elements)
    return result


def experiments_search(user, query_string=''):
    """
    Retrieves experiments meeting search criteria.
    Search query returns all experiments matching all keywords.
    """
    experiments = list(write_authorised_experiments(user))
    results = filter_model_objects_by_str(\
        query_string, Experiment, instance_list=experiments)
    return results


def experiments_shared_search(user, query_string=''):
    """
    Retrieves experiments meeting search criteria.
    Search query returns all experiments matching all keywords.
    """
    experiments = list(shared_experiments(user))
    results = filter_model_objects_by_str(\
        query_string, Experiment, instance_list=experiments)
    return results


def samples_search(experiment, query_string=''):
    """
    Retrieves samples related to experiment and filters them using query.
    Search query returns all experiments matching all keywords.
    """
    samples = Sample.objects.filter(experiment=experiment)
    results = filter_model_objects_by_str(\
        query_string, Sample, instance_list=samples)
    return results


def compounds_search(query_string=''):
    """Retrieves compounds meeting search criteria."""
    results = filter_model_objects_by_str(query_string, Compound)
    return results


def dosimeters_search(query_string=''):
    """Retrieves dosimeters meeting search criteria."""
    results = filter_model_objects_by_str(query_string, Dosimeter)
    return results


def experiment_users_search(experiment, query_string=''):
    """Retrieves users of an experiment meeting search criteria."""
    users = list(experiment.users.all())
    users.append(experiment.responsible)
    results = filter_model_objects_by_str(\
        query_string, User, instance_list=users)
    return results


def users_search(query_string=''):
    """Retrieves users meeting search criteria."""
    results = filter_model_objects_by_str(query_string, User)
    return results


def irradiations_search(query_string=''):
    """Retrieves irradiations meeting search criteria."""
    results = filter_model_objects_by_str(query_string, Irradiation)
    return results


def fluence_factors_search(query_string=''):
    """Retrieves fluence factors meeting search criteria."""
    results = filter_model_objects_by_str(query_string, FluenceFactor)
    return results


def dosimetry_results_search(query_string=''):
    """Retrieves dosimetry results meeting search criteria."""
    irradiations = Irradiation.objects.filter(Q(status='Completed'))
    results = filter_model_objects_by_str(
        query_string, Irradiation, instance_list=irradiations)
    return results


def boxes_search(query_string=''):
    """Retrieves boxes meeting search criteria."""
    results = filter_model_objects_by_str(query_string, Box)
    return results


def box_items_search(box, query_string=''):
    """Retrieves box items meeting search criteria."""
    results = []
    items = get_box_items(box)
    if query_string != '':
        keywords = query_string.split(' ')
        for item in items:
            if item['id'] != None:
                for keyword in keywords:
                    keyword_low = keyword.lower()
                    if keyword_low in item['id'].lower() or\
                        keyword_low in item['type'].lower():
                        results.append(item)
    else:
        results = items
    return results


def render_partial_experiments_list_to_string(request, experiments=None):
    """Renders experiments list as string."""
    logged_user = get_logged_user(request)
    experiments_all_pages = experiments_search(logged_user) \
        if experiments is None else experiments
    pagination_data = get_pagination_data(request, experiments_all_pages)
    experiments = pagination_data['page_obj'].object_list
    template = 'samples_manager/partial_admin_experiments_list.html' \
        if is_admin(logged_user) else 'samples_manager/partial_experiments_list.html'
    experiment_data = get_registered_samples_number(experiments)
    context = {
        'experiment_data': experiment_data,
        'pagination_data': pagination_data
    }
    result = render_to_string(template, context)
    return result


def render_partial_shared_experiments_list_to_string(request, experiments=None):
    """Renders experiments list as string."""
    logged_user = get_logged_user(request)
    experiments_all_pages = experiments_search(logged_user) \
        if experiments is None else experiments
    pagination_data = get_pagination_data(request, experiments)
    experiment_data = get_registered_samples_number(pagination_data['page_obj'].object_list)
    return render_to_string('samples_manager/partial_experiments_shared_list.html', {
        'experiment_data': experiment_data,
        'pagination_data': pagination_data
    })


def render_partial_samples_list_to_string(request, experiment, samples=None):
    """Renders samples list as string."""
    samples_all_pages = Sample.objects.all() \
        if samples is None else samples
    pagination_data = get_pagination_data(request, samples_all_pages)
    samples = pagination_data['page_obj'].object_list
    result = render_to_string(
        'samples_manager/partial_experiment_samples_list.html', {
            'samples': samples,
            'experiment': experiment,
            'pagination_data': pagination_data
    })
    return result


def render_partial_compounds_list_to_string(request, compounds=None):
    """Renders compounds list as string."""
    compounds_all_pages = Compound.objects.all() \
        if compounds is None else compounds
    pagination_data = get_pagination_data(request, compounds_all_pages)
    compounds = pagination_data['page_obj'].object_list
    compounds_data = get_compounds_data(compounds)
    result = render_to_string('samples_manager/partial_compounds_list.html', {
        'compounds_data': compounds_data,
        'pagination_data': pagination_data
    })
    return result


def render_partial_dosimeters_list_to_string(request, dosimeters=None):
    """Renders dosimeters list as string."""
    dosimeters_all_pages = Dosimeter.objects.all() \
        if dosimeters is None else dosimeters
    pagination_data = get_pagination_data(request, dosimeters_all_pages)
    dosimeters = pagination_data['page_obj'].object_list
    result = render_to_string('samples_manager/partial_dosimeters_list.html', {
        'dosimeters': dosimeters,
        'pagination_data': pagination_data
    })
    return result


def render_partial_irradiations_list_to_string(request, irradiations=None):
    """Renders irradiations list as string."""
    irradiations_all_pages = Irradiation.objects.all() \
        if irradiations is None else irradiations
    pagination_data = get_pagination_data(request, irradiations_all_pages)
    irradiations = pagination_data['page_obj'].object_list
    result = render_to_string(
        'samples_manager/partial_irradiations_list.html', {
            'irradiations': irradiations,
            'pagination_data': pagination_data
        }
    )
    return result


def render_partial_fluence_factors_list_to_string(request, factors=None):
    """Renders fluence factors list as string."""
    factors = FluenceFactor.objects.all() \
        if factors is None else factors
    pagination_data = get_pagination_data(request, factors)
    irradiations = pagination_data['page_obj'].object_list
    result = render_to_string(
        'samples_manager/partial_fluence_factors_list.html', {
            'factors': factors,
            'pagination_data': pagination_data
        }
    )
    return result


def render_partial_dosimetry_results_list_to_string(request, irradiations=None):
    """Renders dsoimetry results list as string."""
    irradiations_all_pages = dosimetry_results_search() \
        if irradiations is None else irradiations
    pagination_data = get_pagination_data(request, irradiations_all_pages)
    irradiations = pagination_data['page_obj'].object_list
    result = render_to_string(
        'samples_manager/partial_dosimetry_results_list.html', {
            'results': irradiations,
            'pagination_data': pagination_data
        }
    )
    return result


def render_partial_boxes_list_to_string(request, boxes=None):
    """Renders boxes list as string."""
    boxes_all_pages = Box.objects.all() \
        if boxes is None else boxes
    pagination_data = get_pagination_data(request, boxes_all_pages)
    boxes = pagination_data['page_obj'].object_list
    result = render_to_string('samples_manager/partial_boxes_list.html', {
        'boxes': boxes,
        'pagination_data': pagination_data
    })
    return result


def render_partial_box_items_list_to_string(request, box, box_items=None):
    """Renders box's items list as string."""
    items_all_pages = Box.objects.all() \
        if box_items is None else box_items
    pagination_data = get_pagination_data(request, items_all_pages)
    items = pagination_data['page_obj'].object_list
    result = render_to_string('samples_manager/partial_box_items_list.html', {
        'box': box,
        'items': items,
        'pagination_data': pagination_data
    })
    return result


def render_partial_users_list_to_string(request, users=None):
    """Renders users list as string."""
    users_all_pages = User.objects.all() \
        if users is None else users
    pagination_data = get_pagination_data(request, users_all_pages)
    users = pagination_data['page_obj'].object_list
    users_data = get_users_data(users)
    template = 'samples_manager/partial_users_list.html'
    context = {
        'users_data': users_data,
        'pagination_data': pagination_data
    }
    result = render_to_string(template, context)
    return result


def render_partial_experiment_users_list_to_string(request, experiment, users=None):
    """Renders experiment users list as string."""
    users_all_pages = list(experiment.users.all()) \
        if users is None else users
    pagination_data = get_pagination_data(request, users_all_pages)
    users = pagination_data['page_obj'].object_list
    template = 'samples_manager/partial_experiment_users_list.html'
    context = {
        'users': users,
        'experiment': experiment,
        'pagination_data': pagination_data
    }
    result = render_to_string(template, context)
    return result


def get_collapsible_text_checked_elements(checked_elements, Model):
    """Generates collapsible text listing element selection. Used in list pages."""
    result = {
        'uncollapsed': '',
        'collapsed': ''
    }
    for pk in checked_elements:
        elements = Model.objects.filter(pk=pk)
        is_match = (elements.count() == 1)
        if is_match:
            element = elements[0]
            model_type = str(type(Model)).lower()
            text = ''
            if isinstance(element, Experiment):
                text = str(element.title)
            elif isinstance(element, Sample):
                text = str(element.name)
            elif isinstance(element, Dosimeter):
                text = str(element.dos_id)
            elif isinstance(element, Compound):
                text = str(element.name)
            elif isinstance(element, Irradiation):
                text = str(element.id)
            elif isinstance(element, User):
                text = str(element.email)
            elif isinstance(element, Box):
                text = str(element.box_id)
            result['uncollapsed'] += '- ' + text + '\n'
    
    has_length = (len(result['uncollapsed']) > 0)
    if has_length:
        result['uncollapsed'] = 'The action will be applied to the following '\
            'elements:\n\n' + result['uncollapsed']
    else:
        result['uncollapsed'] =''
        return result

    result['collapsed'] = result['uncollapsed'].split('\n')[0] \
        + ' ...'
    return result


def get_collapsible_text_box_assignment(checked_items, item_type):
    """Generates text regarding dosimeter/sample box assignment."""
    result = {
        'uncollapsed': '',
        'collapsed': ''
    }
    Model = get_model_class_from_name(item_type)

    for pk in checked_items:
        items = Model.objects.filter(pk=pk)
        is_match = (items.count() > 0)
        if is_match:
            item = items[0]
            has_box = (item.box is not None)
            if has_box:
                item_id = ''
                if item_type == 'sample':
                    item_id = item.name
                elif item_type == 'dosimeter':
                    item_id = item.dos_id
                
                result['uncollapsed'] += item_id + ' is assigned to ' \
                    + item.box.box_id + '\n'
    
    has_length = (len(result['uncollapsed']) > 0)
    if has_length:
        result['uncollapsed'] = 'The following ' + item_type + 's from your'\
            ' selection are already assigned to a box:\n\n' + \
            result['uncollapsed']
    else:
        result['uncollapsed'] =''
        return result

    result['collapsed'] = result['uncollapsed'].split('\n')[0] \
        + ' ...'
    return result

def get_collapsible_text_box_items(item_ids):
    """Generates text regarding dosimeter/sample box items."""
    result = {
        'uncollapsed': '',
        'collapsed': ''
    }

    for item_id in item_ids:
        result['uncollapsed'] += '- ' + item_id + '\n'
    
    has_length = (len(result['uncollapsed']) > 0)
    if has_length:
        result['uncollapsed'] = 'The action will be applied to the following '\
            'elements:\n\n' + result['uncollapsed']
    else:
        result['uncollapsed'] =''
        return result

    result['collapsed'] = result['uncollapsed'].split('\n')[0] \
        + ' ...'
    return result


def test(request):
    # Test whatever is needed here
    return JsonResponse({'msg': 'This is a test link.'})
