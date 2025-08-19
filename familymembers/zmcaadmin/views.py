import calendar
import datetime
from datetime import date, datetime, timedelta
from django.http import Http404, HttpResponse, HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.urls import reverse
from django.views import View
from . models import *
from django.contrib.auth.models import User,auth
from members.models import UserProfile,OtherDetails,OwnerDetails,Familyphoto,SpouseDetails,ChildrenDetails
from django.core.paginator import Paginator, EmptyPage
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.mail import send_mail
from .helpers import send_contact_email
from django.template.loader import render_to_string
from django.utils import timezone

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile



from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models.functions import ExtractYear

from .helpers import sendapprovemail
import uuid
from django.conf import Settings
from django.core.mail import send_mail
from django.template.defaultfilters import truncatewords  # Import Django's built-in filter for truncating words
from .models import MembershipDetail,Membership


def index(request):
    current_date = timezone.now()
    current_month_start = datetime(current_date.year, current_date.month, 1)
    current_month_end = datetime(current_date.year, current_date.month + 1, 1) - timedelta(days=1)
    blog_items = Blog.objects.filter(date__range=[current_month_start, current_month_end])
    published_posts = Blog.objects.filter(status='Published').order_by('-timestamp')[:3] 
     # Assuming you want to display the three most recent published posts
      # Fetch the latest 6 gallery items
    latest_gallery_items = GalleryItem.objects.order_by('-timestamp')[:9]
    # print(latest_gallery_items)
    committee_members = CommitteeMember.objects.filter(status='Active')
    carousel_images = CarouselImage.objects.filter(status='Active')
    
    context = {'published_posts': published_posts,
               'latest_gallery_items':latest_gallery_items,
               'committee_members':committee_members,'carousel_images': carousel_images}
    return render(request, 'landing/index.html', context)



def blogs(request):
    b=Blog.objects.all()
    context={'b':b}
    return render(request,'landing/blog.html',context)



def gallery(request):    

    return render(request, 'admin/projects.html')

def committe(request):
    years = range(2000, 2100)  # Generate a range of years from 2000 to 2050
    committee_members = CommitteeMember.objects.all()

 # Search functionality
    search_query = request.GET.get('q')
    if search_query:
        committee_members = committee_members.filter(
            Q(member_name__icontains=search_query) |  # Search by member name (case-insensitive)
            Q(post__icontains=search_query) |        # Search by post (case-insensitive)
            Q(year__icontains=search_query) |        # Search by year (case-insensitive)
            Q(status__icontains=search_query)       # Search by status (case-insensitive)
        )


    paginator = Paginator(committee_members, 10)  # Paginate by 10 items per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == 'POST':
        # Retrieve data from the POST request
        member_name = request.POST.get('member_name')
        post = request.POST.get('post')
        year = request.POST.get('year')
        status = request.POST.get('status')
        image = request.FILES.get('image')  # Get the uploaded image
        
        # Create a new CommitteeMember object and save it to the database
        committee_member = CommitteeMember(
            member_name=member_name,
            post=post,
            year=year,
            status=status,
            image=image
        )
        committee_member.save()
        
        # Redirect to the same page after successful form submission
        return redirect('committe')
        
    return render(request, 'admin/committe.html', {'years': years, 'committee_members': page_obj})
def ourteam(request):
     # Fetching the latest Committee Members based on the year
    latest_committee_members = CommitteeMember.objects.filter(status='Active').order_by('-year')

    context = {
        'latest_committee_members': latest_committee_members
    }
  
    return render(request,'landing/team.html',context)



def editcommitte(request, member_id):
    member = get_object_or_404(CommitteeMember, id=member_id)
    years = range(2000, 2051)  # Generate a range of years from 2000 to 2050
    
    if request.method == 'POST':
        member_name = request.POST.get('member_name')
        post = request.POST.get('post')
        year = request.POST.get('year')
        image = request.FILES.get('image')  # Get the uploaded image file
        
        status = request.POST.get('status')
        
        # Update the member object with new data
        member.member_name = member_name
        member.post = post
        member.year = year
        member.status = status
            # Check if a new image was uploaded
        if image:
            # Save the uploaded image to the media directory
            file_path = default_storage.save('images/' + image.name, ContentFile(image.read()))
            # Update the member object with the new image URL
            member.image = file_path
        
        member.save()
        
        return redirect('committe')
    
    return render(request, 'admin/editcommitte.html', {'member': member, 'years': years})




def delete_member(request, member_id):
    # Fetch the member object corresponding to the given ID
    member = get_object_or_404(CommitteeMember, pk=member_id)

    # Check if the request method is POST
    if request.method == 'POST':
        # Delete the member object
        member.delete()
        # Redirect to a URL after successful deletion
        return redirect('committe')  # Adjust the URL name as needed

    # Render a template for confirmation or provide a response
    return render(request, 'admin/committe.html', {'member': member})

def gallerycat(request): 
    categories = GalleryCategory.objects.filter()
  
    if request.method == 'POST':
        catname = request.POST.get('catname')
        if catname:
            GalleryCategory.objects.create(catname=catname)
            return redirect('gallerycat',{'categories',categories})

    # Pagination
    paginator = Paginator(categories, 5)  # Show 5 categories per page
    page_number = request.GET.get('page')
    try:
        categories = paginator.page(page_number)
    except PageNotAnInteger:
        categories = paginator.page(1)
    except EmptyPage:
        categories = paginator.page(paginator.num_pages)
    
    
    context = {'categories': categories}

    return render(request, 'admin/gallerycategory.html', context)


def edit_category(request, category_id):
    category = get_object_or_404(GalleryCategory, id=category_id)
    if request.method == 'POST':
        catname = request.POST.get('catname')
        if catname:
            category.catname = catname
            category.save()
            return redirect('gallerycat')
    return render(request, 'admin/editgallerycategory.html', {'category': category})


def delete_category(request, category_id=None):
    if category_id is None:
        raise Http404("Category ID not provided")

    try:
        category_id = int(category_id)
    except ValueError:
        raise Http404("Invalid Category ID")

    category = get_object_or_404(GalleryCategory, id=category_id)
    category.delete()

    return redirect('gallerycat')


def contactus(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        admin_email = 'zmcazambia@gmail.com'  # Replace with the admin's email address
        
        try:
            # Save the form data to the ContactMessage model
            contact_message = ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message,
                status=0  # Set status to 0 for pending messages
            )
            
            # Send email to site admin
            send_contact_email(name, email, subject, message, admin_email)
            
            # Add a success message
            messages.success(request, 'Your message has been sent. Thank you!')
        except Exception as e:
            # If an error occurs, display an error message
            messages.error(request, 'An error occurred while sending your message. Please try again later.')
            # Print the error to the console for debugging
            print(f"Error sending email: {e}")
        
        # Redirect to the contact page after processing the form submission
        return redirect('contactus')
    
    # If the request method is not POST, render the contact form page
    return render(request, 'landing/contact.html')

def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)

def adminindex(request):
    ua = UserProfile.objects.filter(status=1)
    uacount = ua.count()
    enquiry = ContactMessage.objects.filter(status=0)
    ecount = enquiry.count()
     # Fetch all contact messages
  # Fetch the latest 5 contact messages
    lm = ContactMessage.objects.order_by('-timestamp')[:5]


    # tf = UserProfile.objects.filter(status=2)
    tf = UserProfile.objects.filter(status__in=[2, 3])

    tfc = tf.count()
    
    up = UserProfile.objects.all().count()
    # owners_count = OwnerDetails.objects.filter(up__status__in=[2, 3]).count()

  # Count owner details with UserProfile status 2 or 3
    owners_count = OwnerDetails.objects.filter(Q(up__status=2) | Q(up__status=3)).count()

# Count spouse details with UserProfile status 2 or 3
    spouses_count = SpouseDetails.objects.filter(Q(up__status=2) | Q(up__status=3)).count()

# Count children details with UserProfile status 2 or 3
    children_count = ChildrenDetails.objects.filter(Q(up__status=2) | Q(up__status=3)).count()

