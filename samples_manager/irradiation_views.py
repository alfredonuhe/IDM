"""Django app views related to Irradiation data model. It also includes
 auxiliary functions."""

from .forms import *
from .views import *
from .models import *
from django.db.models import Q
from django.urls import reverse
from django.http import JsonResponse
from django.template.loader import render_to_string
from .templatetags.custom_filters import num_notation
from django.shortcuts import get_object_or_404, render


ALERT_MESSAGES = {
    'success': 'Operation executed successfully.',
    'create': 'Irradiation was successfully created!',
    'create_irradiation_group': 'Irradiation group was successfully created! '\
        'Now you will be redirected to the irradiations page.',
    'update': 'Irradiation was successfully updated!',
    'clone': 'Irradiation was successfully cloned!',
    'delete': 'Irradiation was successfully deleted!',
    'invalid': 'Form is invalid. Please review the data.',
    'invalid_set_ids': 'Invalid operation. Samples have invalid set ids.',
}


def save_irradiation_form(request, form_data):
    """Display and save Irradiation form."""
    data = dict()
    logged_user = get_logged_user(request)
    data['form_is_valid'] = True
    if request.method == 'POST':
        data['alert_message'] = ALERT_MESSAGES['success']
        if form_data['form'].is_valid():
            irradiation = None
            if form_data['form_action'].lower() == 'create':
                irradiation = Irradiation(
                dos_position=form_data['form'].cleaned_data['dos_position'])
                irradiation.save()
                irradiation.sample = form_data['form'].cleaned_data['sample']
                irradiation.dosimeter = form_data['form'].cleaned_data['dosimeter']
                irradiation.irrad_table = form_data['form'].cleaned_data['irrad_table']
                irradiation.table_position = form_data['form'].cleaned_data['table_position']
                irradiation.date_in = form_data['form'].cleaned_data['date_in']
                irradiation.date_out = form_data['form'].cleaned_data['date_out']
                irradiation.comments = form_data['form'].cleaned_data['comments']
                irradiation.status = 'Registered'
                irradiation.updated_by = logged_user
                irradiation.save()
                data['alert_message'] = data['alert_message'] = ALERT_MESSAGES[form_data['form_action'].lower()]
            elif form_data['form_action'].lower() == 'update':
                irradiation = form_data['form'].save()
                data['alert_message'] = data['alert_message'] = ALERT_MESSAGES[form_data['form_action'].lower()]
            else:
                pass
            set_irradiation_state([irradiation])
            args = {'list_name': 'irradiations_list'}
            data['html_list'] = render_partial_list_to_string(
                request, args)
        else:
            data['form_is_valid'] = False
            data['alert_message'] = ALERT_MESSAGES['invalid']
    
    context = {
        'form': form_data['form'],
        'current_page': form_data['current_page'],
        'render_with_errors': form_data['render_with_errors'],
        'form_action': form_data['form_action'],
        'form_tag_action': form_data['form_tag_action']
    }
    data['html_form'] = render_to_string(form_data['template_name'],
                                         context,
                                         request=request)
    return data


def irradiations_list(request):
    """Retrieves all completed irradiations."""
    has_permission_or_403(request, 'admin')
    logged_user = get_logged_user(request)
    ongoing_irradiations = Irradiation.objects.all()
    search_url = reverse('samples_manager:irradiations_search')
    pagination_data = get_pagination_data(request, ongoing_irradiations)
    return render(request, 'samples_manager/irradiations_list.html', {
        'irradiations': pagination_data['page_obj'].object_list,
        'search_url': search_url,
        'logged_user': logged_user,
        'pagination_data': pagination_data
    })


