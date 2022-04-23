"""Form testing.
"""
from django.test import TestCase
from samples_manager.forms import *
from django.forms.models import inlineformset_factory

class ExperimentFormsTest(TestCase):
    """Test of Experiment forms."""

    fixtures = [
        'experiment_samples_archive.json',
        'boxes.json',
        'compound_elements.json',
        'compounds.json',
        'dosimeters.json',
        'elements.json',
        'experiment_categories.json',
        'experiments.json',
        'irradiations.json',
        'fluence_factors.json',
        'layers.json',
        'materials.json',
        'occupancies.json',
        'requested_fluences.json',
        'samples.json',
        'users.json'
        ]

    @classmethod
    def setUpTestData(cls):
        """Ran once before all tests are run."""
        cls.user_admin = User.objects.get(email='test-admin@gmail.com')
        cls.user = User.objects.get(email='test-user@gmail.com')
        tz = get_cern_timezone()
        date = get_aware_datetime(tz)
        cls.current_date = date.strftime('%d/%m/%Y')

    def test_correct_experiment_data_form_one(self):
        """Test validity form one."""
        form = ExperimentForm1(data={
            'title': 'e-test',
            'description': 'description',
            'cern_experiment': 'IRRAD',
            'responsible': self.user_admin.id,
            'emergency_phone': '1234',
            'availability': self.current_date,
            'constraints': 'constraints'
        })
        self.assertTrue(form.is_valid())

    def test_no_data_experiment_form_one(self):
        """Test required fields form one."""
        form = ExperimentForm1(data={})
        self.assertTrue(len(form.errors) == 6)

    def test_correct_data_experiment_form_two(self):
        """Test validity form two."""
        form = ExperimentForm2(data={
            'irradiation_type': 'Protons',
            'number_samples': 1,
            'category': 'Passive Standard'
        })
        self.assertTrue(form.is_valid())

    def test_no_data_experiment_form_two(self):
        """Test required fields form two."""
        form = ExperimentForm2(data={})
        self.assertTrue(len(form.errors) == 3)

    def test_correct_data_experiment_form_three(self):
        """Test validity form three."""
        form = ExperimentForm3(data={
            'comments': 'comment',
            'regulations_flag': True,
            'public_experiment': True
        })
        self.assertTrue(form.is_valid())

    def test_no_data_experiment_form_three(self):
        """Test required fields form three."""
        form = ExperimentForm3(data={})
        self.assertTrue(len(form.errors) == 1)

    def test_correct_data_experiment_status_form(self):
        """Test validity experiment status form."""
        form = ExperimentStatus(data={
            'status':'Registered'
        })
        self.assertTrue(form.is_valid())

    def test_no_data_experiment_status_form(self):
        """Test required fields experiment status form."""
        form = ExperimentStatus(data={})
        self.assertTrue(len(form.errors) == 1)

    def test_correct_data_experiment_comment_form(self):
        """Test validity experiment comment form."""
        form = ExperimentComment(data={
            'status':'Test comment.'
        })
        self.assertTrue(form.is_valid())

    def test_no_data_experiment_comment_form(self):
        """Test required fields experiment comment form."""
        form = ExperimentComment(data={})
        self.assertTrue(len(form.errors) == 0)

    def test_correct_data_change_visibility(self):
        """Test validity form experiment visibility."""
        form = ExperimentVisibility(data={
            'visibility': 'Private'
        })
        self.assertTrue(form.is_valid())
    
    def test_no_data_change_visibility(self):
        """Test validity form experiment visibility."""
        form = ExperimentVisibility(data={})
        self.assertTrue(len(form.errors) == 1)


