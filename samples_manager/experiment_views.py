"""Django app views related to Experiment data model. It also includes
 auxiliary functions."""
import logging
from .forms import *
from .views import *
from .models import *
from .utilities import *
from django.urls import reverse
from django.http import JsonResponse
from django.forms import inlineformset_factory
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404, render


ALERT_MESSAGES = {
    'success': 'Operation executed successfully.',
    'invalid': 'Form is invalid. Please review the data.',
    'create': 'Your irradiation experiment was successfully saved!\nSoon, '\
        'the facility coordinators will validate your request and you will '\
        'be able to add samples and additional users.',
    'update': 'Your irradiation experiment was successfully updated!',
    'clone': 'Your irradiation experiment was successfully cloned!',
    'delete': 'The experiment was successfully deleted!',
    'validate': 'The experiment was validated. The users will be '\
        'notified now.',
    'missing_fields': 'Please, fill all the required fields!',
    'unknown_action': 'Error. Unknown action.',
    'not_unique': 'This title already exists! Please, choose a different '\
        'title.',
    'multiple_areas': 'Please select only one irradiation area.',
    'no_category': 'Please select a category.',
    'success_contact_responsible': 'Operation executed successfully. Your '\
        'email client should automatically open with the responsible\'s '\
        'email addresses.',
    'invalid_category': 'Invalid category.',
    'invalid_fluence': 'Invalid fluence.',
    'invalid_material': 'Invalid material.',
    'experiment_completed_not_allowed': 'Invalid operation. Action can\'t be '\
        'performed for completed experiments.',
    'invalid_operation_not_validated': 'Invalid operation. Action not '\
        'possible until experiment is validated by administrators.'
}


