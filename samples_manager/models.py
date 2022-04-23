"""Django app data models."""
# -*- coding: utf-8 -*-
from .utilities import *
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
# Create your models here.

CERN_EXPERIMENTS = (('ATLAS', 'ATLAS'), ('CMS', 'CMS'), ('ALICE', 'ALICE'),
                    ('LHCb', 'LHCb'), ('TOTEM', 'TOTEM'), ('Other', 'Other'))
CATEGORIES = (('', 'Please,choose category'), ('Passive Standard',
                                               'Passive Standard'),
              ('Passive Custom', 'Passive Custom'), ('Active', 'Active'))
STORAGE = (('Room temperature', 'Room temperature'), ('Cold storage <20',
                                                      'Cold storage <20 °C'))
STATUS = (('Registered', 'Registered'), ('Updated', 'Updated'),
            ('Validated', 'Validated'), ('In Preparation', 'In Preparation'), 
            ('Ongoing', 'Ongoing'), ('Paused', 'Paused'), ('Completed', 'Completed'),
            ('Approved', 'Approved'), ('Ready', 'Ready'), ('InBeam', 'In beam'),
            ('OutBeam', 'Out of beam'), ('CoolingDown', 'Cooling down'),
            ('InStorage', 'In Storage'), ('OutOfIRRAD', 'Out of IRRAD'), 
            ('Waste', 'Waste'), ('Active', 'Active'), ('Inactive', 'Inactive'))
IRRADIATION_STATUS = (STATUS[0], STATUS[9], STATUS[10], STATUS[6],  STATUS[12])
EXPERIMENT_STATUS = (STATUS[0], STATUS[1], STATUS[2], STATUS[3], STATUS[4], STATUS[5], STATUS[6])
FLUENCE_FACTOR_STATUS = (STATUS[15], STATUS[16])
FLUENCE_FACTOR_NUCLIDE = (('Na-22', 'Na-22'), ('Na-24', 'Na-24'))
EXPERIMENT_VISIBILITY = (('Public', 'Public'), ('Private', 'Private'))
DOSIMETER_CATEGORY = (('Aluminium', 'Aluminium'), ('Film', 'Film'),
                      ('Diamond', 'Diamond'), ('Other', 'Other'))

IRRAD_POSITION = (('IRRAD1_Shuttle', (('IRRAD1', 'IRRAD1-Shuttle'), )),
                  ('IRRAD3', (
                      ('IRRAD3', 'No holder'),
                      ('IRRAD3_Left', 'Left holder'),
                      ('IRRAD3_Center', 'Center holder'),
                      ('IRRAD3_Right', 'Right holder'),
                  )), ('IRRAD5', (('IRRAD5', 'Cold Box'), )), ('IRRAD7', (
                      ('IRRAD7', 'No holder'),
                      ('IRRAD7_Left', 'Left holder'),
                      ('IRRAD7_Center', 'Center holder'),
                      ('IRRAD7_Right', 'Right holder'),
                  )), ('IRRAD9', (
                      ('IRRAD9', 'No holder'),
                      ('IRRAD9_Left', 'Left holder'),
                      ('IRRAD9_Center', 'Center holder'),
                      ('IRRAD9_Right', 'Right holder'),
                  )), ('IRRAD11', (('IRRAD11', 'Cold Box'), )), ('IRRAD13', (
                      ('IRRAD13', 'No holder'),
                      ('IRRAD13_Left', 'Left holder'),
                      ('IRRAD13_Center', 'Center holder'),
                      ('IRRAD13_Right', 'Right holder'),
                  )), ('IRRAD15', (('IRRAD15', 'Cryostat'), )), ('IRRAD13', (
                      ('IRRAD13', 'No holder'),
                      ('IRRAD13_Left', 'Left holder'),
                      ('IRRAD13_Center', 'Center holder'),
                      ('IRRAD13_Right', 'Right holder'),
                  )), ('IRRAD17', (
                      ('IRRAD17', 'No holder'),
                      ('IRRAD17_Left', 'Left holder'),
                      ('IRRAD17_Center', 'Center holder'),
                      ('IRRAD17_Right', 'Right holder'),
                  )), ('IRRAD19', (
                      ('IRRAD19', 'No holder'),
                      ('IRRAD19_Left', 'Left holder'),
                      ('IRRAD19_Center', 'Center holder'),
                      ('IRRAD19_Right', 'Right holder'),
                  )))