class DosimeterFormsTest(TestCase):
    """Test of Dosimeter forms."""

    fixtures = [
        'experiment_samples_archive.json',
        'boxes.json',
        'compound_elements.json',
        'compounds.json',
        'dosimeters.json',
        'elements.json',
        'experiment_categories.json',
        'experiments.json',
        'irradiations.json',
        'fluence_factors.json',
        'layers.json',
        'materials.json',
        'occupancies.json',
        'requested_fluences.json',
        'samples.json',
        'users.json'
        ]

    @classmethod
    def setUpTestData(cls):
        """Ran once before all tests are run."""
        cls.user = User.objects.get(pk=1)
        cls.dosimeter = Dosimeter.objects.get(pk=1)

    def test_correct_data_dosimeter_form_one(self):
        """Test validity form one."""
        form = DosimeterForm1(data={
            'dos_id': 'DOS-009999',
            'length': '0.001',
            'height': '0.001',
            'width': '0.001',
            'weight': '0.001',
            'foils_number': '1',
            'dos_type': 'Aluminium'
        })
        self.assertTrue(form.is_valid())

    def test_no_data_dosimeter_form_one(self):
        """Test required fields form one."""
        form = DosimeterForm1(data={})
        self.assertTrue(len(form.errors) == 2)

    def test_correct_data_dosimeter_form_two(self):
        """Test validity form two."""
        form = DosimeterForm2(data={
            'responsible': self.user.id,
            'current_location': '14/R-012',
            'parent_dosimeter': self.dosimeter.id,
            'comments': ''
        })
        self.assertTrue(form.is_valid())

    def test_no_data_dosimeter_form_two(self):
        """Test required fields form two."""
        form = DosimeterForm2(data={})
        self.assertTrue(len(form.errors) == 2)


class BoxFormsTest(TestCase):
    """Test of Box forms."""

    fixtures = [
        'experiment_samples_archive.json',
        'boxes.json',
        'compound_elements.json',
        'compounds.json',
        'dosimeters.json',
        'elements.json',
        'experiment_categories.json',
        'experiments.json',
        'irradiations.json',
        'fluence_factors.json',
        'layers.json',
        'materials.json',
        'occupancies.json',
        'requested_fluences.json',
        'samples.json',
        'users.json'
        ]

    @classmethod
    def setUpTestData(cls):
        """Ran once before all tests are run."""
        cls.user = User.objects.get(pk=1)
        cls.box = Box.objects.get(pk=1)

    def test_correct_data_box_form(self):
        """Test validity form one."""
        form = BoxForm(data={
            'box_id': 'BOX-000400',
            'description': 'BOX-test',
            'responsible': self.user.id,
            'current_location': '14/R-012',
            'length': '0.001',
            'height': '0.001',
            'width': '0.001',
            'weight': '0.001'
        })
        self.assertTrue(form.is_valid())

    def test_no_data_box_form(self):
        """Test required fields form one."""
        form = BoxForm(data={})
        self.assertTrue(len(form.errors) == 7)

    def test_correct_data_sample_dosimeter_association_box_form(self):
        """Test validity form one."""
        form = SampleDosimeterBoxAssociationForm(data={
            'box_id': self.box.box_id
        })
        self.assertTrue(form.is_valid())

    def test_no_data_sample_dosimeter_association_box_form(self):
        """Test required fields form one."""
        form = SampleDosimeterBoxAssociationForm(data={})
        self.assertTrue(len(form.errors) == 1)