def save_experiment_form_formset(request, form_data):
    """Saves experiment using form data and sends email notification."""
    data = dict()
    logged_user = get_logged_user(request)
    if request.method == 'POST':
        data['form_is_valid'] = True
        data['alert_message'] = ALERT_MESSAGES['success']
        category_form = None
        #create and clone experiment
        if form_data['form_action'].lower() == 'create' or form_data['form_action'].lower() == 'clone':
            logging.info('Experiment create/clone')
            if form_data['form1'].is_valid() and form_data['form2'].is_valid() and form_data['form3'].is_valid(
            ) and form_data['fluence_formset'].is_valid() and form_data['material_formset'].is_valid():
                if form_data['form1'].checking_unique() is True:
                    category_form = get_category_form_from_form_data(form_data)
                    if category_form is not None:
                        if category_form.is_valid():
                            if form_data['fluence_formset'].is_valid():
                                if form_data['material_formset'].is_valid():
                                    #experiment creation
                                    experiment_data = {}
                                    experiment_data.update(form_data['form1'].cleaned_data)
                                    experiment_data.update(form_data['form2'].cleaned_data)
                                    experiment_data.update(form_data['form3'].cleaned_data)
                                    experiment_temp = Experiment.objects.create(
                                        **experiment_data)
                                    experiment = Experiment.objects.get(pk=experiment_temp.pk)
                                    experiment.created_by = logged_user
                                    experiment.updated_by = logged_user
                                    experiment.status = 'Registered'
                                    experiment.save()

                                    if form_data['form_action'].lower() == 'clone':
                                        previous_experiment = Experiment.objects.get(
                                            pk=form_data['form1'].instance.pk)
                                        for user in previous_experiment.users.all():
                                            experiment.users.add(user)
                                    
                                    category = category_form.save()
                                    category.experiment = experiment
                                    category.save()
                                    for form in form_data['fluence_formset'].forms:
                                        fluence = form.save()
                                        fluence.experiment = experiment
                                        fluence.save()
                                    for form in form_data['material_formset'].forms:
                                        material = form.save()
                                        material.experiment = experiment
                                        material.save()

                                    args = {'list_name': 'experiments_list'}
                                    data['html_list'] = render_partial_list_to_string(
                                        request, args)
                                    data['alert_message'] = data['alert_message'] = ALERT_MESSAGES[form_data['form_action'].lower()]

                                    message = mark_safe(
                                        'Dear user,\nyour irradiation experiment with title: '
                                        + experiment.title +
                                        ' was successfully registered by this account: ' +
                                        logged_user.email +
                                        '.\nPlease, find all your experiments at this URL: '\
                                        'placeholder.url.com'\
                                        '/experiments/\nIn case you believe that this '\
                                        'e-mail has been sent to you by mistake please '\
                                        'contact us at placeholder@cern.ch.\nKind regards'\
                                        ',\nCERN IRRAD team.\nplaceholder.url.com'
                                    )
                                    send_mail_notification(
                                        'IRRAD Data Manager: New experiment registered in the '\
                                            'CERN IRRAD Proton Irradiation Facility',
                                        message, 'placeholder@cern.ch',
                                        experiment.responsible.email)
                                    message2irrad = mark_safe(
                                        'The user with the account: ' + logged_user.email +
                                        ' registered a new experiment with title: ' +
                                        experiment.title +
                                        '.\nPlease, find all the registerd experiments in this '\
                                        'link: placeholder.url.com'\
                                        'samples_manager/experiments/'
                                    )
                                    send_mail_notification(
                                        'IRRAD Data Manager: New experiment', message2irrad,
                                        logged_user.email, 'placeholder@cern.ch')
                                else:
                                    data['form_is_valid'] = False
                                    data['alert_message'] = ALERT_MESSAGES['invalid_material']
                            else:
                                data['form_is_valid'] = False
                                data['alert_message'] = ALERT_MESSAGES['invalid_fluence']
                        else:
                            data['form_is_valid'] = False
                            data['alert_message'] = ALERT_MESSAGES['invalid_category']
                    else:
                        data['form_is_valid'] = False
                        data['alert_message'] = ALERT_MESSAGES['no_category']
                else:
                    data['form_is_valid'] = False
                    data['alert_message'] = ALERT_MESSAGES['not_unique']
            else:
                data['form_is_valid'] = False
                data['alert_message'] = ALERT_MESSAGES['invalid']
    
        #update experiment        
        elif form_data['form_action'].lower() == 'update':
            logging.info('Experiment update')
            if form_data['form1'].is_valid() and form_data['form2'].is_valid() and form_data['form3'].is_valid():
                old_experiment = Experiment.objects.get(pk=form_data['form1'].instance.pk)
                category_data = get_category_data_from_form(form_data, old_experiment)
                category_form = category_data['category_form']
                old_category_model = category_data['old_category_model']
                new_category_model = category_data['new_category_model']
                if category_form is not None:
                    if category_form.is_valid() and \
                        category_form.cleaned_data is not None:
                        if form_data['fluence_formset'].is_valid():
                            if form_data['material_formset'].is_valid():
                                #experiment update
                                experiment_updated = form_data['form1'].save()
                                form_data['form2'].save()
                                form_data['form3'].save()
                                form_data['fluence_formset'].save()
                                form_data['material_formset'].save()
                                new_category = category_form.save()
                                new_category.experiment = experiment_updated
                                new_category.save()
                                experiment = Experiment.objects.get(pk=experiment_updated.pk)
                                experiment.updated_by = logged_user
                                experiment.save()
                                # Calculate notification text before removing old cateogry
                                text = get_updated_experiment_data(old_experiment, experiment)
                                if old_category_model != new_category_model:
                                    old_category_model.objects.get(
                                        experiment=old_experiment).delete()

                                args = {'list_name': 'experiments_list'}
                                data['html_list'] = render_partial_list_to_string(
                                    request, args)
                                data['alert_message'] = data['alert_message'] = ALERT_MESSAGES[form_data['form_action'].lower()]
                                message2irrad = mark_safe(
                                    'The user with e-mail: ' + logged_user.email +
                                    ' updated the experiment with title "' + experiment.title +
                                    '" .\n' + 'The updated fields are: \n' + text +
                                    '\nPlease, find all the experiments in this link: '\
                                    'placeholder.url.com'
                                )
                                send_mail_notification(
                                    'IRRAD Data Manager: Updated experiment', message2irrad,
                                    logged_user.email, 'placeholder@cern.ch')
                            else:
                                data['form_is_valid'] = False
                                data['alert_message'] = ALERT_MESSAGES['invalid_material']
                        else:
                            data['form_is_valid'] = False
                            data['alert_message'] = ALERT_MESSAGES['invalid_fluence']
                    else:
                        data['form_is_valid'] = False
                        data['alert_message'] = ALERT_MESSAGES['invalid_category']
                else:
                    data['form_is_valid'] = False
                    data['alert_message'] = ALERT_MESSAGES['no_category']
            else:
                data['form_is_valid'] = False
                data['alert_message'] = ALERT_MESSAGES['missing_fields']

        #validate experiment
        elif form_data['form_action'].lower() == 'validate':
            if form_data['form1'].is_valid() and form_data['form2'].is_valid() and form_data['form3'].is_valid():
                old_experiment = Experiment.objects.get(pk=form_data['form1'].instance.pk)
                category_data = get_category_data_from_form(form_data, old_experiment)
                category_form = category_data['category_form']
                old_category_model = category_data['old_category_model']
                new_category_model = category_data['new_category_model']
                old_category = old_category_model.objects.get(
                    experiment=old_experiment)
                if category_form is not None:
                    if category_form.is_valid() and \
                        category_form.cleaned_data is not None:
                        if form_data['fluence_formset'].is_valid():
                            if form_data['material_formset'].is_valid():
                                experiment_updated = form_data['form1'].save()
                                form_data['form2'].save()
                                form_data['form3'].save()
                                experiment = Experiment.objects.get(pk=experiment_updated.pk)
                                experiment.status = 'Validated'
                                experiment.updated_by = logged_user
                                experiment.save()

                                category = category_form.save()
                                category.experiment = experiment
                                category.save()
                                if old_category_model != new_category_model:
                                    old_category.delete()
                                form_data['fluence_formset'].save()
                                form_data['material_formset'].save()

                                data['alert_message'] = ALERT_MESSAGES['validate']
                                args = {'list_name': 'experiments_list'}
                                data['html_list'] = render_partial_list_to_string(
                                    request, args)
                                message = 'Dear user,\nyour experiment with title "%s" '\
                                    'was validated. \nYou can now add samples and '\
                                    'additional users related to your irradiation '\
                                    'experiment.\nPlease, find all your experiments'\
                                    ' in this link: placeholder.url.com\n\nKind '\
                                    'regards,\nCERN IRRAD team.\n'\
                                    'placeholder.url.com' % experiment.title
                                send_mail_notification(
                                    'IRRAD Data Manager: Experiment  %s validation' %
                                    experiment.title, message, 'placeholder@cern.ch',
                                    experiment.responsible.email)
                                message2irrad = 'You validated the experiment with '\
                                    'title: %s' % experiment.title
                                send_mail_notification(
                                    'IRRAD Data Manager: Experiment %s validation' %
                                    experiment.title, message2irrad, 'placeholder@cern.ch',
                                    'placeholder@cern.ch')
                            else:
                                data['form_is_valid'] = False
                                data['alert_message'] = ALERT_MESSAGES['invalid_material']
                        else:
                            data['form_is_valid'] = False
                            data['alert_message'] = ALERT_MESSAGES['invalid_fluence']
                    else:
                        data['form_is_valid'] = False
                        data['alert_message'] = ALERT_MESSAGES['invalid_category']
                else:
                    data['form_is_valid'] = False
                    data['alert_message'] = ALERT_MESSAGES['no_category']
            else:
                data['form_is_valid'] = False
                data['alert_message'] = ALERT_MESSAGES['missing_fields']
        else:
            data['form_is_valid'] = False
            data['alert_message'] = ALERT_MESSAGES['unknown_action']

    context = {
        'form1': form_data['form1'],
        'form2': form_data['form2'],
        'form3': form_data['form3'],
        'fluence_formset': form_data['fluence_formset'],
        'material_formset': form_data['material_formset'],
        'passive_standard_categories_form': form_data['passive_standard_categories_form'],
        'passive_custom_categories_form': form_data['passive_custom_categories_form'],
        'active_categories_form': form_data['active_categories_form'],
        'current_page': form_data['current_page'],
        'render_with_errors': form_data['render_with_errors'],
        'form_action': form_data['form_action'],
        'form_tag_action': form_data['form_tag_action']
    }
    data['html_form'] = render_to_string(form_data['template_name'],
                                         context,
                                         request=request)
    return data


def get_category_data_from_form(form_data, experiment):
    """Returns category data."""
    result = dict()
    new_category_name = form_data['form2'].cleaned_data['category']
    old_category_name = experiment.category
    result['category_form'] = get_category_form_from_form_data(form_data)
    result['new_category_model'] = get_category_model_from_name(new_category_name)
    result['old_category_model'] = get_category_model_from_name(old_category_name)
    return result


def get_category_form_from_form_data(form_data):
    """Returns category form from experiment form data."""
    category_name = form_data['form2'].cleaned_data['category']
    if category_name == 'Passive Standard':
        result = form_data['passive_standard_categories_form']
    elif category_name == 'Passive Custom':
        result = form_data['passive_custom_categories_form']
    elif category_name == 'Active':
        result = form_data['active_categories_form']
    else:
        result = None
    return result


