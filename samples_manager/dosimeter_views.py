"""Django app views related to Dosimeter data model. It also includes
 auxiliary functions."""
from .forms import *
from .views import *
from .models import *
from django.urls import reverse
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404, render


DOS_ID_NUM_DIGITS = 6
FIRST_DOS_ID_NUMBER = 4000
LAST_DOS_ID_NUMBER = int('9'*DOS_ID_NUM_DIGITS)
ALERT_MESSAGES = {
    'success': 'Operation executed successfully.',
    'create': 'Dosimeter was successfully created!',
    'create_multiple': 'Dosimeters were successfully created!',
    'update': 'Dosimeter was successfully updated!',
    'clone': 'Dosimeter was successfully cloned!',
    'delete': 'Dosimeter was successfully deleted!',
    'invalid': 'Form is invalid. Please review the data.',
    'incorrect_id': 'Dosimeter id is incorrect. If has parent, '\
        'id should be <parent ID>.<number of child>.',
    'box_does_not_exist': 'A box with this id doesn\'t exist.',
    'box_no_selected_dosimeters': 'No dosimeters selected for box assignment.',
    'dosimeters_have_invalid_dos_id': 'At least a dosimeter has an invalid dos id. Please correct.',
    'dosimeters_have_invalid_set_id': 'At least a dosimeter has an invalid set id. Please correct.',
    'default': 'Sorry something went wrong.'
}


def save_dosimeter_form(request, form_data):
    """Display and save Dosimeter form."""
    data = dict()
    logged_user = get_logged_user(request)
    if request.method == 'POST':
        data['form_is_valid'] = True
        data['alert_message'] = ALERT_MESSAGES['success']
        if form_data['form1'].is_valid() and form_data['form2'].is_valid():
            dos_id = form_data['form1'].cleaned_data['dos_id']
            dos_id_is_valid = (get_equipment_type(dos_id) == 'dosimeter')
            has_parent = (form_data['form2']\
                .cleaned_data['parent_dosimeter'] is not None)
            if has_parent:
                parent = form_data['form2'].cleaned_data['parent_dosimeter']
                regex = r'^' + parent.dos_id.replace('.', '\.') + '\.\d{1,3}$'
                dos_id_is_valid = search_re_in_string(regex, dos_id)
            else:
                dos_id_is_valid = (get_equipment_type(dos_id, 2) == 'dosimeter')
            if dos_id_is_valid:
                if form_data['form_action'].lower() == 'create' or form_data['form_action'].lower() == 'clone':
                    dosimeter_data = {}
                    dosimeter_data.update(form_data['form1'].cleaned_data)
                    dosimeter_data.update(form_data['form2'].cleaned_data)
                    dosimeter_temp = Dosimeter.objects.create(**dosimeter_data)
                    dosimeter = Dosimeter.objects.get(pk=dosimeter_temp.pk)
                    dosimeter.status = 'Registered'
                    dosimeter.created_by = logged_user
                    dosimeter.save()
                    data['alert_message'] = data['alert_message'] = ALERT_MESSAGES[form_data['form_action'].lower()]
                elif form_data['form_action'].lower() == 'update':
                    dosimeter_updated = form_data['form1'].save()
                    form_data['form2'].save()
                    dosimeter_updated.status = 'Updated'
                    dosimeter_updated.updated_by = logged_user
                    dosimeter_updated.save()
                    data['alert_message'] = data['alert_message'] = ALERT_MESSAGES[form_data['form_action'].lower()]
                else:
                    pass
                args = {'list_name': 'dosimeters_list'}
                data['html_list'] = render_partial_list_to_string(
                    request, args)
            else:
                data['form_is_valid'] = False
                data['alert_message'] = ALERT_MESSAGES['incorrect_id']
        else:
            data['form_is_valid'] = False
            data['alert_message'] = ALERT_MESSAGES['invalid']
    
    context = {
        'form1': form_data['form1'], 
        'form2': form_data['form2'],
        'current_page': form_data['current_page'],
        'render_with_errors': form_data['render_with_errors'],
        'form_action': form_data['form_action'],
        'form_tag_action': form_data['form_tag_action']
        }
    data['html_form'] = render_to_string(form_data['template_name'],
                                         context,
                                         request=request)
    return data


def dosimeters_list(request):
    """Display all dosimeters."""
    has_permission_or_403(request, 'admin')
    logged_user = get_logged_user(request)
    dosimeters = Dosimeter.objects.order_by('-updated_at')
    search_url = reverse('samples_manager:dosimeters_search')
    pagination_data = get_pagination_data(request, dosimeters)
    return render(
        request, 'samples_manager/dosimeters_list.html', {
            'dosimeters': pagination_data['page_obj'].object_list,
            'search_url': search_url,
            'logged_user': logged_user,
            'pagination_data': pagination_data
        })