class SampleFormsTest(TestCase):
    """Test of Sample forms."""

    fixtures = [
        'experiment_samples_archive.json',
        'boxes.json',
        'compound_elements.json',
        'compounds.json',
        'dosimeters.json',
        'elements.json',
        'experiment_categories.json',
        'experiments.json',
        'irradiations.json',
        'fluence_factors.json',
        'layers.json',
        'materials.json',
        'occupancies.json',
        'requested_fluences.json',
        'samples.json',
        'users.json'
        ]

    @classmethod
    def setUpTestData(cls):
        """Ran once before all tests are run."""
        cls.experiment = Experiment.objects.get(pk=1)
        cls.move_experiment = Experiment.objects.get(pk=3)

    def test_correct_data_sample_form_one(self):
        """Test validity form one."""
        form = SampleForm1(data={
            'material': '1',
            'name': 's-test',
            'set_id': '',
            'weight': '0.001'
        }, experiment_id=self.experiment.id)
        self.assertTrue(form.is_valid())

    def test_no_data_sample_form_one(self):
        """Test required fields form one."""
        form = SampleForm1(data={}, experiment_id=self.experiment.id)
        self.assertTrue(len(form.errors) == 2)

    def test_correct_data_sample_form_two(self):
        """Test validity form two."""
        form = SampleForm2(data={
            'height': '0.001',
            'width': '0.001'
        }, experiment_id=self.experiment.id)
        self.assertTrue(form.is_valid())

    def test_no_data_sample_form_two(self):
        """Test required fields form two."""
        form = SampleForm2(data={}, experiment_id=self.experiment.id)
        self.assertTrue(len(form.errors) == 2)

    def test_correct_data_sample_form_three(self):
        """Test validity form two."""
        form = SampleForm3(data={
            'req_fluence': '1',
            'category': 'Passive standard 5x5 mm²',
            'storage': 'Room temperature',
            'current_location': '14/R-012',
            'comments': ''
        }, experiment_id=self.experiment.id)
        self.assertTrue(form.is_valid())

    def test_no_data_sample_form_three(self):
        """Test required fields form two."""
        form = SampleForm3(data={}, experiment_id=self.experiment.id)
        self.assertTrue(len(form.errors) == 4)

    def test_correct_data_move_sample_one(self):
        """Test validity form one."""
        form = MoveSampleToExperimentForm1(data={
            'experiment': str(self.move_experiment.id)
            },
            logged_user=User.objects.get(pk=1), 
            experiment_old_id=self.experiment.id)
        self.assertTrue(form.is_valid())
    
    def test_no_data_move_sample_one(self):
        """Test validity form one."""
        form = MoveSampleToExperimentForm1(data={},
            logged_user=User.objects.get(pk=1),
            experiment_old_id=self.experiment.id)
        self.assertTrue(len(form.errors) == 1)

    def test_correct_data_move_sample_two(self):
        """Test validity form two."""
        form = MoveSampleToExperimentForm2(data={
            'req_fluence': '1',
            'category': 'Passive standard 5x5 mm²',
            'material': '1'
        }, experiment_new_id=self.experiment.id)
        self.assertTrue(form.is_valid())
    
    def test_no_data_move_sample_two(self):
        """Test validity form two."""
        form = MoveSampleToExperimentForm2(data={}, 
            experiment_new_id=self.experiment.id)
        self.assertTrue(len(form.errors) == 3)


