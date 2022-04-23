"""Model tests."""
from django.test import TestCase
from samples_manager.models import *


class ExperimentModelTest(TestCase):
    """Test Experiment model."""

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
        cls.user_admin = User.objects.get(pk=1)
        cls.experiment = Experiment.objects.get(pk=1)

    def test_experiment_creation(self):
        """Tests experiment creation."""
        experiment = Experiment.objects.create(
            title='e-test',
            description='description',
            cern_experiment='IRRAD',
            constraints='constraints',
            number_samples=1,
            category='Passive Standard',
            regulations_flag=True,
            irradiation_type='Protons',
            emergency_phone='1234',
            status='Registered',
            public_experiment=True,
            responsible=self.user_admin,
            created_at='2020-12-12T14:00:00+00:00',
            updated_at='2020-12-12T14:00:00+00:00',
            created_by=self.user_admin,
            updated_by=self.user_admin)

        self.assertTrue(isinstance(experiment, Experiment))

    def test_experiment_string_representation(self):
        """Tests experiment __str__ method."""
        self.assertTrue(str(self.experiment) == self.experiment.title)


class SampleModelTest(TestCase):
    """Test Sample model."""

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
        cls.user_admin = User.objects.get(pk=1)
        cls.material = Material.objects.get(pk=1)
        cls.fluence = ReqFluence.objects.get(pk=1)
        cls.sample = Sample.objects.get(pk=1)

    def test_sample_creation(self):
        """Tests sample creation."""
        sample = Sample.objects.create(
            name='s-test',
            current_location='14/R-012',
            height=1,
            width=1,
            weight=1,
            comments='comment',
            category='Passive Standard',
            storage='Room temperature',
            status='Registered',
            material=self.material,
            req_fluence=self.fluence,
            created_at='2020-12-12T14:00:00+00:00',
            updated_at='2020-12-12T14:00:00+00:00',
            created_by=self.user_admin,
            updated_by=self.user_admin)

        self.assertTrue(isinstance(sample, Sample))

    def test_sample_string_representation(self):
        """Tests sample __str__ method."""
        self.assertTrue(str(self.sample) == self.sample.name)

class IrradiationModelTest(TestCase):
    """Test Irradiation model."""

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
        cls.user_admin = User.objects.get(pk=1)
        cls.sample = Sample.objects.get(pk=1)
        cls.dosimeter = Dosimeter.objects.get(pk=1)
    
    def test_irradiation_creation(self):
        """Tests irradiation creation."""
        irradiation = Irradiation.objects.create(
            sample=self.sample,
            dosimeter=self.dosimeter,
            date_in='2020-12-12T14:00:00+00:00',
            date_out='2020-12-13T14:00:00+00:00',
            table_position='Center',
            irrad_table='IRRAD17',
            sec=1,
            estimated_fluence=0.0000001,
            fluence_error=0.001,
            status='Registered',
            dos_position=1,
            comments='comment',
            created_at='2020-12-12T14:00:00+00:00',
            updated_at='2020-12-12T14:00:00+00:00',
            created_by=self.user_admin,
            updated_by=self.user_admin)

        self.assertTrue(isinstance(irradiation, Irradiation))

    def test_irradiation_group_creation(self):
        """Tests irradiation group creation."""
        irradiation = Irradiation.objects.create(
            sample=self.sample,
            dosimeter=self.dosimeter,
            table_position='Center')

        self.assertTrue(isinstance(irradiation, Irradiation))


class UserModelTest(TestCase):
    """Test User model."""

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
    
    def test_user_creation(self):
        """Tests user creation."""
        user = User.objects.create(
            email='test-user@gmail.com',
            name='Test',
            surname='Temp User',
            telephone='1234',
            db_telephone='1234',
            department='EP',
            home_institute='CERN',
            role='User',
            last_login='')

        


        self.assertTrue(isinstance(user, User))

    def test_user_string_representation(self):
        """Tests user __str__ method."""
        self.assertTrue(str(self.user) == self.user.email)


