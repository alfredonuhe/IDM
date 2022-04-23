"""Django app views related to User data model. It also includes
 auxiliary functions."""
from .views import *
from .forms import *
from .models import *
from django.urls import reverse
from django.http import HttpResponse
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404, render


ALERT_MESSAGES = {
    'success': 'Operation executed successfully.',
    'create': 'User was successfully created! The user should still subscribe in irrad-ps-users e-group if he/she is not a member!',
    'add': 'User was successfully added to experiment!',
    'update': 'User was successfully updated!',
    'clone': 'User was successfully cloned!',
    'delete': 'User was successfully deleted! He/she will not have access to the related experiments and samples anymore!',
    'remove': 'User was successfully removed to experiment!',
    'invalid': 'Form is invalid. Please review the data.',
    'remove_experiment_responsible': 'Experiment reponsible can\'t be removed.'
}


def save_user_form(request, form_data):
    """Creates user in admin view."""
    data = dict()
    if request.method == 'POST':
        data['form_is_valid'] = True
        data['alert_message'] = ALERT_MESSAGES['success']
        if form_data['form'].is_valid():
            form_data['form'].save()
            data['form_is_valid'] = True
            args = {'list_name': 'users_list'}
            data['html_list'] = render_partial_list_to_string(
                request, args)
        else:
            data['form_is_valid'] = False
            data['alert_message'] = ALERT_MESSAGES['invalid']
    context = {
        'form': form_data['form'],
        'form_action': form_data['form_action'],
        'form_tag_action':form_data['form_tag_action']
        }
    data['html_form'] = render_to_string(form_data['template_name'],
                                         context,
                                         request=request)
    return data


def save_add_experiment_user_form(request, form_data):
    """Adds user to experiment."""
    data = dict()
    if request.method == 'POST':
        data['form_is_valid'] = True
        data['alert_message'] = ALERT_MESSAGES['success']
        if form_data['form'].is_valid():
            user = User.objects.get(email=form_data['form'].cleaned_data['email'])
            form_data['form'].experiment.users.add(user)
            form_data['form'].experiment.save()
            args = {
                'list_name': 'experiment_users_list', 
                'ids': [form_data['form'].experiment.id]
            }
            data['html_list'] = render_partial_list_to_string(
                request, args)
            data['alert_message'] = ALERT_MESSAGES['add']
        else:
            data['form_is_valid'] = False
            data['alert_message'] = ALERT_MESSAGES['invalid']
    context = {
        'form': form_data['form'],
        'render_with_errors': True, 
        'experiment': form_data['form'].experiment
    }
    data['html_form'] = render_to_string(form_data['template_name'], context,
        request=request)
    return data


def view_user(request):
    """Renders page user details."""
    #only in production
    logged_user = get_logged_user(request)
    #logged_user = 'placeholder@cern.ch'
    html = '<html><body><div id="user_id">User e-mail %s.</div></body></html>' % logged_user.email
    return HttpResponse(html)


def users_list(request):
    """Renders page with all available users and number of related experiments."""
    has_permission_or_403(request, 'admin')
    logged_user = get_logged_user(request)
    users = User.objects.all()
    search_url = reverse('samples_manager:users_search')
    pagination_data = get_pagination_data(request, users)
    users_data = get_users_data(pagination_data['page_obj'].object_list)
    return render(request, 'samples_manager/users_list.html', {
        'search_url': search_url,
        'users_data': users_data,
        'logged_user': logged_user,
        'pagination_data': pagination_data
    })


def user_create(request):
    """Creates admin user."""
    has_permission_or_403(request, 'admin')
    if request.method == 'POST':
        form = UserForm(request.POST)
    else:
        form = UserForm()

    form_data = {
        'form': form,
        'form_action': 'Create',
        'form_tag_action': reverse('samples_manager:user_create'),
        'template_name': 'samples_manager/partial_user_create_update.html'
    }

    data = save_user_form(request, form_data)
    return JsonResponse(data)

def experiment_users_list(request, pk):
    """Retrieves users related to experiment."""
    has_permission_or_403(request, 'experiment', pk)
    experiment = Experiment.objects.get(pk=pk)
    logged_user = get_logged_user(request)
    users_all_pages = list(experiment.users.values())
    users_all_pages.append(experiment.responsible)
    search_url = reverse('samples_manager:experiment_users_search',\
        args=[experiment.id])
    pagination_data = get_pagination_data(request, users_all_pages)
    users = pagination_data['page_obj'].object_list
    base_template = 'samples_manager/base_all_tab_list.html' \
        if logged_user.role == "Admin" else \
        'samples_manager/base_all_tab_list.html'
    return render(request, 'samples_manager/experiment_users_list.html', {
        'users': users,
        'search_url': search_url,
        'experiment': experiment,
        'logged_user': logged_user,
        'base_template': base_template,
        'pagination_data': pagination_data
    })