def dosimeter_create(request):
    """
    Displays dosimeter creation form and also handles submission. GET request displays form, 
    POST request handles submission.
    """
    has_permission_or_403(request, 'admin')
    logged_user = get_logged_user(request)
    current_page = 1
    render_with_errors = True
    if 'current_page' in request.POST.keys():
        current_page = int(request.POST['current_page'])
    if 'render_with_errors' in request.POST.keys():
        render_with_errors = bool(request.POST['render_with_errors'] == 'on')
    if request.method == 'POST':
        form1 = DosimeterForm1(request.POST)
        form2 = DosimeterForm2(request.POST)
    else:
        data = {'dos_id': generate_dos_id(), 'responsible': logged_user}
        form1 = DosimeterForm1(initial=data)
        form2 = DosimeterForm2(initial=data)

    form_data = {
        'form1': form1,
        'form2': form2,
        'current_page': current_page,
        'render_with_errors': render_with_errors,
        'form_action': 'Create',
        'form_tag_action': reverse('samples_manager:dosimeter_create'),
        'template_name': 'samples_manager/partial_dosimeter_create_update_clone.html'
    }
    data = save_dosimeter_form(request, form_data)
    return JsonResponse(data)


def dosimeter_update(request):
    """Updates dosimeter."""
    data = dict()
    has_permission_or_403(request, 'admin')
    checked_elements = get_checked_elements(request)
    validation_data = checked_elements_are_valid(checked_elements, 'single', Dosimeter)
    if validation_data['valid']:
        current_page = 1
        render_with_errors = True
        if 'current_page' in request.POST.keys():
            current_page = int(request.POST['current_page'])
        if 'render_with_errors' in request.POST.keys():
            render_with_errors = bool(request.POST['render_with_errors'] == 'on')
        pk = checked_elements[0]
        dosimeter = get_object_or_404(Dosimeter, pk=pk)
        if request.method == 'POST':
            form1 = DosimeterForm1(request.POST, instance=dosimeter)
            form2 = DosimeterForm2(request.POST, instance=dosimeter)
        else:
            form1 = DosimeterForm1(instance=dosimeter)
            form2 = DosimeterForm2(instance=dosimeter)

        form_data = {
            'form1': form1,
            'form2': form2,
            'current_page': current_page,
            'render_with_errors': render_with_errors,
            'form_action': 'Update',
            'form_tag_action': reverse('samples_manager:dosimeter_update'),
            'template_name': 'samples_manager/partial_dosimeter_create_update_clone.html'
        }
        data = save_dosimeter_form(request, form_data)
    else:
        data['form_is_valid'] = False
        data['alert_message'] = validation_data['msg']
    return JsonResponse(data)


def dosimeter_clone(request):
    """Clones dosimeter."""
    data = dict()
    has_permission_or_403(request, 'admin')
    checked_elements = get_checked_elements(request)
    validation_data = checked_elements_are_valid(checked_elements, 'single', Dosimeter)
    if validation_data['valid']:
        current_page = 1
        render_with_errors = True
        if 'current_page' in request.POST.keys():
            current_page = int(request.POST['current_page'])
        if 'render_with_errors' in request.POST.keys():
            render_with_errors = bool(request.POST['render_with_errors'] == 'on')
        pk = checked_elements[0]
        dosimeter = get_object_or_404(Dosimeter, pk=pk)
        if request.method == 'POST':
            form1 = DosimeterForm1(request.POST)
            form2 = DosimeterForm2(request.POST)
        else:
            data = {'dos_id': generate_dos_id()}
            form1 = DosimeterForm1(instance=dosimeter, initial=data)
            form2 = DosimeterForm2(instance=dosimeter)
        
        form_data = {
            'form1': form1,
            'form2': form2,
            'current_page': current_page,
            'render_with_errors': render_with_errors,
            'form_action': 'Clone',
            'form_tag_action': reverse('samples_manager:dosimeter_clone'),
            'template_name': 'samples_manager/partial_dosimeter_create_update_clone.html'
        }
        data = save_dosimeter_form(request, form_data)
    else:
        data['form_is_valid'] = False
        data['alert_message'] = validation_data['msg']
    return JsonResponse(data)


