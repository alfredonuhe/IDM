"""Django app views related to Compound data model. It also includes
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
    'create': 'Compound was successfully created!',
    'update': 'Compound was successfully updated!',
    'clone': 'Compound was successfully cloned!',
    'delete': 'Compound was successfully deleted!',
    'invalid': 'Form is invalid. Please review the data.',
    'not_sum_100': 'Element\'s percentage don\'t sum to 100%.',
    'empty_formset': 'Please add at least one element to compound.',
    'have_associated_samples': 'Invalid operation. At least one compound has an associated sample.'
}


def save_compound_form(request, form_data):
    """Saves compound and the elements related to it."""
    data = dict()
    if request.method == 'POST':
        data['form_is_valid'] = True
        data['alert_message'] = ALERT_MESSAGES['success']
        if form_data['form'].is_valid() and form_data['elem_formset'].is_valid():
            if form_data['elem_formset'].cleaned_data is not None:
                total = 0
                for elem in form_data['elem_formset'].forms:
                    total = total + float(elem.cleaned_data['percentage'])
                if total == 100:
                    compound = form_data['form'].save()
                    for elem in form_data['elem_formset'].forms:
                        element = elem.save()
                        element.compound = compound
                        element.save()

                    data['compound_id'] = compound.id
                    data['compound_name'] = compound.name
                    data['alert_message'] = data['alert_message'] = ALERT_MESSAGES[form_data['form_action'].lower()]
                else:
                    logging.error('data not ok!')
                    data['form_is_valid'] = False
                    data['alert_message'] = ALERT_MESSAGES['not_sum_100']
                args = {'list_name': 'compounds_list'}
                data['html_list'] = render_partial_list_to_string(
                    request, args)
            else:
                logging.error('No data in compound form')
                data['form_is_valid'] = False
                data['alert_message'] = ALERT_MESSAGES['empty_formset']
        else:
            if form_data['form'].is_valid() and \
                form_data['form_action'].lower() == 'update':
                form_data['form'].save()
                args = {'list_name': 'compounds_list'}
                data['html_list'] = render_partial_list_to_string(
                    request, args)
            else:
                data['form_is_valid'] = False
                data['alert_message'] = ALERT_MESSAGES['invalid']
                logging.error('form not valid!')

    context = {
        'form': form_data['form'], 
        'elem_formset': form_data['elem_formset'],
        'current_page': form_data['current_page'],
        'render_with_errors': form_data['render_with_errors'],
        'form_action': form_data['form_action'],
        'form_tag_action': form_data['form_tag_action']
        }
    data['html_form'] = render_to_string(form_data['template_name'],
                                         context,
                                         request=request)
    return data


def compound_create(request):
    """Creates compound."""
    current_page = 1
    render_with_errors = True
    if 'current_page' in request.POST.keys():
        current_page = int(request.POST['current_page'])
    if 'render_with_errors' in request.POST.keys():
        render_with_errors = bool(request.POST['render_with_errors'] == 'on')
    ElemFormSet = inlineformset_factory(
        Compound,
        CompoundElement,
        form=CompoundElementForm,
        extra=0,
        min_num=1,
        validate_min=True,
        error_messages="Compound is not filled",
        formset=CompoundElementFormSet)
    if request.method == 'POST':
        form = CompoundForm(request.POST)
        elem_formset = ElemFormSet(request.POST, prefix='ce-fs')
    else:
        form = CompoundForm()
        elem_formset = ElemFormSet(prefix='ce-fs')
    status = 'new'

    form_data = {
        'form': form,
        'elem_formset': elem_formset,
        'current_page': current_page,
        'render_with_errors': render_with_errors,
        'form_action': 'Create',
        'form_tag_action': reverse('samples_manager:compound_create'),
        'template_name': 'samples_manager/partial_compound_create_update.html'
    }
    data = save_compound_form(request, form_data)
    return JsonResponse(data)


def compound_update(request):
    """Updates compound."""
    has_permission_or_403(request, 'admin')
    data = dict()
    checked_elements = get_checked_elements(request)
    validation_data = checked_elements_are_valid(checked_elements, 'single', Compound)
    if validation_data['valid']:
        pk = checked_elements[0]
        compound = get_object_or_404(Compound, pk=pk)
        current_page = 1
        render_with_errors = True
        if 'current_page' in request.POST.keys():
            current_page = int(request.POST['current_page'])
        if 'render_with_errors' in request.POST.keys():
            render_with_errors = bool(request.POST['render_with_errors'] == 'on')
        ElemFormSet = inlineformset_factory(
            Compound,
            CompoundElement,
            form=CompoundElementForm,
            extra=0,
            error_messages="Compound is not filled",
            formset=CompoundElementFormSet)
        if request.method == 'POST':
            form = CompoundForm(request.POST, instance=compound)
            elem_formset = ElemFormSet(request.POST,
                                    instance=compound,
                                    prefix='ce-fs')
        else:
            form = CompoundForm(instance=compound)
            elem_formset = ElemFormSet(instance=compound, prefix='ce-fs')
    else:
        data['form_is_valid'] = False
        data['alert_message'] = validation_data['msg']
    form_data = {
        'form': form,
        'elem_formset': elem_formset,
        'current_page': current_page,
        'render_with_errors': render_with_errors,
        'form_action': 'Update',
        'form_tag_action': reverse('samples_manager:compound_update'),
        'template_name': 'samples_manager/partial_compound_create_update.html'
    }
    data = save_compound_form(request, form_data)
    return JsonResponse(data)


def compound_delete(request):
    """Deletes compound."""
    has_permission_or_403(request, 'admin')
    data = dict()
    checked_elements = get_checked_elements(request)
    validation_data = checked_elements_are_valid(checked_elements, 'group', Compound)
    if validation_data['valid']:
        have_associated_samples = \
            compounds_have_associated_samples(checked_elements)
        if not have_associated_samples:
            if request.method == 'POST':
                for pk in checked_elements:
                    compound = get_object_or_404(Compound, pk=pk)
                    compound.delete()
                data['alert_message'] = ALERT_MESSAGES['delete']
                args = {'list_name': 'compounds_list'}
                data['html_list'] = render_partial_list_to_string(
                    request, args)
            else:
                context = dict()
                context['additional_text'] = get_collapsible_text_checked_elements(
                checked_elements, Compound)
                data['html_form'] = render_to_string(
                    'samples_manager/partial_compound_delete.html',
                    context,
                    request=request,
                )
        else:
            data['form_is_valid'] = False
            data['alert_message'] = ALERT_MESSAGES['have_associated_samples']
    else:
        data['form_is_valid'] = False
        data['alert_message'] = validation_data['msg']
    return JsonResponse(data)


def compounds_have_associated_samples(compound_pks):
    """Calculates if list of compounds have an associated sample."""
    for pk in compound_pks:
        compound = Compound.objects.get(pk=pk)
        layers = Layer.objects.filter(compound_type=compound)
        has_asssocaited_sample = len(layers) > 0
        if has_asssocaited_sample:
            return True
    return False


def compounds_list(request):
    """Lists all compounds."""
    has_permission_or_403(request, 'admin')
    logged_user = get_logged_user(request)
    compounds = Compound.objects.all()
    search_url = reverse('samples_manager:compounds_search')
    pagination_data = get_pagination_data(request, compounds)
    compounds_data = get_compounds_data(
        pagination_data['page_obj'].object_list)
    return render(
        request, 'samples_manager/compounds_list.html', {
            'search_url': search_url,
            'compounds_data': compounds_data,
            'logged_user': logged_user,
            'pagination_data': pagination_data
        })
