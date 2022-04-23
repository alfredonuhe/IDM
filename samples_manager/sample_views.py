"""Django app views related to Sample data model. It also includes
 auxiliary functions."""
import logging
from .forms import *
from .views import *
from .models import *
from django.urls import reverse
from django.http import JsonResponse
from django.forms import inlineformset_factory
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404, render


ALERT_MESSAGES = {
    'success': 'Operation executed successfully.',
    'create': 'Sample was successfully created!',
    'update': 'Sample was successfully updated!',
    'clone': 'Sample was successfully cloned!',
    'delete': 'Sample was successfully deleted!',
    'incorrect_box_id_format': 'Box id must folow the format "BOX-XXXXXX".',
    'not_unique': 'Sample already exists.',
    'empty_formset': 'Please add at least one layer to sample.',
    'invalid': 'Form is invalid. Please review the data.',
    'box_does_not_exist': 'A box with this id doesn\'t exist.',
    'box_no_selected_samples': 'No samples selected for box assignment.',
    'samples_have_invalid_set_id': 'At least a sample has an invalid set id. Please correct.',
    'samples_already_have_set_id': 'At least one sample already has a SET ID.',
    'infoream_error': 'Error remote database unavailable. Please try again later.',
    'default': 'Sorry something went wrong.',
    
}