def get_category_form_from_name(category_name):
    """Returns category form from name."""
    if category_name == 'Passive Standard':
        result = PassiveStandardCategoryForm
    elif category_name == 'Passive Custom':
        result = PassiveCustomCategoryForm
    elif category_name == 'Active':
        result = ActiveCategoryForm
    else:
        result = None
    return result


def get_category_model_from_name(category_name):
    """Returns category model using a category name."""
    if category_name == 'Passive Standard':
        result = PassiveStandardCategory
    elif category_name == 'Passive Custom':
        result = PassiveCustomCategory
    elif category_name == 'Active':
        result = ActiveCategory
    else:
        result = None
    return result


def get_category_forms_for_experiment(experiment = None, post_data = None):
    """Returns category forms for experiment."""
    result = dict()
    if experiment is not None:
        category_model = get_category_model_from_name(experiment.category)
        category_instance = category_model.objects.get(experiment=experiment)
        if post_data is not None:
            if experiment.category == 'Passive Standard':
                result['passive_standard'] = PassiveStandardCategoryForm(post_data, instance=category_instance)
                result['passive_custom'] = PassiveCustomCategoryForm(post_data)
                result['active'] = ActiveCategoryForm(post_data)
            elif experiment.category == 'Passive Custom':
                result['passive_standard'] = PassiveStandardCategoryForm(post_data)
                result['passive_custom'] = PassiveCustomCategoryForm(post_data, instance=category_instance)
                result['active'] = ActiveCategoryForm(post_data)
            elif experiment.category == 'Active':
                result['passive_standard'] = PassiveStandardCategoryForm(post_data)
                result['passive_custom'] = PassiveCustomCategoryForm(post_data)
                result['active'] = ActiveCategoryForm(post_data, instance=category_instance)
            else:
                result = None
        else:
            if experiment.category == 'Passive Standard':
                result['passive_standard'] = PassiveStandardCategoryForm(instance=category_instance)
                result['passive_custom'] = PassiveCustomCategoryForm()
                result['active'] = ActiveCategoryForm()
            elif experiment.category == 'Passive Custom':
                result['passive_standard'] = PassiveStandardCategoryForm()
                result['passive_custom'] = PassiveCustomCategoryForm(instance=category_instance)
                result['active'] = ActiveCategoryForm()
            elif experiment.category == 'Active':
                result['passive_standard'] = PassiveStandardCategoryForm()
                result['passive_custom'] = PassiveCustomCategoryForm()
                result['active'] = ActiveCategoryForm(instance=category_instance)
            else:
                result = None
    else:
        if post_data is not None:
            result['passive_standard'] = PassiveStandardCategoryForm(post_data)
            result['passive_custom'] = PassiveCustomCategoryForm(post_data)
            result['active'] = ActiveCategoryForm(post_data)
        else:
            result['passive_standard'] = PassiveStandardCategoryForm()
            result['passive_custom'] = PassiveCustomCategoryForm()
            result['active'] = ActiveCategoryForm()
    return result


def get_category_forms_for_experimentt(experiment):
    """Returns category forms for experiment."""
    result = {
        'passive_standard': None,
        'passive_custom': None,
        'active': None
    }
    category_model = get_category_model_from_name(experiment.category)
    category_instance = category_model.objects.get(experiment=experiment)
    
    if experiment.category == 'Passive Standard':
        result['passive_standard'] = PassiveStandardCategoryForm(instance=category_instance)
        result['passive_custom'] = PassiveCustomCategoryForm()
        result['active'] = ActiveCategoryForm()
    elif experiment.category == 'Passive Custom':
        result['passive_standard'] = PassiveStandardCategoryForm()
        result['passive_custom'] = PassiveCustomCategoryForm(instance=category_instance)
        result['active'] = ActiveCategoryForm()
    elif experiment.category == 'Active':
        result['passive_standard'] = PassiveStandardCategoryForm()
        result['passive_custom'] = PassiveCustomCategoryForm()
        result['active'] = ActiveCategoryForm(instance=category_instance)
    else:
        result = None
    return result


def get_req_fluence_formset_copy_for_experiment(experiment):
    """Returns requested fluence formset copy for experiment."""
    result = None
    initial = []
    instances = ReqFluence.objects.filter(experiment=experiment)
    extra_forms = len(instances) - 1
    inline_formset = get_experiment_inline_formset(
        ReqFluence, ReqFluenceForm, ReqFluenceFormSet, extra = extra_forms)
    for instance in instances:
        initial.append({
            'req_fluence': instance.req_fluence
        })
    result = inline_formset(initial=initial, prefix='f-fs')
    return result


def get_material_formset_copy_for_experiment(experiment):
    """Returns material formset copy for experiment."""
    result = None
    initial = []
    instances = Material.objects.filter(experiment=experiment)
    extra_forms = len(instances) - 1
    inline_formset = get_experiment_inline_formset(
        Material, MaterialForm, MaterialFormSet, extra = extra_forms)
    for instance in instances:
        initial.append({
            'material': instance.material
        })
    result = inline_formset(initial=initial, prefix='m-fs')
    return result


def get_experiment_inline_formset(model, form, formset, min_num = 1, extra = 0):
    """Returns inline formset for experiment."""
    result = None
    if model != None and form != None and formset != None:
        result = inlineformset_factory(
            Experiment,
            model,
            form=form,
            extra=extra,
            min_num=1,
            validate_min=True,
            error_messages='Field is not correctly filled.',
            formset=formset)
    return result


def get_experiment_details_data(experiment):
    """Retrieves data related to experiment in JSON format."""
    if experiment.category == 'Passive Standard':
        category_object = get_object_or_404(PassiveStandardCategory,
                                            experiment=experiment)
    elif experiment.category == 'Passive Custom':
        category_object = get_object_or_404(PassiveCustomCategory,
                                            experiment=experiment)
    else:
        category_object = get_object_or_404(ActiveCategory,
                                            experiment=experiment)
    requested_fluences = ReqFluence.objects.filter(experiment=experiment)
    materials = Material.objects.filter(experiment=experiment)
    experiment_samples = Sample.objects.filter(experiment=experiment)
    fluences = []
    for sample in experiment_samples:
        irradiations = Irradiation.objects.filter(sample=sample)
        tuple_list = []
        for irradiation in irradiations:
            if irradiation.estimated_fluence:
                if '.' in str(irradiation.dosimeter):
                    logging.info('no calculation')
                else:
                    dosimeter_area = irradiation.dosimeter.width * irradiation.dosimeter.height
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
                                'width':
                                tuple_list[tuple_list_length - 1][1].width,
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
    data = {
        'experiment': experiment,
        'category_object': category_object,
        'requested_fluences': requested_fluences,
        'materials': materials,
        'experiment_samples': experiment_samples,
        'fluences': fluences
    }
    return data