ROLE = (('Owner', 'Owner'), ('Operator', 'Operator'),
        ('Coordinator', 'Coordinator'), ('User', 'User'))


def validate_negative(value):
    """Raises error if number is negative."""
    if value < 0:
        raise ValidationError(
                _('%(value)s is negative'),
                params={'value': value},
            )


class User(models.Model):
    """
    User. 

    Attributes:
        email (EmailField): email address. 
        name (CharField): first name.
        surname (CharField): last name.
        telephone (CharField): contact telephone.
        db_telephone (CharField): contact telephone.
        department (CharField): CERN department.
        home_institute (CharField): instutional affiliation.
        role (CharField): app role (Admin, User).
        last_login (DateTimeField): leatest login's timestamp.
    """
    email = models.EmailField(max_length=200, unique=True)
    name = models.CharField(max_length=200, null=True)
    surname = models.CharField(max_length=200, null=True)
    telephone = models.CharField(max_length=200, null=True)
    db_telephone = models.CharField(max_length=200, null=True)
    department = models.CharField(max_length=200, null=True)
    home_institute = models.CharField(max_length=200, null=True)
    role = models.CharField(max_length=100,
                            choices=ROLE,
                            default='User',
                            null=True)
    last_login = models.DateTimeField()

    def save(self, *args, **kwargs):
        """Overwritten method. See Model class. On save update timestamps."""
        self.last_login = get_aware_datetime()
        return super(User, self).save(*args, **kwargs)

    def __str__(self):  # __str__ on Python 2
        """Overwritten method. See object class."""
        return self.email

    class Meta:
        ordering = ['name']


