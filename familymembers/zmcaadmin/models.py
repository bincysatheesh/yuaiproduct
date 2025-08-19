from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from members.models import UserProfile


# Create your models here.
class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    status=models.IntegerField()

    def __str__(self):
        return self.subject
    
    # PENDING = 0
    # COMPLETED = 1
    # PROCESSING = 2

    # STATUS_CHOICES = [
    #     (PENDING, 'Pending'),
    #     (COMPLETED, 'Completed'),
    #     (PROCESSING, 'Processing'),
    #       status = models.IntegerField(choices=STATUS_CHOICES)
 
    # ]

class CarouselImage(models.Model):
    STATUS_CHOICES = (
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    )

    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='carousel_images/')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')

    def __str__(self):
        return self.title

class GalleryCategory(models.Model):
    catname = models.CharField(max_length=100)

    def __str__(self):
        return self.catname

class GalleryImage(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='gallery_images/')
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    photoby = models.CharField(max_length=255)
    gallerycatid = models.ForeignKey(GalleryCategory, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
    



class CommitteeMember(models.Model):
    id = models.AutoField(primary_key=True)
    member_name = models.CharField(max_length=100)
    post = models.CharField(max_length=100)
    image = models.ImageField(upload_to='committee_member_images/', blank=True, null=True)

    year = models.IntegerField()
    status_choices = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]
    status = models.CharField(max_length=10, choices=status_choices)

    def __str__(self):
        return self.member_name

# class BirthdayWish(models.Model):
#     sender_email = models.EmailField()
#     recipient_email = models.EmailField()
#     message = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ['-timestamp']



class GalleryItem(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images/')
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20)

    def __str__(self):
        return self.title
    


class EventNotification(models.Model):
    id = models.AutoField(primary_key=True)
    event_name = models.CharField(max_length=100)
    description = models.TextField()
    date = models.DateField()
    timestamp = models.DateTimeField(auto_now_add=True)  # Change TimeField to DateTimeField

    status = models.CharField(max_length=20)
    image = models.ImageField(upload_to='images/')  # Define the image field

    def __str__(self):
        return self.event_name
    


class Blog(models.Model):
    id = models.AutoField(primary_key=True)
    image = models.ImageField(upload_to='blog_images/')
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    timestamp = models.DateTimeField(auto_now_add=True)
    author_name = models.CharField(max_length=100)
    
    # Define choices for the status field
    DRAFT = 'Draft'
    PUBLISHED = 'Published'
    STATUS_CHOICES = [
        (DRAFT, 'Draft'),
        (PUBLISHED, 'Published'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=DRAFT)

    def __str__(self):
        return self.title
    




class Membership(models.Model):
    MEMBERSHIP_STATUS = [
        (1, 'Active'),
        (0, 'Inactive'),
    ]
    
    MEMBER_CATEGORY_CHOICES = [
        ('With Family', 'With Family'),
        ('Alone', 'Alone'),
    ]

    membership_id = models.AutoField(primary_key=True)
    from_date = models.DateField()
    to_date = models.DateField()
    with_family_amount = models.DecimalField(max_digits=10, decimal_places=2)
    alone_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.IntegerField(choices=MEMBERSHIP_STATUS, default=1)

    def __str__(self):
        return f"Membership ID: {self.membership_id}, Status: {self.get_status_display()}"
    
class MembershipDetail(models.Model):
    PAYMENT_STATUS = [
        (1, 'Paid'),
        (0, 'Unpaid'),
    ]
    
    mdid = models.AutoField(primary_key=True)
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE)
    membership_year = models.CharField(max_length=9)  # Store the membership year as a string (e.g., "2023-2024")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, limit_choices_to={'status': 2})
    usercategory = models.CharField(max_length=255)  # Assuming you're storing the category as a string
    status = models.IntegerField(choices=PAYMENT_STATUS)

    def __str__(self):
        return f"Membership Detail ID: {self.mdid}, User: {self.user_profile}, Status: {'Paid' if self.status == 1 else 'Unpaid'}"