# Count other details with UserProfile status 2 or 3
    other_details_count = OtherDetails.objects.filter(Q(up__status=2) | Q(up__status=3)).count()
    tc = owners_count + spouses_count + children_count + other_details_count

    query = request.GET.get('q')  # Get the search query from the request
    user_profiles = UserProfile.objects.filter(status=1)

    if query:  # If a search query exists
        user_profiles = user_profiles.filter(
            Q(firstname__icontains=query) |
            Q(lastname__icontains=query) |
            Q(familyname__icontains=query) |
            Q(phonenumber__icontains=query) |
            Q(email__icontains=query)
        )

    paginator = Paginator(user_profiles, 7)  # 7 items per page

    page_number = request.GET.get('page')
    try:
        user_profiles_paginated = paginator.page(page_number)
    except PageNotAnInteger:
        user_profiles_paginated = paginator.page(1)
    except EmptyPage:
        user_profiles_paginated = paginator.page(paginator.num_pages)
    from datetime import datetime

# Get the current year
    current_year = datetime.now().year

# Count committee members for the current year or the next year
    # committee_members_count = CommitteeMember.objects.filter(year__in=[current_year, current_year + 1]).count()

    committee_members_count = CommitteeMember.objects.filter(status='Active').count()
 

    return render(request, 'admin/adminindex.html', {'user_profiles': user_profiles_paginated, 't': tc, 'tf': tfc, 'ua': ua, 'uac': uacount,'ecount':ecount,'enquiry':lm,'c':committee_members_count})

def members_view(request):
    ua = UserProfile.objects.filter(status__in=[2, 3])
    uacount = ua.count()

    up = UserProfile.objects.all().count()
    owners_count = OwnerDetails.objects.filter(up__status__in=[2, 3]).count()
    spouses_count = SpouseDetails.objects.filter(up__status__in=[2, 3]).count()
    children_count = ChildrenDetails.objects.filter(up__status__in=[2, 3]).count()
    other_details_count = OtherDetails.objects.filter(up__status__in=[2, 3]).count()
    tf = up
    tc = owners_count + spouses_count + children_count + other_details_count
    members_info = UserProfile.objects.filter(status__in=[2, 3])
    owner = OwnerDetails.objects.filter(up__status__in=[2, 3])
    spouse = SpouseDetails.objects.filter(up__status__in=[2, 3])
    children = ChildrenDetails.objects.filter(up__status__in=[2, 3])
    other = OtherDetails.objects.filter(up__status__in=[2, 3])

    total_user_profiles = members_info.count()
    owner_details_info = OwnerDetails.objects.all()

    query = request.GET.get('q')
    if query:
        members_info = members_info.filter(
            Q(firstname__icontains=query) |
            Q(lastname__icontains=query) |
            Q(familyname__icontains=query) |
            Q(email__icontains=query) |
            Q(phonenumber__icontains=query) |
            Q(ownerdetails__owner_first_name__icontains=query) |
            Q(ownerdetails__owner_last_name__icontains=query) |
            Q(ownerdetails__address_zambia__icontains=query) |
            Q(ownerdetails__lcity__icontains=query) |
            Q(ownerdetails__lprovince__icontains=query) |
            Q(ownerdetails__address_india__icontains=query) |
            Q(ownerdetails__gender__icontains=query) |
            Q(ownerdetails__dob__icontains=query) |
            Q(ownerdetails__blood_group__icontains=query) |
            Q(ownerdetails__work_name__icontains=query) |
            Q(ownerdetails__company_name__icontains=query) |
            Q(ownerdetails__contact_no_india__icontains=query) |
            Q(ownerdetails__contact_no_zm__icontains=query) |
            Q(ownerdetails__whatsapp_no__icontains=query) |
            Q(ownerdetails__email__icontains=query) |
            Q(ownerdetails__zmstatus__icontains=query)|
            Q(spousedetails__spouse_name__icontains=query) |
            Q(spousedetails__gender__icontains=query) |
            Q(spousedetails__spouse_dob__icontains=query) |
            Q(spousedetails__blood_group__icontains=query) |
            Q(spousedetails__spouse_phone_no__icontains=query) |
            Q(spousedetails__spouse_whatsapp_no__icontains=query) |
            Q(spousedetails__spouse_work__icontains=query) |
            Q(spousedetails__spouse_email__icontains=query) |
            Q(spousedetails__status__icontains=query) |
            Q(childrendetails__child_name__icontains=query) |
            Q(childrendetails__gender__icontains=query) |
            Q(childrendetails__birth_order__icontains=query) |
            Q(childrendetails__dob__icontains=query) |
            Q(childrendetails__blood_group__icontains=query) |
            Q(childrendetails__status__icontains=query) |
            Q(otherdetails__fname__icontains=query) |
            Q(otherdetails__lname__icontains=query) |
            Q(otherdetails__gender__icontains=query) |
            Q(otherdetails__whatsappno__icontains=query) |
            Q(otherdetails__email__icontains=query) |
            Q(otherdetails__dob__icontains=query) |
            Q(otherdetails__blood_group__icontains=query) |
            Q(otherdetails__relationship_with_owner__icontains=query) |
            Q(otherdetails__status__icontains=query)
        ).distinct()

    items_per_page = 7
    paginator = Paginator(members_info, items_per_page)
    page_number = request.GET.get('page', 1)

    try:
        current_page = paginator.page(page_number)
    except EmptyPage:
        current_page = paginator.page(paginator.num_pages)

    for user in current_page:
        owner_complete = OwnerDetails.objects.filter(up=user).exists()
        spouse_complete = SpouseDetails.objects.filter(up=user).exists()
        child_complete = ChildrenDetails.objects.filter(up=user).exists()
        other_complete = OtherDetails.objects.filter(up=user).exists()
        photo_complete = Familyphoto.objects.filter(up=user).exists()

        user.owner_completion_percentage = calculate_completion_percentage(owner_complete)
        user.spouse_completion_percentage = calculate_completion_percentage(spouse_complete)
        user.child_completion_percentage = calculate_completion_percentage(child_complete)
        user.other_completion_percentage = calculate_completion_percentage(other_complete)
        user.photo_completion_percentage = calculate_completion_percentage(photo_complete)

        user.owner_complete = owner_complete
        user.spouse_complete = spouse_complete
        user.child_complete = child_complete
        user.other_complete = other_complete
        user.photo_complete = photo_complete

        user.owner_count = OwnerDetails.objects.filter(up=user).count()
        user.spouse_count = SpouseDetails.objects.filter(up=user).count()
        user.child_count = ChildrenDetails.objects.filter(up=user).count()
        user.other_count = OtherDetails.objects.filter(up=user).count()
        user.total = user.owner_count + user.spouse_count + user.child_count + user.other_count

    context = {
        'uacount': uacount,
        'tf': tf,
        'members_info': current_page,
        't': tc,
        'owner': owner,
        'sp': spouse,
        'children': children,
        'other': other,
        'spouse': spouses_count,
        'child': children_count,
        'other': other_details_count,
        'current': uacount,
        'current_page':current_page,
    }

    return render(request, 'admin/membersview.html', context)

def calculate_completion_percentage(complete):
    return 100 if complete else 0

# def members_view(request):
#     # Retrieve information from UserProfile and related models
#     members_info = UserProfile.objects.filter(status=2)

#     # Calculate the total count of members
#     total_members_count = members_info.count()
    
#     # Fetch related information for each member
#     for member in members_info:
#         member.owner_details = OwnerDetails.objects.filter(up=member)
#         member.spouse_details = SpouseDetails.objects.filter(up=member)
#         member.children_details = ChildrenDetails.objects.filter(up=member)
#         member.other_details = OtherDetails.objects.filter(up=member)
#         member.family_photos = Familyphoto.objects.filter(up=member)

#     # Set the number of items per page
#     items_per_page = 7

#     # Create a Paginator instance
#     paginator = Paginator(members_info, items_per_page)

#     # Get the current page number from the request's GET parameters
#     page = request.GET.get('page', 1)

#     try:
#         # Get the current page
#         current_page = paginator.page(page)
#     except EmptyPage:
#         # If the page is out of range, deliver the last page of results
#         current_page = paginator.page(paginator.num_pages)

#     # Pass the data to the template
#     context = {
#         'members_info': current_page,
#         'current_page': current_page,
#         't': total_members_count,
#     }

#     return render(request, 'admin/membersview.html', context)