class Experiment(models.Model):
    """
    Experiment. 

    Attributes:
        title (CharField): title of experiment.
        description (TextField): description of experiment.
        cern_experiment (CharField): cern experiment where experiment results will be used.
        availability (DateField): experiment test date.
        constraints (CharField): constraints required to perform test.
        number_samples (PositiveIntegerField): Number of samples used.
        number_registered_samples (PositiveIntegerField): Number of samples registered.
        number_users (PositiveIntegerField): Number of users.
        radiation_length_occupancy (PositiveIntegerField): Radiation length.
        nu_coll_length_occupancy (PositiveIntegerField): Nuclear collision length.
        nu_int_length_occupancy (PositiveIntegerField): Nuclear interaction length.
        comments (TextField): additional comments.
        category (CharField): category of experiment. Passive Standard, Passive Custom or Active.
        regulations_flag (BooleanField): acceptance of site regulations.
        irradiation_type (CharField): type of irradiation. Particles used in test.
        emergency_phone (CharField): emergency phone contact number
        status (CharField): experiment status
        responsible (User): user responsible of experiment
        users (ManyToManyField): users related to the experiment.
        created_at (DateField): creation timestamp.
        updated_at (DateField): update timestamp
        created_by (User): user who created experiment.
        updated_by (User): user who has last updated the experiment.
        correct.
        public_experiment (BooleanField): if true visible to all.
    """
    title = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    cern_experiment = models.CharField(max_length=100)
    availability = models.DateField(null=True)
    constraints = models.CharField(max_length=2000)
    number_samples = models.PositiveIntegerField(
        default=0, validators=[MinValueValidator(0)])
    number_registered_samples = models.PositiveIntegerField(default=0)
    number_users = models.PositiveIntegerField(default=0)
    radiation_length_occupancy = models.DecimalField(default=0, max_digits=9,
        decimal_places=3, null=True)
    nu_coll_length_occupancy = models.DecimalField(default=0, max_digits=9,
        decimal_places=3, null=True)
    nu_int_length_occupancy = models.DecimalField(default=0, max_digits=9,
        decimal_places=3, null=True)
    comments = models.TextField(null=True)
    category = models.CharField(max_length=100,
        choices=CATEGORIES,
        blank=False)
    regulations_flag = models.BooleanField()
    irradiation_type = models.CharField(max_length=100)
    emergency_phone = models.CharField(max_length=200)
    # these fields should be autofilled
    status = models.CharField(max_length=50, choices=EXPERIMENT_STATUS)
    responsible = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                    related_name='%(class)s_responsible')
    users = models.ManyToManyField(User)
    created_at = models.DateTimeField(editable=False)
    updated_at = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL,
                                   related_name='%(class)s_created_by',
                                   null=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL,
                                   related_name='%(class)s_updated_by',
                                   null=True)
    public_experiment = models.BooleanField()

    def __str__(self):  # __str__ on Python 2
        """Overwritten method. See object class."""
        return self.title

    def save(self, *args, **kwargs):
        """Overwritten method. See Model class. On save update timestamps."""
        if not self.id:
            self.created_at = get_aware_datetime()
            self.updated_at = get_aware_datetime()
            super(Experiment, self).save(*args, **kwargs)
            args = ()
            kwargs = {}
        else:
            self.updated_at = get_aware_datetime()
        self.set_additional_info()
        super(Experiment, self).save(*args, **kwargs)
    
    def set_additional_info(self):
        """Method to set additional information in model."""
        samples = Sample.objects.filter(experiment=self.id)
        radiation_length_occupancy = 0
        nu_coll_length_occupancy = 0
        nu_int_length_occupancy = 0
        for sample in samples:
            radiation_length_occupancy += sample.radiation_length_occupancy
            nu_coll_length_occupancy += sample.nu_coll_length_occupancy
            nu_int_length_occupancy += sample.nu_int_length_occupancy
        self.number_registered_samples = samples.count()
        self.number_users = self.users.count() + 1
        self.radiation_length_occupancy = radiation_length_occupancy
        self.nu_coll_length_occupancy = nu_coll_length_occupancy
        self.nu_int_length_occupancy = nu_int_length_occupancy
    
    class Meta:
        ordering = ['-updated_at', 'title']


class PassiveStandardCategory(models.Model):
    """
    Experiment category Passive Standard.

    Attributes:
        irradiation_area_5x5 (BooleanField): boolean. Irradiation area.
        irradiation_area_10x10 (BooleanField): boolean. Irradiation area.
        irradiation_area_20x20 (BooleanField): boolean. Irradiation area.
        experiment (Experiment): experiment instance which belongs to this category.
    """
    irradiation_area_5x5 = models.BooleanField()
    irradiation_area_10x10 = models.BooleanField()
    irradiation_area_20x20 = models.BooleanField()
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, null=True)

    def __str__(self):  # __str__ on Python 2
        """Overwritten method. See object class."""
        return str(self.irradiation_area_5x5)


class PassiveCustomCategory(models.Model):
    """
    Experiment category Passive Custom.

    Attributes:
        passive_category_type (CharField): type of experiment category.
        passive_irradiation_area (CharField): irradiation area.
        passive_modus_operandi (TextField): Description of instructins to 
            execute passive custom experiment.
        experiment (Experiment): experiment instance which belongs to this category.
    """
    passive_category_type = models.CharField(max_length=50)
    passive_irradiation_area = models.CharField(max_length=50)
    passive_modus_operandi = models.TextField()
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, null=True)

    def __str__(self):  # __str__ on Python 2
        """Overwritten method. See object class."""
        return self.passive_category_type