class IrradiationFormsTest(TestCase):
    """Test of Irradiation forms."""

    fixtures = [
        'experiment_samples_archive.json',
        'boxes.json',
        'compound_elements.json',
        'compounds.json',
        'dosimeters.json',
        'elements.json',
        'experiment_categories.json',
        'experiments.json',
        'irradiations.json',
        'fluence_factors.json',
        'layers.json',
        'materials.json',
        'occupancies.json',
        'requested_fluences.json',
        'samples.json',
        'users.json'
        ]

    @classmethod
    def setUpTestData(cls):
        """Ran once before all tests are run."""
        cls.dosimeter = Dosimeter.objects.get(pk=1)
        cls.sample = Sample.objects.get(pk=1)
        tz = get_cern_timezone()
        date = get_aware_datetime(tz)
        cls.past_date = get_past_aware_datetime(3).strftime('%Y/%m/%d %H:%M')
        cls.current_date = date.strftime('%Y/%m/%d %H:%M')

    def test_correct_data_irradiation_form(self):
        """Test validity irradiation form."""
        form = IrradiationForm(data={
            'sample': self.sample.id,
            'dosimeter': self.dosimeter.id,
            'irrad_table': 'IRRAD3',
            'table_position': 'Center',
            'dos_position': '1',
            'date_in': self.past_date,
            'date_out': self.current_date,
            'comments': '',
            'is_scan': 'True'
        })
        self.assertTrue(form.is_valid())

    def test_incorrect_data_irradiation_form(self):
        """Test validity incorrect irradiation form."""
        # Test date conflict
        form = IrradiationForm(data={
            'sample': self.sample.id,
            'dosimeter': self.dosimeter.id,
            'previous_irradiation': 'None',
            'irrad_table': 'IRRAD3',
            'table_position': 'Center',
            'dos_position': '1',
            'date_in': '2020/12/12 16:00',
            'date_out': '2020/12/12 19:00',
            'comments': '',
            'is_scan': 'True'
        })
        self.assertTrue(form.is_valid() == False)

        # Test only date_out
        form = IrradiationForm(data={
            'sample': self.sample.id,
            'dosimeter': self.dosimeter.id,
            'previous_irradiation': 'None',
            'irrad_table': 'IRRAD3',
            'table_position': 'Center',
            'dos_position': '1',
            'date_out': '2020/12/12 19:00',
            'comments': '',
            'is_scan': 'True'
        })
        self.assertTrue(form.is_valid() == False)

        # Test future date_in
        form = IrradiationForm(data={
            'sample': self.sample.id,
            'dosimeter': self.dosimeter.id,
            'previous_irradiation': 'None',
            'irrad_table': 'IRRAD3',
            'table_position': 'Center',
            'dos_position': '1',
            'date_in': '2120/12/12 16:00',
            'comments': '',
            'is_scan': 'True'
        })
        self.assertTrue(form.is_valid() == False)

        # Test future dates
        form = IrradiationForm(data={
            'sample': self.sample.id,
            'dosimeter': self.dosimeter.id,
            'previous_irradiation': 'None',
            'irrad_table': 'IRRAD3',
            'table_position': 'Center',
            'dos_position': '1',
            'date_in': '2120/12/12 16:00',
            'date_out': '2120/12/12 19:00',
            'comments': '',
            'is_scan': 'True'
        })
        self.assertTrue(form.is_valid() == False)

        # Test later date_in than date_out
        form = IrradiationForm(data={
            'sample': self.sample.id,
            'dosimeter': self.dosimeter.id,
            'previous_irradiation': 'None',
            'irrad_table': 'IRRAD3',
            'table_position': 'Center',
            'dos_position': '1',
            'date_in': '2020/12/12 19:00',
            'date_out': '2020/12/12 16:00',
            'comments': '',
            'is_scan': 'True'
        })
        self.assertTrue(form.is_valid() == False)

    def test_no_data_irradiation_form(self):
        """Test required fields irradiation form."""
        form = IrradiationForm(data={})
        self.assertTrue(len(form.errors) == 3)

    def test_correct_data_irradiation_group_form(self):
        """Test validity irradiation group form."""
        form = GroupIrradiationForm(data={
            'dosimeter': self.dosimeter.id,
            'irrad_table': 'IRRAD17',
            'table_position': 'Center',
            'is_scan': False
        })
        self.assertTrue(form.is_valid())

    def test_no_data_irradiation_group_form(self):
        """Test required fields irradiation group form."""
        form = GroupIrradiationForm(data={})
        self.assertTrue(len(form.errors) == 3)

    def test_correct_data_irradiation_status_form(self):
        """Test validity irradiation status form."""
        form = IrradiationStatus(data={
            'status':'Registered'
        })
        self.assertTrue(form.is_valid())

    def test_no_data_irradiation_status_form(self):
        """Test required fields irradiation status form."""
        form = IrradiationStatus(data={})
        self.assertTrue(len(form.errors) == 1)


class FluenceFactorFormsTest(TestCase):
    """Test of FluenceFactor forms."""

    fixtures = [
        'experiment_samples_archive.json',
        'boxes.json',
        'compound_elements.json',
        'compounds.json',
        'dosimeters.json',
        'elements.json',
        'experiment_categories.json',
        'experiments.json',
        'irradiations.json',
        'fluence_factors.json',
        'layers.json',
        'materials.json',
        'occupancies.json',
        'requested_fluences.json',
        'samples.json',
        'users.json'
        ]

    @classmethod
    def setUpTestData(cls):
        """Ran once before all tests are run."""
        pass

    def test_correct_data_fluence_factor_form(self):
        """Test validity fluence factor form."""
        form = FluenceFactorForm(data={
            "value": 406200,
            "dosimeter_height": 10,
            "dosimeter_width": 10,
            "irrad_table": "IRRAD7",
            "is_scan": True,
            "status": "Active",
            "nuclide": "Na-22"
        })
        self.assertTrue(form.is_valid())


    def test_no_data_fluence_factor_form(self):
        """Test required fields fluence factor form."""
        form = FluenceFactorForm(data={})
        self.assertTrue(len(form.errors) == 6)


class CompoundFormsTest(TestCase):
    """Test of Compound forms."""

    fixtures = [
        'experiment_samples_archive.json',
        'boxes.json',
        'compound_elements.json',
        'compounds.json',
        'dosimeters.json',
        'elements.json',
        'experiment_categories.json',
        'experiments.json',
        'irradiations.json',
        'fluence_factors.json',
        'layers.json',
        'materials.json',
        'occupancies.json',
        'requested_fluences.json',
        'samples.json',
        'users.json'
        ]

    @classmethod
    def setUpTestData(cls):
        """Ran once before all tests are run."""
        pass

    def test_correct_data_compound_form(self):
        """Test validity compound form."""
        form = CompoundForm(data={
            'name': 'c-test',
            'density': '0.0000001'
        })
        self.assertTrue(form.is_valid())

    def test_no_data_compound_form(self):
        """Test required fields compound form."""
        form = CompoundForm(data={})
        self.assertTrue(len(form.errors) == 2)