def experiment_details(request, pk):
    """Displays data regarding an experiment."""
    has_permission_or_403(request, 'experiment_details', pk)
    experiment = get_object_or_404(Experiment, pk=pk)
    data = get_experiment_details_data(experiment)
    data['logged_user'] = get_logged_user(request)
    return render(request, 'samples_manager/experiment_details.html', data)


def admin_experiments_user_view(request, pk):
    """Displays experiments where user is involved."""
    has_permission_or_403(request, 'admin')
    logged_user = get_logged_user(request)
    user = User.objects.get(id=pk)
    experiments = write_authorised_experiments(user)
    pagination_data = get_pagination_data(request, experiments)
    partial_template = 'samples_manager/partial_admin_experiments_list.html'
    experiment_data = get_registered_samples_number(experiments)
    return render(request, 'samples_manager/experiments_list.html', {
        'base_template': 'samples_manager/base_all_tab_list.html',
        'partial_template': partial_template,
        'experiment_data': experiment_data,
        'logged_user': logged_user,
        'pagination_data': pagination_data,
    })


def experiments_list(request):
    """Retreives experiments accesible by user and additional data."""
    context = dict()
    has_permission_or_403(request, 'login')
    logged_user = get_logged_user(request)
    experiments = write_authorised_experiments(logged_user)
    search_url = reverse('samples_manager:experiments_search')
    pagination_data = get_pagination_data(request, experiments)
    context['experiment_data'] = get_registered_samples_number(pagination_data['page_obj'].object_list)
    context['base_template'] = 'samples_manager/base_all_tab_list.html'
    context['partial_template'] = 'samples_manager/partial_admin_experiments_list.html' \
        if is_admin(logged_user) else 'samples_manager/partial_experiments_list.html'
    context['search_url'] = search_url
    context['logged_user'] = logged_user
    context['pagination_data'] = pagination_data
    return render(request, 'samples_manager/experiments_list.html', context)


def experiments_shared_list(request):
    """Retreives experiments accesible by user and additional data."""
    has_permission_or_403(request, 'login')
    logged_user = get_logged_user(request)
    experiments = shared_experiments(logged_user)
    search_url = reverse('samples_manager:experiments_shared_search')
    pagination_data = get_pagination_data(request, experiments)
    experiment_data = get_registered_samples_number(pagination_data['page_obj'].object_list)
    return render(request, 'samples_manager/experiments_shared_list.html', {
        'search_url': search_url,
        'experiment_data': experiment_data,
        'logged_user': logged_user,
        'pagination_data': pagination_data
    })


def experiment_create(request):
    """Adds experiment."""
    logged_user = get_logged_user(request)
    current_page = 1
    render_with_errors = True
    if 'current_page' in request.POST.keys():
        current_page = int(request.POST['current_page'])
    if 'render_with_errors' in request.POST.keys():
        render_with_errors = bool(request.POST['render_with_errors'] == 'on')
    FluenceFormSetInline = get_experiment_inline_formset(ReqFluence, 
        ReqFluenceForm, ReqFluenceFormSet)
    MaterialFormSetInline = get_experiment_inline_formset(Material, 
        MaterialForm, MaterialFormSet)
    cern_experiments = Experiment.objects.order_by('cern_experiment').values(
        'cern_experiment').distinct()
    cern_experiments_list = []
    for item in cern_experiments:
        cern_experiments_list.append(item['cern_experiment'])
    if request.method == 'POST':
        logging.debug('POST request')
        form1 = ExperimentForm1(request.POST, data_list=cern_experiments_list)
        form2 = ExperimentForm2(request.POST)
        form3 = ExperimentForm3(request.POST)
        fluence_formset = FluenceFormSetInline(request.POST, prefix='f-fs')
        material_formset = MaterialFormSetInline(request.POST, prefix='m-fs')
        category_forms = get_category_forms_for_experiment(post_data=request.POST)
        passive_standard_categories_form = category_forms['passive_standard']
        passive_custom_categories_form = category_forms['passive_custom']
        active_categories_form = category_forms['active']
    else:
        form1 = ExperimentForm1(data_list=cern_experiments_list,
            initial={'responsible': logged_user})
        form2 = ExperimentForm2()
        form3 = ExperimentForm3()
        fluence_formset = FluenceFormSetInline(prefix='f-fs')
        material_formset = MaterialFormSetInline(prefix='m-fs')
        category_forms = get_category_forms_for_experiment()
        passive_standard_categories_form = category_forms['passive_standard']
        passive_custom_categories_form = category_forms['passive_custom']
        active_categories_form = category_forms['active']

    form_data = {
        'form1': form1,
        'form2': form2,
        'form3': form3,
        'fluence_formset': fluence_formset,
        'material_formset': material_formset,
        'passive_standard_categories_form': passive_standard_categories_form,
        'passive_custom_categories_form': passive_custom_categories_form,
        'active_categories_form': active_categories_form,
        'current_page': current_page,
        'render_with_errors': render_with_errors,
        'form_action': 'Create',
        'form_tag_action': reverse('samples_manager:experiment_create'),
        'template_name': 'samples_manager/partial_experiment_create_update_clone_validate.html'
    }

    data = save_experiment_form_formset(request, form_data)

    return JsonResponse(data)