class ActiveCategory(models.Model):
    """
    Experiment category Active.

    Attributes:
        active_category_type (CharField): type of experiment category.
        active_irradiation_area (CharField): irradiation area.
        active_modus_operandi (TextField): Description of instructins to 
            execute active experiment.
        experiment (Experiment): experiment instance which belongs to this category.
    """
    active_category_type = models.CharField(max_length=50)
    active_irradiation_area = models.CharField(max_length=50)
    active_modus_operandi = models.TextField()
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, null=True)

    def __str__(self):  # __str__ on Python 2
        """Overwritten method. See object class."""
        return self.active_category_type


class ReqFluence(models.Model):
    """
    Experiment's Requested fluence.

    Attributes:
        req_fluence (CharField): requested fluence for experiment.
        experiment (Experiment): experiment instance which belongs to this category.
    """
    req_fluence = models.CharField(max_length=50)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, null=True)

    def __str__(self):  # __str__ on Python 2
        """Overwritten method. See object class."""
        return self.req_fluence


class Material(models.Model):
    """
    Experiment's Material.

    Attributes:
        material (CharField): material name. Displayed as sample type.
        experiment (Experiment): experiment instance where materials will be used.
    """
    material = models.CharField(max_length=50)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, null=True)

    def __str__(self):  # __str__ on Python 2
        """Overwritten method. See object class."""
        return self.material


class Box(models.Model):
    """
    Physical storing of samples in a box.

    Attributes:
        box_id (CharField): id of box.
        description (CharField): description of box.
        responsible (User): user responsible of box.
        current_location (CharField): location of box.
        last_location (CharField): previous location of box.
        length (CharField): length of box.
        height (CharField): height of box.
        width (CharField): width of box.
        created_at (DateField): creation timestamp.
        updated_at (DateField): lastest update's timestamp. 
        created_by (User): user who created instance.
        updated_by (User): user who last updated instance.
    """
    box_id = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=200, null=True)
    responsible = models.ForeignKey(User, on_delete=models.SET_NULL, 
                                    null=True, 
                                    related_name='%(class)s_responsible')
    current_location = models.CharField(max_length=100)
    last_location = models.CharField(max_length=100)
    length = models.DecimalField(max_digits=12, decimal_places=3)
    height = models.DecimalField(max_digits=12, decimal_places=3)
    width = models.DecimalField(max_digits=12, decimal_places=3)
    weight = models.DecimalField(max_digits=12, decimal_places=3)
    created_at = models.DateTimeField(editable=False)
    updated_at = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL,
                                   related_name="%(class)s_created_by",
                                   null=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL,
                                   related_name="%(class)s_updated_by",
                                   null=True)

    def __str__(self):  # __str__ on Python 2
        """Overwritten method. See object class."""
        return self.box_id

    def save(self, *args, **kwargs):
        """Overwritten method. See Model class. On save update timestamps."""
        if not self.id:
            self.created_at = get_aware_datetime()
        self.updated_at = get_aware_datetime()
        return super(Box, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-updated_at', 'box_id']


class Sample(models.Model):
    """
    Experiment sample.

    Attributes:
        set_id (CharField): sample id.
        name (CharField): name of sample.
        current_location (CharField): current location of sample.
        height (DecimalField): height of sample.
        width (DecimalField): width of sample.
        weight (DecimalField): weight of sample.
        comments (TextField): additional comments.
        req_fluence (ReqFluence): requested fluence for sample.
        material (Material): material used in sample.
        category (CharField): category of sample.
        storage (CharField): requested storage temperature.
        status (CharField): status of sample.
        last_location (CharField): building where sample was last located.
        experiment (Experiment): experiment instance where sample belongs.
        box (Box): Box where sample is stored.
        radiation_length_occupancy (PositiveIntegerField): Radiation length.
        nu_coll_length_occupancy (PositiveIntegerField): Nuclear collision length.
        nu_int_length_occupancy (PositiveIntegerField): Nuclear interaction length.
        created_at (DateField): creation timestamp.
        updated_at (DateField): lastest update's timestamp.
        created_by (User): user who created instance.
        updated_by (User): user who last updated instance.
    """
    set_id = models.CharField(max_length=50, null=True)
    name = models.CharField(max_length=200, unique=True)
    current_location = models.CharField(max_length=100)
    height = models.DecimalField(max_digits=12, decimal_places=3)
    width = models.DecimalField(max_digits=12, decimal_places=3)
    weight = models.DecimalField(max_digits=12, decimal_places=3, null=True)
    comments = models.TextField()
    req_fluence = models.ForeignKey(ReqFluence, on_delete=models.SET_NULL, null=True)
    material = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True)
    category = models.CharField(max_length=200)
    storage = models.CharField(max_length=50, choices=STORAGE)
    #samples characteristics
    status = models.CharField(max_length=50, choices=STATUS)
    last_location = models.CharField(max_length=100, null=True)
    experiment = models.ForeignKey(Experiment, on_delete=models.SET_NULL, null=True)
    box = models.ForeignKey(Box, on_delete=models.SET_NULL, null=True)
    radiation_length_occupancy = models.DecimalField(max_digits=9,
        decimal_places=3, null=True)
    nu_coll_length_occupancy = models.DecimalField(max_digits=9,
        decimal_places=3, null=True)
    nu_int_length_occupancy = models.DecimalField(max_digits=9,
        decimal_places=3, null=True)
    created_at = models.DateTimeField(editable=False)
    updated_at = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL,
        related_name="%(class)s_created_by", null=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL,
        related_name="%(class)s_updated_by", null=True)

    def __str__(self):  # __str__ on Python 2
        """Overwritten method. See object class."""
        return self.name

    def save(self, *args, **kwargs):
        """Overwritten method. See Model class."""
        if not self.id:
            self.created_at = get_aware_datetime()
        self.updated_at = get_aware_datetime()
        self.set_additional_info()
        super(Sample, self).save(*args, **kwargs)
        if self.experiment:
            self.experiment.save()
    
    def set_additional_info(self):
        """Method to set additional information in model."""
        occ_list = Occupancy.objects.filter(sample=self.id)
        radiation_length_occupancy = 0
        nu_coll_length_occupancy = 0
        nu_int_length_occupancy = 0
        for occ in occ_list:
            radiation_length_occupancy += occ.radiation_length_occupancy
            nu_coll_length_occupancy += occ.nu_coll_length_occupancy
            nu_int_length_occupancy += occ.nu_int_length_occupancy
        
        self.radiation_length_occupancy = radiation_length_occupancy
        self.nu_coll_length_occupancy = nu_coll_length_occupancy
        self.nu_int_length_occupancy = nu_int_length_occupancy

    class Meta:
        ordering = ['-updated_at', 'set_id']