def save_sample_form(request, form_data):
    """Creates sample and saves it in DB."""
    data = dict()
    logged_user = get_logged_user(request)
    if request.method == 'POST':
        data['form_is_valid'] = True
        if form_data['with_alert_message']:
            data['alert_message'] = ALERT_MESSAGES['success']
        if form_data['render_with_errors']:
            if form_data['form1'].is_valid() and form_data['form2'].is_valid() and form_data['form3'].is_valid(
            ) and form_data['layer_formset'].is_valid():
                if form_data['form_action'].lower() == 'create':
                    if form_data['form1'].checking_unique_sample() == True:
                        sample_data = {}
                        sample_data.update(form_data['form1'].cleaned_data)
                        sample_data.update(form_data['form2'].cleaned_data)
                        sample_data.update(form_data['form3'].cleaned_data)
                        sample_temp = Sample.objects.create(**sample_data)
                        sample = Sample.objects.get(pk=sample_temp.pk)
                        sample.status = 'Registered'
                        sample.created_by = logged_user
                        sample.updated_by = logged_user
                        sample.experiment = form_data['experiment']
                        sample.save()
                        if form_data['layer_formset'].is_valid():
                            if not form_data['layer_formset'].cleaned_data:
                                data['form_is_valid'] = False
                                if form_data['with_alert_message']:
                                    data['alert_message'] =  ALERT_MESSAGES['empty_formset']
                            else:
                                logging.info('Saving layer_formset')
                                for form in form_data['layer_formset'].forms:
                                    layer = form.save()
                                    layer.sample = sample
                                    logging.info('Layer sample save')
                                    layer.save()
                                if form_data['with_alert_message']:
                                    data['alert_message'] = ALERT_MESSAGES[form_data['form_action'].lower()]
                                save_occupancies(sample, form_data['form_action'].lower())
                                args = {
                                    'list_name': 'experiment_samples_list',
                                    'ids': [form_data['experiment'].id]
                                }
                                data['html_list'] = render_partial_list_to_string(
                                    request, args)
                    else:
                        data['form_is_valid'] = False
                        if form_data['with_alert_message']:
                            data['alert_message'] = ALERT_MESSAGES['not_unique']
                elif form_data['form_action'].lower() == 'update':
                    sample_temp = form_data['form1'].save()
                    form_data['form2'].save()
                    form_data['form3'].save()
                    sample_updated = Sample.objects.get(pk=sample_temp.pk)
                    sample_updated.status = 'Updated'
                    sample_updated.updated_by = logged_user
                    sample_updated.experiment = form_data['experiment']
                    sample_updated.save()
                    if form_data['layer_formset'].is_valid():
                        form_data['layer_formset'].save()
                    if form_data['with_alert_message']:
                        data['alert_message'] = ALERT_MESSAGES[form_data['form_action'].lower()]
                    save_occupancies(sample_updated, form_data['form_action'].lower())
                    args = {
                        'list_name': 'experiment_samples_list',
                        'ids': [form_data['experiment'].id]
                    }
                    data['html_list'] = render_partial_list_to_string(
                        request, args)
                elif form_data['form_action'].lower() == 'clone':
                    logging.info('Sample clone')
                    if form_data['form1'].checking_unique_sample() == True:
                        sample_data = {}
                        sample_data.update(form_data['form1'].cleaned_data)
                        sample_data.update(form_data['form2'].cleaned_data)
                        sample_data.update(form_data['form3'].cleaned_data)
                        sample_data.update({
                            'status': 'Registered',
                            'created_by': logged_user,
                            'updated_by': logged_user,
                            'experiment': form_data['experiment']
                        })
                        sample = Sample.objects.create(**sample_data)
                        if form_data['layer_formset'].is_valid():
                            if not form_data['layer_formset'].cleaned_data:
                                if form_data['with_alert_message']:
                                    data['alert_message'] =  ALERT_MESSAGES['empty_formset']
                                data['form_is_valid'] = False
                            else:
                                for lay in form_data['layer_formset'].cleaned_data:
                                    layer = Layer()
                                    layer.name = lay['name']
                                    layer.length = lay['length']
                                    layer.compound_type = lay['compound_type']
                                    layer.sample = sample
                                    layer.save()
                                if form_data['with_alert_message']:
                                    data['alert_message'] = ALERT_MESSAGES[form_data['form_action'].lower()]
                                save_occupancies(sample, form_data['form_action'].lower())
                                args = {
                                    'list_name': 'experiment_samples_list',
                                    'ids': [form_data['experiment'].id]
                                }
                                data['html_list'] = render_partial_list_to_string(
                                    request, args)
                    else:
                        data['form_is_valid'] = False
                        if form_data['with_alert_message']:
                            data['alert_message'] = ALERT_MESSAGES['not_unique']
                else:
                    sample_updated = form_data['form1'].save()
                    form_data['form2'].save()
                    form_data['form3'].save()
                    sample_updated.save()
                    if form_data['layer_formset'].is_valid():
                        form_data['layer_formset'].save()
                    if form_data['with_alert_message']:
                        data['alert_message'] = ALERT_MESSAGES[form_data['form_action'].lower()]
                    save_occupancies(sample_updated, form_data['form_action'].lower())
                    args = {
                        'list_name': 'experiment_samples_list',
                        'ids': [form_data['experiment'].id]
                    }
                    data['html_list'] = render_partial_list_to_string(
                        request, args)
            else:
                data['form_is_valid'] = False
                if form_data['with_alert_message']:
                    data['alert_message'] = ALERT_MESSAGES['invalid']
                logging.error('Sample data invalid')
    context = {
        'form1': form_data['form1'],
        'form2': form_data['form2'],
        'form3': form_data['form3'],
        'layer_formset': form_data['layer_formset'],
        'experiment': form_data['experiment'],
        'current_page': form_data['current_page'],
        'render_with_errors': form_data['render_with_errors'],
        'form_action': form_data['form_action'],
        'form_tag_action': form_data['form_tag_action']
    }
    data['html_form'] = render_to_string(form_data['template_name'],
                                         context,
                                         request=request)
    return data


def experiment_samples_archive(request, pk):
    """Retrieves archived samples related to experiment."""
    has_permission_or_403(request, 'experiment', pk)
    logged_user = get_logged_user(request)
    experiment = Experiment.objects.get(pk=pk)
    archives = ArchiveExperimentSample.objects.filter(experiment=experiment)
    pagination_data = get_pagination_data(request, archives)
    return render(
        request, 'samples_manager/experiment_samples_archive.html', {
            'archives': pagination_data['page_obj'].object_list,
            'logged_user': logged_user,
            'experiment': experiment,
            'pagination_data': pagination_data
        })