def dosimeter_delete(request):
    """
    Shows delete confirmation and deletes dosimeter if request is a 
    POST request.
    """
    has_permission_or_403(request, 'admin')
    data = dict()
    checked_elements = get_checked_elements(request)
    validation_data = checked_elements_are_valid(checked_elements, 'group', Dosimeter)
    if validation_data['valid']:   
        if request.method == 'POST':
            for pk in checked_elements:
                dosimeter = get_object_or_404(Dosimeter, pk=pk)
                dosimeter.delete()
            data['alert_message'] = ALERT_MESSAGES['delete']
            args = {'list_name': 'dosimeters_list'}
            data['html_list'] = render_partial_list_to_string(
                request, args)
        else:
            context = dict()
            context['additional_text'] = get_collapsible_text_checked_elements(
                checked_elements, Dosimeter)
            data['html_form'] = render_to_string(
                'samples_manager/partial_dosimeter_delete.html',
                context,
                request=request,
            )
    else:
        data['form_is_valid'] = False
        data['alert_message'] = validation_data['msg']
    return JsonResponse(data)


def dosimeter_details(request, pk):
    """Shows detail page for dosimeter"""
    has_permission_or_403(request, 'admin')
    logged_user = get_logged_user(request)
    dosimeter = get_object_or_404(Dosimeter, pk=pk)
    data = dict()

    return render(request, 'samples_manager/dosimeter_details.html', {
        'logged_user': logged_user,
        'dosimeter': dosimeter
    })


def generate_dos_id():
    """Generates ID for dosimeter."""
    all_dosimeters = Dosimeter.objects.all()
    dosimeter_numbers = []
    for dosimeter in all_dosimeters:
        if get_equipment_type(dosimeter.dos_id) == 'dosimeter':
            dos_id = dosimeter.dos_id.split('.')[0]
            dosimeter_numbers.append(int(dos_id[4:]))
    dosimeter_numbers.sort(reverse=False)
    id_num = FIRST_DOS_ID_NUMBER
    while (id_num <= LAST_DOS_ID_NUMBER):
        if id_num not in dosimeter_numbers:
            break
        id_num += 1
    result = 'DOS-' + ('0'*(DOS_ID_NUM_DIGITS - \
        (math.floor(math.log10(id_num)) + 1))) + str(id_num)
    return result


def create_dos_ids(request):
    """Generates IDs for several dosimeters."""
    has_permission_or_403(request, 'admin')
    data = dict()
    if request.method == 'POST':
        data['form_is_valid'] = True
        data['alert_message'] = ALERT_MESSAGES['create_multiple']
        number_ids = int(request.POST['num_ids'])
        form = DosimeterGenerateIds(request.POST)
        if form.is_valid():
            for i in range(0, number_ids):
                status = 'Registered'
                dos_type = 'Aluminium'
                dosimeter = Dosimeter(status=status, dos_type=dos_type)
                dosimeter.save()
                if get_equipment_type(dosimeter.dos_id) != 'dosimeter':
                    dosimeter.dos_id = generate_dos_id()
                dosimeter.save()
            args = {'list_name': 'dosimeters_list'}
            data['html_list'] = render_partial_list_to_string(
                request, args)
        else:
            data['form_is_valid'] = False
            data['alert_message'] = ALERT_MESSAGES['invalid']
    else:
        form = DosimeterGenerateIds()
    context = dict()
    context['form'] = form
    context['render_with_errors'] = True
    data['html_form'] = render_to_string(
        'samples_manager/partial_dosimeter_generate_dos_ids.html',
        context,
        request=request,
    )
    return JsonResponse(data)


def dosimeter_write_infoream(request):
    """Writes dosimeter to inforEAM."""
    has_permission_or_403(request, 'admin')
    data = dict()
    data['form_is_valid'] = True
    checked_elements = get_checked_elements(request)
    validation_data = checked_elements_are_valid(checked_elements, 'group', Dosimeter, 5)
    if validation_data['valid']:
        dosimeters_ids_are_valid = \
            equipment_ids_are_correct_type(checked_elements, 'dosimeter')
        if dosimeters_ids_are_valid:
            if request.method == 'POST':
                equipment_ids = get_ids_from_checked_equipments(checked_elements, 
                    'dosimeter')
                data = write_equipment_in_infoream(equipment_ids)
            else:
                context = dict()
                context['additional_text'] = get_collapsible_text_checked_elements(
                    checked_elements, Dosimeter)
                data['html_form'] = render_to_string(
                    'samples_manager/partial_write_dosimeter_infoream.html',
                    context,
                    request=request,
                )
        else:
            data['form_is_valid'] = False
            data['alert_message'] = ALERT_MESSAGES['dosimeters_have_invalid_set_id']
    else:
        data['form_is_valid'] = False
        data['alert_message'] = validation_data['msg']
    return JsonResponse(data)


