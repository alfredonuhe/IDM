"""Django app forms."""
# -*- coding: utf-8 -*-
from .models import *
from .fields import *
from .utilities import *
from django import forms
from django.db.models import Q
from django.urls import reverse
from django.forms import ModelForm
from django.utils.safestring import mark_safe
from samples_manager.fields import ListTextWidget
from django.core.exceptions import ValidationError
from .templatetags.custom_filters import num_notation
from django.utils.translation import ugettext_lazy as _

BOOLEAN = (
    ('True', 'True'),
    ('False', 'False')
)

OPTIONS = (
    ('5x5 mm²', '5x5 mm²'),
    ('10x10 mm²', '10x10 mm²'),
    ('20x20 mm²', '20x20 mm²'),
)

ACTIVE_OPTIONS = (
    ('Cold box', 'Cold box irradiation (-25°C)'),
    ('Cryostat', 'Cryostat (< 5 K)'),
    ('Room temperature', 'Room temperature (~ 20 °C)'),
)

PARTICLES = (
    ('Protons', 'Protons'),
    ('Heavy ions', 'Heavy ions'),
    ('Pions', 'Pions'),
)

IRRAD_TABLES = (
    ('', 'Select IRRAD table'),
    ('Shuttle', 'Shuttle'),
    ('IRRAD3', 'IRRAD3'),
    ('IRRAD5', 'IRRAD5'),
    ('IRRAD7', 'IRRAD7'),
    ('IRRAD9', 'IRRAD9'),
    ('IRRAD11', 'IRRAD11'),
    ('IRRAD13', 'IRRAD13'),
    ('IRRAD15', 'IRRAD15'),
    ('IRRAD17', 'IRRAD17'),
    ('IRRAD19', 'IRRAD19'),
)

TABLE_POSITIONS = (
    ('', 'Select position'),
    ('Center', 'Center'),
    ('Left', 'Left'),
    ('Right', 'Right'),
)

THEME_CHOICES = (
    ('round', 'Round'),
    ('github', 'GitHub'),
    ('default', 'Default'),
    ('amazon', 'Amazon'),
    ('material', 'Material'),
    ('colored', 'Colored'),
    ('bookish', 'Bookish'),
    ('flat', 'Flat'),
)

PRINTERS = (
    ('irrad-eam-printer', 'IRRAD_LAB'),
)

PRINTER_TEMPLATES = (
    ('THT-59-7425-2-SC', 'small_qr'),
)

MAX_PRINT_COPIES = 50
MAX_NUM_GEN_DOS_IDS = 50


def get_fluences(experiment_id, queryset=False):
    """Retrieves fluences related to experiment."""
    result = []
    fluences = ReqFluence.objects.filter(experiment=experiment_id)
    if queryset:
        result = fluences
    else:
        for fluence in fluences:
            result.append((fluence.id, str(fluence)))
    return result


def get_materials(experiment_id, queryset=False):
    """Retrieves materials related to experiment."""
    result = []
    materials = Material.objects.filter(experiment=experiment_id)
    if queryset:
        result = materials
    else:
        for material in materials:
            result.append((material.id, str(material)))
    return result


def get_categories(experiment_id):
    """Retrieves categories related to experiment."""
    experiment = Experiment.objects.get(pk=experiment_id)
    if experiment.category == 'Passive Standard':
        category = PassiveStandardCategory.objects.filter(
            experiment=experiment_id)
        categories = ()
        if category[0].irradiation_area_5x5 == True:
            categories = categories + (
                ('Passive standard 5x5 mm²', 'Passive standard 5x5 mm²'), )
        if category[0].irradiation_area_10x10 == True:
            categories = categories + (
                ('Passive standard 10x10 mm²', 'Passive standard 10x10 mm²'), )
        if category[0].irradiation_area_20x20 == True:
            categories = categories + (
                ('Passive standard 20x20 mm²', 'Passive standard 20x20 mm²'), )
    elif experiment.category == 'Passive Custom':
        passive_custom_categories = PassiveCustomCategory.objects.filter(
            experiment=experiment_id)
        categories = ()
        for category in passive_custom_categories:
            categories = categories + (
                (category.passive_category_type + ', in irradiation area: ' +
                 category.passive_irradiation_area,
                 category.passive_category_type + ', in irradiation area: ' +
                 category.passive_irradiation_area), )
    elif experiment.category == 'Active':
        active_categories = ActiveCategory.objects.filter(
            experiment=experiment_id)
        categories = ()
        for category in active_categories:
            categories = categories + (
                (category.active_category_type + ', in irradiation area: ' +
                 category.active_irradiation_area,
                 category.active_category_type + ', in irradiation area: ' +
                 category.active_irradiation_area), )
    return categories


def get_box_id_choices():
    """Returns an iterable of 2-tuples to use as choices for box ids."""
    result = [('None', 'No box')]
    boxes = Box.objects.all().order_by('box_id')
    for box in boxes:
        result.append((box.box_id, box.box_id))
    return result


def get_previous_irradiation_choices():
    """
    Returns an iterable of 2-tuples to use as choices for parent 
    irradiations.
    """
    result = []
    irradiations = Irradiation.objects.filter(Q(status='Completed') | Q(status='OutBeam')).order_by('id')
    for irradiation in irradiations:
        children = Irradiation.objects.filter(previous_irradiation=irradiation.id)
        has_no_children = (len(children) == 0)
        if has_no_children:
            name = str(irradiation.dosimeter.dos_id)
            has_sample = (irradiation.sample is not None)
            if has_sample:
                name = name + '|' + str(irradiation.sample.set_id)
            name = name + '|' + str(irradiation.id)
            result.append((irradiation.id, name))
    return result


def get_write_authorised_experiments(logged_user, excluded=[]):
    """Retrieves experiments logged user can modify."""
    result = []
    experiments = []

    if is_admin(logged_user):
        experiments = Experiment.objects.order_by('title')
    else:
        experiments = Experiment.objects.filter(
            Q(users=logged_user)
            | Q(responsible=logged_user)).order_by('title')
    for experiment in experiments:
        if experiment.id not in excluded:
            result.append((experiment.id, experiment.title))
    return result


def get_sample_move_choices(logged_user, old_experiment_id):
    """Retrieves experiments logged user can modify and are validated."""
    not_validated_experiments = Experiment.objects.filter(status='Registered')
    excluded = []

    if not is_admin(logged_user):
        for experiment in not_validated_experiments:
            excluded.append(experiment.id)

    if old_experiment_id not in excluded:
        excluded.append(int(old_experiment_id))
    
    result = get_write_authorised_experiments( \
        logged_user, excluded)
    return result


