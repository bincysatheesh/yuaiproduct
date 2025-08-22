from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Agency
from multiselectfield import MultiSelectField
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Staff
from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Staff
from django.db.models import Count


def agency_signup(request):
    agency_types = Agency._meta.get_field('agency_type').choices
    service_categories = Agency._meta.get_field('service_categories').choices
    if request.method == 'POST':
        try:
            username = request.POST.get('email')  # Using email as username
            email = request.POST.get('email')
            password = request.POST.get('password')
            cpassword = request.POST.get('cpassword')
            
            # Password validation
            if password != cpassword:
                messages.error(request, "Passwords do not match!")
                return redirect('agency_signup')
                
            if User.objects.filter(username=username).exists():
                messages.error(request, "An account with this email already exists!")
                return redirect('agency_signup')
                
            # Create the user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            # Handle agency data
            agency_name = request.POST.get('agency_name')
            owner_contact_person = request.POST.get('owner_contact_person')
            contact_number = request.POST.get('contact_number')
            country_code = request.POST.get('country_code', '')
            full_phone = f"+{country_code}{contact_number}" if country_code else contact_number
            
            agency = Agency.objects.create(
                user=user,
                agency_name=agency_name,
                owner_contact_person=owner_contact_person,
                contact_number=full_phone,
                email=email,
                office_address=request.POST.get('office_address'),
                agency_type=request.POST.getlist('agency_type'),  # For multiple values
                service_categories=request.POST.getlist('service_categories'),
                years_in_operation=request.POST.get('years_in_operation'),
                number_of_staff=request.POST.get('number_of_staff'),
                preferred_service_area=request.POST.get('preferred_service_area'),
                availability=request.POST.get('availability'),
                short_description=request.POST.get('short_description'),
                consent_agreed=bool(request.POST.get('consent_agreed')),
                status='Submitted'
            )
            
            # Handle file upload
            if 'verification_documents' in request.FILES:
                agency.verification_documents = request.FILES['verification_documents']
                agency.save()
            
            messages.success(request, "Agency registration successful! Your account will be activated after verification.")
            return redirect('mlogin')  # Redirect to login page
            
        except Exception as e:
            messages.error(request, f"Error during registration: {str(e)}")
            return redirect('agency_signup')
    

    context = {
        'AGENCY_TYPES': agency_types,
        'SERVICE_CATEGORIES': service_categories
    }
    return render(request, 'services/agencysignup.html', context)


from members.models import *


def agency_dashboard(request):
    agency = Agency.objects.get(user=request.user)
    all_staff = Staff.objects.filter(agency=agency)
    posts = Post.objects.filter(is_active=False)

    total_staff = all_staff.count()
    approved_staff = all_staff.filter(status='Approved').count()
    pending_staff = all_staff.filter(status='Submitted').count()
    rejected_staff = all_staff.filter(status='Rejected').count()
    
    page = request.GET.get('page', 1)
    paginator = Paginator(all_staff, 10)  # Show 10 staff per page
    staff_list = paginator.get_page(page)
    
    context = {
        'total_staff': total_staff,
        'approved_staff': approved_staff,
        'pending_staff': pending_staff,
        'rejected_staff': rejected_staff,
        'staff_list': staff_list,
        'posts':posts,
 
        'notifications': [],  # You can add actual notifications here
    }
    return render(request, 'services/agencydash.html', context)



def view_staff(request, staff_id):
    agency = Agency.objects.get(user=request.user)

    staff = get_object_or_404(Staff, id=staff_id, agency=agency)
    return render(request, 'services/staffview.html', {'staff': staff})