def dosimeter_read_infoream(request):
    """Reads sample's inforEAM information."""
    has_permission_or_403(request, 'admin')
    data = dict()
    data['form_is_valid'] = True
    checked_elements = get_checked_elements(request)
    validation_data = checked_elements_are_valid(checked_elements, 'single', Dosimeter)
    if validation_data['valid']:
        pk = checked_elements[0]
        dos_id = Dosimeter.objects.get(pk=pk).dos_id
        data['redirect_url'] = reverse('samples_manager:read_equipment_infoream',
            args=[dos_id])
    else:
        data['form_is_valid'] = False
        data['alert_message'] = validation_data['msg']
    return JsonResponse(data)


def redirect_dosimeter_details(request):
    """Redirects user to dosimeter's details page."""
    data = dict()
    data['form_is_valid'] = True
    logged_user = get_logged_user(request)
    checked_elements = get_checked_elements(request)
    validation_data = checked_elements_are_valid(checked_elements, 'single', Dosimeter)
    if validation_data['valid']:
        pk = checked_elements[0]
        dosimeter = get_object_or_404(Dosimeter, pk=pk)
        has_permission_or_403(request, 'dosimeter', dosimeter.id)
        data['redirect_url'] = reverse('samples_manager:dosimeter_details',
            args=[dosimeter.id])     
    else:
        data['form_is_valid'] = False
        data['alert_message'] = validation_data['msg']
    return JsonResponse(data)


def dosimeter_attach_box(request):
    """Assigns Box to dosimeter."""
    has_permission_or_403(request, 'admin')
    data = dict()
    data['form_is_valid'] = True
    checked_elements = get_checked_elements(request)
    validation_data = checked_elements_are_valid(checked_elements, 'group', Dosimeter)
    if validation_data['valid']:
        if request.method == 'POST':
            form = SampleDosimeterBoxAssociationForm(request.POST)
            dosimeters_ids = get_ids_from_checked_equipments(checked_elements, 
                'dosimeter')
            if form.is_valid():
                try:
                    box = None
                    if request.POST['box_id'] != 'None':
                        box = Box.objects.get(box_id=request.POST['box_id'])
                    dosimeters_ids_are_valid = True
                    for dos_id in dosimeters_ids:
                        dosimeter = Dosimeter.objects.get(dos_id=dos_id)
                        if get_equipment_type(dosimeter.dos_id) != 'dosimeter':
                            dosimeters_ids_are_valid = False
                            break
                    if dosimeters_ids_are_valid:
                        for dos_id in dosimeters_ids:
                            try:
                                dosimeter = Dosimeter.objects.get(dos_id=dos_id)
                                dosimeter.box = box
                                dosimeter.save()
                                data['alert_message'] = ALERT_MESSAGES['success']
                            except Box.DoesNotExist:
                                data['form_is_valid'] = False
                                data['alert_message'] = ALERT_MESSAGES['default']
                    else:
                        data['form_is_valid'] = False
                        data['alert_message'] = ALERT_MESSAGES['dosimeters_have_invalid_dos_id']
                except Box.DoesNotExist:
                    data['form_is_valid'] = False
                    data['alert_message'] = ALERT_MESSAGES['invalid']
            else:
                data['form_is_valid'] = False
                data['alert_message'] = ALERT_MESSAGES['invalid']
        else:
            is_single = checked_elements_are_valid(checked_elements, \
                'group', Dosimeter)
            if is_single:
                pk = checked_elements[0]
                dosimeter = Dosimeter.objects.get(pk=pk)
                box_exists = (dosimeter.box != None)
                if box_exists:
                    data = {'box_id': dosimeter.box.box_id}
                    form = SampleDosimeterBoxAssociationForm(initial=data)
                else:
                    form = SampleDosimeterBoxAssociationForm()
            else:
                form = SampleDosimeterBoxAssociationForm()
        
        dosimeter_ids = get_ids_from_checked_equipments(checked_elements, 
                'dosimeter')
        additional_text = get_collapsible_text_box_assignment(checked_elements, 'dosimeter')
        display_additional_text = (len(additional_text['collapsed']) > 0)
        context = {
            'form': form,
            'form_tag_action': reverse('samples_manager:dosimeter_attach_box'),
            'additional_text': additional_text,
            'display_additional_text': display_additional_text
        }
        args = {'list_name': 'dosimeters_list'}
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