class ExperimentForm1(forms.ModelForm):
    """
    First page of experiment form.

    Used for submitting/updating/cloning an experiment.
    """
    cern_experiment = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        _cern_experiment_list = kwargs.pop('data_list', None)
        self.title_validation = \
            kwargs.pop('title_validation', True)
        super(ExperimentForm1, self).__init__(*args, **kwargs)
        self.use_required_attribute = False
        self.fields['title'].label = 'Irradiation experiment title'
        self.fields['title'].help_text = '<p>A unique name for the '\
            'irradiation experiment.</p>'
        self.fields['description'].label = 'Description'
        self.fields['description'].help_text = '<p>Short description '\
            'of the irradiation experiment.</p>'
        self.fields['cern_experiment'].widget = ListTextWidget(
            data_list=_cern_experiment_list, name='cern_experiment_-list')
        self.fields['cern_experiment'].label = 'CERN experiment/Projects'
        self.fields['cern_experiment'].help_text = '<p>CERN Experiment '\
            'to which the irradiation experiment is associated, if it '\
            'does not exist users can create a new one.</p>'
        self.fields['responsible'].label = 'Responsible person'
        self.fields['responsible'].help_text = '<p>The e-mail of the '\
            'person that will be responsible for the specific irradiation '\
            'experiment.</p>'
        self.fields['emergency_phone'].label = 'Emergency telephone number'
        self.fields['emergency_phone'].help_text = '<p>A telephone number '\
            'where the responsible person can be reached at any time '\
            'during the execution of its experiment.</p>'
        self.fields['constraints'].required = False
        self.fields['constraints'].help_text = '<p>Any constraints '\
            'regarding the irradiation experiment (e.g. time constraints '\
            'due to prior/post test beam activities, etc.).</p>'
        self.fields['availability'] = forms.DateField(
            input_formats=['%d/%m/%Y'], widget=forms.DateInput(
                format='%d/%m/%Y',
                attrs={
                    'placeholder':
                    'When your samples will be available for irradiation'
                }))
        self.fields['availability'].label = 'Availability'
        self.fields['availability'].help_text = '<p>Time when samples '\
            'will be ready for irradiation.</p>'

    class Meta:
        """Form metadata."""
        model = Experiment
        exclude = ('category', 'number_samples', 'comments',
                   'regulations_flag', 'irradiation_type', 'public_experiment')
        fields = [
            'title',
            'description',
            'cern_experiment',
            'responsible',
            'emergency_phone',
            'availability',
            'constraints',
        ]
        widgets = {
            'title':forms.TextInput(
                attrs={
                    'placeholder':
                    'Please, provide a unique title for your irradiation experiment'
                }),
            'description':forms.Textarea(
                attrs={
                    'placeholder':
                    'Please, provide a short description of your experiment',
                    'rows': 2
                }),
            'constraints':forms.TextInput(
                attrs={
                    'placeholder':
                    'Please,provide any time constraints, e.g. test beam'
                }),
            'emergency_phone':forms.TextInput(
                attrs={
                    'placeholder':
                    'Please, provide a telephone number in case of emergency'
                }),
        }

    def clean_title(self):
        """Validates field title."""
        title = self.cleaned_data['title']
        if self.title_validation:
            is_valid = True
            experiments = Experiment.objects.all()
            for experiment in experiments:
                if title == experiment.title:
                    is_valid = False
                    break

            if not is_valid:
                raise forms.ValidationError('Experiment already exists.')
        
        return title

    def checking_unique(self):
        """Checks if experiment already exists."""
        cleaned_data = self.cleaned_data
        title = cleaned_data['title']
        experiments = Experiment.objects.all()
        titles = []
        for exp in experiments:
            titles.append(exp.title)
        if title in titles:
            return False
        return True


class ExperimentForm2(forms.ModelForm):
    """
    Second page of experiment submission form.

    Used for submitting/updating/cloning an experiment.
    """
    def __init__(self, *args, **kwargs):
        super(ExperimentForm2, self).__init__(*args, **kwargs)
        self.use_required_attribute = False
        self.fields['irradiation_type'].label = 'Irradiation type'
        self.fields['irradiation_type'] = forms.ChoiceField(choices=PARTICLES)
        self.fields['irradiation_type'].help_text = '<p>Protons: normal '\
            'IRRAD operation during the PS proton.<p/><p>Heavy ions: if beam '\
            'schedule foresee some weeks per year during the PS ion run.<p/>'\
            '<p>Pions: ions: irradiation campaigns at Paul Scherrer '\
            'Institute – PSI scheduled on users requests and the PSI beam '\
            'availability.</p>'
        self.fields['number_samples'] = forms.CharField(max_length=3,
            widget=forms.TextInput(attrs={'placeholder': 'e.g. 1'}))
        self.fields['number_samples'].label = 'Number of samples'
        self.fields['number_samples'].help_text = '<p>An estimation of '\
            'the total number of samples to be irradiated. Further details '\
            'about the samples will be requested when the experiment is '\
            'validated.</p>'
        self.fields['category'].label = 'Category'
        self.fields['category'].help_text = '<p>Passive Standard: '\
            'irradiation of a passive Device Under Test - DUT (e.g. without '\
            'Front-End electronics, etc.) for an irradiation area of 5×5 '\
            'mm2, 10×10 mm2 or 20×20 mm2. Users should select at least one '\
            'irradiation area.<p/><p>Passive Custom: irradiation of a '\
            'passive DUT of bigger or smaller irradiation '\
            'area/dimensions/volumes/etc. than the Passive Standard '\
            'category.<p/><p>Active: irradiation of a DUT (with Front-End '\
            'electronics, etc.) which need to be powered and monitored '\
            'during irradiation.<p/><p>If you need more than one category, '\
            'please, create a new experiment.</p>'

    class Meta:
        """Form metadata."""
        model = Experiment
        exclude = ('title', 'description', 'cern_experiment', 'responsible',
                   'availability', 'constraints', 'comments',
                   'regulations_flag', 'public_experiment')
        fields = [
            'irradiation_type',
            'number_samples',
            'category',
        ]

    def clean_number_samples(self):
        """Validates number samples."""
        value = self.cleaned_data['number_samples']
        result = clean_number_in_range(value, int, [0])

        return result


class ExperimentForm3(forms.ModelForm):
    """
    Third page of experiment submission form.

    Used for submitting/updating/cloning an experiment.
    """
    def __init__(self, *args, **kwargs):
        super(ExperimentForm3, self).__init__(*args, **kwargs)
        self.use_required_attribute = False
        self.fields['comments'].required = False
        self.fields['comments'].help_text = '<p>Any additional '\
        'comment or request related to the described irradiation '\
        'experiment.</p>'
        self.fields['public_experiment'].required = False
        self.fields['public_experiment'].label = mark_safe(
            'Would you like to make your experiment details '\
            'public to other IRRAD users?<br> This will allow '\
            'you to view other users\' experiments, too.'
        )
        self.fields['public_experiment'].help_text = '<p>By accepting '\
            'this field, the experiment details will be visible to other '\
            'IDM users through the <a target="_blank" href="' + \
            reverse('samples_manager:experiments_shared_list') + '">SHARED '\
            'EXPERIMENTS</a> page and the users will be allowed to view '\
            'other shared experiments, as well.</p>'
        self.fields['regulations_flag'].required = True
        self.fields['regulations_flag'].label = 'Please, accept terms and '\
            'conditions'
        self.fields['regulations_flag'].help_text = '<p>Acknowledgement of '\
            'the terms and conditions of IDM and irradiation experiment '\
            'operation in the IRRAD facility. For more information click '\
            '<a target="_blank" href="' + \
            reverse('samples_manager:regulations') + '">here</a>.</p>'

    class Meta:
        """Form metadata."""
        model = Experiment
        exclude = ('title', 'description', 'responsible', 'cern_experiment'
                   'availability', 'constraints', 'category', 'number_samples',
                   'irradiation_type')
        fields = ['comments', 'regulations_flag', 'public_experiment']
        widgets = {
            'comments':
                forms.Textarea(
                    attrs={
                        'placeholder': 'Any additional comments?',
                        'rows': 4
                    }),
        }


class ExperimentStatus(forms.Form):
    """
    Experiment status form.

    Used for updating experiment's status.
    """
    status = forms.ChoiceField(label='Choose status:', choices=EXPERIMENT_STATUS)

    def __init__(self, *args, **kwargs):
        super(ExperimentStatus, self).__init__(*args, **kwargs)
        self.use_required_attribute = False


class ExperimentVisibility(forms.Form):
    """
    Experiment visibility form.

    Used for updating experiment's visibility.
    """
    visibility = forms.ChoiceField(label='Choose visibility:', 
        choices=EXPERIMENT_VISIBILITY)

    def __init__(self, *args, **kwargs):
        super(ExperimentVisibility, self).__init__(*args, **kwargs)
        self.use_required_attribute = False
        self.fields['visibility'].help_text='<p>Public experiment\'s '\
        'details will be visible to other IDM users through the <a '\
        'target="_blank" href="' + \
        reverse('samples_manager:experiments_shared_list') + '">SHARED '\
        'EXPERIMENTS</a> page and the users will be allowed to view '\
        'other shared experiments, as well.</p>'