def add_experiment_user(request, pk):
    """Adds user to experiment."""
    has_permission_or_403(request, 'experiment', pk)
    experiment = Experiment.objects.get(pk=pk)
    if request.method == 'POST':
        form = AddUserToExperimentForm(request.POST, experiment=experiment)
    else:
        form = AddUserToExperimentForm(experiment=experiment)

    form_data = {
        'form': form,
        'template_name': 'samples_manager/partial_experiment_user_add.html'
    }

    data = save_add_experiment_user_form(request, form_data)
    return JsonResponse(data)


def remove_experiment_user(request, pk):
    """Removes user from experiment."""
    has_permission_or_403(request, 'experiment', pk)
    experiment = Experiment.objects.get(pk=pk)
    data = dict()
    checked_elements = get_checked_elements(request)
    validation_data = checked_elements_are_valid(checked_elements, 'group', User)
    data['form_is_valid'] = True
    if validation_data['valid']:
        has_experiment_responsible = \
            includes_experiment_responsible(checked_elements, experiment)
        if has_experiment_responsible:
            if request.method == 'POST':
                data['alert_message'] = ALERT_MESSAGES['remove']
                for pk_user in checked_elements:
                    user = get_object_or_404(User, pk=pk_user)
                    experiment.users.remove(user)
                    experiment.save()
                args = {
                    'list_name': 'experiment_users_list', 
                    'ids': [experiment.id]
                }
                data['html_list'] = render_partial_list_to_string(
                    request, args)
            else:
                context = dict()
                context['experiment'] = experiment
                context['additional_text'] = get_collapsible_text_checked_elements(
                checked_elements, User)
                data['html_form'] = render_to_string(
                    'samples_manager/partial_experiment_user_remove.html',
                    context,
                    request=request,
                )
        else:
            data['form_is_valid'] = False
            data['alert_message'] = \
                ALERT_MESSAGES['remove_experiment_responsible']
    else:
        data['form_is_valid'] = False
        data['alert_message'] = validation_data['msg']
    return JsonResponse(data)


def user_delete(request):
    """Displays form and deletes user on form submission."""
    has_permission_or_403(request, 'admin')
    data = dict()
    checked_elements = get_checked_elements(request)
    validation_data = checked_elements_are_valid(checked_elements, 'group', User)
    data['form_is_valid'] = True
    if validation_data['valid']:
        if request.method == 'POST':
            for pk in checked_elements:
                user = get_object_or_404(User, pk=pk)
                user.delete()
            data['alert_message'] = ALERT_MESSAGES['delete']
            args = {'list_name': 'users_list'}
            data['html_list'] = render_partial_list_to_string(
                request, args)
        else:
            context = dict()
            context['additional_text'] = get_collapsible_text_checked_elements(
                checked_elements, User)
            data['html_form'] = render_to_string(
                'samples_manager/partial_user_delete.html',
                context,
                request=request,
            )
    else:
        data['form_is_valid'] = False
        data['alert_message'] = validation_data['msg']
    return JsonResponse(data)


def user_update(request):
    """Updates user information."""
    has_permission_or_403(request, 'admin')
    data = dict()
    checked_elements = get_checked_elements(request)
    validation_data = checked_elements_are_valid(checked_elements, 'single', User)
    data['form_is_valid'] = True
    if validation_data['valid']:
        pk = checked_elements[0]
        user = get_object_or_404(User, pk=pk)
        if request.method == 'POST':
            form = UserForm(request.POST, instance=user)
        else:
            form = UserForm(instance=user)

        form_data = {
            'form': form,
            'form_action': 'Update',
            'form_tag_action': reverse('samples_manager:user_update'),
            'template_name': 'samples_manager/partial_user_create_update.html'
        }
        data = save_user_form(request, form_data)
    else:
        data['form_is_valid'] = False
        data['alert_message'] = validation_data['msg']
    return JsonResponse(data)


#!!! to be continued
def users_samples(request):
    """Displays samples related to logged user."""
    logged_user = get_logged_user(request)
    samples = authorised_samples(logged_user)
    return render(request, 'samples_manager/experiment_samples_list.html', {
        'samples': samples,
        'logged_user': logged_user
    })


def includes_experiment_responsible(users, experiment):
    """Checks if experiment responsible is in list."""
    result = True
    for pk in users:
        user = get_object_or_404(User, pk=pk)
        if user == experiment.responsible:
            result = False
            break
    return result