class CompoundElementFormsTest(TestCase):
    """Test of CompoundElement forms."""

    fixtures = [
        'experiment_samples_archive.json',
        'boxes.json',
        'compound_elements.json',
        'compounds.json',
        'dosimeters.json',
        'elements.json',
        'experiment_categories.json',
        'experiments.json',
        'irradiations.json',
        'fluence_factors.json',
        'layers.json',
        'materials.json',
        'occupancies.json',
        'requested_fluences.json',
        'samples.json',
        'users.json'
        ]

    @classmethod
    def setUpTestData(cls):
        """Ran once before all tests are run."""
        pass

    def test_correct_data_compound_element_form(self):
        """Test validity compound element form."""
        form = CompoundElementForm(data={
            'element_type': '4',
            'percentage': '54'
        })
        self.assertTrue(form.is_valid())

    def test_no_data_compound_element_form(self):
        """Test required fields compound element form."""
        form = CompoundElementForm(data={})
        self.assertTrue(len(form.errors) == 2)

    def test_correct_data_compound_element_formset(self):
        """Test validity compound element formset."""
        data={
            'ce-fs-TOTAL_FORMS': '2',
            'ce-fs-INITIAL_FORMS': '0',
            'ce-fs-MIN_NUM_FORMS': '1',
            'ce-fs-MAX_NUM_FORMS': '1000',
            'ce-fs-0-id': '',
            'ce-fs-0-compound': '',
            'ce-fs-0-element_type': '4',
            'ce-fs-0-percentage': '54',
            'ce-fs-0-DELETE': '',
            'ce-fs-1-id': '',
            'ce-fs-1-compound': '',
            'ce-fs-1-element_type': '4',
            'ce-fs-1-percentage': '46',
            'ce-fs-1-DELETE': ''
        }

        CompoundElementInlineFormSet = inlineformset_factory(
            Compound,
            CompoundElement,
            form=CompoundElementForm,
            extra=0,
            min_num=1,
            validate_min=True,
            error_messages='Compound is not filled',
            formset=CompoundElementFormSet)
        formset = CompoundElementInlineFormSet(data, prefix='ce-fs')
        self.assertTrue(formset.is_valid())

    def test_no_data_compound_element_formset(self):
        """Test required fields compound element formset."""
        data={
            'ce-fs-TOTAL_FORMS': '1',
            'ce-fs-INITIAL_FORMS': '0',
            'ce-fs-MIN_NUM_FORMS': '1',
            'ce-fs-MAX_NUM_FORMS': '1000',
            'ce-fs-0-id': '',
            'ce-fs-0-compound': '',
            'ce-fs-0-element_type': '',
            'ce-fs-0-percentage': ''
        }
        CompoundElementInlineFormSet = inlineformset_factory(
            Compound,
            CompoundElement,
            form=CompoundElementForm,
            extra=0,
            min_num=1,
            validate_min=True,
            error_messages='Compound is not filled',
            formset=CompoundElementFormSet)
        formset = CompoundElementInlineFormSet(data, prefix='ce-fs')
        #Number of erroneous forms
        self.assertTrue(len(formset.errors) == 1)
        #Number of errors in erroneous form
        self.assertTrue(len(formset.errors[0].keys()) == 2)