class ExperimentComment(forms.ModelForm):
    """
    Experiment comment form.

    Used for updating experiment's comment section.
    """
    def __init__(self, *args, **kwargs):
        super(ExperimentComment, self).__init__(*args, **kwargs)
        self.use_required_attribute = False
        self.fields['comments'].required = False
        self.fields[
            'comments'].label = 'Add additional comments(e.g. link to publications):'

    class Meta:
        """Form metadata."""
        model = Experiment
        fields = ['comments']
        widgets = {
            'comments':forms.Textarea(
                attrs={
                    'placeholder': 'Add any link to publication',
                    'rows': 4
                }),
        }


class BoxForm(ModelForm):
    """Box management form in admin view."""
    def __init__(self, *args, **kwargs):
        super(BoxForm, self).__init__(*args, **kwargs)
        self.use_required_attribute = False
        self.fields['box_id'].label = 'Box ID'
        self.fields['box_id'].help_text = '<p>Unique identifier '\
            'generated in IDM.</p>'
        self.fields['responsible'].label = 'Responsible'
        self.fields['responsible'].help_text = '<p>Responsible of '\
            'the specific box.</p>'
        self.fields['description'].label = 'Description'
        self.fields['description'].required = False
        self.fields['description'].help_text = '<p>Description of '\
            'the box.</p>'
        self.fields['current_location'] = RemoteChoiceField()
        self.fields['current_location'].label = 'Current Location'
        self.fields['current_location'].help_text = '<p>Building '\
            'and room where the box is located.</p>'
        self.fields['length'] = forms.CharField(max_length=12)
        self.fields['length'].label = 'Length (cm)'
        self.fields['length'].help_text = '<p>Length of the box.</p>'
        self.fields['height'] = forms.CharField(max_length=12)
        self.fields['height'].label = 'Height (cm)'
        self.fields['height'].help_text = '<p>Height of the box.</p>'
        self.fields['width'] = forms.CharField(max_length=12)
        self.fields['width'].label = 'Width (cm)'
        self.fields['width'].help_text = '<p>Width of the box.</p>'
        self.fields['weight'] = forms.CharField(max_length=12)
        self.fields['weight'].label = 'Weight (kg)'
        self.fields['weight'].help_text = '<p>Weight of the box.</p>'

    class Meta:
        """Form metadata."""
        model = Box
        fields = ['box_id', 'description', 'responsible', 'current_location', 
            'length', 'height', 'width', 'weight']
        exclude = (
            'created_at',
            'updated_at',
            'created_by',
            'updated_by',
            'last_location'
        )

    def clean_box_id(self):
        """Validates field box_id."""
        box_id = self.cleaned_data['box_id']

        is_valid = (get_equipment_type(box_id) == 'box')

        if not is_valid:
            raise forms.ValidationError('Please enter id following the '\
                'correct format "BOX-XXXXXX".')
        
        return box_id

    def clean_length(self):
        """Validates length."""
        value = self.cleaned_data['length']
        result = clean_number_in_range(value, float, [0])

        return result

    def clean_height(self):
        """Validates height."""
        value = self.cleaned_data['height']
        result = clean_number_in_range(value, float, [0])

        return result

    def clean_width(self):
        """Validates width."""
        value = self.cleaned_data['width']
        result = clean_number_in_range(value, float, [0])

        return result

    def clean_weight(self):
        """Validates weight."""
        value = self.cleaned_data['weight']
        result = clean_number_in_range(value, float, [0])

        return result

class UserForm(ModelForm):
    """User management form in admin view."""
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.use_required_attribute = False
        self.fields['name'].label = 'First Name'
        self.fields['surname'].label = 'Last Name'
        self.fields['email'].label = 'Email Address'
        self.fields['telephone'].required = False
        self.fields['telephone'].label = 'Telephone Number'
        self.fields['role'].label = 'Role'

    class Meta:
        """Form metadata."""
        model = User
        fields = ['name', 'surname', 'email', 'telephone', 'role']
        exclude = (
            'db_telephone',
            'department',
            'home_institute',
            'last_login',
        )

class AddUserToExperimentForm(forms.Form):
    """User management form in admin view."""
    email = forms.CharField(label='Email Address', max_length=100)

    def __init__(self, *args, **kwargs):
        if 'experiment' in kwargs:
            # cache the user object you pass in
            self.experiment = kwargs.pop('experiment')
        super(AddUserToExperimentForm, self).__init__(*args, **kwargs)
        self.use_required_attribute = False

    def clean_email(self):
        """Validates form."""
        user_email = self.cleaned_data['email']
        user = User.objects.filter(email=user_email)
        not_exists = (not user.exists())
        is_responsible = (user_email == self.experiment.responsible.email)

        if not_exists:
            raise ValidationError(
                _('User doesn\'t exist'),
                code='invalid',
            )

        if is_responsible:
            raise ValidationError(
                _('User can\'t be experiment responsible'),
                code='invalid',
            )

        return user_email


class ReqFluenceFormSet(forms.BaseInlineFormSet):
    """
    Form set used to record fluences of experiment.

    This form set is used inside the experiment submission form.
    """
    def __init__(self, *args, **kwargs):
        super(ReqFluenceFormSet, self).__init__(*args, **kwargs)
        self.use_required_attribute = False
        for form in self.forms:
            form.empty_permitted = False


class ReqFluenceForm(ModelForm):
    """
    Experiment fluence form.

    This form is part of the ReqFluenceFormSet.
    """
    def __init__(self, *args, **kwargs):
        super(ReqFluenceForm, self).__init__(*args, **kwargs)
        self.use_required_attribute = False
        self.fields['req_fluence'].label = mark_safe(
            'Requested fluence (protons/cm²)')
        self.fields['req_fluence'].required = True
        self.fields['req_fluence'].help_text = '<p>Requested '\
            'values of fluences for the different samples. '\
            'The correspondence of the fluences with the '\
            'samples will be done when the experiment is '\
            'validated.</p><p>If the surface area of samples is '\
            'large, then use the target fluence, not the '\
            'calculated fluence.</p><p>For information on '\
            'fluence conversion, click <a target=\'_blank\ href=\'' \
            + reverse('samples_manager:fluence_conversion') + \
            '\'>here</a>.</p>'

    class Meta:
        """Form metadata."""
        model = ReqFluence
        fields = ['id', 'req_fluence']
        widgets = {
            'req_fluence':forms.TextInput(
                attrs={
                    'placeholder': 'e.g. 1.234E+15'
                }),
        }
        exclude = ('experiment', )

    def clean_req_fluence(self):
        """Validates requested fluence."""
        value = self.cleaned_data['req_fluence']
        result = clean_number_in_range(value, float, [0])
        result = num_notation(result, '4e')
        return result


class MaterialFormSet(forms.BaseInlineFormSet):
    """
    Form set used to record materials of experiment.

    This form set is used inside the experiment submission form.
    """
    def __init__(self, *args, **kwargs):
        super(MaterialFormSet, self).__init__(*args, **kwargs)
        self.use_required_attribute = False
        for form in self.forms:
            form.empty_permitted = False


class MaterialForm(ModelForm):
    """
    Experiment material form.

    This form is part of the MaterialFormSet.
    """
    def __init__(self, *args, **kwargs):
        super(MaterialForm, self).__init__(*args, **kwargs)
        self.use_required_attribute = False
        self.fields['material'].label = mark_safe('Types of sample')
        self.fields['material'].required = True
        self.fields['material'].help_text = '<p>Material type of the '\
            'samples E.g. silicon detector, fiber optics, etc. </p>'

    class Meta:
        """Form metadata."""
        model = Material
        fields = [
            'id',
            'material',
        ]
        widgets = {
            'material': forms.TextInput(
                attrs={
                    'placeholder': 'e.g. Silicon'
                })
        }
        exclude = ('experiment', )