def irradiation_status_update(request):
    """Updates status of irradiation."""
    has_permission_or_403(request, 'admin')
    data = dict()
    checked_elements = get_checked_elements(request)
    validation_data = checked_elements_are_valid(checked_elements, 'group', Irradiation)
    data['form_is_valid'] = True
    if validation_data['valid']:
        if request.method == 'POST':
            data['alert_message'] = ALERT_MESSAGES['success']
            for pk in checked_elements:
                irradiation = get_object_or_404(Irradiation, pk=pk)
                new_status = request.POST['status']
                same_status = \
                    (irradiation.status == new_status)
                beam_transition = \
                    ('beam' in irradiation.status.lower() or \
                    'beam' in new_status.lower())
                form = IrradiationStatus(request.POST, instance=irradiation)
                if form.is_valid():
                    if not same_status:
                        if beam_transition:
                            set_beam_irradiation_state([pk], new_status)
                        else:
                            form.save()
                            set_irradiation_state([irradiation])
                            irradiation.save()
                else:
                    data['form_is_valid'] = False
                    data['alert_message'] = ALERT_MESSAGES['invalid']
            args = {'list_name': 'irradiations_list'}
            data['html_list'] = render_partial_list_to_string(
                request, args)
        else:
            is_single = checked_elements_are_valid(checked_elements, 'single', Irradiation)
            if is_single:
                pk = checked_elements[0]
                irradiation = Irradiation.objects.get(pk=pk)
                form = IrradiationStatus(instance=irradiation)
            else:
                form = IrradiationStatus()
        context = dict()
        context['form'] = form
        context['additional_text'] = get_collapsible_text_checked_elements(
            checked_elements, Irradiation)
        data['html_form'] = render_to_string(
            'samples_manager/partial_irradiation_status_update.html',
            context,
            request=request,
        )
    else:
        data['form_is_valid'] = False
        data['alert_message'] = validation_data['msg']
    return JsonResponse(data)


def irradiation_create(request):
    """Creates irradiation."""
    has_permission_or_403(request, 'admin')
    current_page = 1
    render_with_errors = True
    if 'current_page' in request.POST.keys():
        current_page = int(request.POST['current_page'])
    if 'render_with_errors' in request.POST.keys():
        render_with_errors = bool(request.POST['render_with_errors'] == 'on')
    if request.method == 'POST':
        form = IrradiationForm(request.POST)
    else:
        form = IrradiationForm()
    form_data = {
        'form': form,
        'current_page': current_page,
        'render_with_errors': render_with_errors,
        'form_action': 'Create',
        'form_tag_action': reverse('samples_manager:irradiation_create'),
        'template_name': 'samples_manager/partial_irradiation_create_update.html'
    }
    data = save_irradiation_form(request, form_data)
    return JsonResponse(data)


def irradiation_update(request):
    """Updates irradiation."""
    has_permission_or_403(request, 'admin')
    checked_elements = get_checked_elements(request)
    validation_data = checked_elements_are_valid(checked_elements, 'single', Irradiation)
    data = dict()
    if validation_data['valid']:
        pk = checked_elements[0]
        irradiation = get_object_or_404(Irradiation, pk=pk)
        current_page = 1
        render_with_errors = True
        if 'current_page' in request.POST.keys():
            current_page = int(request.POST['current_page'])
        if 'render_with_errors' in request.POST.keys():
            render_with_errors = bool(request.POST['render_with_errors'] == 'on')
        if request.method == 'POST':
            form = IrradiationForm(request.POST, instance=irradiation)
        else:
            form = IrradiationForm(instance=irradiation)
        form_data = {
            'form': form,
            'current_page': current_page,
            'render_with_errors': render_with_errors,
            'form_action': 'Update',
            'form_tag_action': reverse('samples_manager:irradiation_update'),
            'template_name': 'samples_manager/partial_irradiation_create_update.html'
        }
        data = save_irradiation_form(request, form_data)
    else:
        data['form_is_valid'] = False
        data['alert_message'] = validation_data['msg']
    return JsonResponse(data)


def irradiation_delete(request):
    """Deletes irradiation."""
    has_permission_or_403(request, 'admin')
    data = dict()
    checked_elements = get_checked_elements(request)
    validation_data = checked_elements_are_valid(checked_elements, 'group', Irradiation)
    if validation_data['valid']:
        if request.method == 'POST':
            for pk in checked_elements:
                irradiation = get_object_or_404(Irradiation, pk=pk)
                irradiation.delete()
            data['alert_message'] = ALERT_MESSAGES['delete']
            args = {'list_name': 'irradiations_list'}
            data['html_list'] = render_partial_list_to_string(
                request, args)
        else:
            context = dict()
            context['additional_text'] = get_collapsible_text_checked_elements(
                checked_elements, Irradiation)
            data['html_form'] = render_to_string(
                'samples_manager/partial_irradiation_delete.html',
                context,
                request=request,
            )
    else:
        data['form_is_valid'] = False
        data['alert_message'] = validation_data['msg']
    return JsonResponse(data)