def experiment_status_update(request):
    """Updates experiment's status and sends an email notifiation to users."""
    has_permission_or_403(request, 'admin')
    data = dict()
    checked_elements = get_checked_elements(request)
    validation_data = checked_elements_are_valid(checked_elements, 'group', Experiment)
    if validation_data['valid']:
        if request.method == 'POST':
            data['form_is_valid'] = True
            data['alert_message'] = ALERT_MESSAGES['success']
            form = ExperimentStatus(request.POST)
            if form.is_valid():
                for pk in checked_elements:
                    experiment = get_object_or_404(Experiment, pk=pk)
                    experiment.status = form.cleaned_data['status']
                    experiment.save()
                    if experiment.status == 'Completed':
                        message = mark_safe(
                            'Dear user,\nyour irradiation experiment with title ' +
                            experiment.title +
                            ' was completed.\nTwo weeks time is still needed '\
                            'for the cool down. Please, contact us after '\
                            'that period.\n\nKind regards,\nCERN IRRAD '\
                            'team.\nplaceholder.url.com'
                        )
                        send_mail_notification(
                            'IRRAD Data Manager: Experiment "%s"  was completed' %
                            experiment.title, message, 'placeholder@cern.ch',
                            experiment.responsible.email)
                        exp_users = experiment.users.values()
                        for user in exp_users:
                            send_mail_notification(
                                'IRRAD Data Manager: Experiment "%s"  was completed' %
                                experiment.title, message, 'placeholder@cern.ch',
                                user['email'])
                args = {'list_name': 'experiments_list'}
                data['html_list'] = render_partial_list_to_string(
                    request, args)
            else:
                data['form_is_valid'] = False
                data['alert_message'] = ALERT_MESSAGES['invalid']
        else:
            is_single = checked_elements_are_valid(checked_elements, 'single', Experiment)
            if is_single:
                experiment = Experiment.objects.get(pk=checked_elements[0])
                initial_data = {'status': experiment.status}
                form = ExperimentStatus(initial = initial_data)
            else:
                form = ExperimentStatus()
        context = dict()
        context['form'] = form
        context['additional_text'] = get_collapsible_text_checked_elements(
                checked_elements, Experiment)
        
        data['html_form'] = render_to_string(
            'samples_manager/experiment_status_update.html',
            context,
            request=request,
        )
    else:
        data['form_is_valid'] = False
        data['alert_message'] = validation_data['msg']
    return JsonResponse(data)


def experiment_comment_update(request, pk):
    """Updates comment section of experiment."""
    has_permission_or_403(request, 'experiment', pk)
    data = dict()
    experiment = get_object_or_404(Experiment, pk=pk)
    if request.method == 'POST':
        data['form_is_valid'] = True
        data['alert_message'] = ALERT_MESSAGES['success']
        form = ExperimentComment(request.POST, instance=experiment)
        if form.is_valid():
            form.save()
            template = 'samples_manager/partial_experiment_details.html'
            context = get_experiment_details_data(experiment)
            data['html_experiment'] = render_to_string(template, context)
        else:
            data['form_is_valid'] = False
            data['alert_message'] = ALERT_MESSAGES['invalid']
    else:
        form = ExperimentComment(instance=experiment)
    context = {'form': form, 'experiment': experiment}
    data['html_form'] = render_to_string(
        'samples_manager/experiment_comment_update.html',
        context,
        request=request,
    )
    return JsonResponse(data)


def experiment_update(request):
    """Updates experiment."""
    data = dict()
    current_page = 1
    render_with_errors = True
    if 'current_page' in request.POST.keys():
        current_page = int(request.POST['current_page'])
    if 'render_with_errors' in request.POST.keys():
        render_with_errors = bool(request.POST['render_with_errors'] == 'on')
    cern_experiments = Experiment.objects.order_by('cern_experiment').values(
        'cern_experiment').distinct()
    cern_experiments_list = []
    for item in cern_experiments:
        cern_experiments_list.append(item['cern_experiment'])
    FluenceFormSetInline = get_experiment_inline_formset(ReqFluence, 
        ReqFluenceForm, ReqFluenceFormSet)
    MaterialFormSetInline = get_experiment_inline_formset(Material, 
        MaterialForm, MaterialFormSet)
    checked_elements = get_checked_elements(request)
    validation_data = checked_elements_are_valid(checked_elements, 'single', Experiment)
    if validation_data['valid']:
        pk = checked_elements[0]
        experiment = get_object_or_404(Experiment, pk=pk)
        has_permission_or_403(request, 'experiment', pk)
        is_not_completed = (experiment.status.lower() != 'completed')
        if is_not_completed:
            if request.method == 'POST':
                form1 = ExperimentForm1(request.POST,
                                        instance=experiment,
                                        data_list=cern_experiments_list,
                                        title_validation=False)
                form2 = ExperimentForm2(request.POST, instance=experiment)
                form3 = ExperimentForm3(request.POST, instance=experiment)
                fluence_formset = FluenceFormSetInline(request.POST, 
                    instance=experiment, prefix='f-fs')
                material_formset = MaterialFormSetInline(request.POST, 
                    instance=experiment, prefix='m-fs')
                category_forms = get_category_forms_for_experiment(
                    experiment=experiment, post_data=request.POST)
                passive_standard_categories_form = category_forms['passive_standard']
                passive_custom_categories_form = category_forms['passive_custom']
                active_categories_form = category_forms['active']
            else:
                form1 = ExperimentForm1(instance=experiment,
                                        data_list=cern_experiments_list,
                                        title_validation=False)
                form2 = ExperimentForm2(instance=experiment)
                form3 = ExperimentForm3(instance=experiment)
                fluence_formset = FluenceFormSetInline(
                    instance=experiment, prefix='f-fs')
                material_formset = MaterialFormSetInline(
                    instance=experiment, prefix='m-fs')
                category_forms = get_category_forms_for_experiment(experiment)
                passive_standard_categories_form = category_forms['passive_standard']
                passive_custom_categories_form = category_forms['passive_custom']
                active_categories_form = category_forms['active']

            form_data = {
                'form1': form1,
                'form2': form2,
                'form3': form3,
                'fluence_formset': fluence_formset,
                'material_formset': material_formset,
                'passive_standard_categories_form': passive_standard_categories_form,
                'passive_custom_categories_form': passive_custom_categories_form,
                'active_categories_form': active_categories_form,
                'current_page': current_page,
                'render_with_errors': render_with_errors,
                'form_action': 'Update',
                'form_tag_action': reverse('samples_manager:experiment_update'),
                'template_name': 'samples_manager/partial_experiment_create_update_clone_validate.html'
            }
            data = save_experiment_form_formset(request, form_data)
        else:
            data['form_is_valid'] = False
            data['alert_message'] = ALERT_MESSAGES['experiment_completed_not_allowed']
    else:
        data['form_is_valid'] = False
        data['alert_message'] = validation_data['msg']
    return  JsonResponse(data)