def generate_set_id():
    """Generates a set_id for a sample."""
    all_samples = Sample.objects.all()
    samples_numbers = []
    for sample in all_samples:
        if get_equipment_type(sample.set_id) == 'sample':
            samples_numbers.append(int(sample.set_id[4:]))
    samples_numbers.sort(reverse=False)
    is_empty = (len(samples_numbers) > 0)
    max_in_idm = samples_numbers[-1] if is_empty else FIRST_SET_ID_NUMBER
    last_id_num = int('9'*SET_ID_NUM_DIGITS)
    id_nums = generate_number_list(FIRST_SET_ID_NUMBER, max_in_idm, samples_numbers)
    id_nums = get_random_values_from_list(id_nums, 10)
    end_num = max_in_idm
    while (True):
        start_num = end_num + 1
        end_num = (start_num + 20 - len(id_nums))
        over_max_number = (end_num > last_id_num)
        if over_max_number:
            end_num = last_id_num
        id_nums = id_nums + generate_number_list(start_num, end_num)
        set_ids = [get_set_id_from_number(num) for num in id_nums]
        infoream_ids = [get_infoream_id(set_id) for set_id in set_ids]
        if len(infoream_ids) == 0:
            return None
        data = {
            'infoream_ids': infoream_ids
        }
        response = read_equipment_list(data)
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
            else:
                if item['response']['serialNumber'] is None:
                    return set_ids[i]
        id_nums = []


def assign_set_ids(request, pk):
    """Assigns set_id to experiment's samples."""
    has_permission_or_403(request, 'experiment', pk)
    experiment = Experiment.objects.get(pk=pk)
    data = dict()
    checked_elements = get_checked_elements(request)
    validation_data = checked_elements_are_valid(checked_elements, 'group', Sample, 5)
    if validation_data['valid']:
        if request.method == 'GET':
            data['form_is_valid'] = True
            data['alert_message'] = ALERT_MESSAGES['success']
            valid_samples = True
            for pk_sample in checked_elements:
                sample = Sample.objects.get(pk=pk_sample)
                has_id = (get_equipment_type(sample.set_id) == 'sample')
                if has_id:
                    valid_samples = False
                    break
            if valid_samples:
                for pk_sample in checked_elements:
                    sample = Sample.objects.get(pk=pk_sample)
                    set_id = generate_set_id()
                    if set_id is not None:
                        sample.set_id = set_id
                        sample.save()
                    else:
                        data['form_is_valid'] = False
                        data['alert_message'] = ALERT_MESSAGES['infoream_error']
            else:
                data['form_is_valid'] = False
                data['alert_message'] = ALERT_MESSAGES['samples_already_have_set_id']
    else:
        data['form_is_valid'] = False
        data['alert_message'] = validation_data['msg']

    args = {
        'list_name': 'experiment_samples_list',
        'ids': [experiment.id]
    }
    data['html_list'] = render_partial_list_to_string(
        request, args)

    return JsonResponse(data)


def experiment_samples_list(request, pk):
    """Retrieves samples related to experiment."""
    has_permission_or_403(request, 'experiment_samples', pk)
    logged_user = get_logged_user(request)
    experiment = Experiment.objects.get(pk=pk)
    samples = Sample.objects.filter(experiment=experiment).order_by('updated_at')
    search_url = reverse('samples_manager:experiment_samples_search',\
        args=[experiment.id])
    pagination_data = get_pagination_data(request, samples)
    samples_data = get_samples_occupancies(
        pagination_data['page_obj'].object_list)
    experiments = write_authorised_experiments(logged_user)
    template_url = 'samples_manager/experiment_samples_list.html'
    base_template = 'samples_manager/base_all_tab_list.html' \
        if logged_user.role == "Admin" else \
        'samples_manager/base_all_tab_list.html'
    return render(
        request, template_url, {
            'samples': pagination_data['page_obj'].object_list,
            'search_url': search_url,
            'samples_data': samples_data,
            'experiment': experiment,
            'logged_user': logged_user,
            'experiments': experiments,
            'base_template': base_template,
            'pagination_data': pagination_data
        })


def admin_samples_list(request):
    """Retrieves all available samples."""
    has_permission_or_403(request, 'admin')
    template_url = 'samples_manager/experiment_samples_list.html'
    logged_user = get_logged_user(request)
    samples = Sample.objects.all()
    search_url = reverse('samples_manager:samples_search', args=[experiment.id])
    pagination_data = get_pagination_data(request, samples)
    return render(
        request, template_url, {
            'samples': pagination_data['page_obj'].object_list,
            'search_url': search_url,
            'logged_user': logged_user,
            'pagination_data': pagination_data
        })