class PassiveStandardCategoryForm(ModelForm):
    """
    Form for Passive Standard Categories experiments. 

    This form set is used inside the experiment submission form.
    """
    def __init__(self, *args, **kwargs):
        super(PassiveStandardCategoryForm, self).__init__(*args, **kwargs)
        self.use_required_attribute = False
        self.fields['irradiation_area_5x5'] = IrradiationCheckboxField()
        self.fields['irradiation_area_5x5'].label = '5x5 mm²'
        self.fields['irradiation_area_10x10'] = IrradiationCheckboxField()
        self.fields['irradiation_area_10x10'].label = '10x10 mm²'
        self.fields['irradiation_area_20x20'] = IrradiationCheckboxField()
        self.fields['irradiation_area_20x20'].label = '20x20 mm²'
        
    class Meta:
        """Form metadata."""
        model = PassiveStandardCategory
        fields = [
            'id', 'irradiation_area_5x5', 'irradiation_area_10x10',
            'irradiation_area_20x20'
        ]
        exclude = ('experiment', )

    def clean(self):
        """Checks if an area has been selected.

        Raises:
            forms.ValidationError: Error raised if user doesn't select 
                an area."""
        irradiation_areas = [
            self.cleaned_data['irradiation_area_5x5'],
            self.cleaned_data['irradiation_area_10x10'],
            self.cleaned_data['irradiation_area_20x20']
            ]
        for i in range(0, len(irradiation_areas)):
            if(irradiation_areas[i]):
                return
        raise ValidationError(
            _('More than one area selected.'),
            code='invalid',
            )


class PassiveCustomCategoryForm(ModelForm):
    """
    Form for Passive Custom Categories experiments. 

    This form set is used inside the experiment submission form.
    """
    def __init__(self, *args, **kwargs):
        super(PassiveCustomCategoryForm, self).__init__(*args, **kwargs)
        self.use_required_attribute = False
        self.fields['passive_category_type'] = forms.ChoiceField(
            choices=ACTIVE_OPTIONS)
        self.fields['passive_category_type'].label = 'Type'
        self.fields['passive_category_type'].help_text = '<p> Cold box '\
            'irradiation (-25°C): samples get irradiated inside a cold box '\
            'with temperature down to (-25°C).</p><p>Cryostat (< 5 K): '\
            'samples get irradiated inside a cryostat with temperature less '\
            'than 5 K.</p><p>Room temperature (~ 20 °C): samples get in room '\
            'temperature (~ 20 °C).</p>'
        self.fields['passive_irradiation_area'].label = 'Irradiation area'
        self.fields['passive_irradiation_area'].help_text = '<p>The area of '\
            'the samples that is going to be irradiated.</p>'
        self.fields['passive_modus_operandi'].label = 'Modus operandi'
        self.fields['passive_modus_operandi'].help_text = '<p>Details about '\
            'the way of operation.</p>'

    class Meta:
        """Form metadata."""
        model = PassiveCustomCategory
        fields = [
            'id', 'passive_category_type', 'passive_irradiation_area',
            'passive_modus_operandi'
        ]
        widgets = {
            'passive_modus_operandi':forms.Textarea(
                attrs={
                    'placeholder': 'please, provide more details',
                    'rows': 3
                }),
            'passive_irradiation_area':forms.TextInput(
                attrs={
                    'placeholder': 'e.g. 25x25 mm²'
                }),
        }
        exclude = ('experiment', )


class ActiveCategoryForm(ModelForm):
    """
    Form for Active Categories experiments. 

    This form set is used inside the experiment submission form.
    """
    def __init__(self, *args, **kwargs):
        super(ActiveCategoryForm, self).__init__(*args, **kwargs)
        self.use_required_attribute = False
        self.fields['active_category_type'] = forms.ChoiceField(
            choices=ACTIVE_OPTIONS)
        self.fields['active_category_type'].label = 'Type'
        self.fields['active_category_type'].help_text = '<p> Cold box '\
            'irradiation (-25°C): samples get irradiated inside a cold box '\
            'with temperature down to (-25°C).</p><p>Cryostat (< 5 K): '\
            'samples get irradiated inside a cryostat with temperature less '\
            'than 5 K.</p>'
        self.fields['active_irradiation_area'].label = 'Irradiation area'
        self.fields['active_irradiation_area'].help_text = '<p>The area of '\
            'the samples that is going to be irradiated.</p>'
        self.fields['active_modus_operandi'].label = mark_safe(
            'Modus operandi and IRRAD connectivity')
        self.fields['active_modus_operandi'].help_text = '<p>Details about '\
            'the way of operation. For details about IRRAD connectivity '\
            'click <a target="_blank" '\
            'href="placeholder.url.com">here'\
            '</a>.</p>'

    class Meta:
        """Form metadata."""
        model = ActiveCategory
        fields = [
            'id', 'active_category_type', 'active_irradiation_area',
            'active_modus_operandi'
        ]
        widgets = {
            'active_modus_operandi':forms.Textarea(
                attrs={
                    'placeholder':
                        'Please, provide more details and cabling requirements.',
                    'rows': 3
                }),
            'active_irradiation_area':forms.TextInput(
                attrs={
                    'placeholder': 'e.g. 25x25 mm²'
                }),
        }
        exclude = ('experiment', )


class SampleForm1(ModelForm):
    """First page of sample submission form."""
    def __init__(self, *args, **kwargs):
        if 'set_id_readonly' in kwargs:
            self.set_id_readonly = kwargs.pop('set_id_readonly')
        else:
            self.set_id_readonly = False
        if 'experiment_id' in kwargs:
            self.experiment_id = kwargs.pop('experiment_id')
        else:
            self.experiment_id = False
        self.name_validation = \
            kwargs.pop('name_validation', True)
        set_id_label = 'SET ID'
        if not self.set_id_readonly:
            set_id_label +=  ' <span style="color: #F00; '\
                'text-align:justify">Only if your sample has already an '\
                'assigned SET ID (e.g. from previous irradiation)</span>'
        else:
            set_id_label +=  ' <span style="color: #F00; '\
                'text-align:justify"> (read only field)</span>'
        super(SampleForm1, self).__init__(*args, **kwargs)
        self.use_required_attribute = False
        self.fields['set_id'] = forms.CharField(max_length=10)
        self.fields['set_id'].label = mark_safe(set_id_label)
        self.fields['set_id'].widget.attrs['readonly'] = self.set_id_readonly
        self.fields['set_id'].required = False
        self.fields['set_id'].help_text = '<p>A unique CERN IRRAD '\
            'identifier. This field applies only in the case the sample '\
            'has already a SET ID (probably from previous irradiations).</p>'
        self.fields['name'].label = 'Sample name'
        self.fields['name'].help_text = '<p>A unique name for the sample '\
            'that can be easily identified by the user.</p>'
        self.fields['weight'] = forms.CharField(max_length=6)
        self.fields['weight'].label = 'Weight (kg) '
        self.fields['weight'].required = False
        self.fields['weight'].help_text = '<p>Weight of the sample.</p>'
        self.fields['material'] = forms.ModelChoiceField(
            queryset=get_materials(self.experiment_id, True))
        self.fields['material'].label = 'Type of sample'
        self.fields['material'].help_text = '<p>Selection  one  of  the '\
            'type(s)  of samples  that was  declared  in  the experiments '\
            'registration.</p>'

    class Meta:
        """Form metadata."""
        model = Sample
        exclude = ('comments', 'req_fluence', 'category', 'current_location',
                   'storage', 'height', 'width')
        fields = ['material', 'name', 'set_id', 'weight']
        widgets = {
            'set_id': forms.TextInput(
                attrs={
                    'placeholder': 'e.g.SET-001029'
                }),
            'weight':forms.TextInput(
                attrs={
                    'placeholder':
                        'Please, provide the weight if this is above 1 Kg'
                }),
        }

    def clean_name(self):
        """Validates field name."""
        name = self.cleaned_data['name']
        if self.name_validation:
            is_valid = True
            samples = Sample.objects.all()
            for sample in samples:
                if name == sample.name:
                    is_valid = False
                    break

            if not is_valid:
                raise forms.ValidationError('Sample already exists.')
        
        return name

    def clean_weight(self):
        """Validates weight."""
        value = self.cleaned_data['weight']
        result = clean_number_in_range(value, float, [0])

        return result


    def checking_unique_sample(self):
        """Checks if sample is unique."""
        cleaned_data = self.cleaned_data
        name = cleaned_data['name']
        unique = True
        samples = Sample.objects.all()
        names = []
        for sample in samples:
            names.append(sample.name)
        if name in names:
            unique = False
        return unique