def experiment_validate(request):
    """Changes validity status of experiment."""
    data = dict()
    current_page = 1
    render_with_errors = True
    if 'current_page' in request.POST.keys():
        current_page = int(request.POST['current_page'])
    if 'render_with_errors' in request.POST.keys():
        render_with_errors = bool(request.POST['render_with_errors'] == 'on')
    cern_experiments = Experiment.objects.order_by('cern_experiment').values(
        'cern_experiment').distinct()
    cern_experiments_list = []
    for item in cern_experiments:
        cern_experiments_list.append(item['cern_experiment'])
    FluenceFormSetInline = get_experiment_inline_formset(ReqFluence, 
        ReqFluenceForm, ReqFluenceFormSet)
    MaterialFormSetInline = get_experiment_inline_formset(Material, 
        MaterialForm, MaterialFormSet)
    checked_elements = get_checked_elements(request)
    validation_data = checked_elements_are_valid(checked_elements, 'single', Experiment)
    if validation_data['valid']:
        pk = checked_elements[0]
        experiment = get_object_or_404(Experiment, pk=pk)
        has_permission_or_403(request, 'admin')
        is_not_completed = (experiment.status.lower() != 'completed')
        if is_not_completed:
            if request.method == 'POST':
                form1 = ExperimentForm1(request.POST,
                                        instance=experiment,
                                        data_list=cern_experiments_list,
                                        title_validation=False)
                form2 = ExperimentForm2(request.POST, instance=experiment)
                form3 = ExperimentForm3(request.POST, instance=experiment)
                fluence_formset = FluenceFormSetInline(request.POST, 
                    instance=experiment, prefix='f-fs')
                material_formset = MaterialFormSetInline(request.POST, 
                    instance=experiment, prefix='m-fs')
                category_forms = get_category_forms_for_experiment(
                    experiment=experiment, post_data=request.POST)
                passive_standard_categories_form = category_forms['passive_standard']
                passive_custom_categories_form = category_forms['passive_custom']
                active_categories_form = category_forms['active']
            else:
                form1 = ExperimentForm1(instance=experiment,
                                        data_list=cern_experiments_list,
                                        title_validation=False)
                form2 = ExperimentForm2(instance=experiment)
                form3 = ExperimentForm3(instance=experiment)
                fluence_formset = FluenceFormSetInline(instance=experiment, prefix='f-fs')
                material_formset = MaterialFormSetInline(instance=experiment, prefix='m-fs')
                category_forms = get_category_forms_for_experiment(
                    experiment=experiment)
                passive_standard_categories_form = category_forms['passive_standard']
                passive_custom_categories_form = category_forms['passive_custom']
                active_categories_form = category_forms['active']
            form_data = {
                'form1': form1,
                'form2': form2,
                'form3': form3,
                'fluence_formset': fluence_formset,
                'material_formset': material_formset,
                'passive_standard_categories_form': passive_standard_categories_form,
                'passive_custom_categories_form': passive_custom_categories_form,
                'active_categories_form': active_categories_form,
                'current_page': current_page,
                'render_with_errors': render_with_errors,
                'form_action': 'Validate',
                'form_tag_action': reverse('samples_manager:experiment_validate'),
                'template_name': 'samples_manager/partial_experiment_create_update_clone_validate.html'
            }
            data = save_experiment_form_formset(request, form_data)
        else:
            data['form_is_valid'] = False
            data['alert_message'] = ALERT_MESSAGES['experiment_completed_not_allowed']
    else:
        data['form_is_valid'] = False
        data['alert_message'] = validation_data['msg']
    return  JsonResponse(data)

def experiment_clone(request):
    """Clones experiment."""
    data = dict()
    current_page = 1
    render_with_errors = True
    if 'current_page' in request.POST.keys():
        current_page = int(request.POST['current_page'])
    if 'render_with_errors' in request.POST.keys():
        render_with_errors = bool(request.POST['render_with_errors'] == 'on')
    cern_experiments = Experiment.objects.order_by('cern_experiment').values(
        'cern_experiment').distinct()
    cern_experiments_list = []
    for item in cern_experiments:
        cern_experiments_list.append(item['cern_experiment'])
    FluenceFormSetInline = get_experiment_inline_formset(ReqFluence, 
        ReqFluenceForm, ReqFluenceFormSet)
    MaterialFormSetInline = get_experiment_inline_formset(Material, 
        MaterialForm, MaterialFormSet)
    checked_elements = get_checked_elements(request)
    validation_data = checked_elements_are_valid(checked_elements, 'single', Experiment)
    if validation_data['valid']:
        pk = checked_elements[0]
        experiment = get_object_or_404(Experiment, pk=pk)
        has_permission_or_403(request, 'experiment', pk)
        if request.method == 'POST':
            form1 = ExperimentForm1(request.POST,
                                    instance=experiment,
                                    data_list=cern_experiments_list)
            form2 = ExperimentForm2(request.POST, instance=experiment)
            form3 = ExperimentForm3(request.POST, instance=experiment)
            fluence_formset = FluenceFormSetInline(request.POST, 
                prefix='f-fs')
            material_formset = MaterialFormSetInline(request.POST, 
                prefix='m-fs')
            category_forms = get_category_forms_for_experiment(
                post_data=request.POST)
            passive_standard_categories_form = category_forms['passive_standard']
            passive_custom_categories_form = category_forms['passive_custom']
            active_categories_form = category_forms['active']
        else:
            form1 = ExperimentForm1(instance=experiment,
                                    data_list=cern_experiments_list)
            form2 = ExperimentForm2(instance=experiment)
            form3 = ExperimentForm3(instance=experiment)
            fluence_formset = get_req_fluence_formset_copy_for_experiment(experiment)
            material_formset = get_material_formset_copy_for_experiment(experiment)
            category_forms = get_category_forms_for_experiment(
                experiment=experiment)
            passive_standard_categories_form = category_forms['passive_standard']
            passive_custom_categories_form = category_forms['passive_custom']
            active_categories_form = category_forms['active']
        form_data = {
            'form1': form1,
            'form2': form2,
            'form3': form3,
            'fluence_formset': fluence_formset,
            'material_formset': material_formset,
            'passive_standard_categories_form': passive_standard_categories_form,
            'passive_custom_categories_form': passive_custom_categories_form,
            'active_categories_form': active_categories_form,
            'current_page': current_page,
            'render_with_errors': render_with_errors,
            'form_action': 'Clone',
            'form_tag_action': reverse('samples_manager:experiment_clone'),
            'template_name': 'samples_manager/partial_experiment_create_update_clone_validate.html'
        }
        data = save_experiment_form_formset(request, form_data)
    else:
        data['form_is_valid'] = False
        data['alert_message'] = validation_data['msg']
    return  JsonResponse(data)


