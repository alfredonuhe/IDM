"""Django app views related to Box data model. It also includes
 auxiliary functions."""
import logging
from .forms import *
from .views import *
from .models import *
from django.urls import reverse
from django.http import JsonResponse
from django.forms import formset_factory
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404, render


FIRST_BOX_ID_NUMBER = 1
LAST_BOX_ID_NUMBER = 400
BOX_ID_NUM_DIGITS = 6
ALERT_MESSAGES = {
    'success': 'Operation executed successfully.',
    'create': 'Box was successfully created!',
    'update': 'Box was successfully updated!',
    'clone': 'Box was successfully cloned!',
    'delete': 'Box was successfully deleted!',
    'item_remove': 'Box item was successfully removed!',
    'items_add': 'Box items were successfully added!',
    'invalid': 'Form is invalid. Please review the data.',
    'box_not_exist': "Box doesn't exist!",
    'unknown_operation': 'Unknown operation. Options: create, update, clone and delete.',
    'no_boxes_selected': 'No boxes appear as selected. Operation can\'t be performed.',
    'boxes_have_invalid_set_id': 'At least a box has an invalid set id. Please correct.',
    'invalid_item_id': 'Item ID is invalid.',
}


def save_box_form(request, form_data):
    """Display and save Box form."""
    data = dict()
    logged_user = get_logged_user(request)
    if request.method == 'POST':
        data['form_is_valid'] = True
        data['alert_message'] = ALERT_MESSAGES['success']
        if form_data['render_with_errors']:
            if form_data['form'].is_valid():
                if form_data['form_action'].lower() == 'create' or \
                    form_data['form_action'].lower() == 'clone':
                    box = form_data['form'].save()
                    box.last_location = box.current_location
                    box.created_by = logged_user
                    box.updated_by = logged_user
                    box.save()
                    data['alert_message'] = ALERT_MESSAGES[form_data['form_action'].lower()]
                elif form_data['form_action'].lower() == 'update':
                    box = form_data['form'].save()
                    box.updated_by = logged_user
                    box.save()
                    data['alert_message'] = ALERT_MESSAGES[form_data['form_action'].lower()]
                else:
                    data['form_is_valid'] = False
                    data['alert_message'] = ALERT_MESSAGES['unknown_operation']
                args = {'list_name': 'boxes_list'}
                data['html_list'] = render_partial_list_to_string(
                    request, args)
            else:
                data['form_is_valid'] = False
                data['alert_message'] = ALERT_MESSAGES['invalid']
                logging.error('Box data invalid')
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


def boxes_list(request):
    """Display boxes list page."""
    has_permission_or_403(request, 'admin')
    logged_user = get_logged_user(request)
    boxes = Box.objects.order_by('-updated_at')
    search_url = reverse('samples_manager:boxes_search')
    pagination_data = get_pagination_data(request, boxes)
    return render(
        request, 'samples_manager/boxes_list.html', {
            'boxes': pagination_data['page_obj'].object_list,
            'search_url': search_url,
            'logged_user': logged_user,
            'pagination_data': pagination_data
        })


def box_create(request):
    """
    Displays box creation form and also handles submission. 
    GET request displays form, POST request handles submission.
    """
    logged_user = get_logged_user(request)
    has_permission_or_403(request, 'admin')
    current_page = 1
    render_with_errors = True
    if 'current_page' in request.POST.keys():
        current_page = int(request.POST['current_page'])
    if 'render_with_errors' in request.POST.keys():
        render_with_errors = bool(request.POST['render_with_errors'] == 'on')
    if request.method == 'POST':
        form = BoxForm(request.POST)
    else:
        data = {'box_id': generate_box_id(), 'responsible': logged_user}
        form = BoxForm(initial=data)
    form_data = {
        'form': form,
        'current_page': current_page,
        'render_with_errors': render_with_errors,
        'form_action': 'Create',
        'form_tag_action': reverse('samples_manager:box_create'),
        'template_name': 'samples_manager/partial_box_create_update_clone.html'
    }
    data = save_box_form(request, form_data)
    return JsonResponse(data)