def fam_view(request):
    ua= UserProfile.objects.filter(status__in=[2,3])
    uacount=ua.count()
    # Retrieve information from UserProfile and OwnerDetails models
    up = UserProfile.objects.all().count()
    owners_count = OwnerDetails.objects.all().count()
    spouses_count = SpouseDetails.objects.all().count()
    children_count = ChildrenDetails.objects.all().count()
    other_details_count = OtherDetails.objects.all().count()
    tc=0
    tf=0
    tf=up
    #total
    tc = owners_count + spouses_count + children_count + other_details_count
    # members_info = UserProfile.objects.all()
    members_info = UserProfile.objects.filter(status__in=[2,3])
    # Count the total number of user profiles
    total_user_profiles = members_info.count()
    owner_details_info = OwnerDetails.objects.all()

    
  
    # Search functionality
    query = request.GET.get('q')
    if query:
        # Filter user profiles based on search query
        members_info = members_info.filter(
            Q(firstname__icontains=query) |
            Q(lastname__icontains=query) |
            Q(familyname__icontains=query) |
            Q(email__icontains=query) |
            Q(phonenumber__icontains=query) |
            Q(ownerdetails__owner_first_name__icontains=query) |
            Q(ownerdetails__owner_last_name__icontains=query) |
            Q(ownerdetails__address_zambia__icontains=query) |
            Q(ownerdetails__lcity__icontains=query) |
            Q(ownerdetails__lprovince__icontains=query) |
            Q(ownerdetails__address_india__icontains=query) |
            Q(ownerdetails__gender__icontains=query) |
            Q(ownerdetails__dob__icontains=query) |
            Q(ownerdetails__blood_group__icontains=query) |
            Q(ownerdetails__work_name__icontains=query) |
            Q(ownerdetails__company_name__icontains=query) |
            Q(ownerdetails__contact_no_india__icontains=query) |
            Q(ownerdetails__contact_no_zm__icontains=query) |
            Q(ownerdetails__whatsapp_no__icontains=query) |
            Q(ownerdetails__email__icontains=query) |
            Q(ownerdetails__zmstatus__icontains=query)|
            Q(spousedetails__spouse_name__icontains=query) |  # Filtering based on spouse details
            Q(spousedetails__gender__icontains=query) |
            Q(spousedetails__spouse_dob__icontains=query) |
            Q(spousedetails__blood_group__icontains=query) |
            Q(spousedetails__spouse_phone_no__icontains=query) |
            Q(spousedetails__spouse_whatsapp_no__icontains=query) |
            Q(spousedetails__spouse_work__icontains=query) |
            Q(spousedetails__spouse_email__icontains=query) |
            Q(spousedetails__status__icontains=query) |
            Q(childrendetails__child_name__icontains=query) |  # Filtering based on children details
            Q(childrendetails__gender__icontains=query) |
            Q(childrendetails__birth_order__icontains=query) |
            Q(childrendetails__dob__icontains=query) |
            Q(childrendetails__blood_group__icontains=query) |
            Q(childrendetails__status__icontains=query) |
            Q(otherdetails__fname__icontains=query) |  # Filtering based on other details
            Q(otherdetails__lname__icontains=query) |
            Q(otherdetails__gender__icontains=query) |
            Q(otherdetails__whatsappno__icontains=query) |
            Q(otherdetails__email__icontains=query) |
            Q(otherdetails__dob__icontains=query) |
            Q(otherdetails__blood_group__icontains=query) |
            Q(otherdetails__relationship_with_owner__icontains=query) |
            Q(otherdetails__status__icontains=query)
        ).distinct()
     # Calculate completion percentages for each user
    for user in members_info:
        owner_complete = OwnerDetails.objects.filter(up=user).exists()
        spouse_complete = SpouseDetails.objects.filter(up=user).exists()
        child_complete = ChildrenDetails.objects.filter(up=user).exists()
        other_complete = OtherDetails.objects.filter(up=user).exists()
        photo_complete = Familyphoto.objects.filter(up=user).exists()

        # Add owner_complete attribute to the user object
        user.owner_complete = owner_complete
        user.spouse_complete = spouse_complete
        user.child_complete = child_complete
        user.other_complete = other_complete
        user.photo_complete = photo_complete
         # Count owner, spouse, children, and other details for the current user
        user.owner_count = OwnerDetails.objects.filter(up=user).count()
        user.spouse_count = SpouseDetails.objects.filter(up=user).count()
        user.child_count = ChildrenDetails.objects.filter(up=user).count()
        user.other_count = OtherDetails.objects.filter(up=user).count()
        user.total=0
        user.total=user.owner_count+user.spouse_count+user.child_count+user.other_count


         # Fetch membership details for each user profile
        membership_details = MembershipDetail.objects.filter(user_profile=user).first()
        if membership_details:
            # If membership details exist, set the payment status
            user.payment_status = "Paid" if membership_details.status == 1 else "Unpaid"
        else:
            # If membership details do not exist, set the payment status as not found
            user.payment_status = "Membership detail not found"








    # -----------paginator----------
     # Set the number of items per page
    items_per_page = 7

    # Create a Paginator instance
    paginator = Paginator(members_info, items_per_page)

    # Get the current page number from the request's GET parameters
    page = request.GET.get('page', 1)

    try:
        # Get the current page
        current_page = paginator.page(page)
    except EmptyPage:
        # If the page is out of range, deliver the last page of results
        current_page = paginator.page(paginator.num_pages)

        
    # -----------end paginator-------

    # Pass the data to the template
    context = {
             'owner_details_info': owner_details_info,
        't':tc,'tf':tf,
        'members_info': current_page,
        't': tc,
        'tf': tf,
        'current_page': current_page,
        'uac':uacount,
    }

    return render(request, 'admin/fam.html', context)

def view_family(request, user_id):
    # Retrieve the user profile for the given user_id
    user_profile = get_object_or_404(UserProfile, id=user_id)
    

    # Retrieve family details related to the user_profile
    owner_details = OwnerDetails.objects.filter(up=user_profile)
    spouse_details = SpouseDetails.objects.filter(up=user_profile)
    children_details = ChildrenDetails.objects.filter(up=user_profile)
    other_details = OtherDetails.objects.filter(up=user_profile)

    # Retrieve family photos for the given user profile
    family_photos = Familyphoto.objects.filter(up=user_profile).first()
    



    # Prepare the context for rendering the template
    context = {
        'user_profile': user_profile,
        'od': owner_details,
        'sd': spouse_details,
        'cd': children_details,
        'other': other_details,
        'fp': family_photos,
        #  'membership_details': membership_details,
        #   'payment_status': payment_status,  # Add payment status to the context
    }
    
    # Render the 'viewfamily.html' template with the provided context
    return render(request, 'admin/viewfamily.html',context)


# def approvefamily(request, family_id):
#     # Get the Family object
#         family_instance = get_object_or_404(UserProfile, id=family_id)

#     # Update the status in the Family table
#         family_instance.status = 2  # Assuming 2 means 'Approved'
#         family_instance.save()

#     # Update is_superuser in the user table
#         user_instance = family_instance.userid
#         user_instance.last_name = "approved"  # Assuming 'approved' for is_superuser
#         user_instance.save()

#     # Redirect to the nurserylist page
#         return redirect('members_view')


def approvefamily(request, family_id):
    try:
        # Get the Family object
        family_instance = get_object_or_404(UserProfile, id=family_id)

        # Update the status in the Family table
        family_instance.status = 2  # Assuming 2 means 'Approved'
        family_instance.save()

        # Update is_superuser in the user table
        user_instance = family_instance.userid
        user_instance.last_name = "approved"  # Assuming 'approved' for is_superuser
        user_instance.save()

        # Get the username (assuming it is the email) from the user profile
        username = family_instance.userid.username

        # Send the approval email
        sendapprovemail(username)

        # Redirect to the members_view page
        return redirect('members_view')

    except Exception as e:
        print(e)
        messages.error(request, 'An error occurred.')
        return redirect('members_view')

def deletefamily1(request, f_id=None):
    try:
        if f_id is None:
            raise Http404("Family ID not provided")
        
        f_id = int(f_id)
        
        family = get_object_or_404(UserProfile, id=f_id)
        family.delete()

        return redirect('fam_view')

    except ValueError:
        # Handle the case where f_id is not a valid integer
        raise Http404("Invalid Family ID")
    except UserProfile.DoesNotExist:
        # Handle the case where UserProfile with given ID does not exist
        raise Http404("Family not found")
    
def deletefamily(request, f_id=None):
    try:
        if f_id is None:
            raise Http404("Family ID not provided")
        
        f_id = int(f_id)
        
        family = get_object_or_404(UserProfile, id=f_id)
        family.delete()

        return redirect('adminindex')

    except ValueError:
        # Handle the case where f_id is not a valid integer
        raise Http404("Invalid Family ID")
    except UserProfile.DoesNotExist:
        # Handle the case where UserProfile with given ID does not exist
        raise Http404("Family not found")
    