class LayerFormsTest(TestCase):
    """Test of Layer forms."""

    fixtures = [
        'experiment_samples_archive.json',
        'boxes.json',
        'compound_elements.json',
        'compounds.json',
        'dosimeters.json',
        'elements.json',
        'experiment_categories.json',
        'experiments.json',
        'irradiations.json',
        'fluence_factors.json',
        'layers.json',
        'materials.json',
        'occupancies.json',
        'requested_fluences.json',
        'samples.json',
        'users.json'
        ]

    @classmethod
    def setUpTestData(cls):
        """Ran once before all tests are run."""
        cls.sample = Sample.objects.get(pk=1)

    def test_correct_data_layer_form(self):
        """Test validity layer form."""
        form = LayerForm(data={
            'name': 'L0',
            'length': '0.000001',
            'compound_type': '1'
        })
        self.assertTrue(form.is_valid())

    def test_no_data_layer_form(self):
        """Test required fields layer form."""
        form = LayerForm(data={})
        self.assertTrue(len(form.errors) == 3)

    def test_correct_data_layer_formset(self):
        """Test validity layer formset."""
        data={
            'layer_set-TOTAL_FORMS': '2',
            'layer_set-INITIAL_FORMS': '0',
            'layer_set-MIN_NUM_FORMS': '1',
            'layer_set-MAX_NUM_FORMS': '1000',
            'layer_set-0-id': '',
            'layer_set-0-sample': self.sample.id,
            'layer_set-0-name': 'L0',
            'layer_set-0-length': '0.000001',
            'layer_set-0-compound_type': '1',
            'layer_set-0-DELETE': '',
            'layer_set-1-sample': self.sample.id,
            'layer_set-1-name': 'L1',
            'layer_set-1-length': '0.000001',
            'layer_set-1-compound_type': '2',
            'layer_set-1-DELETE': '',
        }

        LayerInlineFormset = inlineformset_factory(
            Sample,
            Layer,
            form=LayerForm,
            extra=0,
            min_num=1,
            validate_min=True,
            error_messages='Layers not correctly filled.',
            formset=LayerFormSet)
        formset = LayerInlineFormset(data, instance = self.sample)
        self.assertTrue(formset.is_valid())

    def test_no_data_layer_formset(self):
        """Test required fields layer formset."""
        data={
            'layer_set-TOTAL_FORMS': '1',
            'layer_set-INITIAL_FORMS': '0',
            'layer_set-MIN_NUM_FORMS': '1',
            'layer_set-MAX_NUM_FORMS': '1000',
            'layer_set-0-id': '',
            'layer_set-0-sample': '',
            'layer_set-0-name': '',
            'layer_set-0-length': '',
            'layer_set-0-compound_type': '',
            'layer_set-0-DELETE': '',
        }
        LayerInlineFormset = inlineformset_factory(
            Sample,
            Layer,
            form=LayerForm,
            extra=0,
            min_num=1,
            validate_min=True,
            error_messages='Layers not correctly filled.',
            formset=LayerFormSet)
        formset = LayerInlineFormset(data)
        #Number of erroneous forms
        self.assertTrue(len(formset.errors) == 1)
        #Number of errors in erroneous form
        self.assertTrue(len(formset.errors[0].keys()) == 3)


class MaterialFormsTest(TestCase):
    """Test of Material forms."""

    fixtures = [
        'experiment_samples_archive.json',
        'boxes.json',
        'compound_elements.json',
        'compounds.json',
        'dosimeters.json',
        'elements.json',
        'experiment_categories.json',
        'experiments.json',
        'irradiations.json',
        'fluence_factors.json',
        'layers.json',
        'materials.json',
        'occupancies.json',
        'requested_fluences.json',
        'samples.json',
        'users.json'
        ]

    @classmethod
    def setUpTestData(cls):
        """Ran once before all tests are run."""
        cls.experiment = Experiment.objects.get(pk=1)

    def test_correct_data_material_form(self):
        """Test validity material form."""
        form = MaterialForm(data={
            'material': 'silicon'
        })
        self.assertTrue(form.is_valid())

    def test_no_data_material_form(self):
        """Test required fields material form."""
        form = MaterialForm(data={})
        self.assertTrue(len(form.errors) == 1)

    def test_correct_data_material_formset(self):
        """Test validity material formset."""
        data={
            'm-fs-TOTAL_FORMS': '2',
            'm-fs-INITIAL_FORMS': '0',
            'm-fs-MIN_NUM_FORMS': '1',
            'm-fs-MAX_NUM_FORMS': '1000',
            'm-fs-0-id': '',
            'm-fs-0-experiment': self.experiment.id,
            'm-fs-0-material': 'silicon',
            'm-fs-0-DELETE': '',
            'm-fs-1-id': '',
            'm-fs-1-experiment': self.experiment.id,
            'm-fs-1-material': 'silicon',
            'm-fs-1-DELETE': ''
        }

        MaterialInlineFormSet = inlineformset_factory(
            Experiment,
            Material,
            form=MaterialForm,
            extra=0,
            min_num=1,
            validate_min=True,
            error_messages='Sample type field is not correctly filled.',
            formset=MaterialFormSet)
        formset = MaterialInlineFormSet(data, instance=self.experiment, prefix='m-fs')
        self.assertTrue(formset.is_valid())

    def test_no_data_material_formset(self):
        """Test required fields material formset."""
        data={
            'm-fs-TOTAL_FORMS': '1',
            'm-fs-INITIAL_FORMS': '0',
            'm-fs-MIN_NUM_FORMS': '1',
            'm-fs-MAX_NUM_FORMS': '1000',
            'm-fs-0-id': '',
            'm-fs-0-experiment': '',
            'm-fs-0-material': '',
            'm-fs-0-DELETE': '',
        }
        MaterialInlineFormSet = inlineformset_factory(
            Experiment,
            Material,
            form=MaterialForm,
            extra=0,
            min_num=1,
            validate_min=True,
            error_messages='Sample type field is not correctly filled.',
            formset=MaterialFormSet)
        formset = MaterialInlineFormSet(data, instance=self.experiment, prefix='m-fs')
        #Number of erroneous forms
        self.assertTrue(len(formset.errors) == 1)
        #Number of errors in erroneous form
        self.assertTrue(len(formset.errors[0].keys()) == 1)