def group_irradiation_create(request, pk):
    """
    Displays and saves IrradiationGroup form. 

    POST request saved form. GET request displays form.
    """
    has_permission_or_403(request, 'experiment', pk)
    data = dict()
    checked_elements = get_checked_elements(request)
    validation_data = checked_elements_are_valid(checked_elements, 'group', Sample)
    if validation_data['valid']:
        if request.method == 'POST':
            data['form_is_valid'] = True
            data['alert_message'] = ALERT_MESSAGES['create_irradiation_group']
            form = GroupIrradiationForm(request.POST)
            if form.is_valid():
                if form.cleaned_data is not None:
                    dosimeter = form.cleaned_data['dosimeter']
                    for pk in checked_elements:
                        logged_user = get_logged_user(request)
                        sample = Sample.objects.get(pk=pk)
                        irradiation = Irradiation(dos_position=1)
                        irradiation.save()
                        irradiation.sample = sample
                        irradiation.dosimeter = dosimeter
                        irradiation.irrad_table = form.cleaned_data['irrad_table']
                        irradiation.table_position = form.cleaned_data[
                            'table_position']
                        irradiation.status = 'Registered'
                        irradiation.updated_by = logged_user
                        irradiation.created_by = logged_user
                        irradiation.dos_position = 1
                        set_irradiation_state([irradiation])
                        irradiation.save()
                data['form_is_valid'] = True
            else:
                data['form_is_valid'] = False
                data['alert_message'] = ALERT_MESSAGES['invalid']
        else:
            valid_ids = True
            for pk in checked_elements:
                valid_ids = (get_equipment_type(\
                    Sample.objects.get(pk=pk).set_id) != None)
                if not valid_ids:
                    break
            if valid_ids:
                form = GroupIrradiationForm()
                context = dict()
                context['form'] = form
                context['experiment_id'] = pk
                context['additional_text'] = get_collapsible_text_checked_elements(
                    checked_elements, Sample)
                data['html_form'] = render_to_string(
                    'samples_manager/partial_sample_group_irradiation_form.html',
                    context,
                    request=request)
            else:
                data['form_is_valid'] = False
                data['alert_message'] = ALERT_MESSAGES['invalid_set_ids']
    else:
        data['form_is_valid'] = False
        data['alert_message'] = validation_data['msg']
    return JsonResponse(data)


def dosimetry_results_list(request):
    """Retrieves all dosimery results."""
    has_permission_or_403(request, 'admin')
    logged_user = get_logged_user(request)
    results = Irradiation.objects.filter(Q(status='Completed')).order_by('id')
    search_url = reverse('samples_manager:dosimetry_results_search')
    pagination_data = get_pagination_data(request, results)
    return render(request, 'samples_manager/dosimetry_results_list.html', {
        'results': pagination_data['page_obj'].object_list,
        'search_url': search_url,
        'logged_user': logged_user,
        'pagination_data': pagination_data
    })


def sample_dosimetry_results(request, pk):
    """Retreives irradiations dosiemtry results related to sample."""
    has_permission_or_403(request, 'sample', pk)
    logged_user = get_logged_user(request)
    results = Irradiation.objects.filter(sample=pk)
    pagination_data = get_pagination_data(request, results)
    sample = get_object_or_404(Sample, pk=pk)
    sample_fluences = get_sample_fluences(sample)
    return render(request, 'samples_manager/sample_dosimetry_results_list.html', {
            'sample': sample,
            'results': pagination_data['page_obj'].object_list,
            'logged_user': logged_user,
            'sample_fluences': sample_fluences,
            'pagination_data': pagination_data
    })