@login_required
def delete_owner(request, user_profile_id):
    # if not request.user.is_superuser:
    #     return HttpResponseForbidden("Permission denied")

    user_profile = get_object_or_404(UserProfile, id=user_profile_id)

    # Additional checks if needed

    # Delete owner details
    owner_details = OwnerDetails.objects.filter(up=user_profile)
    owner_details.delete()

    # Finally, delete the user profile
    # user_profile.delete()

    return redirect('view_family')  # Redirect to the appropriate page after deletion

@login_required
def delete_spouse(request, user_profile_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Permission denied")

    user_profile = get_object_or_404(UserProfile, id=user_profile_id)

    # Additional checks if needed

    # Delete spouse details
    spouse_details = SpouseDetails.objects.filter(up=user_profile)
    spouse_details.delete()

    return redirect('view_family')  # Redirect to the appropriate page after deletion

@login_required
def delete_children(request, user_profile_id):
    # if not request.user.is_superuser:
    #     return HttpResponseForbidden("Permission denied")

    user_profile = get_object_or_404(UserProfile, id=user_profile_id)

    # Additional checks if needed

    # Delete children details
    children_details = ChildrenDetails.objects.filter(up=user_profile)
    children_details.delete()

    return redirect('view_family')  # Redirect to the appropriate page after deletion

@login_required
def delete_other_details(request, user_profile_id):
    # if not request.user.is_superuser:
    #     return HttpResponseForbidden("Permission denied")

    user_profile = get_object_or_404(UserProfile, id=user_profile_id)

    # Additional checks if needed

    # Delete other details
    other_details = OtherDetails.objects.filter(up=user_profile)
    other_details.delete()

    return redirect('view_family')  # Redirect to the appropriate page after deletion

@login_required
def delete_family_photo(request, user_profile_id):
    # if not request.user.is_superuser:
    #     return HttpResponseForbidden("Permission denied")

    user_profile = get_object_or_404(UserProfile, id=user_profile_id)

    # Additional checks if needed

    # Delete family photo
    family_photo = Familyphoto.objects.filter(up=user_profile).first()
    if family_photo:
        family_photo.delete()

    return redirect('view_family')


def adminedit_owner(request, user_profile_id):
    owner = get_object_or_404(OwnerDetails, pid=user_profile_id)

    if request.method == 'POST':
        # If the form is submitted, update the existing owner data
        owner.owner_first_name = request.POST.get('owner_first_name')
        owner.owner_last_name = request.POST.get('owner_last_name')
        owner.family_name = request.POST.get('family_name')
        owner.address_zambia = request.POST.get('address_zambia')
        owner.lcity = request.POST.get('lcity')
        owner.lprovince = request.POST.get('lprovince')
        owner.address_india = request.POST.get('address_india')
        owner.gender = request.POST.get('gender')
        owner.dob = f'2022-{request.POST.get("dob_month")}-{request.POST.get("dob_day")}'  # Concatenate month and day
        owner.blood_group = request.POST.get('blood_group')
        owner.work_name = request.POST.get('work_name')
        owner.company_name = request.POST.get('company_name')
        owner.contact_no_india = request.POST.get('contact_no_india')
        owner.contact_no_zm = request.POST.get('contact_no_zm')
        owner.whatsapp_no = request.POST.get('whatsapp_no')
        owner.email = request.POST.get('email')
        owner.zmstatus = request.POST.get('zmstatus')
        owner.status = 1

        # Validate and construct the date
        try:
            # Using a fixed year (e.g., 2022)
            dob = datetime.strptime(owner.dob, '%Y-%m-%d').strftime('%Y-%m-%d')
            owner.dob = dob
        except ValueError as e:
            messages.error(request, f'Invalid date of birth. {str(e)}')
            return render(request, 'admin/admineditowner.html', {'owner': owner})

        owner.save()

        # Redirect to a success page or any other desired page
        return redirect('view_family', user_id=owner.up.id)

    else:
        # If it's a GET request, pre-fill the form with existing data
        # Extracting year, month, and day from the saved date
        dob_month = owner.dob.month
        dob_day = owner.dob.day

        dob_month_names = list(calendar.month_name)[1:]
        dob_days = [str(i).zfill(2) for i in range(1, 32)]

        context = {
            'owner': owner,
            'dob_month_names': dob_month_names,
            'dob_days': dob_days,
            'dob_month': dob_month,
            'dob_day': dob_day,
        }
        return render(request, 'admin/admineditowner.html', context)


def enquiry_list(request):
    # Retrieve all messages with status=0
    enquiries = ContactMessage.objects.filter(status=0)
    ecount = enquiries.count()

# search
    query = request.GET.get('q')
    if query:
        # Filter user profiles based on search query
        enquiries = enquiries.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(subject__icontains=query) |
            Q(message__icontains=query))

    # paginator
    paginator = Paginator(enquiries, 15)  # 7 items per page
    page_number = request.GET.get('page')
    try:
        enquiries_paginated = paginator.page(page_number)
    except PageNotAnInteger:
        enquiries_paginated = paginator.page(1)
    except EmptyPage:
        enquiries_paginated = paginator.page(paginator.num_pages)

    return render(request, 'admin/enquiry.html', {'enquiries':enquiries_paginated,'ecount':ecount})


def delete_enquiry(request, message_id):
    # Retrieve the contact message object
    message = get_object_or_404(ContactMessage, id=message_id)
    
    # Delete the contact message
    message.delete()
    
    # Redirect to the enquiry list page
    return redirect('enquiry_list')

def delete_enquiry1(request, message_id):
    # Retrieve the contact message object
    message = get_object_or_404(ContactMessage, id=message_id)
    
    # Delete the contact message
    message.delete()
    
    # Redirect to the enquiry list page
    return redirect('allenquiry_list')


def allenquiry_list(request):
    # Retrieve all messages with status=0/1
    # enquiries = ContactMessage.objects.all()
    # Filter enquiries based on status
    enquiries = ContactMessage.objects.filter(status__in=[1])

    ecount = enquiries.count()
    statuses = {
        0: 'PENDING',
        1: 'PROCESSING',
        2: 'COMPLETED'
    }

    # Iterate over each enquiry and set its status
    for enquiry in enquiries:
        enquiry.status = statuses.get(enquiry.status, statuses)


   # Filter by status if requested
    status_filter = request.GET.get('status')
    if status_filter in ['0', '1']:
        enquiries = enquiries.filter(status=status_filter)


# search
    query = request.GET.get('q')
    if query:
        # Filter user profiles based on search query
        enquiries = enquiries.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(subject__icontains=query) |
            Q(message__icontains=query))

    # paginator
    paginator = Paginator(enquiries, 15)  # 7 items per page
    page_number = request.GET.get('page')
    try:
        enquiries_paginated = paginator.page(page_number)
    except PageNotAnInteger:
        enquiries_paginated = paginator.page(1)
    except EmptyPage:
        enquiries_paginated = paginator.page(paginator.num_pages)

    return render(request, 'admin/allenquiry.html', {'enquiries':enquiries_paginated,'ecount':ecount,'statuses':statuses})


def completedenquirylist(request):
    # Retrieve all messages with status=0/1
    # enquiries = ContactMessage.objects.all()
    # Filter enquiries based on status
    enquiries = ContactMessage.objects.filter(status__in=[2])

    ecount = enquiries.count()
    statuses = {
        0: 'PENDING',
        1: 'PROCESSING',
        2: 'COMPLETED'
    }

    # Iterate over each enquiry and set its status
    for enquiry in enquiries:
        enquiry.status = statuses.get(enquiry.status, statuses)


   # Filter by status if requested
    status_filter = request.GET.get('status')
    if status_filter in ['0', '1']:
        enquiries = enquiries.filter(status=status_filter)


# search
    query = request.GET.get('q')
    if query:
        # Filter user profiles based on search query
        enquiries = enquiries.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(subject__icontains=query) |
            Q(message__icontains=query))

    # paginator
    paginator = Paginator(enquiries, 15)  # 7 items per page
    page_number = request.GET.get('page')
    try:
        enquiries_paginated = paginator.page(page_number)
    except PageNotAnInteger:
        enquiries_paginated = paginator.page(1)
    except EmptyPage:
        enquiries_paginated = paginator.page(paginator.num_pages)

    return render(request, 'admin/completedenquiry.html', {'enquiries':enquiries_paginated,'ecount':ecount,'statuses':statuses})

def editenquiry(request, gid):
    enquiry = get_object_or_404(ContactMessage, pk=gid)
    
    if request.method == 'POST':
        
        
        enquiry.status = request.POST.get('status')
        
        
        enquiry.save()
        return redirect('enquiry_list')
    
    return render(request, 'admin/editenquirystatus.html', {'enquiry': enquiry})