def experiment_delete(request):
    """Deletes experiments and sends email notificaiton."""
    data = dict()
    logged_user = get_logged_user(request)
    checked_elements = get_checked_elements(request)
    validation_data = checked_elements_are_valid(checked_elements, 'group', Experiment)
    if validation_data['valid']:
        if request.method == 'POST':
            for pk in checked_elements:
                has_permission_or_403(request, 'experiment', [pk])
                experiment = get_object_or_404(Experiment, pk=pk)
                experiment.delete()
                args = {'list_name': 'experiments_list'}
                data['html_list'] = render_partial_list_to_string(
                    request, args)
                data['alert_message'] = ALERT_MESSAGES['delete']
                message = mark_safe(
                    'Dear user,\nyour irradiation experiment with title ' +
                    experiment.title + ' was deleted by the account: ' +
                    logged_user.email +
                    '.\nPlease, find all your experiments at this URL: '\
                    'placeholder.url.com'\
                    '/experiments/\n\nKind regards,\nCERN IRRAD team.'\
                    '\nplaceholder.url.com'
                )
                send_mail_notification(
                    'IRRAD Data Manager: Experiment "%s"  was deleted' %
                    experiment.title, message, 'placeholder@cern.ch',
                    experiment.responsible.email)
                message2irrad = mark_safe('The user with the account: ' +
                                        logged_user.email +
                                        ' deleted the experiment with title "' +
                                        experiment.title + '".\n')
                send_mail_notification(
                    'IRRAD Data Manager: Experiment "%s"  was deleted' %
                    experiment.title, message2irrad, experiment.responsible.email,
                    'placeholder@cern.ch')
        else:
            context = dict()
            context['additional_text'] = get_collapsible_text_checked_elements(
                checked_elements, Experiment)
            data['html_form'] = render_to_string(
                'samples_manager/partial_experiment_delete.html',
                context,
                request=request,
            )
    else:
        data['form_is_valid'] = False
        data['alert_message'] = validation_data['msg']
    
    return JsonResponse(data)


def experiment_update_visibility(request):
    """Changes experiment visibility."""
    data = dict()
    logged_user = get_logged_user(request)
    checked_elements = get_checked_elements(request)
    validation_data = checked_elements_are_valid(checked_elements, 'group', Experiment)
    data['form_is_valid'] = True
    if validation_data['valid']:
        has_permission_or_403(request, 'experiment', checked_elements)
        if request.method == 'POST':
            data['alert_message'] = ALERT_MESSAGES['success']
            try:
                for pk in checked_elements:
                    experiment = Experiment.objects.get(pk=pk)
                    change = request.POST['visibility']
                    if change == 'Public':
                        experiment.public_experiment = True
                    else:
                        experiment.public_experiment = False
                    experiment.save()
                    args = {'list_name': 'experiments_list'}
                    data['html_list'] = render_partial_list_to_string(
                        request, args)
            except:
                data['form_is_valid'] = False
                data['alert_message'] = ALERT_MESSAGES['invalid']
        else:
            form = None
            is_single = checked_elements_are_valid(checked_elements, 'single', Experiment)
            if is_single:
                pk = checked_elements[0]
                experiment = experiment = Experiment.objects.get(pk=pk)
                initial_data = {
                    'visibility': 'Public' if experiment.public_experiment \
                        else 'Private'
                }
                form = ExperimentVisibility(initial=initial_data)
            else:
                form = ExperimentVisibility()
            context = dict()
            context['form'] = form
            context['form_tag_action'] = reverse(\
                'samples_manager:experiment_update_visibility')
            context['additional_text'] = get_collapsible_text_checked_elements(
                checked_elements, Experiment)
            data['html_form'] = render_to_string(
                'samples_manager/partial_experiment_update_visibility.html',
                context,
                request=request,
            )   
    else:
        data['form_is_valid'] = False
        data['alert_message'] = validation_data['msg']
    return JsonResponse(data)


def experiment_upload_attachment(request):
    """Uploads attachment to experiment."""
    data = dict()
    logged_user = get_logged_user(request)
    checked_elements = get_checked_elements(request)
    validation_data = checked_elements_are_valid(checked_elements, 'single', Experiment)
    if validation_data['valid']:
        if request.method == 'POST':
            pass
            data['form_is_valid'] = True
        else:
            context = dict()
            context['experiment_id'] = checked_elements[0]
            context['upload_attachment_url'] = CERNBOX_UPLOAD_URL
            data['form_is_valid'] = True
            data['html_form'] = render_to_string(
                'samples_manager/partial_experiment_upload_attachment.html',
                context,
                request=request,
            )
    else:
        data['form_is_valid'] = False
        data['alert_message'] = validation_data['msg']
    
    return JsonResponse(data)


def redirect_experiment_details(request):
    """Redirects user to experiment's details page."""
    data = dict()
    data['form_is_valid'] = True
    logged_user = get_logged_user(request)
    checked_elements = get_checked_elements(request)
    validation_data = checked_elements_are_valid(checked_elements, 'single', Experiment)
    if validation_data['valid']:
        pk = checked_elements[0]
        experiment = get_object_or_404(Experiment, pk=pk)
        has_permission_or_403(request, 'experiment_details', experiment.id)
        data['redirect_url'] = reverse('samples_manager:experiment_details',
            args=[experiment.id])     
    else:
        data['form_is_valid'] = False
        data['alert_message'] = validation_data['msg']
    return JsonResponse(data)


def redirect_experiment_samples_list(request):
    """Redirects user to experiment's sample page."""
    data = dict()
    data['form_is_valid'] = True
    logged_user = get_logged_user(request)
    checked_elements = get_checked_elements(request)
    validation_data = checked_elements_are_valid(checked_elements, 'single', Experiment)
    if validation_data['valid']:
        pk = checked_elements[0]
        experiment = get_object_or_404(Experiment, pk=pk)
        is_validated = (experiment.status != 'Registered' or \
            is_admin(logged_user))
        if is_validated:
            has_permission_or_403(request, 'experiment', experiment.id)
            data['redirect_url'] = reverse('samples_manager:experiment_samples_list',
                args=[experiment.id])     
        else:
            data['form_is_valid'] = False
            data['alert_message'] = ALERT_MESSAGES['invalid_operation_not_validated']
    else:
        data['form_is_valid'] = False
        data['alert_message'] = validation_data['msg']
    return JsonResponse(data)


def redirect_experiment_users_list(request):
    """Redirects user to experiment's user page."""
    data = dict()
    data['form_is_valid'] = True
    logged_user = get_logged_user(request)
    checked_elements = get_checked_elements(request)
    validation_data = checked_elements_are_valid(checked_elements, 'single', Experiment)
    if validation_data['valid']:
        pk = checked_elements[0]
        experiment = get_object_or_404(Experiment, pk=pk)
        is_validated = (experiment.status != 'Registered' or \
            is_admin(logged_user))
        if is_validated:
            has_permission_or_403(request, 'experiment', experiment.id)
            data['redirect_url'] = reverse('samples_manager:experiment_users_list',
                args=[experiment.id])
        else:
            data['form_is_valid'] = False
            data['alert_message'] = ALERT_MESSAGES['invalid_operation_not_validated'] 
    else:
        data['form_is_valid'] = False
        data['alert_message'] = validation_data['msg']
    return JsonResponse(data)


