from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class UserProfile(models.Model):
    id = models.AutoField(primary_key=True)
    userid = models.OneToOneField(User, on_delete=models.CASCADE)
    firstname = models.CharField(max_length=30)
    lastname = models.CharField(max_length=30)
    familyname = models.CharField(max_length=30)
    phonenumber = models.CharField(max_length=15)
    email = models.EmailField()
    password = models.CharField(max_length=255)
    status=models.IntegerField()
    

    def delete(self, *args, **kwargs):
        # Delete the associated User instance
        self.userid.delete()
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.email

class OwnerDetails(models.Model):
    pid = models.AutoField(primary_key=True)
    up = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    owner_first_name = models.CharField(max_length=255)
    owner_last_name = models.CharField(max_length=255)
    family_name = models.CharField(max_length=255)
    address_zambia = models.TextField()
    lcity=models.CharField(max_length=255)
    lprovince=models.CharField(max_length=255)
    address_india = models.TextField()
    GENDER_CHOICES = [('M', 'Male'),('F', 'Female'),('O', 'Other'),]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    dob = models.DateField()
    blood_group = models.CharField(max_length=10)
    work_name=models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)   
    contact_no_india = models.CharField(max_length=15)
    cperson = models.CharField(max_length=255)
    contact_no_zm = models.CharField(max_length=15)
    whatsapp_no = models.CharField(max_length=15)
    email = models.EmailField()
    zmstatus=models.CharField(max_length=15)
    status=models.IntegerField()
    # def save(self, *args, **kwargs):
    #     # Parse the 'DD/MM' formatted date and convert it to 'YYYY-MM-DD'
    #     if '/' in self.dob:
    #         day, month = self.dob.split('/')
    #         self.dob = f'2022-{month.zfill(2)}-{day.zfill(2)}'

    #     super().save(*args, **kwargs)

class SpouseDetails(models.Model):
    spid=models.AutoField(primary_key=True)
    up = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    spouse_name = models.CharField(max_length=255)
    GENDER_CHOICES = [('M', 'Male'),('F', 'Female'),('O', 'Other'),]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    spouse_dob = models.DateField()
    blood_group = models.CharField(max_length=10)
    spouse_phone_no = models.CharField(max_length=15)
    spouse_whatsapp_no = models.CharField(max_length=15)
    spouse_work = models.CharField(max_length=255)
    spouse_designation = models.CharField(max_length=255)
    spouse_email = models.EmailField()
    STATUS_CHOICES = [
        ('1', 'LivingInZambia'),
        ('2', 'LivingInOtherCountry'),
        ('3', 'Deceased'),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

class ChildrenDetails(models.Model):
    cid = models.AutoField(primary_key=True)
    up = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    child_name = models.CharField(max_length=255)
    GENDER_CHOICES = [('M', 'Male'),('F', 'Female'),('O', 'Other'),]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    BIRTH_ORDER_CHOICES = [
        ('Firstborn', 'Firstborn'),
        ('Secondborn', 'Secondborn'),
        ('Thirdborn', 'Thirdborn'),
       ('Fourtborn','Fourtborn'),
        ('Fifthborn', 'Fifthborn'),
        ('Sixthborn', 'Sixthborn'),
        ('seventhborn', 'seventhborn'),
       ('eighthborn','eighthborn'),
        ('ninenthborn', 'ninenthborn'),
       ('tenthborn','tenthborn'),]
    birth_order = models.CharField(max_length=15,choices=BIRTH_ORDER_CHOICES)
    dob = models.DateField()
    blood_group = models.CharField(max_length=10)
    status=models.IntegerField()
    
    def __str__(self):
        return f"{self.get_birth_order_display()} {self.get_gender_display()}"


class OtherDetails(models.Model):
   
    oid = models.AutoField(primary_key=True)
    up = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    fname = models.CharField(max_length=255)
    lname = models.CharField(max_length=255)
    GENDER_CHOICES = [('M', 'Male'),('F', 'Female'),('O', 'Other'),]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    whatsappno = models.CharField(max_length=15)
    email = models.EmailField()
    dob = models.DateField()
    blood_group = models.CharField(max_length=10)
    relationship_with_owner = models.CharField(max_length=255)
    status=models.IntegerField()

class Familyphoto(models.Model):
   
    fpid = models.AutoField(primary_key=True)
    up = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    familyphoto = models.ImageField(upload_to='family_photos/', null=True, blank=True)   
    status=models.IntegerField()





class HelperProfile(models.Model):
    STATUS_CHOICES = [
        ('SUBMITTED', 'Submitted'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    LIVE_IN_CHOICES = [
        ('LIVE_IN', 'Live-in'),
        ('LIVE_OUT', 'Live-out'),
    ]

    SKILL_CHOICES = [
        ('Cleaning', 'Cleaning'),
        ('Cooking', 'Cooking'),
        ('Childcare', 'Childcare'),
        ('Elderly care', 'Elderly care'),
    ]

    name = models.CharField(max_length=100)
    area = models.CharField(max_length=100)

    skills = models.CharField(
        max_length=50,
        choices=SKILL_CHOICES
    )

    live_in_status = models.CharField(
        max_length=10,
        choices=LIVE_IN_CHOICES
    )

    days_hours = models.CharField(max_length=200, help_text="e.g. Mon–Fri, 8am–5pm")
    experience = models.PositiveIntegerField(help_text="Years of experience")
    languages = models.CharField(max_length=200, help_text="e.g. English, Bemba")
    salary_range = models.CharField(max_length=100, blank=True, help_text="Optional")
    availability_date = models.DateField()
    contact_phone = models.CharField(max_length=20)
    contact_email = models.EmailField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='SUBMITTED'
    )
    nrc_document = models.FileField(
        upload_to='nrc_documents/',
        blank=True,
        help_text="Upload NRC document (PDF or image)"
    )
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