def delete_enquiry(request, message_id):
    # Retrieve the contact message object
    message = get_object_or_404(ContactMessage, id=message_id)
    
    # Delete the contact message
    message.delete()
    
    # Redirect to the enquiry list page
    return redirect('enquiry_list')

def reply_to_enquiry(request, message_id):
    # Retrieve the ContactMessage object
    enquiry = get_object_or_404(ContactMessage, pk=message_id)

    # Update the status to 1
    enquiry.status = 1
    enquiry.save()

    # Send email
    subject = 'Reply to Your Enquiry'
    message = 'Your message has been received. We will get back to you shortly.'
    sender = 'zmcazambia@gmail.com'  # Your email address
    recipient = enquiry.email  # Email address of the sender
    send_mail(subject, message, sender, [recipient])

    
    # Add success message
    messages.success(request, 'Response sent successfully!')


    return redirect('enquiry_list')

def bloodgroupadmin(request):
    user_profile = UserProfile.objects.all()
    # Retrieve all data from OwnerDetails, SpouseDetails, ChildrenDetails, and OtherDetails
    owners = OwnerDetails.objects.all()
    spouses = SpouseDetails.objects.all()
    children = ChildrenDetails.objects.all()
    others = OtherDetails.objects.all()

    # Filter based on the search input if provided in the request
    search_query = request.GET.get('q')
    if search_query:
        # Filter owners
        owners = owners.filter(
            Q(owner_first_name__icontains=search_query) |
            Q(owner_last_name__icontains=search_query) |
            Q(blood_group__icontains=search_query)
        )
        # Filter spouses
        spouses = spouses.filter(
            Q(spouse_name__icontains=search_query) |
            Q(blood_group__icontains=search_query)
        )
        # Filter children
        children = children.filter(
            Q(child_name__icontains=search_query) |
            Q(blood_group__icontains=search_query)
        )
        # Filter others
        others = others.filter(
            Q(fname__icontains=search_query) |
            Q(lname__icontains=search_query) |
            Q(blood_group__icontains=search_query)
        )

    # Prepare data for rendering
    owner_data = [(f"{owner.owner_first_name} {owner.owner_last_name}", owner.blood_group) for owner in owners]
    spouse_data = [(spouse.spouse_name, spouse.blood_group) for spouse in spouses]
    children_data = [(child.child_name, child.blood_group) for child in children]
    other_data = [(f"{other.fname} {other.lname}", other.blood_group) for other in others]
     # Paginate the combined queryset
       # Combine all data into a single list
    all_data = owner_data + spouse_data + children_data + other_data

    paginator = Paginator(all_data, 10)  # 10 items per page
    page_number = request.GET.get('page')
    try:
        paginated_data = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        paginated_data = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        paginated_data = paginator.page(paginator.num_pages)


    # Prepare context data
    context = {
        'owner_data': owner_data,
        'spouse_data': spouse_data,
        'children_data': children_data,
        'other_data': other_data,
        'up': user_profile,
            'paginated_data': paginated_data,
    }

    return render(request, 'admin/bloodgroupadmin.html', context)



# def birthdaydetails1(request):
#     user_profile = UserProfile.objects.all()

#     owners = OwnerDetails.objects.all()
#     spouses = SpouseDetails.objects.all()
#     children = ChildrenDetails.objects.all()
#     others = OtherDetails.objects.all()

#     # Filter birthdays based on the selected month if provided in the request
#     selected_month = request.GET.get('month')
#     if selected_month:
#         owners = owners.filter(dob__month=selected_month)
#         spouses = spouses.filter(spouse_dob__month=selected_month)
#         children = children.filter(dob__month=selected_month)
#         others = others.filter(dob__month=selected_month)
#      # Filter birthdays based on the search input if provided in the request
#     search_name = request.GET.get('q')
#     if search_name:
#         owners = owners.filter(owner_first_name__icontains=search_name) | owners.filter(owner_last_name__icontains=search_name)
#         spouses = spouses.filter(spouse_name__icontains=search_name)
#         children = children.filter(child_name__icontains=search_name)
#         others = others.filter(fname__icontains=search_name) | others.filter(lname__icontains=search_name)
#     today = date.today()  # Get the current date


#     owner_data = [(f"{owner.owner_first_name} {owner.owner_last_name}", owner.dob) for owner in owners]
#     spouse_data = [(spouse.spouse_name, spouse.spouse_dob) for spouse in spouses]
#     children_data = [(child.child_name, child.dob) for child in children]
#     other_data = [(f"{other.fname} {other.lname}", other.dob) for other in others]

#       # Fetch recipient email addresses from UserProfile
#     # recipient_emails = {owner.owner_first_name: user_profile.filter(user_id=owner.up).first().email for owner in owners}


#     context = {
#         'today':today,
#         'owner_data': owner_data,
#         'spouse_data': spouse_data,
#         'children_data': children_data,
#         'other_data': other_data,
#         'up': user_profile,
#         # 'recipient_emails': recipient_emails,
#     }

#     return render(request, 'admin/birthdaywish.html', context)



def birthdaydetails1(request):
    user_profile = UserProfile.objects.all()
    owners = OwnerDetails.objects.all()
    spouses = SpouseDetails.objects.all()
    children = ChildrenDetails.objects.all()
    others = OtherDetails.objects.all()

    today = date.today()

    owner_birthdays = {f"{owner.owner_first_name} {owner.owner_last_name}": owner.dob for owner in owners}
    spouse_birthdays = {spouse.spouse_name: spouse.spouse_dob for spouse in spouses}
    children_birthdays = {child.child_name: child.dob for child in children}
    other_birthdays = {f"{other.fname} {other.lname}": other.dob for other in others}

    owner_data = [(name, dob) for name, dob in owner_birthdays.items()]
    spouse_data = [(name, dob) for name, dob in spouse_birthdays.items()]
    children_data = [(name, dob) for name, dob in children_birthdays.items()]
    other_data = [(name, dob) for name, dob in other_birthdays.items()]

    # Combine all the data into a single list
    all_data = owner_data + spouse_data + children_data + other_data
   # Sort the combined data based on month and day
    sorted_data = sorted(all_data, key=lambda x: (x[1].month, x[1].day))

    # Paginate the data
    paginator = Paginator(sorted_data, 10)  # Show 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'today': today,
        'page_obj': page_obj,
        'up': user_profile,
    }

    return render(request, 'admin/birthdaywish.html', context)
def send_birthday_wish(request):
    if request.method == 'POST':
        recipient_name = request.POST.get('recipient_name')
        
        # Split recipient_name into first and last names if possible
        recipient_name_parts = recipient_name.split()
        if len(recipient_name_parts) == 1:
            # If only one name is provided, assume it's the first name
            owner_first_name = recipient_name_parts[0]
            owner_last_name = ""  # Set last name to empty string
        else:
            # If two or more names are provided, assume the last name is the last part
            owner_first_name = recipient_name_parts[0]
            owner_last_name = " ".join(recipient_name_parts[1:])

        # Check if recipient_name exists in OwnerDetails
        owner_recipient = None
        if owner_last_name:
            owner_recipient = OwnerDetails.objects.filter(owner_first_name=owner_first_name, owner_last_name=owner_last_name).first()
        else:
            owner_recipient = OwnerDetails.objects.filter(owner_first_name=owner_first_name).first()

        if owner_recipient:
            recipient_user = owner_recipient.up
        else:
            try:
                # Check if recipient_name exists in SpouseDetails
                spouse_recipient = SpouseDetails.objects.get(spouse_name=recipient_name)
                recipient_user = spouse_recipient.up
            except SpouseDetails.DoesNotExist:
                try:
                    # Check if recipient_name exists in ChildrenDetails
                    child_recipient = ChildrenDetails.objects.get(child_name=recipient_name)
                    recipient_user = child_recipient.up
                except ChildrenDetails.DoesNotExist:
                    try:
                        # Check if recipient_name exists in OtherDetails
                        other_recipient = OtherDetails.objects.get(fname=owner_first_name, lname=owner_last_name)
                        recipient_user = other_recipient.up
                    except OtherDetails.DoesNotExist:
                        return render(request, 'admin/birthday_wish.html', {'success': False, 'error': 'Recipient not found.'})

        # Fetch recipient's email address from UserProfile
        recipient_email = recipient_user.email

        # Send birthday wish email
        subject = 'Birthday Wishes'
        message = f"Dear {recipient_name},\n\nWishing you a very happy birthday!\n\nBest regards,\nZMCA,Lusaka,Zambia"
        sender_email = 'zmcazambia@gmail.com'  # Set your email address here
        try:
            send_mail(subject, message, sender_email, [recipient_email])
            return render(request, 'admin/birthday_wish.html', {'success': True})
        except Exception as e:
            return render(request, 'admin/birthday_wish.html', {'success': False, 'error': str(e)})

    return HttpResponseRedirect(reverse('send_birthday_wish'))

