import calendar
from django.http import HttpResponse, JsonResponse
from django.http import Http404
# from django.shortcuts import get_object_or_404, redirect
from .models import Familyphoto
from django.shortcuts import get_object_or_404, render,redirect
from django.contrib.auth import login, authenticate
from django.conf import settings
from services.models import  Agency
from django.contrib import messages
from django.views import View
from . models import *
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import date, datetime
from django.contrib.auth.models import User,auth
from django.shortcuts import render, redirect
from zmcaadmin.models import EventNotification

from .models import ChildrenDetails,OtherDetails,Familyphoto
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.template.loader import get_template
from django.views import View
from xhtml2pdf import pisa
from django.template.loader import render_to_string
from io import BytesIO
from .helpers import send_forget_password_mail,send_user_email
import uuid
from django.conf import Settings
from django.core.mail import send_mail
from zmcaadmin.models import CommitteeMember,Membership,MembershipDetail
from django.db.models import Max
from django.db.models.functions import ExtractYear






# Create your views here.




# def changepassword(request, token):
#     context = {}
    
#     try:
#         profile_obj = UserProfile.objects.filter(password=token).first()
#         context = {'user_id': profile_obj.userid.id}
#         print(profile_obj)

#         if request.method == 'POST':
#             new_password = request.POST.get('npassword')
#             confirm_password = request.POST.get('cpassword')
#             user_id = request.POST.get('user_id')

#             if user_id is None:
#                 messages.error(request, 'No user id found.')
#                 return redirect(f'/changepassword/{token}/')
#             if new_password != confirm_password:
#                 messages.error(request, 'Both passwords should be equal.')
#                 return redirect(f'/changepassword/{token}/')         

#             user_obj = User.objects.get(id=user_id)
#             user_obj.set_password(new_password)
#             user_obj.save()

         
#             messages.success(request, 'Password successfully changed.')
#             return redirect('changepassword')  # Redirect to home page      

#     except Exception as e:
#         print(e)
        
#     return render(request, 'member/cpw.html', context)


# @login_required
def changepassword(request, token):
    context = {}
    
    try:
        # Attempt to find a UserProfile with the provided token
        profile_obj = UserProfile.objects.filter(password=token).first()
        
        if profile_obj:
            # Regular user password change process
            user_id = profile_obj.userid.id

            if request.method == 'POST':
                new_password = request.POST.get('npassword')
                confirm_password = request.POST.get('cpassword')

                if new_password != confirm_password:
                    messages.error(request, 'Both passwords should be equal.')
                    return redirect(f'/changepassword/{token}/')

                try:
                    user_obj = User.objects.get(id=user_id)
                    user_obj.set_password(new_password)
                    user_obj.save()

                    # Add success message
                    messages.success(request, 'Password successfully changed.')
                    return redirect('changepassword',token=token)  # Redirect to home page or wherever appropriate
                except User.DoesNotExist:
                    messages.error(request, 'User not found.')
                    return redirect('changepassword', token=token)
        else:
            # If profile_obj is not found, it could be an admin user
            admin_user = User.objects.filter(is_superuser=True,email='zmcazambia@gmail.com').first()
            print(admin_user)
            if admin_user:
                if request.method == 'POST':
                    new_password = request.POST.get('npassword')
                    confirm_password = request.POST.get('cpassword')
                    print(new_password)
                    print(confirm_password)

                    if new_password != confirm_password:
                        messages.error(request, 'Both passwords should be equal.')
                        return redirect(f'/changepassword/{token}/')

                    admin_user.set_password(new_password)
                    admin_user.save()

                    # Add success message
                    messages.success(request, 'Password successfully changed for admin.')
                    return redirect('changepassword',token=token)  # Redirect to home page or wherever appropriate
    except Exception as e:
        print(f"An error occurred: {e}")
       
        messages.error(request, 'An error occurred. Please try again later.')

    return render(request, 'landing/cpw.html', context)

def forgetpassword(request):
    try:
        if request.method == 'POST':
            email = request.POST.get('username')  # Assuming email is being used as username
            print(email)

            # Check if the entered email corresponds to a superuser (admin)
            admin_user = User.objects.filter(username=email, is_superuser=True).first()
            if admin_user:
                admin_email = email
                token = str(uuid.uuid4())
                send_forget_password_mail(email, token)  # Send to admin
                messages.success(request, 'An email has been sent to the admin for password reset.')
                return redirect('forgetpassword')
            else:
                # For regular users
                user_obj = User.objects.filter(username=email).first()
                if not user_obj:
                    messages.error(request, 'No user found with this email address.')
                    return redirect('forgetpassword')

                token = str(uuid.uuid4())
                profile_obj = UserProfile.objects.get(userid=user_obj)
                profile_obj.password = token
                profile_obj.save()

                send_forget_password_mail(email, token)  # Send to normal user
                messages.success(request, "We've emailed you instructions for setting your password.")
                return redirect('forgetpassword')

    except Exception as e:
        print(e)
        
    return render(request, 'landing/rpw.html')


def aboutus(request):
  
    return render(request, 'landing/about.html')

def adminaboutus(request):    

    return render(request, 'member/adminaboutus.html')

@login_required
def memberaboutus(request):
    try:
        user_profile = UserProfile.objects.get(userid=request.user)
    except UserProfile.DoesNotExist:
        messages.error(request, 'UserProfile does not exist for this user.')
        return redirect('index')

    # Check if owner details and membership exist (like in customerindex)
    try:
        owner_details = OwnerDetails.objects.get(up=user_profile)
    except OwnerDetails.DoesNotExist:
        owner_details = None

    # Check current membership
    current_date = date.today()
    try:
        current_membership = Membership.objects.get(from_date__lte=current_date, to_date__gte=current_date, status=1)
        current_membership_year = f"{current_membership.from_date.year}-{current_membership.to_date.year}"
        membership_detail = MembershipDetail.objects.get(
            user_profile=user_profile,
            membership_year=current_membership_year,
            status=1
        )
    except (Membership.DoesNotExist, MembershipDetail.DoesNotExist):
        membership_detail = None

    # Get counts needed for sidebar
    committecount = CommitteeMember.objects.filter(status='Active').count()
    uacount = UserProfile.objects.filter(status__in=[2, 3]).count()
    active_events_count = EventNotification.objects.filter(status='Active').count()
    pending_events_count = EventNotification.objects.filter(status='Pending').count()
    teventscount = active_events_count + pending_events_count

    context = {
        'ufn': user_profile.firstname,
        'uln': user_profile.lastname,
        'fn': user_profile.familyname,
        'email': user_profile.email,
        'owner_details': owner_details,
        'membership_detail': membership_detail,
        'teventscount': teventscount,
        'ccount': committecount,
        'uacount': uacount,
    }
    
    return render(request, 'member/memberaboutus.html', context)

def gallerycategory(request):    

    return render(request, 'member/gallerycategory.html')










def finish(request):
    # You may want to retrieve some information to display on the finish page
    # For example, the family details or any relevant data

    context = {
        # Add any context data you want to display on the finish page
    }

    return render(request, 'finish.html', context)
def complete(request):
    context = {
        # Add any context data you want to display on the finish page
    }

    return render(request, 'complete.html', context)


@login_required
def save_fp(request):
    user_profile = request.user.userprofile
    od = OwnerDetails.objects.filter(up=user_profile).first()
    sd = SpouseDetails.objects.filter(up=user_profile).first()
    cd = ChildrenDetails.objects.filter(up=user_profile).first()
    other = OtherDetails.objects.filter(up=user_profile).first()

    family_photos = Familyphoto.objects.filter(up=request.user.userprofile)

    if request.method == 'POST':
        family_photo = request.FILES.get('familyphoto')

        if family_photo:
            try:
                user_profile = request.user.userprofile
                status = 1

                family_photo_instance = Familyphoto.objects.create(up=user_profile, familyphoto=family_photo, status=status)

                messages.success(request, 'Family photo uploaded successfully!')
                family_photos = Familyphoto.objects.filter(up=request.user.userprofile)
                return redirect('submitfamilyview')
                # return render(request, 'familyphoto.html', {'family_photos': family_photos, 'od': od, 'sd': sd, 'cd': cd, 'other': other})
            except Exception as e:
                messages.error(request, f'Error uploading family photo: {str(e)}')
        else:
            messages.error(request, 'Please choose a family photo to upload.')

    return render(request, 'member/familyphoto.html', {'family_photos': family_photos, 'od': od, 'sd': sd, 'cd': cd, 'other': other})


def is_admin(user):
    return user.is_superuser