class ReqFluenceFormsTest(TestCase):
    """Test of ReqFluence forms."""

    fixtures = [
        'experiment_samples_archive.json',
        'boxes.json',
        'compound_elements.json',
        'compounds.json',
        'dosimeters.json',
        'elements.json',
        'experiment_categories.json',
        'experiments.json',
        'irradiations.json',
        'fluence_factors.json',
        'layers.json',
        'materials.json',
        'occupancies.json',
        'requested_fluences.json',
        'samples.json',
        'users.json'
        ]

    @classmethod
    def setUpTestData(cls):
        """Ran once before all tests are run."""
        cls.experiment = Experiment.objects.get(pk=1)

    def test_correct_data_req_fluence_form(self):
        """Test validity requested fluence form."""
        form = ReqFluenceForm(data={
            'req_fluence': '1'
        })
        self.assertTrue(form.is_valid())

    def test_no_data_req_fluence_form(self):
        """Test required fields requested fluence form."""
        form = ReqFluenceForm(data={})
        self.assertTrue(len(form.errors) == 1)

    def test_correct_data_req_fluence_formset(self):
        """Test validity requested fluence formset."""
        data={
            'f-fs-TOTAL_FORMS': '2',
            'f-fs-INITIAL_FORMS': '0',
            'f-fs-MIN_NUM_FORMS': '1',
            'f-fs-MAX_NUM_FORMS': '1000',
            'f-fs-0-id': '',
            'f-fs-0-experiment': self.experiment.id,
            'f-fs-0-req_fluence': '1',
            'f-fs-0-DELETE': '',
            'f-fs-1-id': '',
            'f-fs-1-experiment': self.experiment.id,
            'f-fs-1-req_fluence': '1',
            'f-fs-1-DELETE': ''
        }

        ReqFluenceInlineFormSet = inlineformset_factory(
            Experiment,
            ReqFluence,
            form=ReqFluenceForm,
            extra=0,
            min_num=1,
            validate_min=True,
            error_messages='Fluence field is not correctly filled.',
            formset=ReqFluenceFormSet)
        formset = ReqFluenceInlineFormSet(data, instance=self.experiment, prefix='f-fs')
        self.assertTrue(formset.is_valid())

    def test_no_data_req_fluence_formset(self):
        """Test required fields requested fluence formset."""
        data={
            'f-fs-TOTAL_FORMS': '1',
            'f-fs-INITIAL_FORMS': '0',
            'f-fs-MIN_NUM_FORMS': '1',
            'f-fs-MAX_NUM_FORMS': '1000',
            'f-fs-0-id': '',
            'f-fs-0-experiment': '',
            'f-fs-0-req_fluence': '',
            'f-fs-0-DELETE': ''
        }
        ReqFluenceInlineFormSet = inlineformset_factory(
            Experiment,
            ReqFluence,
            form=ReqFluenceForm,
            extra=0,
            min_num=1,
            validate_min=True,
            error_messages='Fluence field is not correctly filled.',
            formset=ReqFluenceFormSet)
        formset = ReqFluenceInlineFormSet(data, instance=self.experiment, prefix='f-fs')
        #Number of erroneous forms
        self.assertTrue(len(formset.errors) == 1)
        #Number of errors in erroneous form
        self.assertTrue(len(formset.errors[0].keys()) == 1)