class CategoryModelsTest(TestCase):
    """Test categories models."""

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
        cls.passive_standard_category = PassiveStandardCategory\
            .objects.get(pk=1)
        cls.passive_custom_category = PassiveCustomCategory\
            .objects.get(pk=1)
        cls.active_category = ActiveCategory.objects.get(pk=1)
    
    def test_passive_standard_category_creation(self):
        """Tests passive standard category creation."""
        passive_standard_category = PassiveStandardCategory.objects.create(
                irradiation_area_5x5 = True,
                irradiation_area_10x10 = True,
                irradiation_area_20x20 = False,
                experiment = self.experiment)

        self.assertTrue(isinstance(passive_standard_category, \
            PassiveStandardCategory))

    def test_passive_standard_category_string_representation(self):
        """Tests passive standard category __str__ method."""
        self.assertTrue(str(self.passive_standard_category) == \
            str(self.passive_standard_category.irradiation_area_5x5))

    def test_passive_custom_category_creation(self):
        """Tests passive custom category creation."""
        passive_custom_category = PassiveCustomCategory.objects.create(
            passive_category_type = 'Room temperature',
            passive_irradiation_area = '25x25 mm²',
            passive_modus_operandi = 'Modus operandi.',
            experiment = self.experiment)

        self.assertTrue(isinstance(passive_custom_category, \
            PassiveCustomCategory))

    def test_passive_custom_category_string_representation(self):
        """Tests passive custom category __str__ method."""
        self.assertTrue(str(self.passive_custom_category) == \
            self.passive_custom_category.passive_category_type)

    def test_active_category_creation(self):
        """Tests active category creation."""
        active_category = ActiveCategory.objects.create(
            active_category_type = 'Room temperature',
            active_irradiation_area = '25x25 mm²',
            active_modus_operandi = 'Modus operandi.',
            experiment = self.experiment)

        self.assertTrue(isinstance(active_category, ActiveCategory))

    def test_active_category_string_representation(self):
        """Tests active category __str__ method."""
        self.assertTrue(str(self.active_category) == \
            self.active_category.active_category_type)


class ReqFluenceModelTest(TestCase):
    """Test requested fluence model."""

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
        cls.requested_fluence = ReqFluence.objects.get(pk=1)
    
    def test_requested_fluence_creation(self):
        """Tests requested fluence creation."""
        requested_fluence = ReqFluence.objects.create(
            req_fluence = '1',
            experiment = self.experiment)

        self.assertTrue(isinstance(requested_fluence, ReqFluence))

    def test_requested_fluence_string_representation(self):
        """Tests requested fluence __str__ method."""
        self.assertTrue(str(self.requested_fluence) == \
            str(self.requested_fluence.req_fluence))


class MaterialModelTest(TestCase):
    """Test material model."""

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
        cls.material = Material.objects.get(pk=1)
    
    def test_material_creation(self):
        """Tests material creation."""
        material = Material.objects.create(
            material = 'silicon',
            experiment = self.experiment)

        self.assertTrue(isinstance(material, Material))

    def test_material_string_representation(self):
        """Tests material __str__ method."""
        self.assertTrue(str(self.material) == str(self.material.material))


class BoxModelTest(TestCase):
    """Test box model."""

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
    
    def test_box_creation(self):
        """Tests box creation."""
        box = Box.objects.create(
            box_id='BOX-004000',
            description='',
            responsible=self.user,
            current_location='14/R-012',
            last_location='14/R-012',
            length='0.100',
            height='0.100',
            width='0.100',
            weight='0.100',
            created_at='2020-12-12T13:00:00+00:00',
            updated_at='2020-12-12T13:00:00+00:00',
            created_by=self.user,
            updated_by=self.user)

        self.assertTrue(isinstance(box, Box))

    def test_box_string_representation(self):
        """Tests box __str__ method."""
        self.assertTrue(str(self.box) == str(self.box.box_id))


class OccupancyModelTest(TestCase):
    """Test occupancy model."""

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
        cls.occupancy = Occupancy.objects.get(pk=1)
    
    def test_occupancy_creation(self):
        """Tests occupancy creation."""
        occupancy = Occupancy.objects.create(
            radiation_length_occupancy = '0.100',
            nu_coll_length_occupancy = '0.100',
            nu_int_length_occupancy = '0.100',
            sample = self.sample)

        self.assertTrue(isinstance(occupancy, Occupancy))

    def test_occupancy_string_representation(self):
        """Tests occupancy __str__ method."""
        self.assertTrue(str(self.occupancy) == \
            str(self.occupancy.radiation_length_occupancy) + ' ' + str(
            self.occupancy.nu_coll_length_occupancy) + ' ' + str(
                self.occupancy.nu_int_length_occupancy))