def box_update(request):
    """Updates box."""
    has_permission_or_403(request, 'admin')
    data = dict()
    checked_elements = get_checked_elements(request)
    validation_data = checked_elements_are_valid(checked_elements, 'single', Box)
    if validation_data['valid']:
        pk = checked_elements[0]
        box = get_object_or_404(Box, pk=pk)
        current_page = 1
        render_with_errors = True
        if 'current_page' in request.POST.keys():
            current_page = int(request.POST['current_page'])
        if 'render_with_errors' in request.POST.keys():
            render_with_errors = bool(request.POST['render_with_errors'] == 'on')
        if request.method == 'POST':
            form = BoxForm(request.POST, instance=box)
        else:
            form = BoxForm(instance=box)
        form_data = {
            'form': form,
            'current_page': current_page,
            'render_with_errors': render_with_errors,
            'form_action': 'Update',
            'form_tag_action': reverse('samples_manager:box_update'),
            'template_name': 'samples_manager/partial_box_create_update_clone.html'
        }
        data = save_box_form(request, form_data)
    else:
        data['form_is_valid'] = False
        data['alert_message'] = validation_data['msg']
    return JsonResponse(data)


def box_clone(request):
    """Clones box."""
    has_permission_or_403(request, 'admin')
    data = dict()
    checked_elements = get_checked_elements(request)
    validation_data = checked_elements_are_valid(checked_elements, 'single', Box)
    if validation_data['valid']:
        pk = checked_elements[0]
        box = get_object_or_404(Box, pk=pk)
        current_page = 1
        render_with_errors = True
        if 'current_page' in request.POST.keys():
            current_page = int(request.POST['current_page'])
        if 'render_with_errors' in request.POST.keys():
            render_with_errors = bool(request.POST['render_with_errors'] == 'on')
        if request.method == 'POST':
            form = BoxForm(request.POST)
        else:
            data = {'box_id': generate_box_id()}
            form = BoxForm(instance=box, initial=data)
        form_data = {
            'form': form,
            'current_page': current_page,
            'render_with_errors': render_with_errors,
            'form_action': 'Clone',
            'form_tag_action': reverse('samples_manager:box_clone'),
            'template_name': 'samples_manager/partial_box_create_update_clone.html'
        }
        data = save_box_form(request, form_data)
    else:
        data['form_is_valid'] = False
        data['alert_message'] = validation_data['msg']
    return JsonResponse(data)


def box_delete(request):
    """
    Shows delete confirmation and deletes box if request is a 
    POST request.
    """
    has_permission_or_403(request, 'admin')
    data = dict()
    checked_elements = get_checked_elements(request)
    validation_data = checked_elements_are_valid(checked_elements, 'group', Box)
    if validation_data['valid']:
        if request.method == 'POST':
            for pk in checked_elements:
                box = Box.objects.get(pk=pk)
                box.delete()
            data['alert_message'] = ALERT_MESSAGES['delete']
            args = {'list_name': 'boxes_list'}
            data['html_list'] = render_partial_list_to_string(
                request, args)
        else:
            context = dict()
            context['additional_text'] = get_collapsible_text_checked_elements(
                checked_elements, Box)
            data['html_form'] = render_to_string(
                'samples_manager/partial_box_delete.html',
                context,
                request=request,
            )
    else:
        data['form_is_valid'] = False
        data['alert_message'] = validation_data['msg']
    return JsonResponse(data)