class SampleForm2(ModelForm):
    """Second page of sample submission form."""
    def __init__(self, *args, **kwargs):
        self.experiment_id = kwargs.pop('experiment_id')
        super(SampleForm2, self).__init__(*args, **kwargs)
        self.use_required_attribute = False
        self.fields['height'] = forms.CharField(max_length=6)
        self.fields['height'].label = 'Total height layers (mm)'
        self.fields['height'].help_text = '<p>Height of the sample (see '\
        'picture).</p>'
        self.fields['width'] = forms.CharField(max_length=6)
        self.fields['width'].label = 'Total width layers (mm)'
        self.fields['width'].help_text = '<p>Width of the sample (see '\
        'picture).</p>'

    class Meta:
        """Form metadata."""
        model = Sample
        exclude = ('comments', 'req_fluence', 'category', 'current_location',
                   'storage', 'material', 'name', 'set_id', 'weight')
        fields = ['height', 'width']

    def clean_height(self):
        """Validates height."""
        value = self.cleaned_data['height']
        result = clean_number_in_range(value, float, [0])

        return result

    def clean_width(self):
        """Validates width."""
        value = self.cleaned_data['width']
        result = clean_number_in_range(value, float, [0])

        return result

class SampleForm3(ModelForm):
    """Third page of sample submission form."""
    def __init__(self, *args, **kwargs):
        self.experiment_id = kwargs.pop('experiment_id')
        super(SampleForm3, self).__init__(*args, **kwargs)
        self.use_required_attribute = False
        self.fields['req_fluence'] = forms.ModelChoiceField(
            queryset=get_fluences(self.experiment_id, True))
        self.fields['req_fluence'].label = 'Requested fluence'
        self.fields['req_fluence'].help_text = '<p>Selection of the '\
            'requested fluence for the specific sample, that was already '\
            'declared in the experiment registration.</p>'
        self.fields['category'].label = 'Category'
        self.fields['category'] = forms.ChoiceField(
            choices=get_categories(self.experiment_id))
        self.fields['category'].help_text = '<p>Selection of the category '\
            'of the irradiation, based on the categories declared in the '\
            'experiment registration.</p>'
        self.fields['storage'].label = 'Storage'
        self.fields['storage'].help_text = '<p>Requested storage for the '\
            'specific sample, after irradiation.</p>'
        self.fields['current_location'] = RemoteChoiceField()
        self.fields['current_location'].label = 'Current location'
        self.fields['current_location'].help_text = '<p>Current location '\
            '(building, room) of the sample.</p>'
        self.fields['comments'].required = False
        self.fields['comments'].help_text = '<p>Additional comments related '\
            'to the samples.</p>'

    class Meta:
        """Form metadata."""
        model = Sample
        exclude = ('name', 'set_id', 'height', 'width', 'weight', 'material')
        fields = [
            'req_fluence', 'category', 'storage', 'current_location',
            'comments'
        ]
        widgets = {
            'comments':forms.Textarea(
                attrs={
                    'placeholder':
                        'Any additional comments  e.g some emergency phone',
                    'rows': 2
                }),
        }


class MoveSampleToExperimentForm1(forms.Form):
    """Movement of samples from one experiment to another."""
    experiment = forms.ChoiceField(label='Experiment')
    def __init__(self, *args, **kwargs):
        self.logged_user = kwargs.pop('logged_user') \
            if 'logged_user' in kwargs.keys() else None
        self.experiment_old_id = kwargs.pop('experiment_old_id') \
            if 'experiment_old_id' in kwargs.keys() else 1
        super(MoveSampleToExperimentForm1, self).__init__(*args, **kwargs)
        self.use_required_attribute = False
        excluded_ids = [int(self.experiment_old_id)]
        self.fields['experiment'].choices = \
            get_sample_move_choices( \
            self.logged_user, self.experiment_old_id)
        self.fields['experiment'].help_text = '<p>Experiment where sample '\
            'is going to be moved.</p>'

    class Meta:
        """Form metadata."""
        fields = ['experiment']


class MoveSampleToExperimentForm2(forms.Form):
    """Movement of samples from one experiment to another."""
    req_fluence = forms.ChoiceField(label='Requested fluence (protons/cm²)')
    material = forms.ChoiceField(label='Type of sample')
    category = forms.ChoiceField(label='Category')
    def __init__(self, *args, **kwargs):
        self.experiment_new_id = kwargs.pop('experiment_new_id') \
            if 'experiment_new_id' in kwargs.keys() else 1
        super(MoveSampleToExperimentForm2, self).__init__(*args, **kwargs)
        self.use_required_attribute = False
        self.fields['req_fluence'].choices = \
            get_fluences(self.experiment_new_id)
        self.fields['req_fluence'].help_text = '<p>Selection of the '\
            'requested fluence for the specific sample, that was already '\
            'declared in the experiment registration.</p>'
        self.fields['material'].choices = \
            get_materials(self.experiment_new_id)
        self.fields['material'].help_text = '<p>Selection  one  of  the '\
            'type(s)  of samples  that was  declared  in  the experiments '\
            'registration.</p>'
        self.fields['category'].choices = \
            get_categories(self.experiment_new_id)
        self.fields['category'].help_text = '<p>Selection of the category '\
            'of the irradiation, based on the categories declared in the '\
            'experiment registration.</p>'


class LayerFormSet(forms.BaseInlineFormSet):
    """
    Form set used to record layers of samples.

    This form set is used inside the sample submission form.
    """
    def __init__(self, *args, **kwargs):
        super(LayerFormSet, self).__init__(*args, **kwargs)
        self.use_required_attribute = False
        for form in self.forms:
            form.empty_permitted = False


class LayerForm(ModelForm):
    """Sample layer form."""
    def __init__(self, *args, **kwargs):
        super(LayerForm, self).__init__(*args, **kwargs)
        self.use_required_attribute = False
        self.fields['name'].label = 'Layer name'
        self.fields['name'].required = True
        self.fields['length'] = forms.CharField(max_length=28)
        self.fields['length'].label = 'Layer length (mm)'
        self.fields['length'].required = True
        self.fields['compound_type'].label = 'Element/Compound'
        self.fields['compound_type'].widget.attrs = {'class': 'select_element'}
        self.fields['compound_type'].required = True
        
        

    class Meta:
        """Form metadata."""
        model = Layer
        fields = ['id', 'name', 'length', 'compound_type']
        exclude = ('sample',)
        widgets = {
            'name':forms.TextInput(
                attrs={
                    'placeholder': 'e.g. L1'
                }),
            'comments':forms.Textarea(
                attrs={
                    'placeholder': 'Any additional comments?',
                    'rows': 2
                }),
        }

    def clean_length(self):
        """Validates length."""
        value = self.cleaned_data['length']
        result = clean_number_in_range(value, float, [0])

        return result