def fr(request):
      
    user_profile = request.user.userprofile

    # Check if the user has already submitted owner details
    existing_owner_details = OwnerDetails.objects.filter(up=user_profile).first()
    existing_spouse_details = SpouseDetails.objects.filter(up=user_profile).first()

    cd = ChildrenDetails.objects.filter(up=user_profile).first()
    other = OtherDetails.objects.filter(up=user_profile).first()

    family_photos = Familyphoto.objects.filter(up=request.user.userprofile)
    context={'od':existing_owner_details,
             'sd':existing_spouse_details,'cd':cd,'other':other,'fp':family_photos}

    

  
    return render(request, 'member/familyregister.html',context)



def memberindex(request):
    user_profile = UserProfile.objects.get(userid=request.user)
    #  user_profile = request.user.userprofile

    # Check if the user has already submitted owner details
    existing_owner_details = OwnerDetails.objects.filter(up=user_profile).first()
    existing_spouse_details = SpouseDetails.objects.filter(up=user_profile).first()

    cd = ChildrenDetails.objects.filter(up=user_profile).first()
    other = OtherDetails.objects.filter(up=user_profile).first()

    family_photos = Familyphoto.objects.filter(up=request.user.userprofile)


    

    context = {'od':existing_owner_details,
             'sd':existing_spouse_details,'cd':cd,'other':other,'fp':family_photos,
      
        'ufn': user_profile.firstname,
        'uln': user_profile.lastname,
        'fn': user_profile.familyname,
     
    }

    return render(request, 'member/memberindex.html', context)



@login_required
def customerindex(request):
    try:
        user_profile = UserProfile.objects.get(userid=request.user)
    except UserProfile.DoesNotExist:
        messages.error(request, 'UserProfile does not exist for this user.')
        return redirect('index')  # Redirect to the home page or any other appropriate URL
    
    # Check if the user has already submitted owner, spouse, children, other details, and family photos
    existing_owner_details = OwnerDetails.objects.filter(up=user_profile).exists()
    existing_spouse_details = SpouseDetails.objects.filter(up=user_profile).exists()
    existing_children_details = ChildrenDetails.objects.filter(up=user_profile).exists()
    existing_other_details = OtherDetails.objects.filter(up=user_profile).exists()
    existing_family_photos = Familyphoto.objects.filter(up=user_profile).exists()

    # Calculate total progress based on the availability of entries
    total_progress = 0
    if(user_profile.status==3):
    
        total_progress=100
    
    else:
    
        if existing_owner_details:
            total_progress += 20
        if existing_spouse_details:
            total_progress += 20
        if existing_children_details:
            total_progress += 20
        if existing_other_details:
            total_progress += 20
        if existing_family_photos:
            total_progress += 20
    

    # Count the total number of active users and total profiles
    uacount = UserProfile.objects.filter(status__in=[2, 3]).count()
    up = UserProfile.objects.all().count()

    # Count the total number of entries for each section
    owners_count = OwnerDetails.objects.filter(up__status__in=[2, 3]).count()
    spouses_count = SpouseDetails.objects.filter(up__status__in=[2, 3]).count()
    children_count = ChildrenDetails.objects.filter(up__status__in=[2, 3]).count()
    other_details_count = OtherDetails.objects.filter(up__status__in=[2, 3]).count()
    tc = owners_count + spouses_count + children_count + other_details_count
    # committecount = CommitteeMember.objects.count()
    committecount = CommitteeMember.objects.filter(status='Active').count()
 

       # Fetch counts of active and pending events
    active_events_count = EventNotification.objects.filter(status='Active').count()
    pending_events_count = EventNotification.objects.filter(status='Pending').count()
    teventscount=active_events_count+pending_events_count


    # -------------------------------
     
    # Fetch the owner details for the current user profile
    try:
        owner_details = OwnerDetails.objects.get(up=user_profile)
    except OwnerDetails.DoesNotExist:
        owner_details = None  # If owner details don't exist, set to None

    # Fetch the current membership year
    current_date = date.today()
    try:
        current_membership = Membership.objects.get(from_date__lte=current_date, to_date__gte=current_date, status=1)
        current_membership_year = f"{current_membership.from_date.year}-{current_membership.to_date.year}"
    except Membership.DoesNotExist:
        current_membership_year = None

    # Check if the user has paid the current membership amount
    try:
        membership_detail = MembershipDetail.objects.get(
            user_profile=user_profile,
            membership_year=current_membership_year,
            status=1  # Assuming 1 represents paid status
        )
    except MembershipDetail.DoesNotExist:
        membership_detail = None  # If membership detail doesn't exist, set to None


    # -----------------------------------
        # print("cm",membership_detail)
        # if membership_detail:
        #     cmmm=1
        # print(cmmm)
        # print("ownerddetails",owner_details)



    context = {
        'tc': tc,
        'c':committecount,
        'uacount': uacount,
        'od': existing_owner_details,
        'sd': existing_spouse_details,
        'ecd': existing_children_details,
        'eod': existing_other_details,
        'efp': existing_family_photos,
        'ufn': user_profile.firstname,
        'uln': user_profile.lastname,
        'fn': user_profile.familyname,
        'email': user_profile.email,
        'total_progress': total_progress,
        'teventscount':teventscount,
        'ccount':committecount,
        'owner_details': owner_details,
        'membership_detail': membership_detail
    }

    return render(request, 'member/customerindex.html', context)