def box_write_infoream(request):
    """Writes box to inforEAM."""
    has_permission_or_403(request, 'admin')
    data = dict()
    data['form_is_valid'] = True
    checked_elements = get_checked_elements(request)
    validation_data = checked_elements_are_valid(checked_elements, 'group', Box, 1)
    if validation_data['valid']:
        boxes_ids_are_valid = \
            equipment_ids_are_correct_type(checked_elements, 'box')
        if boxes_ids_are_valid:
            if request.method == 'POST':
                equipment_ids = get_ids_from_checked_equipments(checked_elements, 
                    'box')
                data = write_equipment_in_infoream(equipment_ids)
            else:
                context = dict()
                context['additional_text'] = get_collapsible_text_checked_elements(
                    checked_elements, Box)
                data['html_form'] = render_to_string(
                    'samples_manager/partial_write_box_infoream.html',
                    context,
                    request=request,
                )
        else:
            data['form_is_valid'] = False
            data['alert_message'] = ALERT_MESSAGES['boxes_have_invalid_set_id']
    else:
        data['form_is_valid'] = False
        data['alert_message'] = validation_data['msg']
    return JsonResponse(data)


def box_read_infoream(request):
    """Reads box's inforEAM information."""
    has_permission_or_403(request, 'admin')
    data = dict()
    data['form_is_valid'] = True
    checked_elements = get_checked_elements(request)
    validation_data = checked_elements_are_valid(checked_elements, 'single', Box)
    if validation_data['valid']:
        pk = checked_elements[0]
        box_id = Box.objects.get(pk=pk).box_id
        data['redirect_url'] = reverse('samples_manager:read_equipment_infoream',
            args=[box_id])
    else:
        data['form_is_valid'] = False
        data['alert_message'] = validation_data['msg']
    return JsonResponse(data)


def redirect_box_details(request):
    """Redirects user to box's details page."""
    data = dict()
    data['form_is_valid'] = True
    logged_user = get_logged_user(request)
    checked_elements = get_checked_elements(request)
    validation_data = checked_elements_are_valid(checked_elements, 'single', Box)
    if validation_data['valid']:
        pk = checked_elements[0]
        box = get_object_or_404(Box, pk=pk)
        has_permission_or_403(request, 'box', box.id)
        data['redirect_url'] = reverse('samples_manager:box_details',
            args=[box.id])     
    else:
        data['form_is_valid'] = False
        data['alert_message'] = validation_data['msg']
    return JsonResponse(data)


def box_details(request, pk):
    """Shows detail page for box"""
    has_permission_or_403(request, 'box_details', pk)
    logged_user = get_logged_user(request)
    box = get_object_or_404(Box, pk=pk)
    items = get_box_items(box)
    data = dict()

    return render(request, 'samples_manager/box_details.html', {
        'logged_user': logged_user,
        'box': box,
        'items': items
    })


def generate_box_id():
    """Generates a box_id for a box."""
    all_boxes = Box.objects.all()
    box_numbers = []
    for box in all_boxes:
        if get_equipment_type(box.box_id) == 'box':
            box_numbers.append(int(box.box_id[4:]))
    box_numbers.sort(reverse=False)
    id_num = FIRST_BOX_ID_NUMBER
    while (id_num <= LAST_BOX_ID_NUMBER):
        if id_num not in box_numbers:
            break
        id_num += 1
    result = 'BOX-' + ('0'*(BOX_ID_NUM_DIGITS - \
        (math.floor(math.log10(id_num)) + 1))) + str(id_num)
    return result


def redirect_box_items_list(request):
    """Redirects to box items list."""
    has_permission_or_403(request, 'admin')
    data = dict()
    data['form_is_valid'] = True
    checked_elements = get_checked_elements(request)
    validation_data = checked_elements_are_valid(checked_elements, 'single', Sample)
    if validation_data['valid']:
        pk = checked_elements[0]
        data['redirect_url'] = reverse('samples_manager:box_items_list',
            args=[pk])
    else:
        data['form_is_valid'] = False
        data['alert_message'] = validation_data['msg']
    return JsonResponse(data)