class DosimeterForm1(ModelForm):
    """First page of dosimeter submission form."""
    def __init__(self, *args, **kwargs):
        super(DosimeterForm1, self).__init__(*args, **kwargs)
        self.use_required_attribute = False
        self.fields['dos_id'] = forms.CharField(max_length=14)
        self.fields['dos_id'].label = 'Dosimeter ID'
        self.fields['dos_id'].help_text = '<p>Unique identifier of the '\
            'dosimeter. If the Dosimeter has already an assigned ID, '\
            'it can be added there, or it will be autogenerated by IDM '\
            'after submission.</p>'
        self.fields['length'] = forms.CharField(max_length=18)
        self.fields['length'].required = False
        self.fields['length'].label = 'Length (mm)'
        self.fields['length'].help_text = '<p>Length of the dosimeter '\
            ' (thickness).</p>'
        self.fields['height'] = forms.CharField(max_length=18)
        self.fields['height'].required = False
        self.fields['height'].label = 'Height (mm)'
        self.fields['height'].help_text = '<p>Height of the dosimeter.</p>'
        self.fields['width'] = forms.CharField(max_length=18)
        self.fields['width'].required = False
        self.fields['width'].label = 'Width (mm)'
        self.fields['width'].help_text = '<p>Width of the dosimeter.</p>'
        self.fields['weight'] = forms.CharField(max_length=18)
        self.fields['weight'].required = False
        self.fields['weight'].label = 'Weight (g)'
        self.fields['weight'].help_text = '<p>Weight of the dosimeter.</p>'
        self.fields['dos_type'].label = 'Dosimeter type'
        self.fields['dos_type'].help_text = '<p>Material type of the '\
            'dosimeter, most common types are Aluminium, Film or Diamond.</p>'
        self.fields['foils_number'].required = False
        self.fields['foils_number'].help_text = '<p>Number of foils the '\
            'dosimeter is composed of.</p>'

    class Meta:
        """Form metadata."""
        model = Dosimeter
        fields = [
            'dos_id',
            'length',
            'height',
            'width',
            'weight',
            'foils_number',
            'dos_type',
        ]
        exclude = ('responsible', 'current_location', 'comments',
                   'parent_dosimeter')
        widgets = {
            'dos_id': forms.TextInput(
                attrs={
                    'placeholder': 'e.g.DOS-002929'
                }),
            'weight':forms.TextInput(
                attrs={
                    'placeholder':
                    'Please, provide weight expecially if it is more than 1 kg'
                }),
        }
    
    def clean_dos_id(self):
        """Validates field dos_id."""
        dos_id = self.cleaned_data['dos_id']

        is_valid = (get_equipment_type(dos_id) == 'dosimeter')

        if not is_valid:
            raise forms.ValidationError('Please enter id following the '\
                'correct format "DOS-XXXXXX" or "DOS-XXXXXX.XXX".')
        
        return dos_id

    def clean_length(self):
        """Validates length."""
        value = self.cleaned_data['length']
        result = clean_number_in_range(value, float, [0])

        return result

    def clean_height(self):
        """Validates height."""
        value = self.cleaned_data['height']
        result = clean_number_in_range(value, float, [0])

        return result

    def clean_width(self):
        """Validates width."""
        value = self.cleaned_data['width']
        result = clean_number_in_range(value, float, [0])

        return result

    def clean_weight(self):
        """Validates weight."""
        value = self.cleaned_data['weight']
        result = clean_number_in_range(value, float, [0])

        return result


class DosimeterForm2(ModelForm):
    """Second page of dosimeter submission form."""
    def __init__(self, *args, **kwargs):
        super(DosimeterForm2, self).__init__(*args, **kwargs)
        self.use_required_attribute = False
        self.fields['comments'].required = False
        self.fields['comments'].help_text = '<p>Additional comments '\
            'for the dosimeter.</p>'
        self.fields['responsible'].empty_label = None
        self.fields['responsible'].help_text = '<p>Contact person '\
            'responsible for the dosimeter.</p>'
        self.fields['current_location'] = RemoteChoiceField()
        self.fields['current_location'].label = 'Current location'
        self.fields['current_location'].help_text = '<p>Current location '\
            '(building, room) of the sample.</p>'
        self.fields['parent_dosimeter'].required = False
        self.fields['parent_dosimeter'].help_text = '<p>If the dosimeter is '\
            'splitted into parts, this field identifies the dosimeter '\
            'they belong to.</p>'

    class Meta:
        """Form metadata."""
        model = Dosimeter
        fields = [
            'responsible', 'current_location', 'parent_dosimeter', 'comments'
        ]
        exclude = ('dos_id', 'length', 'height', 'width', 'weight',
                   'foils_number', 'dos_type')
        widgets = {
            'comments':forms.Textarea(
                attrs={
                    'rows': 3
                }),
        }

class DosimeterGenerateIds(forms.Form):
    """First page of dosimeter submission form."""

    num_ids = forms.CharField(max_length=2)

    def __init__(self, *args, **kwargs):
        super(DosimeterGenerateIds, self).__init__(*args, **kwargs)
        self.use_required_attribute = False
        self.fields['num_ids'].label = 'Number of new dosimeters ids'
    
    def clean_num_ids(self):
        """Validates num_ids."""
        value = self.cleaned_data['num_ids']
        result = clean_number_in_range(value, int, [0, MAX_NUM_GEN_DOS_IDS])

        return result


class GroupIrradiationForm(ModelForm):
    """
    Create an irradiation linking samples and dosimeters.

    This form is located in the samples list view of an experiment.
    """
    def __init__(self, *args, **kwargs):
        super(GroupIrradiationForm, self).__init__(*args, **kwargs)
        self.use_required_attribute = False
        self.fields['dosimeter'].required = True
        self.fields['dosimeter'].empty_label = 'Select dosimeter'
        self.fields['dosimeter'] = forms.ModelChoiceField(
            Dosimeter.objects.filter(dos_id__isnull=False).order_by('dos_id'))
        self.fields['dosimeter'].help_text = '<p>The dosimeter associated '\
            'to this sample for the specific irradiation time interval of '\
            'Date in and Date out.</p>'
        self.fields['irrad_table'] = forms.ChoiceField(choices=IRRAD_TABLES)
        self.fields['irrad_table'].required = True
        self.fields['irrad_table'].help_text = '<p>The IRRAD Table or '\
            'shuttle where the sample and dosimeter will be placed.</p>'
        self.fields['table_position'] = forms.ChoiceField(
            choices=TABLE_POSITIONS)
        self.fields['table_position'].required = False
        self.fields['table_position'].help_text = '<p>The standard IRRAD '\
            'holders have 3 positions Left, Center or Right. If it is not '\
            'a standard placeholder, Center should be the default position.'\
            '</p>'
        self.fields['is_scan'] = forms.ChoiceField(
            choices=BOOLEAN)
        self.fields['is_scan'].label = 'Is this irradiation a scan?'
        self.fields['is_scan'].help_text = '<p>If the irradiation is '\
            'scanned or a regular radiation.</p>'

    class Meta:
        """Form metadata."""
        model = Irradiation
        fields = ['dosimeter', 'irrad_table', 'table_position', 'is_scan']
        exclude = ('sample', 'date_in', 'date_out', 'estimated_fluence',
                   'sec', 'fluence_error', 'dos_position')

    def clean_is_scan(self):
        """Validates is scan."""
        value = self.cleaned_data['is_scan']
        result = (value == 'True')

        return result