def staff_list(request):
    agency = Agency.objects.get(user=request.user)
    staff_queryset = Staff.objects.filter(agency=agency)
    
    service_type = request.GET.get('service_type')
    status = request.GET.get('status')
    search_query = request.GET.get('search', '').strip()
    
    if service_type:
        staff_queryset = staff_queryset.filter(service_type=service_type)
    
    if status:
        staff_queryset = staff_queryset.filter(status=status)
    
    if search_query:
        staff_queryset = staff_queryset.filter(
            models.Q(full_name__icontains=search_query) |
            models.Q(skills_duties__icontains=search_query) |
            models.Q(languages__icontains=search_query)
        )
    
    status_counts = staff_queryset.values('status').annotate(count=Count('status'))

    # initialize counts
    staff_count = {choice[0]: 0 for choice in Staff.STAFF_STATUS}

    for item in status_counts:
        staff_count[item['status']] = item['count']
    
    paginator = Paginator(staff_queryset.order_by('-created_at'), 25)  # 25 items per page
    page_number = request.GET.get('page')
    staff_page = paginator.get_page(page_number)
    
    context = {
        'staff_page': staff_page,
        'service_types': Staff.SERVICE_TYPES,
        'status_choices': Staff.STAFF_STATUS,
        'staff_count': staff_count,
    }
    
    return render(request, 'services/stafflist.html', context)



def add_staff(request):
    agency = Agency.objects.get(user=request.user)

    if request.method == 'POST':
        form_data = request.POST
        files = request.FILES

        try:
            staff = Staff(
                agency=agency,
                full_name=form_data.get('full_name'),
                age=form_data.get('age'),
                email = form_data.get('email'),
                contact_no = form_data.get('contact_no'),
                address=form_data.get('address'),
                service_type=form_data.get('service_type'),
                skills_duties=form_data.get('skills_duties'),
                experience_years=form_data.get('experience_years'),
                languages=form_data.get('languages'),
                availability=form_data.get('availability'),
                notes=form_data.get('notes'),
                status='Pending'
            )

            if 'photo' in files:
                staff.photo = files['photo']

            staff.save()

            return redirect('staff_list')  

        except Exception as e:
            context = {'error': str(e)}
            return render(request, 'services/addstaff.html', context)

    return render(request, 'services/addstaff.html')

def edit_staff(request, staff_id):
    agency = Agency.objects.get(user=request.user)
    staff = get_object_or_404(Staff, id=staff_id, agency=agency)

    if request.method == 'POST':
        form_data = request.POST
        files = request.FILES

        try:
            staff.full_name = form_data.get('full_name', staff.full_name)
            staff.age = form_data.get('age', staff.age)
            staff.email = form_data.get('email', staff.email)
            staff.contact_number = form_data.get('contact_no', staff.contact_number)
            staff.address = form_data.get('address', staff.address)
            staff.service_type = form_data.get('service_type', staff.service_type)
            staff.skills_duties = form_data.get('skills_duties', staff.skills_duties)
            staff.experience_years = form_data.get('experience_years', staff.experience_years)
            staff.languages = form_data.get('languages', staff.languages)
            staff.availability = form_data.get('availability', staff.availability)
            staff.notes = form_data.get('notes', staff.notes)

            if 'photo' in files:
                staff.photo = files['photo']

            staff.save()
            return redirect('staff_list')  # Redirect to staff list page after update

        except Exception as e:
            context = {'error': str(e), 'staff': staff, 'edit_mode': True}
            return render(request, 'services/staff_form.html', context)

    context = {
        'staff': staff,
        'service_types': Staff.SERVICE_TYPES,   
        'edit_mode': True
    }
    return render(request, 'services/staffedit.html', context)

def activate_staff(request, pk):
    staff = get_object_or_404(Staff, pk=pk)
    staff.status = 'Active'
    staff.save()
    messages.success(request, f"Staff '{staff.full_name}' is now Active ✅")
    return redirect('staff_list')


def deactivate_staff(request, pk):
    staff = get_object_or_404(Staff, pk=pk)
    staff.status = 'Pending'
    staff.save()
    messages.warning(request, f"Staff '{staff.full_name}' has been set to Pending ⏸️")
    return redirect('staff_list')


def delete_staff(request, pk):
    staff = get_object_or_404(Staff, pk=pk)
    staff_name = staff.full_name
    staff.delete()
    messages.error(request, f"Staff '{staff_name}' has been deleted ❌")
    return redirect('staff_list')