def sample_create(request, pk):
    """Creates sample."""
    has_permission_or_403(request, 'experiment', pk)
    logged_user = get_logged_user(request)
    set_id_readonly = (not is_admin(logged_user))
    experiment = Experiment.objects.get(pk=pk)
    current_page = 1
    render_with_errors = True
    with_alert_message = True
    if 'current_page' in request.POST.keys():
        current_page = int(request.POST['current_page'])
    if 'render_with_errors' in request.POST.keys():
        render_with_errors = bool(request.POST['render_with_errors'] == 'on')
    if 'with_alert_message' in request.POST.keys():
        with_alert_message = bool(request.POST['with_alert_message'] == 'on')
    LayerFormset = inlineformset_factory(
        Sample,
        Layer,
        form=LayerForm,
        extra=0,
        min_num=1,
        validate_min=True,
        error_messages='Layers not correctly filled.',
        formset=LayerFormSet)
    if request.method == 'POST':
        form1 = SampleForm1(request.POST, experiment_id=experiment.id\
            , set_id_readonly=set_id_readonly)
        form2 = SampleForm2(request.POST, experiment_id=experiment.id)
        layer_formset = LayerFormset(request.POST)
        form3 = SampleForm3(request.POST, experiment_id=experiment.id)
    else:
        form1 = SampleForm1(experiment_id=experiment.id\
            , set_id_readonly=set_id_readonly)
        form2 = SampleForm2(experiment_id=experiment.id)
        layer_formset = LayerFormset()
        form3 = SampleForm3(experiment_id=experiment.id)
    form_data = {
        'form1': form1,
        'form2': form2,
        'form3': form3,
        'layer_formset': layer_formset,
        'experiment': experiment,
        'current_page': current_page,
        'render_with_errors': render_with_errors,
        'with_alert_message': with_alert_message,
        'form_action': 'Create',
        'form_tag_action': reverse('samples_manager:sample_create' , args=[experiment.id]),
        'template_name': 'samples_manager/partial_sample_create_update_clone.html'
    }

    data = save_sample_form(request, form_data)
    return JsonResponse(data)


def sample_update(request, pk):
    """Updates sample."""
    data = dict()
    has_permission_or_403(request, 'experiment', pk)
    logged_user = get_logged_user(request)
    set_id_readonly = (not is_admin(logged_user))
    experiment = Experiment.objects.get(pk=pk)
    current_page = 1
    render_with_errors = True
    with_alert_message = True
    if 'current_page' in request.POST.keys():
        current_page = int(request.POST['current_page'])
    if 'render_with_errors' in request.POST.keys():
        render_with_errors = bool(request.POST['render_with_errors'] == 'on')
    if 'with_alert_message' in request.POST.keys():
        with_alert_message = bool(request.POST['with_alert_message'] == 'on')
    LayerFormset = inlineformset_factory(
        Sample,
        Layer,
        form=LayerForm,
        extra=0,
        min_num=1,
        validate_min=True,
        error_messages='Layers not correctly filled.',
        formset=LayerFormSet)
    checked_elements = get_checked_elements(request)
    is_form_refresh = (not render_with_errors and not with_alert_message)
    if is_form_refresh:
        valid = True
    else:
        validation_data = checked_elements_are_valid(checked_elements, 'single', Sample)
        valid = validation_data['valid']
    if valid:
        pk_sample = checked_elements[0]
        sample = Sample.objects.get(pk=pk_sample)
        if request.method == 'POST':
            form1 = SampleForm1(request.POST,
                                instance=sample,
                                experiment_id=experiment.id,
                                set_id_readonly=set_id_readonly,
                                name_validation=False)
            form2 = SampleForm2(request.POST,
                                instance=sample,
                                experiment_id=experiment.id)
            form3 = SampleForm3(request.POST,
                                instance=sample,
                                experiment_id=experiment.id,)
            layer_formset = LayerFormset(request.POST, instance=sample)
        else:
            form1 = SampleForm1(instance=sample, experiment_id=experiment.id\
                , set_id_readonly=set_id_readonly, name_validation=False)
            form2 = SampleForm2(instance=sample, experiment_id=experiment.id)
            form3 = SampleForm3(instance=sample, experiment_id=experiment.id)
            layer_formset = LayerFormset(instance=sample)

        form_data = {
            'form1': form1,
            'form2': form2,
            'form3': form3,
            'layer_formset': layer_formset,
            'experiment': experiment,
            'current_page': current_page,
            'render_with_errors': render_with_errors,
            'with_alert_message': with_alert_message,
            'form_action': 'Update',
            'form_tag_action': reverse('samples_manager:sample_update' , args=[experiment.id]),
            'template_name': 'samples_manager/partial_sample_create_update_clone.html'
        } 
        data = save_sample_form(request, form_data)
    else:
        data['form_is_valid'] = False
        data['alert_message'] = validation_data['msg']
    return  JsonResponse(data)