class IrradiationForm(ModelForm):
    """
    Creates an irradiation.

    Located in irradiation list view. Accessed by admins.
    """
    def __init__(self, *args, **kwargs):
        super(IrradiationForm, self).__init__(*args, **kwargs)
        self.use_required_attribute = False
        self.fields['sample'] = SampleIrradiationChoiceField(
            Sample.objects.filter(set_id__isnull=False).exclude(set_id__exact=''))
        self.fields['sample'].required = False
        self.fields['sample'].label = 'Sample'
        self.fields['sample'].help_text = '<p>Selection of the sample '\
            'to be irradiated.</p>'
        self.fields['dosimeter'] = forms.ModelChoiceField(
            Dosimeter.objects.filter(dos_id__isnull=False)
            .order_by('dos_id'))
        self.fields['dosimeter'].label = 'Dosimeter'
        self.fields['dosimeter'].empty_label = 'Select dosimeter'
        self.fields['dosimeter'].help_text = '<p>The dosimeter associated '\
            'to this sample for the specific irradiation time interval of '\
            'Date in and Date out.</p>'
        self.fields['previous_irradiation'] = IDMChoiceField(choices=
            get_previous_irradiation_choices())
        self.fields['previous_irradiation'].required = False
        self.fields['previous_irradiation'].label = 'Previous Irradiation'
        self.fields['previous_irradiation'].help_text = '<p>Parent irradiation '\
            'from which this one will build on top.</p>'
        self.fields['irrad_table'] = forms.ChoiceField(choices=IRRAD_TABLES)
        self.fields['irrad_table'].help_text = '<p>The IRRAD Table or '\
            'shuttle where the sample and dosimeter will be placed.</p>'
        self.fields['table_position'] = IDMChoiceField(
            choices=TABLE_POSITIONS)
        self.fields['table_position'].required = False
        self.fields['table_position'].help_text = '<p>The standard IRRAD '\
            'holders have 3 positions Left, Center or Right. If it is not '\
            'a standard placeholder, Center should be the default position.'\
            '</p>'
        self.fields['measured_fluence'].required = False
        self.fields['measured_fluence'].label = \
            'Masured fluence'
        self.fields['measured_fluence'].help_text = '<p>Fluence value '\
            'measured after dosimetry.</p>'
        self.fields['date_in'] = TimezoneDateTimeField(
            input_formats=['%Y/%m/%d %H:%M'], tz=get_cern_timezone())
        self.fields['date_in'].required = False
        self.fields['date_in'].help_text = '<p>The date and time the '\
            'specific pair of sample and dosimeter were inserted in '\
            'beam.</p>'
        self.fields['date_out'] = TimezoneDateTimeField(
            input_formats=['%Y/%m/%d %H:%M'], tz=get_cern_timezone())
        self.fields['date_out'].required = False
        self.fields['date_out'].help_text = '<p>The date and time the '\
            'specific pair of sample and dosimeter were removed from beam.</p>'
        self.fields['dos_position'] = forms.CharField(max_length=1,
            widget=forms.TextInput(attrs={'placeholder': 'e.g. 1'}))
        self.fields['dos_position'].required = False
        self.fields['dos_position'].label = \
            'Dosimeter Position * (e.g., Front = 1, Middle = 2, Back = 3)'
        self.fields['dos_position'].help_text = '<p>The position of the '\
            'dosimeter with reference to the sample.</p>'
        self.fields['is_scan'] = forms.ChoiceField(
            choices=BOOLEAN)
        self.fields['is_scan'].label = 'Is this irradiation a scan?'
        self.fields['is_scan'].help_text = '<p>If the irradiation is '\
            'scanned or a regular radiation.</p>'
        self.fields['comments'].required = False
        self.fields['comments'].help_text = '<p>Additional comments about '\
            'the specific irradiation.</p>'

    class Meta:
        """Form metadata."""
        model = Irradiation
        fields = [
            'sample',
            'dosimeter',
            'previous_irradiation',
            'dos_position',
            'irrad_table',
            'table_position',
            'measured_fluence',
            'date_in',
            'date_out',
            'is_scan',
            'comments',
        ]
        exclude = ('sec', 'estimated_fluence', 'fluence_error', 'date_first_sec', 'date_last_sec')
        widgets = {
            'date_in':forms.DateTimeInput(
                format='%Y/%m/%d %H:%M',
                attrs={'placeholder': 'Date when samples were in beam'}),
            'date_out':forms.DateTimeInput(
                format='%Y/%m/%d %H:%M',
                attrs={'placeholder': 'Date when samples came out of beam'}),
            'dos_position': forms.TextInput(
                attrs={'placeholder': 'e.g. 1'}),
            'measured_fluence':forms.TextInput(
                attrs={
                    'placeholder': 'e.g. 1.234E+15'
                }),
        }

    def clean(self):
        """Additional validation conditions."""
        cleaned_data = super().clean()
        sample = cleaned_data.get("sample")
        dosimeter = cleaned_data.get("dosimeter")
        date_in = cleaned_data.get("date_in")
        date_out = cleaned_data.get("date_out")
        current_date = get_aware_cern_datetime()
        exists_conflict = False
        # Check if not completed irradiations exist for the same irradiation period.
        if date_in and date_out:
            correct_order = (date_in < date_out)
            if correct_order:
                in_future = (datetime_as_cern_timezone(date_in) > current_date or \
                    datetime_as_cern_timezone(date_out) > current_date)
                if not in_future:
                    irradiations = Irradiation.objects.filter(~Q(status='Completed') & 
                        Q(sample=sample) & Q(dosimeter=dosimeter) & 
                        ((Q(date_in__lte=date_in) & Q(date_out__gte=date_in)) | 
                        (Q(date_in__lte=date_out) & Q(date_out__gte=date_out))))
                    multiple_conflicts = (len(irradiations) > 1)
                    single_conflict = (len(irradiations) == 1)
                    if multiple_conflicts:
                        exists_conflict = True
                    elif single_conflict and self.instance:
                        exists_conflict = (not (irradiations[0].id \
                            == self.instance.id))
                else:
                    raise ValidationError(
                        "Dates can't be in the future."
                    )
            else:
                raise ValidationError(
                    "Date in must be before date out."
                )
        elif date_in and not date_out:
            in_future = (datetime_as_cern_timezone(date_in) > current_date)
            if not in_future:
                irradiations = Irradiation.objects.filter(~Q(status='Completed') & 
                    Q(sample=sample) & Q(dosimeter=dosimeter) & 
                    Q(date_in__lte=date_in) & Q(date_out__gte=date_in))
                multiple_conflicts = (len(irradiations) > 1)
                single_conflict = (len(irradiations) == 1)
                if multiple_conflicts:
                    exists_conflict = True
                elif single_conflict and self.instance:
                    exists_conflict = (not (irradiations[0].id \
                        == self.instance.id))
            else:
                raise ValidationError(
                    "Dates can't be in the future."
                )
        elif not date_in and date_out:
            raise ValidationError(
                "If date out is defined, then date in also needs to be defined."
            )
        if exists_conflict:
            raise ValidationError(
                "This irradiation conflicts with an existing irradiation."
            )

    def clean_previous_irradiation(self):
        result = self.cleaned_data['previous_irradiation']
        is_none = (result == 'None' or result == '')
        if is_none:
            result = None

        return result

    def clean_sec(self):
        """Validates sec."""
        value = self.cleaned_data['sec']
        result = clean_number_in_range(value, int, [0])

        return result

    def clean_fluence_error(self):
        """Validates fluence error."""
        value = self.cleaned_data['fluence_error']
        result = clean_number_in_range(value, float, [0])

        return result

    def clean_measured_fluence(self):
        """Validates measured fluence."""
        value = self.cleaned_data['measured_fluence']
        result = clean_number_in_range(value, float, [0])

        return result

    def clean_dos_position(self):
        """Validates dosimeter position."""
        value = self.cleaned_data['dos_position']
        result = clean_number_in_range(value, int, [0, 3])

        return result

    def clean_is_scan(self):
        """Validates is scan."""
        value = self.cleaned_data['is_scan']
        result = (value == 'True')

        return result


class IrradiationStatus(forms.ModelForm):
    """Irradiation status form. Updates irradiation status."""
    def __init__(self, *args, **kwargs):
        super(IrradiationStatus, self).__init__(*args, **kwargs)
        self.use_required_attribute = False
        self.fields['status'].label = 'Choose status:'
    class Meta:
        """Form metadata."""
        model = Irradiation
        fields = ['status']


class IrradiationInBeamStatus(forms.Form):
    """
    Irradiation in-beam form.

    Used for updating irradiaitons's in-beam state.
    """
    in_beam = forms.ChoiceField(label='Irradiation is in beam?', 
        choices=BOOLEAN)

    def __init__(self, *args, **kwargs):
        super(IrradiationInBeamStatus, self).__init__(*args, **kwargs)
        self.use_required_attribute = False