def irradiation_in_beam_status_update(request):
    """Updates in beam status and displays all irradiations."""
    has_permission_or_403(request, 'admin')
    data = dict()
    checked_elements = get_checked_elements(request)
    validation_data = checked_elements_are_valid(checked_elements, 'group', Irradiation, 10)
    data['form_is_valid'] = True
    if validation_data['valid']:
        if request.method == 'POST':
            data['alert_message'] = ALERT_MESSAGES['success']
            to_in_beam = (request.POST['in_beam'] == 'True')
            in_beam_status, out_beam_status = Irradiation.get_beam_status()
            status = in_beam_status if to_in_beam else out_beam_status
            set_beam_irradiation_state(checked_elements, status)
            args = {'list_name': 'irradiations_list'}
            data['html_list'] = render_partial_list_to_string(
                request, args)
            data['updated_beam_status'] = True
        else:
            is_single = checked_elements_are_valid(checked_elements, 'single', Irradiation)
            if is_single:
                pk = checked_elements[0]
                irradiation = Irradiation.objects.get(pk=pk)
                in_beam = ('in' in irradiation.status.lower() and \
                    'beam' in irradiation.status.lower())
                data = {'in_beam': in_beam}
                form = IrradiationInBeamStatus(initial=data)
            else:
                form = IrradiationInBeamStatus()
            context = dict()
            context['form'] = form
            context['additional_text'] = get_collapsible_text_checked_elements(
                checked_elements, Irradiation)
            data['html_form'] = render_to_string(
                'samples_manager/partial_irradiation_in_beam_status_update.html',
                context,
                request=request,
            )
    else:
        data['form_is_valid'] = False
        data['alert_message'] = validation_data['msg']
    return JsonResponse(data)


def set_beam_irradiation_state(pks, status):
    """Applies action related to beam state."""
    set_in_beam = ('in' in status.lower() and \
        'beam' in status.lower())

    for pk in pks:
        irradiation = get_object_or_404(Irradiation, pk=pk)
        in_beam_status, _ = Irradiation.get_beam_status()
        if irradiation.date_out is None:
            if set_in_beam:
                if irradiation.status != in_beam_status:
                    irradiation.date_in = get_aware_datetime()
                    irradiation.date_out = None
                    irradiation.date_first_sec = None
                    irradiation.date_last_sec = None
                    irradiation.status = status
            else:
                if irradiation.status == in_beam_status:
                    irradiation.date_out = get_aware_datetime()
                    sec_dates = get_sec_dates_from_irradiation(
                        irradiation)
                    irradiation.date_first_sec = sec_dates['date_first_sec']
                    irradiation.date_last_sec = sec_dates['date_last_sec']
                    irradiation.status = status
            set_irradiation_state([irradiation])
            irradiation.save()
        else:
            if set_in_beam:
                if irradiation.status != in_beam_status:
                    Irradiation.objects.create(
                        sample=irradiation.sample,
                        dosimeter=irradiation.dosimeter,
                        previous_irradiation=irradiation,
                        dos_position=irradiation.dos_position,
                        irrad_table=irradiation.irrad_table,
                        table_position=irradiation.table_position,
                        status=in_beam_status,
                        date_in = get_aware_datetime()
                    )


def get_irradiations_factor(irradiations):
    """
    Retrieves irradiation factors for list of irradiations.
    If none match, then assigns a default factor of 1.
    """
    result = []
    default_factor = None
    factors = FluenceFactor.objects.filter(value=1)
    exists = (len(factors) > 0)
    if exists:
        default_factor = factors[0]
    else:
        default_factor = FluenceFactor.objects.create(value=1)
    for i in irradiations:
        factors = FluenceFactor.objects.filter(
            status="Active",
            irrad_table=i.irrad_table,
            dosimeter_height=i.dosimeter.height,
            dosimeter_width=i.dosimeter.width)
        if (len(factors) == 1):
            result.append(factors[0])
        else:
            result.append(default_factor)
    return result


def calc_beam_related_data(irradiations, with_sec_data=False, update=False):
    """Updates beam realted data of irradiaitons in list."""
    data = dict()
    data['irradiation_data'] = []
    for irradiation in irradiations:
        has_parent = (irradiation.previous_irradiation \
            is not None)
        acc_sec = 0
        # If has parent calculate parent's acc_sec if not already done. 
        if has_parent:
            parent_sec = 0 if irradiation.previous_irradiation.sec is None \
                else irradiation.previous_irradiation.sec
            acc_sec += parent_sec
        if irradiation.date_in:
            if irradiation.date_out:
                acc_sec += calc_acc_sec_in_range(irradiation.date_in,
                    irradiation.date_out)
            else:
                acc_sec += calc_acc_sec_in_range(irradiation.date_in)
        # Other values
        factor = get_irradiations_factor([irradiation])[0]
        estimated_fluence = acc_sec * factor.value
        is_in_beam = (irradiation.status == 'InBeam')

        if with_sec_data:
            sec_dates = get_sec_dates_from_irradiation(
                    irradiation)
        
        # Update irradiations if required
        if update:
            irradiation.sec = acc_sec
            irradiation.estimated_fluence = estimated_fluence
            irradiation.fluence_factor = factor
            if with_sec_data:
                irradiation.date_first_sec = sec_dates['date_first_sec']
                irradiation.date_last_sec = sec_dates['date_last_sec']
            irradiation.save()

        element = dict()
        element['pk'] = irradiation.id
        element['sec'] = acc_sec
        element['estimated_fluence'] = estimated_fluence
        element['factor'] = factor
        element['factor_value'] = factor.value
        element['updated_at'] = get_aware_cern_datetime()\
            .strftime('%d/%m/%Y %H:%M:%S')
        element['in_beam'] = is_in_beam
        if with_sec_data:
            element['date_first_sec'] = sec_dates['date_first_sec']
            element['date_last_sec'] = sec_dates['date_last_sec']

        data['irradiation_data'].append(element)

    return data