class Occupancy(models.Model):
    """
    Sample Occupancy.

    Portion of irradiation table occupied by sample in terms of 
    irradiation length.

    Attributes:
        radiation_length_occupancy (DecimalField): radiation length ratio of sample.
        nu_coll_length_occupancy (DecimalField): nuclear collision ratio of sample.
        nu_int_length_occupancy (DecimalField): nuclear interaction ratio of sample.
        sample (Sample): Sample instance where occupancy belongs.
    """
    radiation_length_occupancy = models.DecimalField(max_digits=9,
                                                     decimal_places=3)
    nu_coll_length_occupancy = models.DecimalField(max_digits=9,
                                                   decimal_places=3)
    nu_int_length_occupancy = models.DecimalField(max_digits=9,
                                                  decimal_places=3)
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE, null=True)

    def __str__(self):  # __str__ on Python 2
        """Overwritten method. See object class."""
        return str(self.radiation_length_occupancy) + ' ' + str(
            self.nu_coll_length_occupancy) + ' ' + str(
                self.nu_int_length_occupancy)

    def save(self, *args, **kwargs):
        """Overwritten method. See Model class."""
        super(Occupancy, self).save(*args, **kwargs)
        if self.sample:
            self.sample.save()


class Dosimeter(models.Model):
    """
    Dosimeter. Key component to measure radiation during experiment.

    Attributes:
        dos_id (CharField): dosimeter id.
        responsible (User): user responsible of dosimeter.
        current_location (CharField): location of dosimeter.
        length (DecimalField): length of dosimeter.
        height (DecimalField): height of dosimeter.
        width (DecimalField): width of dosimeter.
        weight (DecimalField): weight of dosimeter.
        foils_number (PositiveIntegerField): number of foils 
            used in dosimeter.
        status (CharField): status of dosimeter.
        dos_type (CharField): type of foils used.
        comments (TextField): additional comments.
        box (Box): Box where dosimeter is stored.
        last_location (CharField): latest location were dosimeter was stored.
        parent_dosimeter (Dosimeter): parent of dosimeter. For spectometry 
            limitations a dosimeter can be divided into smaller parts and 
            this field associates the original dosimeter with divided parts.
        created_at (DateField): creation timestamp.
        updated_at (DateField): lastest update's timestamp.
        created_by (User): user who created instance.
        updated_by (User): user who last updated instance.
    """
    dos_id = models.CharField(max_length=50, unique=True)
    responsible = models.ForeignKey(User, on_delete=models.SET_NULL,
                                    related_name='%(class)s_responsible',
                                    null=True)
    current_location = models.CharField(max_length=100, null=True)
    length = models.DecimalField(max_digits=18, decimal_places=6, null=True)
    height = models.DecimalField(max_digits=18, decimal_places=6, null=True)
    width = models.DecimalField(max_digits=18, decimal_places=6, null=True)
    weight = models.DecimalField(max_digits=21, decimal_places=9, null=True)
    foils_number = models.PositiveIntegerField(null=True)
    status = models.CharField(max_length=50, choices=STATUS)
    dos_type = models.CharField(max_length=50, choices=DOSIMETER_CATEGORY)
    comments = models.TextField(null=True)
    box = models.ForeignKey(Box, on_delete=models.SET_NULL, null=True)
    last_location = models.CharField(max_length=100, null=True)
    parent_dosimeter = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(editable=False)
    updated_at = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL,
                                   related_name='%(class)s_created_by',
                                   null=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL,
                                   related_name='%(class)s_updated_by',
                                   null=True)


    def __str__(self):  # __str__ on Python 2
        return str(self.dos_id)

    def save(self, *args, **kwargs):
        """Overwritten method. See Model class. On save update timestamps."""
        if not self.id:
            self.created_at = get_aware_datetime()
        self.updated_at = get_aware_datetime()
        super(Dosimeter, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-updated_at', 'dos_id']


class Element(models.Model):
    """
    Material element data model. It defines a portion of a compound.

    Attributes:
        atomic_number (PositiveIntegerField): atomic number of element.
        atomic_symbol (CharField): atomic symbol of element.
        atomic_mass (DecimalField): atomic mass of element.
        density (DecimalField): atomic density of element.
        min_ionization (DecimalField): minumum ionization.
        nu_coll_length (DecimalField): nuclear collision length.
        nu_int_length (DecimalField): nuclear interaction length.
        pi_coll_length (DecimalField): pion collision length.
        pi_int_length (DecimalField): pion interaction length.
        radiation_length (DecimalField): radiation length.
    """
    atomic_number = models.PositiveIntegerField()
    atomic_symbol = models.CharField(max_length=5)
    atomic_mass = models.DecimalField(max_digits=15, decimal_places=10)
    density = models.DecimalField(max_digits=9, decimal_places=7)
    min_ionization = models.DecimalField(max_digits=4, decimal_places=3)
    nu_coll_length = models.DecimalField(max_digits=4, decimal_places=1)
    nu_int_length = models.DecimalField(max_digits=4, decimal_places=1)
    pi_coll_length = models.DecimalField(max_digits=4, decimal_places=1)
    pi_int_length = models.DecimalField(max_digits=4, decimal_places=1)
    radiation_length = models.DecimalField(max_digits=4, decimal_places=2)

    def __str__(self):  # __str__ on Python 2
        """Overwritten method. See object class."""
        return str(self.atomic_symbol) + '(' + str(self.atomic_number) + ')'


class Compound(models.Model):
    """
    Compound data model.

    Attributes:
        name (CharField): name of compound.
        density (DecimalField): density of compound.
    """
    name = models.CharField(max_length=30, unique=True)
    density = models.DecimalField(max_digits=16, decimal_places=7, null=True)
    num_associated_samples = models.PositiveIntegerField(default=0)

    def __str__(self):  # __str__ on Python 2
        """Overwritten method. See object class."""
        return self.name

    def save(self, *args, **kwargs):
        """Overwritten method. See Model class. On save update timestamps."""
        self.num_associated_samples = self.get_num_associated_samples()
        super(Compound, self).save(*args, **kwargs)

    def get_num_associated_samples(self):
        layers = Layer.objects.filter(compound_type=self)
        result = []
        for layer in layers:
            if layer.sample not in result:
                result.append(layer.sample)
        return len(result)

    class Meta:
        ordering = ['name']


class CompoundElement(models.Model):
    """
    CompoundElement data model.

    Attributes:
        element_type (Element): element instance.
        percentage (DecimalField): percentage of element in compound.
        compound (Compound): compound instance.
    """
    element_type = models.ForeignKey(Element, on_delete=models.CASCADE)
    percentage = models.DecimalField(max_digits=15, decimal_places=4)
    compound = models.ForeignKey(Compound, on_delete=models.CASCADE, null=True)


class Layer(models.Model):
    """
    Layer data model. Part of a sample. One or more layers compose a sample.

    Attributes:
        name (CharField): name of layer.
        length (DecimalField): length/thickness of layer.
        compound_type (Compound): Compound instance.
        sample (Sample): Sample instace where layer is used.
    """
    name = models.CharField(max_length=20)
    length = models.DecimalField(max_digits=26, decimal_places=6)
    compound_type = models.ForeignKey(Compound, on_delete=models.SET_NULL, null=True)
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE, null=True)

    def __str__(self):  # __str__ on Python 2
        """Overwritten method. See object class."""
        return str(self.name)

    def save(self, *args, **kwargs):
        """Overwritten method. See Model class."""
        super(Layer, self).save(*args, **kwargs)
        if self.compound_type:
            self.compound_type.save()