class FluenceFactorForm(ModelForm):
    """
    Creates a fluence factor.

    Located in fluence factor list view. Accessed by admins.
    """
    def __init__(self, *args, **kwargs):
        super(FluenceFactorForm, self).__init__(*args, **kwargs)
        self.use_required_attribute = False
        self.fields['value'].label = 'Factor Value'
        self.fields['value'].help_text = '<p>Value of factor to be used '\
            'for the specified irradiation table and dosimeter dimension.</p>'
        self.fields['irrad_table'] = forms.ChoiceField(choices=IRRAD_TABLES)
        self.fields['irrad_table'].help_text = '<p>The IRRAD Table or '\
            'shuttle where the sample and dosimeter will be placed.</p>'
        self.fields['dosimeter_height'].label = 'Dosimeter Height (mm)'
        self.fields['dosimeter_height'].help_text = '<p>Height of the dosimeter.</p>'
        self.fields['dosimeter_width'].label = 'Dosimeter Width (mm)'
        self.fields['dosimeter_width'].help_text = '<p>Width of the dosimeter.</p>'
        self.fields['status'] = forms.ChoiceField(\
            choices=FLUENCE_FACTOR_STATUS)
        self.fields['status'].help_text = '<p>Either active or inactive. '\
            'Active factors are the ones used in calculating irradiation '\
            'fluence estimations.</p>'
        self.fields['nuclide'] = forms.ChoiceField(\
            choices=FLUENCE_FACTOR_NUCLIDE)
        self.fields['nuclide'].help_text = '<p>Either 22 or 24. Used for '\
            'information purposes.</p>'
        

    class Meta:
        """Form metadata."""
        model = FluenceFactor
        fields = [
            'value',
            'irrad_table',
            'dosimeter_height',
            'dosimeter_width',
            'status',
            'nuclide'
        ]
        widgets = {
            'value':NumberTextWidget(
                attrs={
                    'placeholder': 'e.g. 1.234E+15'
                }),
            'dosimeter_height':forms.TextInput(
                attrs={
                    'placeholder': 'e.g. 0.001'
                }),
            'dosimeter_width':forms.TextInput(
                attrs={
                    'placeholder': 'e.g. 0.001'
                }),
        }

    def clean_value(self):
        """Validates value."""
        value = self.cleaned_data['value']
        result = clean_number_in_range(value, float, [0])

        result = str(result)

        return result

    def clean_dosimeter_height(self):
        """Validates dosimeter height."""
        value = self.cleaned_data['dosimeter_height']
        result = clean_number_in_range(value, float, [0])

        result = str(result)

        return result

    def clean_dosimeter_width(self):
        """Validates dosimeter width."""
        value = self.cleaned_data['dosimeter_width']
        result = clean_number_in_range(value, float, [0])

        return result


class CompoundElementFormSet(forms.BaseInlineFormSet):
    """
    Form set used to record elements in sample layer compounds.

    This form set is used inside the sample submission form.
    """
    def __init__(self, *args, **kwargs):
        super(CompoundElementFormSet, self).__init__(*args, **kwargs)
        self.use_required_attribute = False
        for form in self.forms:
            form.empty_permitted = False

    def clean(self):
        """Checks if an element has been defined. If not a error is raised."""
        if self.has_changed() == False:
            raise forms.ValidationError('Please add at least one item.')


class CompoundElementForm(ModelForm):
    """
    Element form.

    This form is part of the CompoundElementFormSet.
    """
    def __init__(self, *args, **kwargs):
        super(CompoundElementForm, self).__init__(*args, **kwargs)
        self.use_required_attribute = False
        self.fields['element_type'].label = 'Element'
        self.fields['element_type'].required = True
        self.fields['element_type'].help_text = '<p>Element that the '\
            'compound is composed of.</p>'
        self.fields['percentage'] = forms.CharField(max_length=3,
            widget=forms.TextInput(attrs={'placeholder': 'e.g. 50'}))
        self.fields['percentage'].label = 'Weight fraction (%)'
        self.fields['percentage'].required = True
        self.fields['percentage'].help_text = '<p>Percentage of the '\
            'specified element in the declared compound.</p>'

    class Meta:
        """Form metadata."""
        model = CompoundElement
        fields = [
            'id',
            'element_type',
            'percentage',
        ]
        widgets = {}
        exclude = ('compound', )

    def clean_percentage(self):
        """Validates percentage.

        Raises:
            forms.ValidationError: Validation error."""
        value = self.cleaned_data['percentage']
        result = clean_number_in_range(value, float, [0, 100])

        return result


class CompoundForm(ModelForm):
    """
    Compound form.

    This form is part of the CompoundFormSet.
    """
    def __init__(self, *args, **kwargs):
        super(CompoundForm, self).__init__(*args, **kwargs)
        self.use_required_attribute = False
        self.fields['name'].help_text = '<p>Name of the compound to be '\
            'created.</p>'
        self.fields['density'] = forms.CharField(max_length=16,
            widget=forms.TextInput(attrs={'placeholder': 'e.g. 1.5e-4'}))
        self.fields['density'].label = 'Density (g/cm³)'
        self.fields['density'].help_text = '<p>Density of the compound.</p>'

    class Meta:
        """Form metadata."""
        model = Compound
        fields = ['id', 'name', 'density']
        widgets = {}
        exclude = ('compound', )

    def clean_density(self):
        """Validates density."""
        value = self.cleaned_data['density']
        result = clean_number_in_range(value, float, [0])
        result = str(result)
        return result


class SampleDosimeterBoxAssociationForm(forms.Form):
    """
    Association between boxes, samples and dosiemters.
    Sample view and Dosimeter view.
    """
    box_id = forms.ChoiceField(label='Box ID', choices=get_box_id_choices())

    def clean_box_id(self):
        """Validates field box_id."""
        box_id = self.cleaned_data['box_id']

        if box_id != 'None':
            if 'BOX-' not in box_id:
                raise forms.ValidationError('Please enter box id following the correct format "BOX-XXXXXX".')
            try:
                Box.objects.get(box_id=box_id)
            except Box.DoesNotExist:
                raise forms.ValidationError('Box "' + box_id + '" doesn\'t exist.')
        
        return box_id


class BoxItemFormSet(forms.BaseFormSet):
    """Form set for multiple box items."""
    def __init__(self, *args, **kwargs):
        super(BoxItemFormSet, self).__init__(*args, **kwargs)
        self.use_required_attribute = False
        for form in self.forms:
            form.empty_permitted = False

    def clean(self):
        """Checks validity of all forms."""
        for form in self.forms:
            if not form.is_valid():
                raise forms.ValidationError('Invalid form.')


class BoxItemForm(forms.Form):
    """For to add item to box as item. It can be a dosiemter or sample."""
    box_item_id = forms.CharField(label='Item ID', max_length=100, 
        widget=forms.TextInput(attrs={'placeholder': 'e.g.DOS-002929'})) 
    box_item_id.help_text = '<p>ID of item to add to box.</p>'

    def clean_box_item_id(self):
        """Validates field box_item_id."""
        box_item_id = self.cleaned_data['box_item_id']

        is_dosimeter = (get_equipment_type(box_item_id) == 'dosimeter')
        is_sample = (get_equipment_type(box_item_id) == 'sample')

        if is_dosimeter:
            try:
                Dosimeter.objects.get(dos_id=box_item_id)
            except Dosimeter.DoesNotExist:
                raise forms.ValidationError('Item "' + \
                    box_item_id + '" doesn\'t exist.')
        elif is_sample:
            try:
                Sample.objects.get(set_id=box_item_id)
            except Sample.DoesNotExist:
                raise forms.ValidationError('Item "' + \
                    box_item_id + '" doesn\'t exist.')
        else:
            raise forms.ValidationError('Please enter id following the '\
                'correct format "DOS-XXXXXX"/"SET-XXXXXX".')
        
        return box_item_id
            

class PrintLabelForm(forms.Form):
    """Print equipment label form."""
    printer = forms.ChoiceField(label='Printer', choices=PRINTERS)
    template = forms.ChoiceField(label='Template', choices=PRINTER_TEMPLATES)
    num_copies = forms.CharField(label='Number of copies',  max_length=2)

    def __init__(self, *args, **kwargs):
        super(PrintLabelForm, self).__init__(*args, **kwargs)
        self.use_required_attribute = False

    class Meta:
        """Form metadata."""
        fields = ['printer', 'template', 'num_copies']

    def clean_num_copies(self):
        """Validates number of copies to print."""
        value = self.cleaned_data['num_copies']
        result = clean_number_in_range(value, int, [0, MAX_PRINT_COPIES])
        
        return result