from django.db.models import Q

def gallerycommon(request):
    # Retrieve all gallery items and order them by id
    gallery_items = GalleryItem.objects.order_by('id').all()
    
    # Extract the search query from the GET parameters
    query = request.GET.get('q')
    print(query)
    
    # If a search query exists, filter the gallery items by title or description containing the query
    if query:
        gallery_items = gallery_items.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    
    # Paginate the filtered or unfiltered gallery items with 50 items per page
    paginator = Paginator(gallery_items, 50)
    
    # Get the current page number from the GET parameters
    page = request.GET.get('page')
    
    try:
        # Attempt to retrieve the requested page of gallery items
        gallery_items = paginator.page(page)
    except PageNotAnInteger:
        # If the page parameter is not an integer, deliver the first page
        gallery_items = paginator.page(1)
    except EmptyPage:
        # If the page is out of range, deliver the last page of results
        gallery_items = paginator.page(paginator.num_pages)
    
    # If there is a search query, render the search results template; otherwise, render the regular gallery template
    if query:
        return render(request, 'admin/search_results.html', {'gallery_items': gallery_items, 'query': query})
    else:
        return render(request, 'landing/gallerycommon.html', {'gallery_items': gallery_items, 'query': query})





def galleryview(request):
    gallery_items = GalleryItem.objects.all()
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        gallery_items = gallery_items.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    
    paginator = Paginator(gallery_items, 50)
    
    page = request.GET.get('page')
    try:
        gallery_items = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        gallery_items = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results
        gallery_items = paginator.page(paginator.num_pages)
    
    if query:
        # If there is a search query, render search results template
        return render(request, 'admin/search_results.html', {'gallery_items': gallery_items, 'query': query})
    else:
        # Otherwise, render the regular gallery template
        return render(request, 'admin/gallery1.html', {'gallery_items': gallery_items, 'query': query})

   



def addgalleryview(request):
    gallery_items = GalleryItem.objects.all()


 # Search functionality

    # Search functionality
    search_query = request.GET.get('q')
    if search_query:
        gallery_items = gallery_items.filter(
            Q(title__icontains=search_query) |  # Search by title (case-insensitive)
            Q(description__icontains=search_query)  # Search by description (case-insensitive)
        )
    paginator = Paginator(gallery_items, 30)  # Paginate by 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
      # If search query is cleared, display all items
    if not search_query:
        gallery_items = GalleryItem.objects.all()
        paginator = Paginator(gallery_items, 30)
        page_obj = paginator.get_page(page_number)


    return render(request, 'admin/addgalleryview.html', {'page_obj': page_obj,'search_query': search_query})

def addgallery(request):
    gallery_items = GalleryItem.objects.all()

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        status = 1
        
        # Get the uploaded image file
        # image = request.FILES.get('image')
        images = request.FILES.getlist('image')
           # Create a new GalleryItem object for each uploaded image and save them
        for image in images:
            GalleryItem.objects.create(title=title, description=description, status=status, image=image)
        
        # Create a new GalleryItem object and save it
        # GalleryItem.objects.create(title=title, description=description, status=status, image=image)
        return redirect('addgalleryview')
    return render(request, 'admin/addgallery.html', {'gallery_items': gallery_items})

def editgallery(request, gid):
    g = get_object_or_404(GalleryItem, id=gid)
    
    if request.method == 'POST':
        title = request.POST.get('title')
      
        image = request.FILES.get('image')  # Get the uploaded image file
        description= request.POST.get('description')
        
        status = request.POST.get('status')
        
        
        # Update the g object with new data
        g.title = title
        g.description = description
        g.status = 1
          # Update timestamp
        g.timestamp = timezone.now()
            # Check if a new image was uploaded
        if image:
            # Save the uploaded image to the media directory
            file_path = default_storage.save('images/' + image.name, ContentFile(image.read()))
            # Update the member object with the new image URL
            g.image = file_path
        
        g.save()
        
        return redirect('addgalleryview')
    
    return render(request, 'admin/editgalleryview.html', {'g': g})


def deletegalleryview(request, gid):
    # Fetch the member object corresponding to the given ID
    g = get_object_or_404(GalleryItem, pk=gid)

    # Check if the request method is POST
    if request.method == 'POST':
        # Delete the member object
        g.delete()
        # Redirect to a URL after successful deletion
        return redirect('addgalleryview')  # Adjust the URL name as needed

    # Render a template for confirmation or provide a response
    return render(request, 'admin/addgalleryview.html', {'g': g})


def notification(request):
    if request.method == 'POST':
        # Get data from the request
        event_name = request.POST.get('event_name')
        description = request.POST.get('description')
        date = request.POST.get('date')
        timestamp = request.POST.get('timestamp')
        status = request.POST.get('status')
        image = request.FILES.get('image')

        # Create the EventNotification object
        event_notification = EventNotification(
            event_name=event_name,
            description=description,
            date=date,
            timestamp=timestamp,
            status=status,
            image=image
        )
        event_notification.save()  # Save the object
        messages.success(request, 'Event notification added successfully!')
        return redirect('eventview')  # Redirect to event view page
    return render(request, 'admin/eventnotification.html')



def eventview(request):
    event_items = EventNotification.objects.all()


 # Search functionality
    # Extract search query and year from the input
    search_query = request.GET.get('q')
    if search_query:
        # Check if the search query contains a year
        if search_query.isdigit() and len(search_query) == 4:
            # Search query is a year, filter events by that year
            event_items = event_items.filter(date__year=search_query)
        else:
            # Search query is not a year, perform regular search
            event_items = event_items.filter(
                Q(event_name__icontains=search_query) |  # Search by event name (case-insensitive)
                Q(description__icontains=search_query) |  # Search by description (case-insensitive)
                Q(status__icontains=search_query)  # Search by status (case-insensitive)
            )

    paginator = Paginator(event_items, 15)  # Paginate by 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
   

    return render(request, 'admin/eventview.html', {'page_obj': page_obj,'search_query': search_query})

def allevents(request):
    event_items = EventNotification.objects.all()


 # Search functionality
    # Extract search query and year from the input
    search_query = request.GET.get('q')
    if search_query:
        # Check if the search query contains a year
        if search_query.isdigit() and len(search_query) == 4:
            # Search query is a year, filter events by that year
            event_items = event_items.filter(date__year=search_query)
        else:
            # Search query is not a year, perform regular search
            event_items = event_items.filter(
                Q(event_name__icontains=search_query) |  # Search by event name (case-insensitive)
                Q(description__icontains=search_query) |  # Search by description (case-insensitive)
                Q(status__icontains=search_query)  # Search by status (case-insensitive)
            )

    paginator = Paginator(event_items, 15)  # Paginate by 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
   

    return render(request, 'admin/allevents.html', {'page_obj': page_obj,'search_query': search_query})


def deleventview(request, gid):
    # Fetch the member object corresponding to the given ID
    g = get_object_or_404(EventNotification, pk=gid)

    # Check if the request method is POST
    if request.method == 'POST':
        # Delete the member object
        g.delete()
        # Redirect to a URL after successful deletion
        return redirect('eventview')  # Adjust the URL name as needed

    # Render a template for confirmation or provide a response
    return render(request, 'admin/eventview.html', {'g': g})


def editevent(request, gid):
    event = get_object_or_404(EventNotification, pk=gid)
    
    if request.method == 'POST':
        event.event_name = request.POST.get('event_name')
        event.description = request.POST.get('description')
        
        # Convert the string date to datetime.date object
        date_str = request.POST.get('date')
        event.date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Extract time from the existing timestamp
        existing_timestamp = event.timestamp
        new_time_str = request.POST.get('timestamp')
        new_time = datetime.strptime(new_time_str, '%H:%M:%S').time()

        # Update the timestamp with the new time value
        event.timestamp = datetime.combine(event.date, new_time)
        
        event.status = request.POST.get('status')
        
        if request.FILES.get('image'):
            event.image = request.FILES['image']
        
        event.save()
        return redirect('eventview')
    
    return render(request, 'admin/editevent.html', {'event': event})