def get_irradiation_state(irradiations):
    """Returns irradiation irradiation state."""
    result = []
    for irradiation in irradiations:
        if irradiation.date_in is None and \
            irradiation.date_out is None:
            # Irradiation not started
            result.append(0)
        elif irradiation.date_in is not None and \
            irradiation.date_out is None:
            # Irradiation ongoing
            result.append(1)
        elif irradiation.date_in is not None and \
            irradiation.date_out is not None and \
            irradiation.measured_fluence is None:
            # Irradiation out of beam
            result.append(2)
        elif irradiation.date_in is not None and \
            irradiation.date_out is not None and \
            irradiation.measured_fluence is not None:
            # Irradiation completed
            result.append(3)
        else:
            result.append(None)
    return result


def set_irradiation_state(irradiations):
    """Sets data according to iiradiation state."""
    data = calc_beam_related_data(irradiations, True)['irradiation_data']
    states = get_irradiation_state(irradiations)
    for i in range(0, len(irradiations)):
        for e in data:
            if e['pk'] == irradiations[i].id:
                if states[i] is not None:
                    irradiations[i].sec = None
                    irradiations[i].estimated_fluence = None
                    irradiations[i].fluence_factor = None
                    irradiations[i].date_first_sec = None
                    irradiations[i].date_last_sec = None
                    irradiations[i].status = IRRADIATION_STATUS[states[i]][0]
                    if states[i] > 0:
                        irradiations[i].sec = e['sec']
                        irradiations[i].estimated_fluence = e['estimated_fluence']
                        irradiations[i].fluence_factor = e['factor']
                        irradiations[i].date_first_sec = e['date_first_sec']
                    if states[i] > 1:
                        irradiations[i].date_last_sec = e['date_last_sec']
                    irradiations[i].save()


def update_sec(request):
    """
    Retrieves not completed irradiations and updates 
    accumulated sec values for each irradiation in beam.
    """
    has_permission_or_403(request, 'admin')
    checked_elements = get_checked_elements(request)
    irradiations = []
    for pk in checked_elements:
        irradiation = Irradiation.objects.get(pk=pk)
        if 'InBeam' in irradiation.status:
            irradiations.append(irradiation)
    data = calc_beam_related_data(irradiations, False, True)
    # Apply scientific notation
    for e in data['irradiation_data']:
        e['factor'] = e['factor'].id
        e['estimated_fluence'] = num_notation(e['estimated_fluence'], '4e')
        e['factor_value'] = num_notation(e['factor_value'], '4e')
    data['form_is_valid'] = True
    args = {'list_name': 'irradiations_list'}
    return JsonResponse(data)


def select_table(request):
    """Retrieves irradiations related to a table."""
    has_permission_or_403(request, 'admin')
    logged_user = get_logged_user(request)
    tables = [
        'IRRAD1', 'IRRAD3', 'IRRAD5', 'IRRAD7', 'IRRAD9', 'IRRAD11', 'IRRAD13',
        'IRRAD15', 'IRRAD17', 'IRRAD19'
    ]
    query_string = ''
    irradiations = []
    if ('irrad_table' in request.GET) and request.GET['irrad_table'].strip():
        query_string = request.GET['irrad_table']
        entry_query = get_query(query_string, ['irrad_table'])
        irradiations = Irradiation.objects.filter(entry_query)
    pagination_data = get_pagination_data(request, irradiations)
    return render(request, 'samples_manager/irradiations_list.html', {
        'irradiations': irradiations,
        'logged_user': logged_user,
        'tables': tables,
        'pagination_data': pagination_data
    })
