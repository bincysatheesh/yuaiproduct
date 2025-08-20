from django.db import models
from django.contrib.auth.models import User
from multiselectfield import MultiSelectField



class Agency(models.Model):

    SERVICE_CATEGORIES = (
        ('Driver', 'Driver'),
        ('Maid', 'Maid'),
        ('Security Guard', 'Security Guard'),
        ('Garden Boy', 'Garden Boy'),
        ('Babysitter', 'Babysitter'),
        ('Others', 'Others'),

    )

    AGENCY_TYPES = (
        ('Maids', 'Maids'),
        ('Drivers', 'Drivers'),
        ('Security', 'Security'),
        ('Others', 'Others'),
    )

    AGENCY_STATUS = (
        ('Submitted', 'Submitted'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Suspended', 'Suspended'),
    )


    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='agencies')
    agency_name = models.CharField(max_length=255)
    agency_type = MultiSelectField(choices=AGENCY_TYPES, max_choices=3)
    owner_contact_person = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=20)
    email = models.EmailField()
    office_address = models.TextField()
    service_categories = MultiSelectField(choices=SERVICE_CATEGORIES)
    years_in_operation = models.PositiveIntegerField()
    number_of_staff = models.PositiveIntegerField()
    verification_documents = models.FileField(upload_to='verification_docs/')
    preferred_service_area = models.CharField(max_length=255, help_text="Comma-separated regions (e.g. Lusaka, Ndola)")
    availability = models.CharField(max_length=100, help_text="e.g. Mon–Sat, 8am–6pm")
    short_description = models.TextField()
    consent_agreed = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=AGENCY_STATUS, default='Submitted')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Agency"
        verbose_name_plural = "Agencies"
        ordering = ['-created_at']

    def __str__(self):
        return self.agency_name




class Staff(models.Model):

    
    SERVICE_TYPES = (
        ('Maid', 'Maid'),
        ('Driver', 'Driver'),
        ('Security Guard', 'Security Guard'),
        ('Gardener', 'Gardener'),
        ('Babysitter', 'Babysitter'),
        ('Others', 'Others'),

        
    )

    STAFF_STATUS = (
        ('Submitted', 'Submitted'),
        ('Approved', 'Approved'),
    )
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='agency')

    full_name = models.CharField(max_length=255, help_text="Full name or alias")
    photo = models.ImageField(upload_to='staff_photos/', blank=True, null=True)
    age = models.PositiveIntegerField()
    address = models.CharField(max_length=255, help_text="Residential or work area")
    service_type = models.CharField(max_length=50, choices=SERVICE_TYPES)
    skills_duties = models.TextField(help_text="Describe skills or duties")
    experience_years = models.PositiveIntegerField(default=0)
    languages = models.CharField(max_length=255, help_text="Comma-separated list of languages")
    availability = models.CharField(max_length=100, help_text="E.g. Mon–Fri, 8am–5pm")
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STAFF_STATUS, default='Submitted')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Staff Member"
        verbose_name_plural = "Staff Members"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.service_type}"