def addblog(request):
    if request.method == 'POST':
        # Get data from the request
        title = request.POST.get('blogtitle')
        subtitle = request.POST.get('blogsubtitle')
        description = request.POST.get('description')
        date = request.POST.get('date')
        
        
        author_name=request.POST.get('authorname')
        status = request.POST.get('status')
        image = request.FILES.get('image')

        # Create the EventNotification object
        b = Blog(
            title=title,
            subtitle=subtitle,
            description=description,
            date=date,
            timestamp=timezone.now(),
            status=status,
            image=image,
            author_name=author_name,
        )
        b.save()  # Save the object
        messages.success(request, 'Blog details added successfully!')
        return redirect('addblogview')  # Redirect to event view page
    return render(request, 'admin/addblog.html')


def addblogview(request):
    blog_items = Blog.objects.all()

    # Search functionality
    search_query = request.GET.get('q')
    if search_query:
        if search_query.isdigit() and len(search_query) == 4:
            # Search query is a year, filter events by that year
            blog_items = blog_items.filter(date__year=search_query)
        else:
            # Regular search across multiple fields
            blog_items = blog_items.filter(
                Q(title__icontains=search_query) |
                Q(subtitle__icontains=search_query) |
                Q(author_name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(status__icontains=search_query)
            )

    paginator = Paginator(blog_items, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

   

    return render(request, 'admin/addblogview.html', {'page_obj': page_obj, 'search_query': search_query})




def allblogview(request):
    blog_items = Blog.objects.all()

    # Search functionality
    search_query = request.GET.get('q')
    if search_query:
        if search_query.isdigit() and len(search_query) == 4:
            # Search query is a year, filter events by that year
            blog_items = blog_items.filter(date__year=search_query)
        else:
            # Regular search across multiple fields
            blog_items = blog_items.filter(
                Q(title__icontains=search_query) |
                Q(subtitle__icontains=search_query) |
                Q(author_name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(status__icontains=search_query)
            )

    paginator = Paginator(blog_items, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

   

    return render(request, 'admin/allblogview.html', {'page_obj': page_obj, 'search_query': search_query})

def add_blog_detail(request, blog_id):
    # Retrieve the blog object based on the blog_id
    blog = get_object_or_404(Blog, id=blog_id)
    
    # Pass the blog object to the template for rendering
    return render(request, 'admin/addblogdetail.html', {'blog': blog})
def blogsdetail(request, blog_id):
    # Retrieve the blog object based on the blog_id
    blog = get_object_or_404(Blog, id=blog_id)
    
    # Pass the blog object to the template for rendering
    return render(request, 'landing/blog-details.html', {'blog': blog})



def delblogview(request, gid):
    # Fetch the member object corresponding to the given ID
    g = get_object_or_404(Blog, pk=gid)

    # Check if the request method is POST
    if request.method == 'POST':
        # Delete the member object
        g.delete()
        # Redirect to a URL after successful deletion
        return redirect('addblogview')  # Adjust the URL name as needed

    # Render a template for confirmation or provide a response
    return render(request, 'admin/addblogview.html', {'g': g})



def editblog(request, gid):
    blog = get_object_or_404(Blog, pk=gid)
    
    if request.method == 'POST':
        blog.title = request.POST.get('blogtitle')
        blog.subtitle = request.POST.get('blogsubtitle')
        blog.description = request.POST.get('description')
        blog.status = request.POST.get('status')
        blog.author_name = request.POST.get('authorname')


        # Convert the string date to datetime.date object
        date_str = request.POST.get('date')
        blog.date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
       
        # Save the current time as the timestamp
        blog.timestamp = timezone.now()
        print(blog.timestamp)
        
        
        if request.FILES.get('image'):
            blog.image = request.FILES['image']
        
        blog.save()
        return redirect('addblogview')
    
    return render(request, 'admin/editblog.html', {'blog': blog})





def memberships(request):
    memberships_data = Membership.objects.all()
    # Search functionality
    search_query = request.GET.get('q')
    if search_query:
        if search_query.isdigit() and len(search_query) == 4:
            # Search query is a year, filter memberships by that year
                    memberships_data = memberships_data.filter(
            Q(from_date__year=search_query) | Q(to_date__year=search_query)
        )

        else:
            # Regular search across multiple fields
            memberships_data = memberships_data.filter(
                Q(with_family_amount__icontains=search_query) |
                Q(alone_amount__icontains=search_query)
            )


    paginator = Paginator(memberships_data, 10)  # Show 10 memberships per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == 'POST':
       
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        famount = request.POST.get('with_family_amount')
        amount = request.POST.get('alone_amount')
        
        # Assuming you have validated the form data before saving
        
        # Create a new Membership object
        membership = Membership.objects.create(
            from_date=from_date,
            to_date=to_date,
            with_family_amount=famount,
            alone_amount=amount
        )
        
        # Optionally, you can set additional fields or perform any other logic
        
        # Save the Membership object
        membership.save()
         # Fetch all membership records
     
        messages.success(request, 'Member details added successfully!')
        return redirect('memberships')  # Redirect to event view page
    return render(request, 'admin/membership.html', {'page_obj': page_obj,'search_query': search_query})

def delmemberdata(request, gid):
    # Fetch the member object corresponding to the given ID
    g = get_object_or_404(Membership, pk=gid)

    # Check if the request method is POST
    if request.method == 'POST':
        # Delete the member object
        g.delete()
        # Redirect to a URL after successful deletion
        return redirect('memberships')  # Adjust the URL name as needed

    # Render a template for confirmation or provide a response
    return render(request, 'admin/membership.html', {'g': g})




def editmembershipdata(request, gid):
    member = get_object_or_404(Membership, pk=gid)
    
    if request.method == 'POST':
        member.from_date = request.POST.get('from_date')
        member.to_date= request.POST.get('to_date')
        member.with_family_amount = request.POST.get('with_family_amount')
        member.alone_amount = request.POST.get('alone_amount')
        mstatus = request.POST.get('status') 

        if mstatus=='active':
            status=1
        else:
            status=0
        member.status=status
      
  
       
        member.save()
        return redirect('memberships')
    
    return render(request, 'admin/editmembershipdata.html', {'member': member})

def paynow(request, user_id):
    # Get the user profile based on the user_id or return a 404 page if not found
    user_profile = get_object_or_404(UserProfile, id=user_id)
    
    # Retrieve first name and last name from the user profile
    fname = user_profile.firstname
    lname = user_profile.lastname
    
    # Get owner details related to the user profile if available
    owner_details = OwnerDetails.objects.filter(up=user_profile).first()
    
    # Get ZMCA status from owner details if available
    zmstatus = owner_details.zmstatus if owner_details else None
    
    # Annotate membership years from the Membership model
    membership_years = Membership.objects.annotate(
        from_year=ExtractYear('from_date'),
        to_year=ExtractYear('to_date')
    ).values_list('from_year', 'to_year').distinct()

    print("my",membership_years)
    
    if request.method == 'POST':
        # Retrieve form data from the POST request
        name = request.POST.get('name')
        pdate = request.POST.get('pdate')
        membership_year = request.POST.get('membership_year')
        pcat = request.POST.get('pcat')
        amount = request.POST.get('amount')
        
        # Get the Membership object based on the selected membership year and category
        membership = Membership.objects.get(
            from_date__year__lte=membership_year.split('-')[0],
            to_date__year__gte=membership_year.split('-')[1]
            # member_category=pcat
        )
        
        # Save payment data to MembershipDetail table
        membership_detail = MembershipDetail.objects.create(
            membership=membership,
            membership_year=membership_year,
            amount=amount,
            payment_date=pdate,
            user_profile=user_profile,
            usercategory=pcat,
            status=1
        )
        
    # Retrieve all membership details
    memberships = MembershipDetail.objects.filter(user_profile=user_profile)

    # Search functionality
    search_query = request.GET.get('q')
    if search_query:
        if search_query.isdigit() and len(search_query) == 4:
            # Search query is a year, filter memberships by that year
                    memberships = memberships.filter(
            Q(membership_year=search_query) | Q(payment_date=search_query) 
        )

        else:
            # Regular search across multiple fields
            memberships = memberships.filter(
                Q(amount__icontains=search_query) |
                Q( usercategory__icontains=search_query)
            )


    
    # Pagination: Show 10 memberships per page
    paginator = Paginator(memberships, 10)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        page_obj = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        page_obj = paginator.page(paginator.num_pages)

    # Prepare context data to pass to the template
    context = {
        'user_profile': user_profile,
        'fn': fname,
        'ln': lname,
        'zmstatus': zmstatus,
        'membership_years': membership_years,
        'page_obj': page_obj,
        'search_query':search_query,
    }

    
        
    # Render the payment.html template with the context data
    return render(request, 'admin/payment.html', context)



def get_amount(request):
    if request.method == 'GET':
        year_range = request.GET.get('year')
        pcat = request.GET.get('pcat')

        try:
            year = int(year_range.split('-')[0])

            membership = Membership.objects.get(
                from_date__year__lte=year,
                to_date__year__gte=year,
                status=1  # Assuming you want only active memberships
            )

            if pcat == 'With Family':
                amount = membership.with_family_amount
            elif pcat == 'Alone':
                amount = membership.alone_amount
            else:
                amount = None
        except (Membership.DoesNotExist, ValueError):
            amount = None

        # Return the amount as a JSON response
        return JsonResponse({'amount': amount})
def delmemberdetails(request, gid):
    # Fetch the member object corresponding to the given ID
    g = get_object_or_404(MembershipDetail, pk=gid)

    # Check if the request method is POST
    if request.method == 'POST':
        # Delete the member object
        g.delete()
        # Redirect to the 'paynow' URL with the same user_id
        return redirect('paynow', user_id=g.user_profile.id)  # Assuming user_id is the correct field

    # Render a template for confirmation or provide a response
    return render(request, 'admin/payment.html', {'g': g})

from django.db.models import Min, Max

def editmembershipdetails(request, gid):
    member = get_object_or_404(MembershipDetail, pk=gid)
      # Retrieve the user profile associated with the MembershipDetail object
    user_profile = member.user_profile
    
    # Retrieve the first name and last name from the user profile
    fname = user_profile.firstname
    lname = user_profile.lastname
    
     # Get the minimum and maximum years from the Membership table
    min_year = Membership.objects.aggregate(min_year=Min('from_date__year'))['min_year']
    max_year = Membership.objects.aggregate(max_year=Max('to_date__year'))['max_year']
    
    # Generate a list of membership years from the minimum to maximum year
    membership_years = [(year, year + 1) for year in range(min_year, max_year + 1)]
    
    if request.method == 'POST':
        member.payment_date = request.POST.get('pdate')
        member.membership_year= request.POST.get('membership_year')
        # member.usercategory = request.POST.get('member_category')
        member.amount = request.POST.get('amount')
        member.status = 1  
  
       
        member.save()
        return redirect('paynow',user_id=member.user_profile.id)
    
    return render(request, 'admin/editmembershipdetails.html', {'member': member,'membership_years':membership_years,'fn':fname,'ln':lname})


def block_user(request, user_id):
    if request.method == 'POST':
        user_profile = UserProfile.objects.get(id=user_id)
        user_profile.status = 1
        user_profile.save()

        # Get current year
        current_year = timezone.now().year

        # Fetch membership details for the current year
        membership = Membership.objects.filter(from_date__year=current_year).first()

        if membership:
            # Render the email template with membership details
            html_message = render_to_string('blockuser.html', {
                'with_family_amount': membership.with_family_amount,
                'alone_amount': membership.alone_amount
            })

            # Send email to the user
            subject = 'ZMCA Account Blocked'
            from_email = 'zmcazambia@gmail.com'  # Update with your email
            to_email = user_profile.email
            send_mail(subject, '', from_email, [to_email], html_message=html_message)

    return redirect('fam_view')


def payments(request, user_id):
    # Get the user profile based on the user_id or return a 404 page if not found
    user_profile = get_object_or_404(UserProfile, id=user_id)
    
    # Retrieve first name and last name from the user profile
    fname = user_profile.firstname
    lname = user_profile.lastname
    
    # Get owner details related to the user profile if available
    owner_details = OwnerDetails.objects.filter(up=user_profile).first()
    
    # Get ZMCA status from owner details if available
    zmstatus = owner_details.zmstatus if owner_details else None
    
    # Annotate membership years from the Membership model
    membership_years = Membership.objects.annotate(
        from_year=ExtractYear('from_date'),
        to_year=ExtractYear('to_date')
    ).values_list('from_year', 'to_year').distinct()
    
    if request.method == 'POST':
        # Retrieve form data from the POST request
        name = request.POST.get('name')
        pdate = request.POST.get('pdate')
        membership_year = request.POST.get('membership_year')
        pcat = request.POST.get('pcat')
        amount = request.POST.get('amount')
        
        # Get the Membership object based on the selected membership year and category
        membership = Membership.objects.get(
            from_date__year__lte=membership_year.split('-')[0],
            to_date__year__gte=membership_year.split('-')[1]
            # member_category=pcat
        )
        
        # Save payment data to MembershipDetail table
        membership_detail = MembershipDetail.objects.create(
            membership=membership,
            membership_year=membership_year,
            amount=amount,
            payment_date=pdate,
            user_profile=user_profile,
            usercategory=pcat,
            status=1
        )
        
    # Retrieve all membership details
    memberships = MembershipDetail.objects.filter(user_profile=user_profile)

    # Search functionality
    search_query = request.GET.get('q')
    if search_query:
        if search_query.isdigit() and len(search_query) == 4:
            # Search query is a year, filter memberships by that year
                    memberships = memberships.filter(
            Q(membership_year=search_query) | Q(payment_date=search_query) 
        )

        else:
            # Regular search across multiple fields
            memberships = memberships.filter(
                Q(amount__icontains=search_query) |
                Q( usercategory__icontains=search_query)
            )


    
    # Pagination: Show 10 memberships per page
    paginator = Paginator(memberships, 10)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        page_obj = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        page_obj = paginator.page(paginator.num_pages)

    # Prepare context data to pass to the template
    context = {
        'user_profile': user_profile,
        'fn': fname,
        'ln': lname,
        'zmstatus': zmstatus,
        'membership_years': membership_years,
        'page_obj': page_obj,
        'search_query':search_query,
    }

    
        
    # Render the payment.html template with the context data
    return render(request, 'admin/payments.html', context)




def addhomegallery(request):
    gallery_items = CarouselImage.objects.all()


 # Search functionality

    # Search functionality
    search_query = request.GET.get('q')
    if search_query:
        gallery_items = gallery_items.filter(
            Q(status__icontains=search_query)   # Search by title (case-insensitive)
           # Search by description (case-insensitive)
        )
    paginator = Paginator(gallery_items, 30)  # Paginate by 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
      # If search query is cleared, display all items
    if not search_query:
        gallery_items = CarouselImage.objects.all()
        paginator = Paginator(gallery_items, 30)
        page_obj = paginator.get_page(page_number)


    return render(request, 'admin/addhomegallery.html', {'page_obj': page_obj,'search_query': search_query})




def addhgallery(request):
    gallery_items = CarouselImage.objects.all()

    if request.method == 'POST':

        title = request.POST.get('title')
      
        status = request.POST.get('status')
     
        
        # Get the uploaded image file
        image = request.FILES.get('image')
        
        # Create a new GalleryItem object and save it
        CarouselImage.objects.create(image=image,title=title,status=status)
        return redirect('addhomegallery')
    return render(request, 'admin/addhgallery.html', {'gallery_items': gallery_items})



def edithgallery(request, gid):
    g = get_object_or_404(CarouselImage, id=gid)
    
    if request.method == 'POST':
        title = request.POST.get('title')
      
        image = request.FILES.get('image')  # Get the uploaded image file
      
        status = request.POST.get('status')
        
        
        # Update the g object with new data
        g.title = title
   
        g.status = status
      
            # Check if a new image was uploaded
        if image:
            # Save the uploaded image to the media directory
            file_path = default_storage.save('images/' + image.name, ContentFile(image.read()))
            # Update the member object with the new image URL
            g.image = file_path
        
        g.save()
        
        return redirect('addhomegallery')
    
    return render(request, 'admin/edithgallery.html', {'g': g})




def deletehgallery(request, gid):
    # Fetch the member object corresponding to the given ID
    g = get_object_or_404(CarouselImage, pk=gid)

    # Check if the request method is POST
    if request.method == 'POST':
        # Delete the member object
        g.delete()
        # Redirect to a URL after successful deletion
        return redirect('addhomegallery')  # Adjust the URL name as needed

    # Render a template for confirmation or provide a response
    return render(request, 'admin/addhomegallery.html', {'g': g})



def admin_services_posts(request):
    return render(request, 'admin/admin-post.html')