def box_items_list(request, pk):
    """Displays box items."""
    has_permission_or_403(request, 'admin')
    logged_user = get_logged_user(request)
    box = get_object_or_404(Box, pk=pk)
    items = get_box_items(box)
    search_url = reverse('samples_manager:box_items_search', args=[box.id])
    pagination_data = get_pagination_data(request, items)
    return render(request, 'samples_manager/box_items_list.html', {
        'box': box,
        'items': pagination_data['page_obj'].object_list,
        'search_url': search_url,
        'logged_user': logged_user,
        'pagination_data': pagination_data
    })


def box_items_add(request, pk):
    """Adds item from box."""
    has_permission_or_403(request, 'admin')
    data = dict()
    data['form_is_valid'] = True
    ItemFormSet = formset_factory(
        form=BoxItemForm,
        extra=0,
        min_num=1,
        validate_min=True,
        can_delete=True,
        formset=BoxItemFormSet)
    try:
        box = Box.objects.get(id=pk)
        if request.method == 'POST':
            formset = ItemFormSet(request.POST, prefix='i-fs')
            if formset.is_valid():
                for form in formset.forms:
                    is_dosimeter = (get_equipment_type(\
                        form.cleaned_data['box_item_id']) == 'dosimeter')
                    is_sample = (get_equipment_type(\
                        form.cleaned_data['box_item_id']) == 'sample')
                    if is_sample:
                        item = Sample.objects.get(set_id=\
                            form.cleaned_data['box_item_id'])
                    elif is_dosimeter:
                        item = Dosimeter.objects.get(dos_id=
                            form.cleaned_data['box_item_id'])
                    item.box = box
                    item.save()
                args = {'list_name': 'box_items_list', 'ids': [box.id]}
                data['html_list'] = render_partial_list_to_string(
                    request, args)
                data['alert_message'] = ALERT_MESSAGES['success']
            else:
                data['form_is_valid'] = False
                data['alert_message'] = ALERT_MESSAGES['invalid']
        else:
            formset = ItemFormSet(prefix='i-fs')
    except Box.DoesNotExist:
        data['form_is_valid'] = False
        data['alert_message'] = ALERT_MESSAGES['box_not_exist']

    context = {
        'box': box,
        'formset': formset
        }
    data['html_form'] = render_to_string(
        'samples_manager/partial_box_items_add.html',
        context,
        request=request,
    )
    return JsonResponse(data)



def box_item_remove(request, pk):
    """Removes item from box."""
    has_permission_or_403(request, 'admin')
    box = get_object_or_404(Box, pk=pk)
    data = dict()
    data['form_is_valid'] = True
    checked_elements = get_checked_elements(request)
    items = get_items_from_item_ids(checked_elements)
    if request.method == 'POST':
        data['alert_message'] = ALERT_MESSAGES['item_remove']
        for item in items:
            if item is not None:
                item.box = None
                item.save()
            else:
                data['form_is_valid'] = False
                data['alert_message'] = ALERT_MESSAGES['invalid_item_id']
                break
        args = {'list_name': 'box_items_list', 'ids': [box.id]}
        data['html_list'] = render_partial_list_to_string(
            request, args)
    context = dict()
    context['additional_text'] = \
        get_collapsible_text_box_items(checked_elements)
    context['box'] = box
    data['html_form'] = render_to_string(
        'samples_manager/partial_box_item_remove.html',
        context,
        request=request,
    )
    return JsonResponse(data)


def get_box_items(box):
    """Collects all items belonging to a box."""
    result = []
    samples = Sample.objects.filter(box=box)
    dosimeters = Dosimeter.objects.filter(box=box)
    for sample in samples:
        if sample.box == box:
            result.append({
                'object': sample,
                'id': sample.set_id,
                'type': 'Sample',
                'url': reverse('samples_manager:sample_details', 
                    args=[sample.experiment.id, sample.id])
            })
    for dosimeter in dosimeters:
        if dosimeter.box == box:
            result.append({
                'object': dosimeter,
                'id': dosimeter.dos_id,
                'type': 'Dosimeter',
                'url': reverse('samples_manager:dosimeter_details', 
                    args=[dosimeter.id])
            })
    return result