def redirect_experiment_contact_responsible(request):
    """Redirects user contact responsibles of selected experiments."""
    data = dict()
    data['form_is_valid'] = True
    has_permission_or_403(request, 'admin')
    logged_user = get_logged_user(request)
    checked_elements = get_checked_elements(request)
    validation_data = checked_elements_are_valid(checked_elements, 'group', Experiment)
    if validation_data['valid']:
        emails = []
        for pk in checked_elements:
            experiment = get_object_or_404(Experiment, pk=pk)
            emails.append(experiment.responsible.email)
        data['redirect_url'] = \
            get_mail_to_string_from_emails(emails)
        data['alert_message'] = ALERT_MESSAGES['success_contact_responsible']
    else:
        data['form_is_valid'] = False
        data['alert_message'] = validation_data['msg']
    return JsonResponse(data)


def get_updated_experiment_data(old_experiment, new_experiment):
    """
    Identifies which parts of an experiment have been updated and outputs 
    it as a string. Used during update process of an experiment to see what 
    has changed.
    """
    old_category_model = get_category_model_from_name(
        old_experiment.category)
    old_fluences = ReqFluence.objects.all().filter(
        experiment=old_experiment).order_by('id')
    old_materials = Material.objects.all().filter(
        experiment=old_experiment).order_by('id')
    old_category = old_category_model.objects.get(
        experiment=old_experiment)
    excluded_keys = 'id', 'status', 'responsible', 'users', 'created_at', \
        'updated_at', 'created_by', 'updated_by', '_state'
    old_dict, new_dict = old_experiment.__dict__, new_experiment.__dict__
    experiment_flag, category_flag, fluence_flag, material_flag = False, False, False, False
    text = ''
    for k, v in old_dict.items():
        if k in excluded_keys:
            continue
        try:
            if v != new_dict[k]:
                experiment_flag = True
                text = text + str(k) + ': ' + str(
                    new_dict[k]) + ' (old value: ' + str(old_dict[k]) + ') \n'
        except KeyError:
            logging.error('key error')
    category_text = '\nCategories:\n'
    category_excluded_keys = 'id', 'experiment_id', '_state'
    if new_experiment.category == 'Passive Standard':
        new_category = PassiveStandardCategory.objects.get(
            experiment=new_experiment)
        old_category_dict, new_category_dict = old_category.__dict__, new_category.__dict__
        for k, v in old_category_dict.items():
            if k in excluded_keys:
                continue
            try:
                if v != new_category_dict[k]:
                    category_flag = True
                    category_text = category_text + str(k) + '\n'
            except KeyError:
                logging.error('key error')
    elif new_experiment.category == 'Passive Custom':
        new_category = PassiveCustomCategory.objects.get(
            experiment=new_experiment)
        old_category_dict, new_category_dict = old_category.__dict__, new_category.__dict__
        for k, v in old_category_dict.items():
            if k in excluded_keys:
                continue
            try:
                if v != new_category_dict[k]:
                    category_flag = True
                    category_text = category_text + str(k) + ': ' + str(
                        new_category_dict[k]) + ' (old value: ' + str(
                            old_category_dict[k]) + ') \n'
            except KeyError:
                logging.error('key error')
    elif new_experiment.category == 'Active':
        new_category = ActiveCategory.objects.get(experiment=new_experiment)
        old_category_dict, new_category_dict = old_category.__dict__, new_category.__dict__
        for k, v in old_category_dict.items():
            if k in excluded_keys:
                continue
            try:
                if v != new_category_dict[k]:
                    category_flag = True
                    category_text = category_text + str(k) + ': ' + str(
                        new_category_dict[k]) + ' (old value: ' + str(
                            old_category_dict[k]) + ') \n'
            except KeyError:
                logging.error('key error')
    old_fluences_number = len(old_fluences)
    new_fluences = ReqFluence.objects.filter(
        experiment=new_experiment).order_by('id')
    new_fluences_number = len(new_fluences)
    fluences_text = '\nFluences: \n'
    old_fluence_ids = []
    new_fluence_ids = []
    for f in new_fluences:
        new_fluence_ids.append(f.id)
    fluences_after_removal = []
    for fluence in old_fluences:
        if fluence.id not in new_fluence_ids:
            fluence_flag = True
            fluences_text = fluences_text + 'value ' + str(
                fluence.req_fluence) + ' was removed\n'
        else:
            fluences_after_removal.append(fluence)
    for f in fluences_after_removal:
        old_fluence_ids.append(f.id)
    i = 0
    for fluence in new_fluences:  # checking for updated fluences or newly added
        if fluence.id in old_fluence_ids:
            if fluence.req_fluence != fluences_after_removal[i].req_fluence:
                fluence_flag = True
                fluences_text = fluences_text + str(
                    fluence.req_fluence) + '(old value: ' + str(
                        fluences_after_removal[i].req_fluence) + ')\n'
            else:
                pass
            i = i + 1
        else:
            fluence_flag = True
            fluences_text = fluences_text + str(
                fluence.req_fluence) + ' (New added value)\n'

    old_materials_number = len(old_materials)
    new_materials = Material.objects.filter(
        experiment=new_experiment).order_by('id')
    new_materials_number = len(new_materials)
    materials_text = '\nSample types: \n'
    old_material_ids = []
    new_material_ids = []
    for m in new_materials:
        new_material_ids.append(m.id)
    materials_after_removal = []
    for material in old_materials:
        if material.id not in new_material_ids:
            material_flag = True
            materials_text = materials_text + 'value ' + str(
                material.material) + ' was removed\n'
        else:
            materials_after_removal.append(material)

    for m in materials_after_removal:
        old_material_ids.append(m.id)
    i = 0
    for material in new_materials:  # checking for updated materials or newly added
        if material.id in old_material_ids:
            if material.material != materials_after_removal[i].material:
                material_flag = True
                materials_text = materials_text + str(
                    material.material) + '(old value: ' + str(
                        materials_after_removal[i].material) + ')\n'
            else:
                pass
            i = i + 1
        else:
            material_flag = True
            materials_text = materials_text + str(
                material.material) + ' (New added value)\n'

    if category_flag == True:
        text = text + category_text
    else:
        pass
    if fluence_flag == True:
        text = text + fluences_text
    else:
        pass
    if material_flag == True:
        text = text + materials_text
    else:
        pass
    return text