class DosimeterModelTest(TestCase):
    """Test dosimeter model."""

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
        cls.dosimeter = Dosimeter.objects.get(pk=1)
    
    def test_dosimeter_creation(self):
        """Tests dosimeter creation."""
        dosimeter = Dosimeter.objects.create(
            dos_id = 'DOS-009999',
            responsible = self.user,
            current_location = '14/R-012',
            length = '0.000001',
            height = '0.000001',
            width = '0.000001',
            weight = '0.000001',
            foils_number = '1',
            status = 'Registered',
            dos_type = 'Aluminium',
            comments = '',
            box = self.box,
            last_location = '14/R-012',
            parent_dosimeter = None,
            created_at = '2020-12-12T14:00:00+00:00',
            updated_at = '2020-12-12T14:00:00+00:00',
            created_by = self.user,
            updated_by = self.user)

        self.assertTrue(isinstance(dosimeter, Dosimeter))

    def test_dosimeter_string_representation(self):
        """Tests dosimeter __str__ method."""
        self.assertTrue(str(self.dosimeter) == str(self.dosimeter.dos_id))


class ElementModelTest(TestCase):
    """Test element model."""

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
        cls.element = Element.objects.get(pk=1)
    
    def test_element_creation(self):
        """Tests element creation."""
        element = Element.objects.create(
            atomic_number = '0',
            atomic_symbol = 'N',
            atomic_mass = '0.001',
            density = '0.001',
            min_ionization = '0.001',
            nu_coll_length = '0.001',
            nu_int_length = '0.001',
            pi_coll_length = '0.001',
            pi_int_length = '0.001',
            radiation_length = '0.001')

        self.assertTrue(isinstance(element, Element))

    def test_element_string_representation(self):
        """Tests element __str__ method."""
        self.assertTrue(str(self.element) == \
            str(self.element.atomic_symbol) + '(' + str(self.element.atomic_number) + ')')


class CompoundModelTest(TestCase):
    """Test compound model."""

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
        cls.compound = Compound.objects.get(pk=1)
    
    def test_compound_creation(self):
        """Tests compound creation."""
        compound = Compound.objects.create(
            name = 'c-test',
            density = '0.01')

        self.assertTrue(isinstance(compound, Compound))

    def test_compound_string_representation(self):
        """Tests compound __str__ method."""
        self.assertTrue(str(self.compound) == str(self.compound.name))
        

class CompoundElementModelTest(TestCase):
    """Test compound element model."""

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
        cls.element = Element.objects.get(pk=1)
        cls.compound = Compound.objects.get(pk=1)
        cls.compound_element = CompoundElement.objects.get(pk=1)
    
    def test_compound_element_creation(self):
        """Tests compound element creation."""
        compound_element = CompoundElement.objects.create(
            element_type = self.element,
            percentage = '0.01',
            compound = self.compound)

        self.assertTrue(isinstance(compound_element, CompoundElement))


class LayerModelTest(TestCase):
    """Test layer model."""

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
        cls.compound = Compound.objects.get(pk=1)
        cls.layer = Layer.objects.get(pk=1)

    def test_layer_creation(self):
        """Tests layer creation."""
        layer = Layer.objects.create(
            name = 'L0',
            length = '0.01',
            compound_type = self.compound,
            sample = self.sample)

        self.assertTrue(isinstance(layer, Layer))

    def test_layer_string_representation(self):
        """Tests compound __str__ method."""
        self.assertTrue(str(self.layer) == str(self.layer.name))


class ArchiveExperimentSampleModelTest(TestCase):
    """Test archive experiment sample model."""

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
        cls.experiment = Experiment.objects.get(pk=1)

    def test_compound_element_creation(self):
        """Tests archive experiment sample creation."""
        archive_experiment_sample = ArchiveExperimentSample.objects.create(
            timestamp = '2020-12-12T14:00:00+00:00',
            experiment = self.experiment,
            sample = self.sample)

        self.assertTrue(isinstance(archive_experiment_sample, ArchiveExperimentSample))