class UserFormsTest(TestCase):
    """Test of User forms."""

    fixtures = [
        'experiment_samples_archive.json',
        'boxes.json',
        'compound_elements.json',
        'compounds.json',
        'dosimeters.json',
        'elements.json',
        'experiment_categories.json',
        'experiments.json',
        'irradiations.json',
        'fluence_factors.json',
        'layers.json',
        'materials.json',
        'occupancies.json',
        'requested_fluences.json',
        'samples.json',
        'users.json'
        ]

    @classmethod
    def setUpTestData(cls):
        """Ran once before all tests are run."""
        cls.experiment = Experiment.objects.get(pk=1)
        cls.user = User.objects.get(pk=2)

    def test_correct_data_user_form(self):
        """Test validity user form."""
        form = UserForm(data={
            'name': 'Test',
            'surname': 'User',
            'email': 'test-user@gmail.com',
            'telephone': '1234',
            'role': 'User'
        })
        self.assertTrue(form.is_valid())

    def test_no_data_user_form(self):
        """Test required fields user form."""
        form = UserForm(data={})
        self.assertTrue(len(form.errors) == 4)

    def test_correct_data_experiment_user_form(self):
        """Test validity experiment user form."""
        form = AddUserToExperimentForm(data={
            'email': self.user.email
        }, experiment=self.experiment)
        self.assertTrue(form.is_valid())

    def test_no_data_experiment_user_form(self):
        """Test required fields experiment user form."""
        form = AddUserToExperimentForm(data={}, experiment=self.experiment)
        self.assertTrue(len(form.errors) == 1)


class CategoryFormsTest(TestCase):
    """Test of category forms."""

    fixtures = [
        'experiment_samples_archive.json',
        'boxes.json',
        'compound_elements.json',
        'compounds.json',
        'dosimeters.json',
        'elements.json',
        'experiment_categories.json',
        'experiments.json',
        'irradiations.json',
        'fluence_factors.json',
        'layers.json',
        'materials.json',
        'occupancies.json',
        'requested_fluences.json',
        'samples.json',
        'users.json'
        ]

    @classmethod
    def setUpTestData(cls):
        """Ran once before all tests are run."""
        cls.experiment = Experiment.objects.get(pk=1)
        cls.user = User.objects.get(pk=2)

    def test_correct_data_passive_standard_category_form(self):
        """Test validity passive standard category form."""
        form = PassiveStandardCategoryForm(data={
            'irradiation_area_5x5': 'on',
            'irradiation_area_10x10': 'on',
            'irradiation_area_20x20': ''
        })
        self.assertTrue(form.is_valid())

    def test_no_data_passive_standard_category_form(self):
        """Test required fields passive standard category form."""
        form = PassiveStandardCategoryForm(data={})
        self.assertTrue(len(form.errors) == 1)

    def test_correct_data_passive_custom_category_form(self):
        """Test validity passive custom category form."""
        form = PassiveCustomCategoryForm(data={
            'passive_category_type': 'Room temperature',
            'passive_irradiation_area': '25x25 mm²',
            'passive_modus_operandi': 'Modus operandi.'
        })
        self.assertTrue(form.is_valid())

    def test_no_data_passive_custom_category_form(self):
        """Test required fields passive custom category form."""
        form = PassiveCustomCategoryForm(data={})
        self.assertTrue(len(form.errors) == 3)

    def test_correct_data_active_category_form(self):
        """Test validity active category form."""
        form = ActiveCategoryForm(data={
            'active_category_type': 'Room temperature',
            'active_irradiation_area': '25x25 mm²',
            'active_modus_operandi': 'Modus operandi.'
        })
        self.assertTrue(form.is_valid())

    def test_no_data_experiment_user_form(self):
        """Test required fields active category form."""
        form = ActiveCategoryForm(data={})
        self.assertTrue(len(form.errors) == 3)