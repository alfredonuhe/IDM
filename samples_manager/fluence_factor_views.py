"""Django app views related to FluenceFactor data model. It also includes
 auxiliary functions."""
import logging
from .forms import *
from .views import *
from .models import *
from django.urls import reverse
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404, render


ALERT_MESSAGES = {
    'success': 'Operation executed successfully.',
    'create': 'Factor was successfully created!',
    'update': 'Factor was successfully updated!',
    'delete': 'Factor was successfully deleted!',
    'invalid': 'Form is invalid. Please review the data.',
}


def save_fluence_factor_form(request, form_data):
    """Display and save Dosimeter form."""
    data = dict()
    logged_user = get_logged_user(request)
    data['form_is_valid'] = True
    if request.method == 'POST':
        data['alert_message'] = ALERT_MESSAGES['success']
        if form_data['form'].is_valid():
            form_data['form'].save()
            data['alert_message'] = ALERT_MESSAGES[form_data['form_action'].lower()]
            args = {'list_name': 'fluence_factors_list'}
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


def fluence_factors_list(request):
    """Retrieves all completed irradiations."""
    has_permission_or_403(request, 'admin')
    logged_user = get_logged_user(request)

    factors = FluenceFactor.objects.all()
    pagination_data = get_pagination_data(request, factors)
    return render(request, 'samples_manager/fluence_factor_list.html', {
        'factors': pagination_data['page_obj'].object_list,
        'logged_user': logged_user,
        'pagination_data': pagination_data
    })


def fluence_factor_create(request):
    """Creates irradiation."""
    has_permission_or_403(request, 'admin')
    current_page = 1
    render_with_errors = True
    if 'current_page' in request.POST.keys():
        current_page = int(request.POST['current_page'])
    if 'render_with_errors' in request.POST.keys():
        render_with_errors = bool(request.POST['render_with_errors'] == 'on')
    if request.method == 'POST':
        form = FluenceFactorForm(request.POST)
    else:
        form = FluenceFactorForm()
    form_data = {
        'form': form,
        'current_page': current_page,
        'render_with_errors': render_with_errors,
        'form_action': 'Create',
        'form_tag_action': reverse('samples_manager:fluence_factor_create'),
        'template_name': 'samples_manager/partial_fluence_factor_create_update.html'
    }
    data = save_fluence_factor_form(request, form_data)
    return JsonResponse(data)


def fluence_factor_update(request):
    """Updates irradiation."""
    has_permission_or_403(request, 'admin')
    checked_elements = get_checked_elements(request)
    validation_data = checked_elements_are_valid(checked_elements, 'single', FluenceFactor)
    data = dict()
    if validation_data['valid']:
        pk = checked_elements[0]
        factor = get_object_or_404(FluenceFactor, pk=pk)
        current_page = 1
        render_with_errors = True
        if 'current_page' in request.POST.keys():
            current_page = int(request.POST['current_page'])
        if 'render_with_errors' in request.POST.keys():
            render_with_errors = bool(request.POST['render_with_errors'] == 'on')
        if request.method == 'POST':
            form = FluenceFactorForm(request.POST, instance=factor)
        else:
            form = FluenceFactorForm(instance=factor)
        form_data = {
            'form': form,
            'current_page': current_page,
            'render_with_errors': render_with_errors,
            'form_action': 'Update',
            'form_tag_action': reverse('samples_manager:fluence_factor_update'),
            'template_name': 'samples_manager/partial_fluence_factor_create_update.html'
        }
        data = save_fluence_factor_form(request, form_data)
    else:
        data['form_is_valid'] = False
        data['alert_message'] = validation_data['msg']
    return JsonResponse(data)


def fluence_factor_delete(request):
    """Deletes irradiation."""
    has_permission_or_403(request, 'admin')
    data = dict()
    checked_elements = get_checked_elements(request)
    validation_data = checked_elements_are_valid(checked_elements, 'group', FluenceFactor)
    if validation_data['valid']:
        if request.method == 'POST':
            for pk in checked_elements:
                factor = get_object_or_404(FluenceFactor, pk=pk)
                factor.delete()
            data['alert_message'] = ALERT_MESSAGES['delete']
            args = {'list_name': 'fluence_factors_list'}
            data['html_list'] = render_partial_list_to_string(
                request, args)
        else:
            context = dict()
            context['additional_text'] = get_collapsible_text_checked_elements(
                checked_elements, Irradiation)
            data['html_form'] = render_to_string(
                'samples_manager/partial_fluence_factor_delete.html',
                context,
                request=request,
            )
    else:
        data['form_is_valid'] = False
        data['alert_message'] = validation_data['msg']
    return JsonResponse(data)
