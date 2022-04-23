"""Django app custom fields"""
from django import forms
from .utilities import *
from django.urls import reverse
from .templatetags.custom_filters import *

SAMPLE_TRUNCATED_LENGTH = 30


class NumberTextWidget(forms.TextInput):
    """NumberTextWidget. Custom form datalist widget."""
    def render(self, name, value, attrs=None, renderer=None):
        value = num_notation(value, '3e')
        text_html = super(NumberTextWidget, self)\
            .render(name, value, attrs=attrs)
        return text_html


class ListTextWidget(forms.TextInput):
    """ListTextWidget. Custom form datalist widget."""
    def __init__(self, data_list, name, *args, **kwargs):
        super(ListTextWidget, self).__init__(*args, **kwargs)
        self._name = name
        self._list = data_list
        self.attrs.update({'list': 'list__%s' % self._name})

    def render(self, name, value, attrs=None, renderer=None):
        """Renders field."""
        text_html = super(ListTextWidget, self)\
            .render(name, value, attrs=attrs)
        data_list = '<datalist id="list__%s">' % self._name
        for item in self._list:
            data_list += '<option value="%s">' % item
        data_list += '</datalist>'

        return (text_html + data_list)


class IDMChoiceField(forms.ChoiceField):
    """IDMChoiceField. Choice filed with a clear option."""
    def __init__(self, *args, **kwargs):
        super(IDMChoiceField, self).__init__(*args, **kwargs)
        if 'choices' in kwargs:
            choices = [('', '--------'), ('clear_input', '--------')] + list(self.choices)
            self._set_choices(choices)


class IDMModelChoiceField(forms.ModelChoiceField):
    """IDMModelChoiceField. Model choice filed with a clear option."""
    def __init__(self, *args, **kwargs):
        super(IDMModelChoiceField, self).__init__(*args, **kwargs)
        choices = [('', '--------'), ('clear_input', '--------')] + list(self.choices)
        self._set_choices(choices)


class RemoteChoiceField(forms.ChoiceField):
    """RemoteChoiceField. Custom form remote search choice field."""
    def __init__(self, *args, **kwargs):
        kwargs['choices'] = ()
        super(RemoteChoiceField, self).__init__(*args, **kwargs)
        self.widget = RemoteChoiceWidget()

    def validate(self, value):
        """Validate that the input is in self.choices."""
        self.choices = get_locations_choices()
        super().validate(value)
        self.choices = ()


class RemoteChoiceWidget(forms.Select):
    """Custom widget for RemoteChoiceField."""
    def __init__(self, *args, **kwargs):
        super(RemoteChoiceWidget, self).__init__(*args, **kwargs)
        self.attrs['class'] = 'search-remote'
        self.attrs['search-remote-url'] = reverse('samples_manager:get_locations')

    def render(self, name, value, attrs=None, renderer=None):
        """Modified widget rendering function."""
        text_html = super(RemoteChoiceWidget, self).render(name,
            value, attrs=attrs, renderer=renderer)
        index = text_html.find('\n')
        # Modification needed for field to load populated.
        result = text_html[:index] + '<option value="' + str(value) + \
            '" selected>' + str(value) + '</option>' + text_html[index:]
        return result


class IrradiationCheckboxField(forms.BooleanField):
    """
    BooleanField. Custom form field for irradiation
    area checkboxes. 
    """
    def __init__(self, *args, **kwargs):
        super(IrradiationCheckboxField, self).__init__(*args, **kwargs)
        self.parent_class = 'seven wide'
        self.required = False


class SampleIrradiationChoiceField(IDMModelChoiceField):
    """
    Choice field used in irradiation forms. It lists samples with
    their set-id.
    """
    def label_from_instance(self, obj):
        return obj.set_id + ' (' + str(obj.name)[:SAMPLE_TRUNCATED_LENGTH] + ')'


class TimezoneDateTimeField(forms.DateTimeField):
    """DateTime field modified to interpret dates with CERN timezone."""
    def __init__(self, *args, **kwargs):
        self.tz = kwargs.pop('tz')
        super(TimezoneDateTimeField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        """Interprets date as CERN timezone."""
        result = super(TimezoneDateTimeField, self).to_python(value)
        if result is not None:
            result = datetime_switch_timezone(result, self.tz)
            result = datetime_as_timezone(result)
        return result
        