def sample_clone(request, pk):
    """Clones sample."""
    data = dict()
    has_permission_or_403(request, 'experiment', pk)
    logged_user = get_logged_user(request)
    set_id_readonly = (not is_admin(logged_user))
    experiment = Experiment.objects.get(pk=pk)
    current_page = 1
    render_with_errors = True
    with_alert_message = True
    if 'current_page' in request.POST.keys():
        current_page = int(request.POST['current_page'])
    if 'render_with_errors' in request.POST.keys():
        render_with_errors = bool(request.POST['render_with_errors'] == 'on')
    if 'with_alert_message' in request.POST.keys():
        with_alert_message = bool(request.POST['with_alert_message'] == 'on')
    LayerFormset = inlineformset_factory(
        Sample,
        Layer,
        form=LayerForm,
        extra=0,
        min_num=1,
        validate_min=True,
        error_messages='Layers not correctly filled.',
        formset=LayerFormSet)
    checked_elements = get_checked_elements(request)
    validation_data = checked_elements_are_valid(checked_elements, 'single', Sample)
    if validation_data['valid']:
        pk_sample = checked_elements[0]
        sample = Sample.objects.get(pk=pk_sample)
        if request.method == 'POST':
            form1 = SampleForm1(request.POST,
                                experiment_id=experiment.id,
                                instance=sample,
                                set_id_readonly=set_id_readonly)
            form2 = SampleForm2(request.POST,
                                experiment_id=experiment.id,
                                instance=sample)
            form3 = SampleForm3(request.POST,
                                experiment_id=experiment.id,
                                instance=sample)
            layer_formset = LayerFormset(request.POST, instance=sample)
        else:
            form1 = SampleForm1(experiment_id=experiment.id,
                                instance=sample, 
                                set_id_readonly=set_id_readonly,
                                initial={'set_id': ''})
            form2 = SampleForm2(experiment_id=experiment.id, instance=sample)
            form3 = SampleForm3(experiment_id=experiment.id, instance=sample)
            layer_formset = LayerFormset(instance=sample)

        form_data = {
            'form1': form1,
            'form2': form2,
            'form3': form3,
            'layer_formset': layer_formset,
            'experiment': experiment,
            'current_page': current_page,
            'render_with_errors': render_with_errors,
            'with_alert_message': with_alert_message,
            'form_action': 'Clone',
            'form_tag_action': reverse('samples_manager:sample_clone' , args=[experiment.id]),
            'template_name': 'samples_manager/partial_sample_create_update_clone.html'
        } 
        data = save_sample_form(request, form_data)
    else:
        data['form_is_valid'] = False
        data['alert_message'] = validation_data['msg']
    return  JsonResponse(data)


def sample_delete(request, pk):
    """Deletes sample."""
    has_permission_or_403(request, 'experiment', pk)
    experiment = Experiment.objects.get(pk=pk)
    data = dict()
    checked_elements = get_checked_elements(request)
    validation_data = checked_elements_are_valid(checked_elements, 'group', Sample)
    if validation_data['valid']:
        if request.method == 'POST':
            for pk_sample in checked_elements:
                sample = Sample.objects.get(pk=pk_sample)
                sample.delete()
            data['alert_message'] = ALERT_MESSAGES['delete']
            args = {
                'list_name': 'experiment_samples_list',
                'ids': [experiment.id]
            }
            data['html_list'] = render_partial_list_to_string(
                request, args)
        else:
            context = dict()
            context['experiment'] = experiment
            context['additional_text'] = get_collapsible_text_checked_elements(
                checked_elements, Sample)
            data['html_form'] = render_to_string(
                'samples_manager/partial_sample_delete.html',
                context,
                request=request,
            )
    else:
        data['form_is_valid'] = False
        data['alert_message'] = validation_data['msg']
    return  JsonResponse(data)