class FluenceFactor(models.Model):
    """
    Fluence factor.

    Attributes:
        value (DecimalField): factor value.
        irrad_table (CharField): irradiation table.
        dosimeter_height (DecimalField): dosimeter height related to factor.
        dosimeter_width (DecimalField): dosimeter weight related to factor.
        is_scan (BooleanField): true if factor is for scanned irradiations.
        status (CharField): status of FluenceFactor. Only active factors 
            used in sec calculations.
        nuclide (CharField): nuclide related to dosimeter. This is 
            dosimetry-related information. 
        created_at (DateField): creation timestamp.
        updated_at (DateField): lastest update's timestamp.
    """
    value = models.DecimalField(max_digits=13, decimal_places=3, null=True)
    irrad_table = models.CharField(max_length=50, null=True)
    dosimeter_height = models.DecimalField(max_digits=18, decimal_places=6, null=True)
    dosimeter_width = models.DecimalField(max_digits=18, decimal_places=6, null=True)
    is_scan = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=FLUENCE_FACTOR_STATUS)
    nuclide = models.CharField(max_length=10, choices=FLUENCE_FACTOR_NUCLIDE)
    created_at = models.DateTimeField(editable=False, null=True)
    updated_at = models.DateTimeField(null=True)

    def save(self, *args, **kwargs):
        """Overwritten method. See Model class. On save update timestamps."""
        if not self.id:
            self.created_at = get_aware_datetime()
        self.updated_at = get_aware_datetime()
        return super(FluenceFactor, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-updated_at', 'irrad_table']


class Irradiation(models.Model):
    """
    Irradiation.

    Attributes:
        sample (Sample): sample instance.
        dosimeter (Dosimeter): dosimeter instance.
        previous_irradiation (Irradiation): previous irradiation used as base.
        fluence_factor (FluenceFactor): fluence factor corresponding to irradiation.
        date_in (DateTimeField): timestamp of beguinning of exposure to beam.
        date_out (DateTimeField): timestamp of end of exposure to beam.
        table_position (CharField): position of irradiation on table during experiment.
        irrad_table (CharField): irradiation table where experiment took place.
        sec (PositiveIntegerField): accumulated secondary emission
            chamber measurements of irradiation.
        estimated_fluence (DecimalField): accumulated fluence measured by dosimeter.
        fluence_error (DecimalField): fluence calculation error.
        status (CharField): status of irradiation.
        dos_position (PositiveIntegerField): position of dosimeter on irradiation
            table during experiment.
        is_scan (BooleanField): true if irradiation requires scanning.
        comments (TextField): additional comments.
        created_at (DateField): creation timestamp.
        updated_at (DateField): lastest update's timestamp.
        created_by (User): user who created instance.
        updated_by (User): user who last updated instance.
    """
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE, null=True)
    dosimeter = models.ForeignKey(Dosimeter, on_delete=models.CASCADE, null=True)
    previous_irradiation = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True)
    fluence_factor = models.ForeignKey(FluenceFactor, on_delete=models.SET_NULL, blank=True, null=True)
    date_in = models.DateTimeField(blank=True, null=True)
    date_out = models.DateTimeField(blank=True, null=True)
    date_first_sec = models.DateTimeField(blank=True, null=True)
    date_last_sec = models.DateTimeField(blank=True, null=True)
    table_position = models.CharField(max_length=50, null=True)
    irrad_table = models.CharField(max_length=50, null=True)
    sec = models.PositiveIntegerField(null=True)
    estimated_fluence = models.DecimalField(max_digits=38,
                                              decimal_places=18,
                                              null=True)
    measured_fluence = models.DecimalField(max_digits=38,
                                              decimal_places=18,
                                              null=True)
    fluence_error = models.DecimalField(max_digits=10,
                                        decimal_places=3,
                                        null=True)
    status = models.CharField(max_length=50, choices=STATUS)
    dos_position = models.PositiveIntegerField(null=True)
    is_scan = models.BooleanField(default=False)
    comments = models.TextField(null=True)
    created_at = models.DateTimeField(editable=False, null=True)
    updated_at = models.DateTimeField(null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL,
                                   related_name='%(class)s_created_by',
                                   null=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL,
                                   related_name='%(class)s_updated_by',
                                   null=True)

    def save(self, *args, **kwargs):
        """Overwritten method. See Model class. On save update timestamps."""
        if not self.id:
            self.created_at = get_aware_datetime()
        self.updated_at = get_aware_datetime()
        return super(Irradiation, self).save(*args, **kwargs)

    @staticmethod
    def get_beam_status():
        """Retrieves beam status' values for irradiations."""
        status = [key for key, value in STATUS \
            if 'beam' in key.lower()]
        in_beam = status[0]
        out_beam = status[1]
        return in_beam, out_beam

    class Meta:
        ordering = ['-updated_at', 'irrad_table']


class ArchiveExperimentSample(models.Model):
    """
    ArchiveExperimentSample data model.
    
    Used when samples are moved from one experiment to another.

    Attributes:
        timestamp (DateTimeField): timestamp of creation.
        experiment (Experiment): experiment where sample was used.
        sample (Sample): sample instance.
    """
    timestamp = models.DateTimeField(editable=False)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, null=True)
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE, null=True)

    def save(self, *args, **kwargs):
        """Overwritten method. See Model class. On save update timestamps."""
        if not self.id:
            self.timestamp = get_aware_datetime()
        return super(ArchiveExperimentSample, self).save(*args, **kwargs)

    class Meta:
        ordering = ['timestamp']