def cevents(request):
    event_items = EventNotification.objects.all()

    # Search functionality
    search_query = request.GET.get('q')
    if search_query:
        if search_query.isdigit() and len(search_query) == 4:
            event_items = event_items.filter(date__year=search_query)
        else:
            event_items = event_items.filter(
                Q(event_name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(status__icontains=search_query)
            )

    paginator = Paginator(event_items, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Retrieve user profile information
    user_profile = UserProfile.objects.get(userid=request.user)
    committecount = CommitteeMember.objects.count()
    uacount = UserProfile.objects.filter(Q(status=2) | Q(status=3)).count()

       # Fetch counts of active and pending events
    active_events_count = EventNotification.objects.filter(status='Active').count()
    pending_events_count = EventNotification.objects.filter(status='Pending').count()
    teventscount=active_events_count+pending_events_count

    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'ufn': user_profile.firstname,
        'uln': user_profile.lastname,
        'fn': user_profile.familyname,
        'email': user_profile.email,
        'teventscount':teventscount,
        'ccount':committecount,
        'uacount':uacount,
    }

    return render(request, 'member/cevents.html', context)



def memberlogin(request):
    # messages.success(request, '')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if is_admin(user):
                # messages.success(request, 'Admin login successful.')
                return redirect('adminindex')
            else:
                try:
                    member_profile = UserProfile.objects.get(userid=user)
                    if member_profile.status in [2, 3]  and user.last_name.lower() == 'approved':
                        # messages.success(request, 'Member login successful.')
                        return redirect('customerindex')
                    else:
                        messages.error(request, 'Your account is waiting for admin approval.')
                except UserProfile.DoesNotExist:
                    messages.error(request, 'Member profile not found.')
        else:
            messages.error(request, 'Invalid login credentials. Please try again.')

    return render(request, 'landing/index.html')





def is_admin(user):
    return user.is_superuser or user.is_staff

def mlogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            
            # Check for admin
            if is_admin(user):
                return redirect('adminindex')
            
            # Check for agency user
            try:
                agency_profile = Agency.objects.get(user=user)
                if agency_profile.status == 'Approved':
                    return redirect('agency_dashboard')  # Create this URL/View
                else:
                    messages.error(request, 'Your agency account is pending approval.')
                    return redirect('mlogin')
            except Agency.DoesNotExist:
                pass  # Not an agency, check for member
            
            # Check for member user
            try:
                member_profile = UserProfile.objects.get(userid=user)
                if member_profile.status in [2, 3] and user.last_name.lower() == 'approved':
                    return redirect('customerindex')
                else:
                    messages.error(request, 'Your account is waiting for admin approval.')
                    return redirect('mlogin')
            except UserProfile.DoesNotExist:
                messages.error(request, 'User profile not found.')
                return redirect('mlogin')
        else:
            messages.error(request, 'Invalid login credentials. Please try again.')
            return redirect('mlogin')

    return render(request, 'landing/login.html')
def welcome(request):
    return render(request, 'welcome.html')

def membersignup(request):
    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        familyname = request.POST.get('familyname')
        phonenumber = request.POST.get('phonenumber')
        email = request.POST.get('email')
        username = email  # Assuming email is also the username
        password = request.POST.get('password')
        cpassword = request.POST.get('cpassword')

        if password and cpassword and password == cpassword:
            # Check if the email/username is already in use
            if UserProfile.objects.filter(userid__username=email).exists():
                messages.error(request, "Email is already in use")
            else:
                # Create a new user
                user = User.objects.create_user(username=username, password=cpassword)

                # Create a new user profile (UserProfile)
                user_profile = UserProfile.objects.create(
                    userid=user,
                    firstname=firstname,
                    lastname=lastname,
                    familyname=familyname,
                    phonenumber=phonenumber,
                    email=email,
                    password=password,
                    status=1
                )

                messages.success(request,"Your registration has been successfully submitted. Kindly await approval from the administrator. An email notification will be sent to you once approved.")
                return redirect('memberlogin')
        else:
            messages.error(request, "Password doesn't match")

    return render(request, 'landing/index.html')


# def msignup(request):
#     if request.method == 'POST':
#         firstname = request.POST.get('firstname')
#         lastname = request.POST.get('lastname')
#         familyname = request.POST.get('familyname')
#         phonenumber = request.POST.get('phonenumber')
#         email = request.POST.get('email')
#         username = email  
#         password = request.POST.get('password')
#         cpassword = request.POST.get('cpassword')

#         country_code = request.POST.get('country_code') 
#         print("Country Code:", country_code) 

#         full_phone_number = f"+{country_code} {phonenumber}"

#         if password and cpassword and password == cpassword:
#             if UserProfile.objects.filter(userid__username=email).exists():
#                 messages.error(request, "Email is already in use")
#             else:
#                 user = User.objects.create_user(username=username, password=cpassword)

#                 user_profile = UserProfile.objects.create(
#                     userid=user,
#                     firstname=firstname,
#                     lastname=lastname,
#                     familyname=familyname,
#                     phonenumber=full_phone_number,
#                     email=email,
#                     password=password,
#                     status=1
#                 )
#                 admin_email='yuaiprojects@gmail.com'

#                 subject = 'New User Registration'
#                 sender_email = 'email'  
#                 recipient_email = [admin_email]  

#                 message = (
#     f"Dear Admin,\n\n"
#     f"A new Member has registered with the following details:\n\n"
#     f"Member Name: {firstname}&nbsp;{lastname}\n"   
#     f"Family Name: {familyname}\n"
#     f"Phone Number: {full_phone_number}\n"
#     f"Email: {email}\n\n"
#     "Please take necessary actions.\n\n"
#     "Regards,\n"
#     "ZMCA"
# )

#                 send_mail(subject, message, sender_email, recipient_email, fail_silently=False)

#                 messages.success(request,"Your registration has been successfully submitted. Kindly await approval from the administrator. An email notification will be sent to you once approved.")
#                 return redirect('mlogin')
          
            
#         else:
#             messages.error(request, "Password doesn't match")

#     return render(request, 'msignup.html')



def msignup(request):
    if request.method == 'POST':
        # Retrieve form data
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        familyname = request.POST.get('familyname')
        phonenumber = request.POST.get('phonenumber')
        email = request.POST.get('email')
        username = email  # Assuming email is also the username
        password = request.POST.get('password')
        cpassword = request.POST.get('cpassword')

        # Retrieve country code from hidden input
        country_code = request.POST.get('country_code')  
        print("Country Code:", country_code)  

        # Combine country code and phone number
        full_phone_number = f"+{country_code} {phonenumber}"

        if password and cpassword and password == cpassword:
            try:
                # Check if the email/username is already in use
                if User.objects.filter(username=username).exists():
                    messages.error(request, "An account with this email already exists")
                else:
                    # Create a new user
                    user = User.objects.create_user(username=username, password=cpassword)

                    # Create a new user profile
                    user_profile = UserProfile.objects.create(
                        userid=user,
                        firstname=firstname,
                        lastname=lastname,
                        familyname=familyname,
                        phonenumber=full_phone_number,
                        email=email,
                        password=password,
                        status=1
                    )

                    # Send email notification to admin
                    admin_email = 'your_admin_email@example.com'  # Set the admin email address
                    subject = 'New User Registration'
                    message = (
                        f"Dear Admin,\n\n"
                        f"A new Member has registered with the following details:\n\n"
                        f"Member Name: {firstname} {lastname}\n"   
                        f"Family Name: {familyname}\n"
                        f"Phone Number: {full_phone_number}\n"
                        f"Email: {email}\n\n"
                        "Please take necessary actions.\n\n"
                        "Regards,\n"
                        "Your Website"
                    )
                    sender_email = 'zmcazambia@gmail.com'  # Set the sender email address
                    send_mail(subject, message, sender_email, [admin_email], fail_silently=False)

                    messages.success(request, "Your registration has been successfully submitted. Kindly await approval from the administrator.")
                    return redirect('mlogin')

            except IntegrityError:
                # Handle IntegrityError (duplicate entry)
                messages.error(request, "An account with this email already exists")
        else:
            messages.error(request, "Password doesn't match")

    return render(request, 'landing/msignup.html')

def save_spouse(request):
    user_profile = request.user.userprofile

    # Check if the user has already submitted owner details
    existing_owner_details = OwnerDetails.objects.filter(up=user_profile).first()
    existing_spouse_details = SpouseDetails.objects.filter(up=user_profile).first()

    cd = ChildrenDetails.objects.filter(up=user_profile).first()
    other = OtherDetails.objects.filter(up=user_profile).first()

    family_photos = Familyphoto.objects.filter(up=request.user.userprofile)
    context={'owner_details':existing_owner_details,
             'spouse_details':existing_spouse_details,'cd':cd,'other':other,'family_photos':family_photos}

    

  

    # Check if the user has already submitted spouse details

    if existing_spouse_details:
        # If details exist, display them
        return render(request, 'member/spouse.html',context)
    else:
        # If no details exist, process the form submission
        if request.method == 'POST':
            # Retrieve data from the form
            spouse_name = request.POST.get('spouse_name')
            gender = request.POST.get('gender')
            dob_month = request.POST.get('dob_month')
            dob_day = request.POST.get('dob_day')
            blood_group = request.POST.get('blood_group')
            spouse_living_status = request.POST.get('spouse_living_status')
            spouse_phone_no = request.POST.get('spouse_phone_no')
            spouse_whatsapp_no = request.POST.get('spouse_whatsapp_no')
            spouse_work = request.POST.get('spouse_work')
            spouse_designation = request.POST.get('spouse_designation') 
            spouse_email = request.POST.get('spouse_email')


                 # Extract country codes from the request
            w = request.POST.get('spcode')
            print('w',w)
            w1 = request.POST.get('spcode1')
            print('w1',w1)
            
            whatsapp_no=request.POST.get('spouse_whatsapp_no')
         
            phone=request.POST.get('spouse_phone_no')
    
       
            p1=f"+{w} {whatsapp_no}"
            p2=f"+{w1} {phone}"
           


            # Validate and construct the date
            try:
                # Using a fixed year (e.g., 2022)
                dob = datetime.strptime(f'2022-{dob_month}-{dob_day}', '%Y-%m-%d').strftime('%Y-%m-%d')
            except ValueError as e:
                messages.error(request, f'Invalid date of birth. {str(e)}')
                return render(request, 'member/spouse.html', context)

            # Save data to the SpouseDetails model
            spouse_details = SpouseDetails(
                up=user_profile,
                spouse_name=spouse_name,
                gender=gender,
                spouse_dob=dob,
                blood_group=blood_group,
                status=spouse_living_status,
                spouse_phone_no=p2,
                spouse_whatsapp_no=p1,
                spouse_work=spouse_work,
                spouse_designation=spouse_designation,  # New field
                spouse_email=spouse_email,
            )
            spouse_details.save()

            # Redirect to a success page or the next step
            return redirect('save_children')  # Replace 'save_children' with the URL or name of the next step

        # If no spouse details exist and it's not a form submission, render the template without 'spouse_details'
        return render(request, 'member/spouse.html',context)



# @login_required
# def save_children(request):
#     user_profile = request.user.userprofile

#     # Check if the user has already submitted owner details
#     existing_owner_details = OwnerDetails.objects.filter(up=user_profile).first()
#     existing_spouse_details = SpouseDetails.objects.filter(up=user_profile).first()

    

#     # Pass the owner_details to the context
#     context = {'owner_details': existing_owner_details,'spouse_details':existing_spouse_details}
    
#     # Check if the user has already submitted children details
#     existing_children_details = ChildrenDetails.objects.filter(up=user_profile)

#     if existing_children_details:
#         # If details exist, display them
#         return render(request, 'member/children.html',{'owner_details': existing_owner_details, 'spouse_details': existing_spouse_details,'children_details': existing_children_details})
#     else:
    
#         children_details = ChildrenDetails.objects.all()

#         if request.method == 'POST':
#         # Process the form data when the form is submitted
#             child_name = request.POST.get('Child_name')
#             gender = request.POST.get('child_gender')
#             birth_order = request.POST.get('child_birth_order')
#             dob_month = request.POST.get('dob_month')
#             dob_day = request.POST.get('dob_day')
#             blood_group = request.POST.get('child_blood_group')
#             living_status = request.POST.get('child_living_status')
#           # Validate and construct the date
#             try:
#             # Using a fixed year (e.g., 2022)
#                 dob = datetime.strptime(f'2022-{dob_month}-{dob_day}', '%Y-%m-%d').date()

#             except ValueError as e:
#                 messages.error(request, f'Invalid date of birth. {str(e)}')
#                 return render(request, 'member/owner.html')

#      # Access the UserProfile associated with the currently logged-in user
#             user_profile = request.user.userprofile


#         # Perform any additional validation if needed

#         # Save data to the ChildrenDetails model
#             child_details = ChildrenDetails(
           
#             child_name=child_name,
#             gender=gender,
#             birth_order=birth_order,
#             dob=dob,
#             blood_group=blood_group,
#             status=living_status,
#             up=user_profile
#             )
#             child_details.save()

#         # Redirect to the next step or a success page
#             # messages.success(request, 'Children details saved successfully.')
#             return redirect('save_children')
    
#         # Pass the children details to the template context
#         context1 = {'children_details': child_details}

#         # Render the form when the page is initially loaded
#         return render(request, 'member/children.html',context,context1)
    
def otherview(request):
    # Get the UserProfile object associated with the currently logged-in user
    user_profile = UserProfile.objects.get(userid=request.user)

    # Retrieve ChildrenDetails objects related to the logged-in user
    other_details = OtherDetails.objects.filter(up=user_profile)
    user_profile = request.user.userprofile

    # Check if the user has already submitted owner details
    existing_owner_details = OwnerDetails.objects.filter(up=user_profile).first()
    existing_spouse_details = SpouseDetails.objects.filter(up=user_profile).first()
    existing_children_details = ChildrenDetails.objects.filter(up=user_profile).first()
    fam = Familyphoto.objects.filter(up=request.user.userprofile)


    # Check if the user has already submitted other details
    existing_other_details = OtherDetails.objects.filter(up=request.user.userprofile)


    # Pass the retrieved ChildrenDetails objects to the template
    context = {
        'od':existing_owner_details,
        'sd':existing_spouse_details,
        'cd':existing_children_details,
        'fp':fam,
        'other_details': other_details,
    }

    # Render the template with the provided context
    return render(request, 'member/otherview.html', context)


    
def childrenview(request):
    # Get the UserProfile object associated with the currently logged-in user
    user_profile = UserProfile.objects.get(userid=request.user)

    # Retrieve ChildrenDetails objects related to the logged-in user
    children_details = ChildrenDetails.objects.filter(up=user_profile)
    user_profile = request.user.userprofile

    # Check if the user has already submitted owner details
    existing_owner_details = OwnerDetails.objects.filter(up=user_profile).first()
    existing_spouse_details = SpouseDetails.objects.filter(up=user_profile).first()
    other = OtherDetails.objects.filter(up=user_profile).first()

    fam = Familyphoto.objects.filter(up=request.user.userprofile)
    print("others", other)
    print("fam", fam)
    # Check if the user has already submitted children details
    existing_children_details = ChildrenDetails.objects.filter(up=user_profile)

    # Pass the owner_details to the context
    context = {'owner_details': existing_owner_details, 
               'spouse_details': existing_spouse_details,
               'other': other,
               'family_photos': fam,
                  'children_details': children_details,}
            #    ' existing_children_details': existing_children_details,}
    


    # Render the template with the provided context
    return render(request, 'member/childrenview.html', context)
@login_required
def save_children(request):
    user_profile = request.user.userprofile

    # Check if the user has already submitted owner details
    existing_owner_details = OwnerDetails.objects.filter(up=user_profile).first()
    existing_spouse_details = SpouseDetails.objects.filter(up=user_profile).first()
    other = OtherDetails.objects.filter(up=user_profile).first()

    fam = Familyphoto.objects.filter(up=request.user.userprofile)
    print("others", other)
    print("fam", fam)

    # Pass the owner_details to the context
    context = {'owner_details': existing_owner_details, 
               'spouse_details': existing_spouse_details,
               'other': other,
               'family_photos': fam}
    
    # Check if the user has already submitted children details
    existing_children_details = ChildrenDetails.objects.filter(up=user_profile)

    if request.method == 'POST':
        # Process the form data when the form is submitted
        child_name = request.POST.get('Child_name')
        gender = request.POST.get('child_gender')
        birth_order = request.POST.get('child_birth_order')
        dob_month = request.POST.get('dob_month')
        dob_day = request.POST.get('dob_day')
        blood_group = request.POST.get('child_blood_group')
        living_status = request.POST.get('child_living_status')
            
        # Validate and construct the date
        try:
            # Using a fixed year (e.g., 2022)
            dob = datetime.strptime(f'2022-{dob_month}-{dob_day}', '%Y-%m-%d').date()

        except ValueError as e:
            messages.error(request, f'Invalid date of birth. {str(e)}')
            return render(request, 'member/owner.html')

        # Save data to the ChildrenDetails model
        child_details = ChildrenDetails(
            child_name=child_name,
            gender=gender,
            birth_order=birth_order,
            dob=dob,
            blood_group=blood_group,
            status=living_status,
            up=user_profile
        )
        child_details.save()

        # Redirect to the next step or a success page
        # messages.success(request, 'Children details saved successfully.')
        return redirect('childrenview')
    
    # Pass the children details to the template context
    context['children_details'] = existing_children_details

    # Render the form when the page is initially loaded
    return render(request, 'member/children.html', context)


@login_required
def save_other(request):
    user_profile = request.user.userprofile

    # Check if the user has already submitted owner details
    existing_owner_details = OwnerDetails.objects.filter(up=user_profile).first()
    existing_spouse_details = SpouseDetails.objects.filter(up=user_profile).first()
    existing_children_details = ChildrenDetails.objects.filter(up=user_profile).first()
    fam = Familyphoto.objects.filter(up=request.user.userprofile)


    # Check if the user has already submitted other details
    existing_other_details = OtherDetails.objects.filter(up=request.user.userprofile)

    if request.method == 'POST':
        # Process the form data when the form is submitted
        country_code = request.POST.get('country_code')  # Retrieve country code from hidden input
        print("Country Code:", country_code)  
        whatsappno1 = request.POST.get('whatsappno')

        # Combine country code and phone number
        full_phone_number = f"+{country_code} {whatsappno1}"

        # Retrieve data from the form
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        gender = request.POST.get('gender')
        whatsappno = full_phone_number
        email = request.POST.get('email')
        dob_month = request.POST.get('dob_month')
        dob_day = request.POST.get('dob_day')
        blood_group = request.POST.get('blood_group')
        relationship_with_owner = request.POST.get('relationship_with_owner')
        status = 1

        # Validate and construct the date
        try:
            # Using a fixed year (e.g., 2022)
            dob = datetime.strptime(f'2022-{dob_month}-{dob_day}', '%Y-%m-%d').date()
        except ValueError as e:
            messages.error(request, f'Invalid date of birth. {str(e)}')
            return render(request, 'member/other.html')

        # Create a new OtherDetails instance
        other_details = OtherDetails(
            up=request.user.userprofile,
            fname=fname,
            lname=lname,
            gender=gender,
            whatsappno=whatsappno,
            email=email,
            dob=dob,
            blood_group=blood_group,
            relationship_with_owner=relationship_with_owner,
            status=status,
        )
        other_details.save()

        # Redirect to a success page or the next step
        return redirect('otherview')  # Replace 'success_page' with the URL or name of the next step

    # If no other details exist and it's not a form submission,
    # render the template without 'other_details'
    return render(request, 'member/other.html', {'family_photos':fam,'owner_details': existing_owner_details, 'spouse_details': existing_spouse_details, 'children_details': existing_children_details, 'other_details': existing_other_details})


# --------------editspouse----------

def edit_spouse(request, spouse_id):
    spouse = get_object_or_404(SpouseDetails, spid=spouse_id)
    user_profile = request.user.userprofile

       # Check if the user has already submitted owner details
    existing_owner_details = OwnerDetails.objects.filter(up=user_profile).first()
    existing_children_details = ChildrenDetails.objects.filter(up=user_profile).first()
    existing_fp_details = Familyphoto.objects.filter(up=user_profile).first()
    existing_other_details = OtherDetails.objects.filter(up=user_profile).first()



    if request.method == 'POST':
        # If the form is submitted, update the existing spouse data
        
                 # Extract country codes from the request
        w = request.POST.get('spcode')
        w1 = request.POST.get('spcode1')
        print('w',w)
        print('w1',w1)
            
        whatsapp_no=request.POST.get('spouse_whatsapp_no')
         
        phone=request.POST.get('spouse_phone_no')
    
       
        p1=f"+{w} {whatsapp_no}"
        p2=f"+{w1} {phone}"
           
        spouse.spouse_name = request.POST.get('spouse_name')
        spouse.gender = request.POST.get('gender')
        spouse.spouse_dob = f'2022-{request.POST.get("dob_month")}-{request.POST.get("dob_day")}'  # Concatenate month and day
        spouse.blood_group = request.POST.get('blood_group')
        spouse.status = request.POST.get('status')
        spouse.spouse_phone_no = p2
        spouse.spouse_whatsapp_no = p1
        spouse.spouse_work = request.POST.get('spouse_work')
        spouse.spouse_designation = request.POST.get('spouse_designation')

        spouse.spouse_email = request.POST.get('spouse_email')

        # Validate and construct the date
        try:
            # Using a fixed year (e.g., 2022)
            dob = datetime.strptime(spouse.spouse_dob, '%Y-%m-%d').strftime('%Y-%m-%d')
            spouse.spouse_dob = dob
        except ValueError as e:
            messages.error(request, f'Invalid date of birth. {str(e)}')
            return render(request, 'member/editspouse.html', {'spouse': spouse})

        spouse.save()

        # Redirect to a success page or any other desired page
        return redirect('save_spouse')
    else:
         # If it's a GET request, pre-fill the form with existing data
         # Extracting year, month, and day from the saved date
        dob_month = spouse.spouse_dob.month
        dob_day = spouse.spouse_dob.day
     

      
        dob_month_names = list(calendar.month_name)[1:]
        dob_days = [str(i).zfill(2) for i in range(1, 32)]

        context = {
            'spouse': spouse,
            'od':existing_owner_details,'cd':existing_children_details,
            'other':existing_other_details,'fp':existing_fp_details,
            'dob_month_names': dob_month_names,
            'dob_days': dob_days,
            'dob_month': dob_month,
            'dob_day': dob_day,
        }
        return render(request, 'member/editspouse.html', context)

# ---------------endeditspouse---------------------------
# -------------------editowner---------------

def edit_owner(request, owner_id):
    owner = get_object_or_404(OwnerDetails, pid=owner_id)
    user_profile = request.user.userprofile

       # Check if the user has already submitted owner details
    existing_child_details = ChildrenDetails.objects.filter(up=user_profile).first()
    existing_spouse_details = SpouseDetails.objects.filter(up=user_profile).first()
    existing_fp_details = Familyphoto.objects.filter(up=user_profile).first()
    existing_other_details = OtherDetails.objects.filter(up=user_profile).first()

    

    if request.method == 'POST':
        
      # Extract country codes from the request
        contact_no_india_country_code = request.POST.get('contact_no_india_country_code')
        contact_no_zm_country_code = request.POST.get('contact_no_zm_country_code')
        whatsapp_country_code = request.POST.get('whatsapp_country_code')
        contact_no_india1=request.POST.get('contact_no_india')
         
        contact_no_zm1=request.POST.get('contact_no_zm')
        print(contact_no_zm1)
        whatsapp_no1=request.POST.get('whatsapp_no')
        contact_no_india=f"+{contact_no_india_country_code} {contact_no_india1}"
        contact_no_zm=f"+{contact_no_zm_country_code} {contact_no_zm1}"
        whatsapp_no=f"+{whatsapp_country_code} {whatsapp_no1}"

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
        owner.contact_no_india =contact_no_india
        owner.contact_no_zm =contact_no_zm
        owner.whatsapp_no = whatsapp_no
        owner.email = request.POST.get('email')
        owner.zmstatus = request.POST.get('zmstatus')
        owner.status =1

        # Validate and construct the date
        try:
            # Using a fixed year (e.g., 2022)
            dob = datetime.strptime(owner.dob, '%Y-%m-%d').strftime('%Y-%m-%d')
            owner.dob = dob
        except ValueError as e:
            messages.error(request, f'Invalid date of birth. {str(e)}')
            return render(request, 'member/editowner.html', {'owner': owner})

        owner.save()

        # Redirect to a success page or any other desired page
        return redirect('save_owner')
    else:
        # If it's a GET request, pre-fill the form with existing data
        # Extracting year, month, and day from the saved date
        dob_month = owner.dob.month
        dob_day = owner.dob.day

        dob_month_names = list(calendar.month_name)[1:]
        dob_days = [str(i).zfill(2) for i in range(1, 32)]

        context = {
            'owner': owner,
            'sd':existing_spouse_details,'cd':existing_child_details,
            'other':existing_other_details,'fp':existing_fp_details,
            'dob_month_names': dob_month_names,
            'dob_days': dob_days,
            'dob_month': dob_month,
            'dob_day': dob_day,
        }
        return render(request, 'member/editowner.html', context)
    # -------------endeditowner------------------
# ----------------editchild----------

def edit_child(request, child_id):
    child = get_object_or_404(ChildrenDetails, cid=child_id)
    user_profile = request.user.userprofile

       # Check if the user has already submitted owner details
    existing_owner_details = OwnerDetails.objects.filter(up=user_profile).first()
    existing_spouse_details = SpouseDetails.objects.filter(up=user_profile).first()
    existing_fp_details = Familyphoto.objects.filter(up=user_profile).first()
    existing_other_details = OtherDetails.objects.filter(up=user_profile).first()



    if request.method == 'POST':
        # If the form is submitted, update the existing child data
        child.child_name = request.POST.get('child_name')
        child.gender = request.POST.get('gender')
        child.birth_order = request.POST.get('birth_order')
        dob_day = request.POST.get('dob_day')
        dob_month = request.POST.get('dob_month')

        try:
            # Using a fixed year (e.g., 2022)
            dob = datetime.strptime(f'2022-{dob_month}-{dob_day}', '%Y-%m-%d').strftime('%Y-%m-%d')
            child.dob = dob
        except ValueError as e:
            messages.error(request, f'Invalid date of birth. {str(e)}')
            return render(request, 'member/editchild.html', {'child': child})

        child.blood_group = request.POST.get('blood_group')
        child.status = request.POST.get('status')

        child.save()

        # Redirect to a success page or any other desired page
        return redirect('childrenview')

    else:
        # If it's a GET request, pre-fill the form with existing data
        # Extracting year, month, and day from the saved date
        dob_month = child.dob.month
        dob_day = child.dob.day

        dob_month_names = list(calendar.month_name)[1:]
        dob_days = [str(i).zfill(2) for i in range(1, 32)]

        context = {
            'child': child,
            'od':existing_owner_details,
            'sd':existing_spouse_details,
            'other':existing_other_details,
            'fp':existing_fp_details,
            'dob_month_names': dob_month_names,
            'dob_days': dob_days,
            'dob_month': dob_month,
            'dob_day': dob_day,
        }
        return render(request, 'member/editchild.html', context) 
    
def edit_image(request, fp_id):
    family_photo = get_object_or_404(Familyphoto, fpid=fp_id)
    user_profile = request.user.userprofile

       # Check if the user has already submitted owner details
    existing_owner_details = OwnerDetails.objects.filter(up=user_profile).first()
    existing_spouse_details = SpouseDetails.objects.filter(up=user_profile).first()
    existing_children_details = ChildrenDetails.objects.filter(up=user_profile).first()
    existing_other_details = OtherDetails.objects.filter(up=user_profile).first()


       

    if request.method == 'POST':
        family_photo.familyphoto = request.FILES.get('familyphoto')
        try:
            family_photo.save()
            # messages.success(request, 'Family photo updated successfully!')
            return redirect('submitfamilyview')  # Replace with the appropriate success URL
        except Exception as e:
            messages.error(request, f'Error updating family photo: {str(e)}')

    return render(request, 'member/edit_image.html', {'family_photo': family_photo,'od':existing_owner_details,'sd':existing_spouse_details,'cd':existing_children_details,'other':existing_other_details})


def save_owner(request):
    user_profile = request.user.userprofile

    # Check if the user has already submitted owner details
    existing_owner_details = OwnerDetails.objects.filter(up=user_profile).first()
    sd = SpouseDetails.objects.filter(up=user_profile).first()
    cd = ChildrenDetails.objects.filter(up=user_profile).first()
    other = OtherDetails.objects.filter(up=user_profile).first()

    family_photos = Familyphoto.objects.filter(up=request.user.userprofile)
    context={'owner_details': existing_owner_details,'od':existing_owner_details,
             'sd':sd,'cd':cd,'other':other,'family_photos':family_photos}


    if existing_owner_details:
        # If details exist, display them
        return render(request, 'member/owner.html',context )
    else:
        if request.method == 'POST':
            # Extract form data from the request
            owner_first_name = request.POST.get('owner_first_name')
            owner_last_name = request.POST.get('owner_last_name')
            family_name = request.POST.get('family_name')
            address_zambia = request.POST.get('address_zambia')
            lcity = request.POST.get('lcity')
            lprovince = request.POST.get('lprovince')
            address_india = request.POST.get('address_india')
            dob_day = request.POST.get('dob_day')
            dob_month = request.POST.get('dob_month')
            email = request.POST.get('email')

           


            try:
                # Using a fixed year (e.g., 2022)
                dob = datetime.strptime(f'2022-{dob_month}-{dob_day}', '%Y-%m-%d').strftime('%Y-%m-%d')
            except ValueError as e:
                messages.error(request, f'Invalid date of birth. {str(e)}')
                return render(request, 'member/owner.html')

            # Check if lprovince is provided
            if not lprovince:
                messages.error(request, 'Please select a living province.')
                return render(request, 'member/owner.html')

            # Access the UserProfile associated with the currently logged-in user
            user_profile = request.user.userprofile



               # Extract country codes from the request
            contact_no_india_country_code = request.POST.get('contact_no_india_country_code')
            contact_no_zm_country_code = request.POST.get('contact_no_zm_country_code')
            whatsapp_country_code = request.POST.get('whatsapp_country_code')
            contact_no_india1=request.POST.get('contact_no_india')
         
            contact_no_zm1=request.POST.get('contact_no_zm')
            print(contact_no_zm1)
            whatsapp_no1=request.POST.get('whatsapp_no')
            contact_no_india=f"+{contact_no_india_country_code} {contact_no_india1}"
            contact_no_zm=f"+{contact_no_zm_country_code} {contact_no_zm1}"
            whatsapp_no=f"+{whatsapp_country_code} {whatsapp_no1}"



            # Create a new OwnerDetails instance and save it to the database
            owner_details = OwnerDetails(
                up=user_profile,
                owner_first_name=owner_first_name,
                owner_last_name=owner_last_name,
                family_name=family_name,
                address_zambia=address_zambia,
                lcity=lcity,
                lprovince=lprovince,
                address_india=address_india,
                dob=dob,
                gender=request.POST.get('gender'),
                blood_group=request.POST.get('blood_group'),
                work_name=request.POST.get('work_name'),
                company_name=request.POST.get('company_name'),
                contact_no_india=contact_no_india,
                cperson=request.POST.get('cperson'),
                contact_no_zm=contact_no_zm,
                whatsapp_no=whatsapp_no,
                email=email,
                zmstatus=request.POST.get('zmstatus'),
                status=1
            )
            print("Before save")
            owner_details.save()
            print("After save")

            # owner_details.save()

            return redirect('save_spouse')  # Redirect to a success page or another URL

    return render(request, 'member/owner.html',context)


def deletechild(request, c_id=None):
    if c_id is None:
        # Handle the case where c_id is not provided
        raise Http404("Child ID not provided")
    try:
        # Try to convert c_id to an integer
        c_id = int(c_id)
    except ValueError:
        # Handle the case where c_id is not a valid integer
        raise Http404("Invalid Child ID")
    # Rest of your view logic
    children = get_object_or_404(ChildrenDetails, cid=c_id)
    children.delete()
    return redirect('childrenview')

def deletespouse(request, sp_id=None):
    if sp_id is None:
        # Handle the case where c_id is not provided
        raise Http404("Spouse ID not provided")
    try:
        # Try to convert c_id to an integer
        sp_id = int(sp_id)
    except ValueError:
        # Handle the case where c_id is not a valid integer
        raise Http404("Invalid Spouse ID")
    # Rest of your view logic
    spouse = get_object_or_404(SpouseDetails, spid=sp_id)
    spouse.delete()
    return redirect('save_spouse')

def deleteother(request, o_id=None):
    if o_id is None:
        # Handle the case where c_id is not provided
        raise Http404("Your Guest ID not provided")
    try:
        # Try to convert c_id to an integer
        o_id = int(o_id)
    except ValueError:
        # Handle the case where c_id is not a valid integer
        raise Http404("Invalid Guest ID")
    # Rest of your view logic
    other = get_object_or_404(OtherDetails, oid=o_id)
    other.delete()
    return redirect('otherview')


def deleteimage(request, fp_id=None):
    if fp_id is None:
        # Handle the case where fp_id is not provided
        raise Http404("Your Family photo ID is not provided")

    try:
        # Try to convert fp_id to an integer
        fp_id = int(fp_id)
    except ValueError:
        # Handle the case where fp_id is not a valid integer
        raise Http404("Invalid Family photo ID")

    # Rest of your view logic
    im = get_object_or_404(Familyphoto, fpid=fp_id)
    im.delete()

    # Redirect to 'save_fp' with a success message if needed
    # You can customize the success message based on your requirements
    return redirect('save_fp')



def deleteowner(request, pid=None):
    if pid is None:
        # Handle the case where pid is not provided
        raise Http404("Owner ID not provided")
    try:
        # Try to convert pid to an integer
        pid = int(pid)
    except ValueError:
        # Handle the case where pid is not a valid integer
        raise Http404("Invalid Owner ID")
      # Get the currently logged-in user
    current_user = request.user
    
    # Retrieve the UserProfile associated with the currently logged-in user
    user_profile = get_object_or_404(UserProfile, userid=current_user)
    
    # Set the status to 2 (or any other desired status)
    user_profile.status = 2
    
    # Save the changes to the UserProfile
    user_profile.save()
    
    # Rest of your view logic
    owner = get_object_or_404(OwnerDetails, pid=pid)
    owner.delete()
    return redirect('save_owner')


def edit_other(request, o_id):
    user_profile = request.user.userprofile

       # Check if the user has already submitted owner details
    existing_owner_details = OwnerDetails.objects.filter(up=user_profile).first()
    existing_spouse_details = SpouseDetails.objects.filter(up=user_profile).first()
    existing_children_details = ChildrenDetails.objects.filter(up=user_profile).first()
    fam = Familyphoto.objects.filter(up=request.user.userprofile)

       
    other = get_object_or_404(OtherDetails, oid=o_id)

    if request.method == 'POST':
        # If the form is submitted, update the existing child data


        country_code = request.POST.get('country_code')  # Retrieve country code from hidden input
        print("Country Code:", country_code)  
        whatsappno1 = request.POST.get('whatsappno')

        # Combine country code and phone number
        full_phone_number = f"+{country_code} {whatsappno1}"

        
        other.fname = request.POST.get('fname')
        other.lname = request.POST.get('lname')
        other.gender = request.POST.get('gender')
        other.whatsappno = full_phone_number
        other.email = request.POST.get('email')
        other.relationship_with_owner = request.POST.get('relationship_with_owner')
        dob_day = request.POST.get('dob_day')
        dob_month = request.POST.get('dob_month')
        

        try:
            # Using a fixed year (e.g., 2022)
            dob = datetime.strptime(f'2022-{dob_month}-{dob_day}', '%Y-%m-%d').strftime('%Y-%m-%d')
            other.dob = dob
        except ValueError as e:
            messages.error(request, f'Invalid date of birth. {str(e)}')
            return render(request, 'member/editother.html', {'other': other})

        other.blood_group = request.POST.get('blood_group')
        other.status = 1

        other.save()

        # Redirect to a success page or any other desired page
        return redirect('otherview')

    else:
        # If it's a GET request, pre-fill the form with existing data
        # Extracting year, month, and day from the saved date
        dob_month = other.dob.month
        dob_day = other.dob.day

        dob_month_names = list(calendar.month_name)[1:]
        dob_days = [str(i).zfill(2) for i in range(1, 32)]

        context = {
            'od':existing_owner_details,
            'sd':existing_spouse_details,
            'cd':existing_children_details,
            'fp':fam,
            'other': other,
            'dob_month_names': dob_month_names,
            'dob_days': dob_days,
            'dob_month': dob_month,
            'dob_day': dob_day,
        }
       
   
        return render(request, 'member/editother.html',context) 
    
def familyview(request):
    user_profile = request.user.userprofile

    # Fetch all details related to the user
    od = OwnerDetails.objects.filter(up=user_profile).first()
    sd = SpouseDetails.objects.filter(up=user_profile).first()
    cd = ChildrenDetails.objects.filter(up=user_profile)
    other_details = OtherDetails.objects.filter(up=user_profile).all()

    # other_details = OtherDetails.objects.filter(up=user_profile).first()
    family_photos = Familyphoto.objects.filter(up=request.user.userprofile).all()

    context = {
        'od': od,
        'sd': sd,
        'cd': cd,
        'other_details': other_details,
        'family_photos': family_photos,
    }
    return render(request, 'member/familyview.html', context)


def submitfamilyview(request):
    user_profile = request.user.userprofile

    # Fetch all details related to the user
    od = OwnerDetails.objects.filter(up=user_profile).first()
    sd = SpouseDetails.objects.filter(up=user_profile).first()
    cd = ChildrenDetails.objects.filter(up=user_profile)
    other_details = OtherDetails.objects.filter(up=user_profile).all()

    # other_details = OtherDetails.objects.filter(up=user_profile).first()
    family_photos = Familyphoto.objects.filter(up=request.user.userprofile).all()

    context = {
        'od': od,
        'sd': sd,
        'cd': cd,
        'other_details': other_details,
        'family_photos': family_photos,
    }
    return render(request, 'member/submitfamilyview.html', context)

def submit_status(request):
    if request.method == 'POST':
        status = 3  # Set status to 3
        # Update the user's profile status
        user_profile = UserProfile.objects.get(userid=request.user)
        user_profile.status = status
        user_profile.save()
        # Respond with a JSON indicating success
        return JsonResponse({'status': 'success'})
    else:
        # Respond with a JSON indicating failure for non-POST requests
        return JsonResponse({'status': 'failure'})


# def render_to_pdf(template_src, context_dict):
#     html = render_to_string(template_src, context_dict)
#     result = BytesIO()

#     pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
#     if not pdf.err:
#         response = HttpResponse(content_type='application/pdf')
#         response['Content-Disposition'] = 'filename="your_filename.pdf"'  # Adjust filename as needed
#         response.write(result.getvalue())
#         return response

#     return HttpResponse('Failed to generate PDF: {}'.format(pdf.err), status=500)

# def generate_pdf(request):
#     # Fetch data from your models
#     od = OwnerDetails.objects.first()  # Adjust this to fetch the specific data you need
#     sd = SpouseDetails.objects.first()
#     cd = ChildrenDetails.objects.all()
#     other_details = OtherDetails.objects.all()

#     # Check if variables exist before passing them to the template
#     context = {'od': od}
#     if sd:
#         context['sd'] = sd
#     if cd:
#         context['cd'] = cd
#     if other_details:
#         context['other_details'] = other_details
#         # Include the image paths
#  # Include the image paths
#     context['family_photo_path'] = od.familyphoto.familyphoto.url if od.familyphoto else None
#     context['logo_path'] = '{% static "img/logo.jpg" %}'

#     # Render the PDF and return it in the response
#     return render_to_pdf('familyview.html', context)


def members_view1(request):



    # Retrieve all user profiles with status=2
    # members_info = UserProfile.objects.filter(Q(status=2) | Q(status=3)).count()
    members_info = UserProfile.objects.filter(Q(status=2) | Q(status=3))
    members_count = members_info.count()




     # Retrieve information from UserProfile and OwnerDetails models
    up = UserProfile.objects.all().count()
    owners_count = OwnerDetails.objects.filter(up__status=2).count()
    spouses_count = SpouseDetails.objects.filter(up__status=2).count()
    children_count = ChildrenDetails.objects.filter(up__status=2).count()
    other_details_count = OtherDetails.objects.filter(up__status=2).count()
    tc=0
    tf=0
    tf=up
    tc = owners_count + spouses_count + children_count + other_details_count

    # Search functionality
    query = request.GET.get('q')
    if query:
        # Filter user profiles based on search query
        members_info = members_info.filter(
            Q(firstname__icontains=query) |
            Q(lastname__icontains=query) |
            Q(familyname__icontains=query) |
            Q(email__icontains=query) |
            Q(phonenumber__icontains=query)
        |
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


    # Order the queryset by a field to avoid UnorderedObjectListWarning
    members_info = members_info.order_by('id')

     # Calculate total count for each member
    for member in members_info:
        owner_count = OwnerDetails.objects.filter(up=member).count()
        spouse_count = SpouseDetails.objects.filter(up=member).count()
        children_count = ChildrenDetails.objects.filter(up=member).count()
        other_count = OtherDetails.objects.filter(up=member).count()
        
        member.total = owner_count + spouse_count + children_count + other_count


    # Set the number of items per page
    items_per_page = 7

    # Create a Paginator instance
    paginator = Paginator(members_info, items_per_page)

    # Get the current page number from the request's GET parameters
    page_number = request.GET.get('page', 1)

    try:
        # Get the current page
        current_page = paginator.page(page_number)
    except EmptyPage:
        # If the page is out of range, deliver the last page of results
        current_page = paginator.page(paginator.num_pages)

    try:
        user_profile = UserProfile.objects.get(userid=request.user)
    except UserProfile.DoesNotExist:
        messages.error(request, 'UserProfile does not exist for this user.')
        return redirect('index') 
    
    committecount = CommitteeMember.objects.count()

       # Fetch counts of active and pending events
    active_events_count = EventNotification.objects.filter(status='Active').count()
    pending_events_count = EventNotification.objects.filter(status='Pending').count()
    teventscount=active_events_count+pending_events_count


    context = {
        'ufn': user_profile.firstname,
        'uln': user_profile.lastname,
        'fn': user_profile.familyname,
        'email': user_profile.email,
        'uacount': members_info.count(),
        't': tc,  # Placeholder for total count
        'tf': members_info.count(),  # Placeholder for total family
        'members_info': current_page,  # Pass paginated queryset to the context
        'ccount':committecount,
        'teventscount':teventscount,
    }

    return render(request, 'member/membersview1.html', context)

def fam_view1(request):
    ua= UserProfile.objects.filter(Q(status=2) | Q(status=3)).count()
    uacount=ua.count()
    # Retrieve information from UserProfile and OwnerDetails models
    up = UserProfile.objects.all().count()
    owners_count = OwnerDetails.objects.all().count()
    print(owners_count)
    spouses_count = SpouseDetails.objects.all().count()
    children_count = ChildrenDetails.objects.all().count()
    other_details_count = OtherDetails.objects.all().count()
    tc=0
    tf=0
    tf=up
    #total
    tc = owners_count + spouses_count + children_count + other_details_count
    # members_info = UserProfile.objects.all()
    members_info = UserProfile.objects.filter(Q(status=2) | Q(status=3)).count()
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

    return render(request, 'member/fam.html', context)


def view_family1(request, user_id):
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
    }
    
    # Render the 'viewfamily.html' template with the provided context
    return render(request, 'member/viewfamily1.html',context)





def loadlogout(request):
     # Clear any existing messages
    messages.success(request, '')

    auth.logout(request)
    return redirect('/')

def committemembers(request):
    user_profile = UserProfile.objects.get(userid=request.user)
    years = range(2000, 2051)

    # Get the latest year
    latest_year = CommitteeMember.objects.filter(status='Active').aggregate(latest_year=Max('year'))['latest_year']

    # Fetch active committee members for the latest year initially
    latest_committee_members = CommitteeMember.objects.filter(year=latest_year)

    # ccount = latest_committee_members.count()
      # Get the count of members for the latest year
    latest_committee_members_count = latest_committee_members.count()

    # Search functionality
    search_query = request.GET.get('q')
    search_year = request.GET.get('year')  # Get the year from the request parameters

    # If a year is provided in the search parameters, filter by that year
    if search_year:
        # latest_committee_members = CommitteeMember.objects.filter(status='Active', year=latest_year)

        latest_committee_members = CommitteeMember.objects.filter( year=search_year)

    if search_query:
        latest_committee_members = latest_committee_members.filter(
            Q(member_name__icontains=search_query) |  # Search by member name (case-insensitive)
            Q(post__icontains=search_query)         # Search by post (case-insensitive)
            # Q(status__icontains=search_query)        # Search by status (case-insensitive)
        )

    committecount = CommitteeMember.objects.count()

       # Fetch counts of active and pending events
    active_events_count = EventNotification.objects.filter(status='Active').count()
    pending_events_count = EventNotification.objects.filter(status='Pending').count()
    teventscount=active_events_count+pending_events_count
    uacount = UserProfile.objects.filter(Q(status=2) | Q(status=3)).count()





    return render(request, 'member/committemembers.html', {
        'up': user_profile,
        'years': years,
        'committee_members': latest_committee_members,
        'ccount':latest_committee_members_count,'teventscount':teventscount,'uacount':uacount
    })




def birthdaydetails(request):
    user_profile = UserProfile.objects.get(userid=request.user)

    owners = OwnerDetails.objects.all()
    spouses = SpouseDetails.objects.all()
    children = ChildrenDetails.objects.all()
    others = OtherDetails.objects.all()

    # Filter birthdays based on the selected month if provided in the request
    selected_month = request.GET.get('month')
    if selected_month:
        owners = owners.filter(dob__month=selected_month)
        spouses = spouses.filter(spouse_dob__month=selected_month)
        children = children.filter(dob__month=selected_month)
        others = others.filter(dob__month=selected_month)
     # Filter birthdays based on the search input if provided in the request
    search_name = request.GET.get('q')
    if search_name:
        owners = owners.filter(owner_first_name__icontains=search_name) | owners.filter(owner_last_name__icontains=search_name)
        spouses = spouses.filter(spouse_name__icontains=search_name)
        children = children.filter(child_name__icontains=search_name)
        others = others.filter(fname__icontains=search_name) | others.filter(lname__icontains=search_name)
    today = date.today()  # Get the current date


    # owner_data = [(f"{owner.owner_first_name} {owner.owner_last_name}", owner.dob) for owner in owners]
    # spouse_data = [(spouse.spouse_name, spouse.spouse_dob) for spouse in spouses]
    # children_data = [(child.child_name, child.dob) for child in children]
    # other_data = [(f"{other.fname} {other.lname}", other.dob) for other in others]

       # Combine all birthday data
    birthday_data = []
    for owner in owners:
        birthday_data.append((f"{owner.owner_first_name} {owner.owner_last_name}", owner.dob))
    for spouse in spouses:
        birthday_data.append((spouse.spouse_name, spouse.spouse_dob))
    for child in children:
        birthday_data.append((child.child_name, child.dob))
    for other in others:
        birthday_data.append((f"{other.fname} {other.lname}", other.dob))
    
    # Sort birthday data by month and day
    sorted_birthday_data = sorted(birthday_data, key=lambda x: (x[1].month, x[1].day))




    committecount = CommitteeMember.objects.count()

       # Fetch counts of active and pending events
    active_events_count = EventNotification.objects.filter(status='Active').count()
    pending_events_count = EventNotification.objects.filter(status='Pending').count()
    teventscount=active_events_count+pending_events_count
    uacount = UserProfile.objects.filter(Q(status=2) | Q(status=3)).count()


    context = {
         'birthday_data': sorted_birthday_data,
        'today':today,
        # 'owner_data': owner_data,
        # 'spouse_data': spouse_data,
        # 'children_data': children_data,
        # 'other_data': other_data,
        'up': user_profile,
        'ccount':committecount,
        'teventscount':teventscount,
        'uacount':uacount,  
    }

    return render(request, 'member/birthday.html', context)

def bloodgroup(request):
    user_profile = UserProfile.objects.get(userid=request.user)

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
    committecount = CommitteeMember.objects.count()
    uacount = UserProfile.objects.filter(Q(status=2) | Q(status=3)).count()

       # Fetch counts of active and pending events
    active_events_count = EventNotification.objects.filter(status='Active').count()
    pending_events_count = EventNotification.objects.filter(status='Pending').count()
    teventscount=active_events_count+pending_events_count


    # Prepare context data
    context = {
        'owner_data': owner_data,
        'spouse_data': spouse_data,
        'children_data': children_data,
        'other_data': other_data,
        'up': user_profile,
        'ccount':committecount,
        'teventscount':teventscount,
        'uacount':uacount,
    }
    return render(request, 'member/bloodgroup.html', context)



 

@login_required
def payments1(request):
    # Get the user profile based on the user_id or return a 404 page if not found
    user_profile = get_object_or_404(UserProfile, userid=request.user)
    
    # Retrieve first name and last name from the user profile
    fname = user_profile.firstname
    lname = user_profile.lastname
    
    # Get owner details related to the user profile if available
    owner_details = OwnerDetails.objects.filter(up=user_profile).first()
    
    # Get ZMCA status from owner details if available
    zmstatus = owner_details.zmstatus if owner_details else None
    
    # Retrieve all membership details
    memberships = MembershipDetail.objects.filter(user_profile=user_profile)

    # Additional code to fetch from_date and to_date based on membership_id
    membership_years = []
    for membership_detail in memberships:
        membership_id = membership_detail.membership_id
        membership = get_object_or_404(Membership, membership_id=membership_id)
        membership_years.append((membership.from_date, membership.to_date))

    # print(  "membersshipyears", membership_years)

    # Search functionality
  # Search functionality
    search_query = request.GET.get('q')
    if search_query:
            if search_query.isdigit() and len(search_query) == 4:
        # Search query is a year, filter memberships by that year
                memberships = memberships.filter(
                Q(membership_year=search_query) | Q(payment_date=search_query) 
        )
            else:
        # Regular search across multiple fields in MembershipDetail model
                memberships = memberships.filter(
            Q(amount__icontains=search_query) |
            Q(usercategory__icontains=search_query) |
            Q(payment_date__icontains=search_query)  # Assuming you want to search payment_date as well
            # Include other fields you want to search here
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


         # Retrieve user profile information
    user_profile = UserProfile.objects.get(userid=request.user)
    committecount = CommitteeMember.objects.count()
    uacount = UserProfile.objects.filter(Q(status=2) | Q(status=3)).count()

       # Fetch counts of active and pending events
    active_events_count = EventNotification.objects.filter(status='Active').count()
    pending_events_count = EventNotification.objects.filter(status='Pending').count()
    teventscount=active_events_count+pending_events_count


    # Prepare context data to pass to the template
    context = {
        'user_profile': user_profile,
        'ufn': user_profile.firstname,
        'uln': user_profile.lastname,
        'fn': user_profile.familyname,
        'email': user_profile.email,
        'zmstatus': zmstatus,
        'membership_years': membership_years,  
        'page_obj': page_obj,
        'search_query': search_query,
        'teventscount':teventscount,
        'ccount':committecount,
        'uacount':uacount,
    }

    return render(request, 'member/payments1.html', context)



@login_required
def job_posts(request):
    user_profile = UserProfile.objects.get(userid=request.user)
    posts = Post.objects.filter(is_active=False)
    
    context = {
        'ufn': user_profile.firstname,
        'uln': user_profile.lastname,
        'fn': user_profile.familyname,
        'email': user_profile.email,
        'teventscount': EventNotification.objects.filter(status__in=['Active', 'Pending']).count(),
        'ccount': CommitteeMember.objects.filter(status='Active').count(),
        'uacount': UserProfile.objects.filter(status__in=[2, 3]).count(),
        'posts':posts,
    }
    return render(request, 'member/post-list.html', context)

@login_required
def create_post(request):
    if request.method == "POST":
        post_type = request.POST.get("post_type")
        title = request.POST.get("title")
        description = request.POST.get("description")
        contact_info = request.POST.get("contact")

        if not (title and description and contact_info):
            messages.error(request, "Please fill in all required fields.")
            return redirect("job_posts")

        post = Post.objects.create(
            post_type=post_type,
            title=title,
            description=description,
            contact_info=contact_info,
            status="Open", 
            is_active=False  
        )

        messages.success(request, f"Post '{post.title}' created successfully ")
        return redirect("job_posts")  

    return render(request, "member/create-post.html")
    
def community_services(request):
    return render(request, 'landing/community-service.html')


from services.models import Staff
def agency_posts(request):
    staff_list = Staff.objects.filter(status="Pending").order_by("-created_at")    
    context = {
        'staff_list': staff_list
    }
    return render(request, 'member/agencypost.html', context)

from services.models import StaffRequest

@login_required
def request_staff(request, staff_id):
    staff = get_object_or_404(Staff, id=staff_id)
    try:
        user_profile = UserProfile.objects.get(userid=request.user)
    except UserProfile.DoesNotExist:
        messages.error(request, "[REQUEST] You need a profile to request staff.")
        return redirect("agency_posts") 

    existing_request = StaffRequest.objects.filter(
        requester=user_profile,
        staff=staff
    ).first()

    if existing_request:
        messages.warning(request, f"[REQUEST] You already submitted a request for {staff.full_name}.")
        return redirect("agency_posts")

    # Create a new request
    StaffRequest.objects.create(
        requester=user_profile,
        agency=staff.agency,
        staff=staff,
        status="Pending"
    )
    messages.success(request, f"[REQUEST] Your request for {staff.full_name} has been submitted.")
    return redirect("agency_posts")