def redirect_sample_details(request, pk):
    """Redirects user to sample's details page."""
    data = dict()
    data['form_is_valid'] = True
    experiment = Experiment.objects.get(pk=pk)
    has_permission_or_403(request, 'experiment', experiment.id)
    logged_user = get_logged_user(request)
    checked_elements = get_checked_elements(request)
    validation_data = checked_elements_are_valid(checked_elements, 'single', Sample)
    if validation_data['valid']:
        pk = checked_elements[0]
        sample = get_object_or_404(Sample, pk=pk)
        has_permission_or_403(request, 'sample', sample.id)
        data['redirect_url'] = reverse('samples_manager:sample_details',
            args=[experiment.id, sample.id])
    else:
        data['form_is_valid'] = False
        data['alert_message'] = validation_data['msg']
    return JsonResponse(data)


def sample_details(request, experiment_id, pk):
    """Shows detail page for sample"""
    has_permission_or_403(request, 'experiment', experiment_id)
    logged_user = get_logged_user(request)
    sample = get_object_or_404(Sample, pk=pk)
    layers = Layer.objects.filter(sample=sample)
    data = dict()

    return render(request, 'samples_manager/sample_details.html', {
        'logged_user': logged_user,
        'sample': sample,
        'layers': layers
    })


def sample_move(request, pk):
    """Moves sample to different experiment and records in archive."""
    has_permission_or_403(request, 'experiment', pk)
    experiment = Experiment.objects.get(pk=pk)
    data = dict()
    logged_user = get_logged_user(request)
    checked_elements = get_checked_elements(request)
    validation_data = checked_elements_are_valid(checked_elements, 'group', Sample)
    if validation_data['valid']:
        if request.method == 'POST':
            for pk_sample in checked_elements:
                sample = Sample.objects.get(pk=pk_sample)
                sample.req_fluence = ReqFluence.objects.get(\
                    pk=request.POST['req_fluence'])
                sample.material = Material.objects.get(\
                    pk=request.POST['material'])
                sample.category = request.POST['category']
                sample.experiment = Experiment.objects.get(\
                    pk=request.POST['experiment'])
                sample.save()
                new_archive = ArchiveExperimentSample()
                new_archive.experiment = experiment
                new_archive.sample = sample
                new_archive.save()
            data['alert_message'] = ALERT_MESSAGES['success']
            args = {
                'list_name': 'experiment_samples_list',
                'ids': [experiment.id]
            }
            data['html_list'] = render_partial_list_to_string(
                request, args)
        else:
            experiment_new_id = int(request.GET['experiment']) if 'experiment' \
                in request.GET.keys() else None
            form1_data = {'experiment': experiment_new_id}
            form1 = MoveSampleToExperimentForm1(\
                initial=form1_data, logged_user=logged_user,
                experiment_old_id=pk)
            if experiment_new_id is None:
                experiment_new_id = form1.fields['experiment'].choices[0][0]
            form2 = MoveSampleToExperimentForm2(\
                experiment_new_id=experiment_new_id)
            context = dict()
            context['experiment'] = experiment
            context['form1'] = form1
            context['form2'] = form2
            context['additional_text'] = get_collapsible_text_checked_elements(
                checked_elements, Sample)
            data['html_form'] = render_to_string(
                'samples_manager/partial_sample_move.html',
                context,
                request=request,
            )
    else:
        data['form_is_valid'] = False
        data['alert_message'] = validation_data['msg']
    return  JsonResponse(data)


def sample_attach_box(request, pk):
    """Assigns Box to sample."""
    has_permission_or_403(request, 'experiment', pk)
    experiment = Experiment.objects.get(pk=pk)
    data = dict()
    data['form_is_valid'] = True
    checked_elements = get_checked_elements(request)
    validation_data = checked_elements_are_valid(checked_elements, 'group', Sample)
    if validation_data['valid']:
        if request.method == 'POST':
            form = SampleDosimeterBoxAssociationForm(request.POST)
            if form.is_valid():
                try:
                    box = None
                    if request.POST['box_id'] != 'None':
                        box = Box.objects.get(box_id=request.POST['box_id'])
                    samples_ids_are_valid = \
                        equipment_ids_are_correct_type(checked_elements, 'sample')
                    if samples_ids_are_valid:
                        for pk_sample in checked_elements:
                            try:
                                sample = Sample.objects.get(pk=pk_sample)
                                sample.box = box
                                sample.save()
                                data['alert_message'] = ALERT_MESSAGES['success']
                            except Box.DoesNotExist:
                                data['form_is_valid'] = False
                                data['alert_message'] = ALERT_MESSAGES['default']
                    else:
                        data['form_is_valid'] = False
                        data['alert_message'] = ALERT_MESSAGES['samples_have_invalid_set_id']
                except Box.DoesNotExist:
                    data['form_is_valid'] = False
                    data['alert_message'] = ALERT_MESSAGES['invalid']
            else:
                data['form_is_valid'] = False
                data['alert_message'] = ALERT_MESSAGES['invalid']
        else:
            is_single = checked_elements_are_valid(checked_elements, 'single', Sample)
            if is_single:
                pk_sample = checked_elements[0]
                sample = Sample.objects.get(pk=pk_sample)
                box_exists = (sample.box != None)
                if box_exists:
                    data = {'box_id': sample.box.box_id}
                    form = SampleDosimeterBoxAssociationForm(initial=data)
                else:
                    form = SampleDosimeterBoxAssociationForm()
            else:
                form = SampleDosimeterBoxAssociationForm()

        additional_text = get_collapsible_text_checked_elements(\
            checked_elements, Sample)
        display_additional_text = (len(additional_text['collapsed']) > 0)
        context = {
            'form': form, 
            'experiment': experiment,
            'form_tag_action': reverse('samples_manager:sample_attach_box', args=[experiment.id]),
            'additional_text': additional_text,
            'display_additional_text': display_additional_text
        }
        args = {
            'list_name': 'experiment_samples_list',
            'ids': [experiment.id]
        }
        data['html_list'] = render_partial_list_to_string(
            request, args)
        data['html_form'] = render_to_string(
            'samples_manager/partial_box_association.html',
            context,
            request=request,
        )
    else:
        data['form_is_valid'] = False
        data['alert_message'] = validation_data['msg']
    return JsonResponse(data)


def sample_write_infoream(request, pk):
    """Writes sample to inforEAM."""
    has_permission_or_403(request, 'experiment', pk)
    experiment = Experiment.objects.get(pk=pk)
    data = dict()
    data['form_is_valid'] = True
    checked_elements = get_checked_elements(request)
    validation_data = checked_elements_are_valid(checked_elements, 'group', Sample, 5)
    if validation_data['valid']:
        samples_ids_are_valid = \
            equipment_ids_are_correct_type(checked_elements, 'sample')
        if samples_ids_are_valid:
            if request.method == 'POST':
                equipment_ids = get_ids_from_checked_equipments(checked_elements, 
                    'sample')
                data = write_equipment_in_infoream(equipment_ids)
            else:
                context = dict()
                context['experiment'] = experiment
                context['additional_text'] = get_collapsible_text_checked_elements(
                    checked_elements, Sample)
                data['html_form'] = render_to_string(
                    'samples_manager/partial_write_sample_infoream.html',
                    context,
                    request=request,
                )
        else:
            data['form_is_valid'] = False
            data['alert_message'] = ALERT_MESSAGES['samples_have_invalid_set_id']
    else:
        data['form_is_valid'] = False
        data['alert_message'] = validation_data['msg']
    return JsonResponse(data)

def sample_results(request, pk):
    """Redirects to sample dosimetry results page."""
    has_permission_or_403(request, 'experiment', pk)
    data = dict()
    data['form_is_valid'] = True
    checked_elements = get_checked_elements(request)
    validation_data = checked_elements_are_valid(checked_elements, 'single', Sample)
    if validation_data['valid']:
        pk_sample = checked_elements[0]
        sample = Sample.objects.get(pk=pk_sample)
        data['redirect_url'] = reverse('samples_manager:sample_dosimetry_results',
            args=[sample.id])
    else:
        data['form_is_valid'] = False
        data['alert_message'] = validation_data['msg']
    return JsonResponse(data)

def sample_read_infoream(request, pk):
    """Reads sample's inforEAM information."""
    has_permission_or_403(request, 'experiment', pk)
    data = dict()
    data['form_is_valid'] = True
    checked_elements = get_checked_elements(request)
    validation_data = checked_elements_are_valid(checked_elements, 'single', Sample)
    if validation_data['valid']:
        pk_sample = checked_elements[0]
        set_id = Sample.objects.get(pk=pk_sample).set_id
        data['redirect_url'] = reverse('samples_manager:read_equipment_infoream',
            args=[set_id])
    else:
        data['form_is_valid'] = False
        data['alert_message'] = validation_data['msg']
    return JsonResponse(data)