
from django.urls import path,include
from .import views
urlpatterns = [  
    # # path('', views.index, name='index'),
    # path('adminlogin/',views.adminlogin,name='adminlogin'),
    path('', views.index, name='index'),
    path('adminindex',views.adminindex,name='adminindex'),
    path('membersview/',views.members_view, name='members_view'),
    path('famview/',views.fam_view, name='fam_view'),
    path('contactus/',views.contactus, name='contactus'),
    path('committe/',views.committe, name='committe'),
    path('ourteam/',views.ourteam, name='ourteam'),


    path('editcommitte/<int:member_id>/', views.editcommitte, name='editcommitte'),
    path('delete_member/<int:member_id>/',views.delete_member,name='delete_member'),

    path('gallerycat/',views.gallerycat,name='gallerycat'),
    
    path('edit_category/<int:category_id>/',views. edit_category, name='edit_category'),
    path('delete_category/<int:category_id>/',views. delete_category, name='delete_category'),


    
    path('enquiry_list/',views.enquiry_list, name='enquiry_list'),
    path('delete-enquiry/<int:message_id>/', views.delete_enquiry, name='delete_enquiry'),
    path('delete-enquiry1/<int:message_id>/', views.delete_enquiry1, name='delete_enquiry1'),

    path('reply_enquiry/<int:message_id>/',views.reply_to_enquiry, name='reply_enquiry'),
    path('allenquiry_list/',views.allenquiry_list, name='allenquiry_list'),

    path('completedenquirylist/',views.completedenquirylist, name='completedenquirylist'),
    path('editenquiry/<int:gid>/', views.editenquiry, name='editenquiry'),



    path('view-family/<int:user_id>/',views.view_family, name='view_family'),
    path('approvefamily/<int:family_id>/', views.approvefamily, name='approvefamily'),
    path('deletefamily/<int:f_id>/',views.deletefamily, name='deletefamily'),
    path('deletefamily1/<int:f_id>/',views.deletefamily1, name='deletefamily1'),

    path('delete-owner/<int:user_profile_id>/', views.delete_owner, name='delete_owner'),

    path('delete_spouse/<int:user_profile_id>/',views. delete_spouse, name='delete_spouse'),
    path('delete_children/<int:user_profile_id>/',views. delete_children, name='delete_children'),
    path('delete_other_details/<int:user_profile_id>/',views. delete_other_details, name='delete_other_details'),
    path('delete-family-photo/<int:user_profile_id>/', views.delete_family_photo, name='delete_family_photo'),

    path('adminedit_owner/<int:user_profile_id>/', views.adminedit_owner, name='adminedit_owner'),

    # path('adminedit_image/<int:user_profile_id>/',views.adminedit_image, name='adminedit_image'),
    # path('edit_other/<int:o_id>/',views.edit_other, name='edit_other'),
    # path('edit_spouse/<int:spouse_id>/',views.edit_spouse, name='edit_spouse'),

    

    # path('logout/', views.loadlogout, name='logout'),
    path('birthdaydetails1/',views.birthdaydetails1, name='birthdaydetails1'),
    path('bloodgroupadmin/',views.bloodgroupadmin, name='bloodgroupadmin'),
    
    path('send-birthday-wish/', views.send_birthday_wish, name='send_birthday_wish'),
    path('addgallery/', views.addgallery, name='addgallery'),
    path('galleryview/', views.galleryview, name='galleryview'),
    path('gallerycommon/', views.gallerycommon, name='gallerycommon'),
    path('addgalleryview/', views.addgalleryview, name='addgalleryview'),
    path('gallery/',views.gallery,name='gallery'),
    path('editgallery/<int:gid>/', views.editgallery, name='editgallery'),
    path('deletegalleryview/<int:gid>/', views.deletegalleryview, name='deletegalleryview'),
    path('notification/', views.notification, name='notification'),
    path('eventview/', views.eventview, name='eventview'),
    path('allevents/', views.allevents, name='allevents'),


    path('deleventview/<int:gid>/', views.deleventview, name='deleventview'),
    path('editevent/<int:gid>/', views.editevent, name='editevent'),
    path('addblogview/', views.addblogview, name='addblogview'),
    path('allblogview/', views.allblogview, name='allblogview'),

    path('addblog/', views.addblog, name='addblog'),
    path('addblogdetail/<int:blog_id>/', views.add_blog_detail, name='addblogdetail'),
    path('delblogview/<int:gid>/', views.delblogview, name='delblogview'),
    path('editblog/<int:gid>/', views.editblog, name='editblog'),
    path('blogs/', views.blogs, name='blogs'),
    path('blogsdetail/<int:blog_id>/', views.blogsdetail, name='blogsdetail'),


    path('memberships/', views.memberships, name='memberships'),
    path('delmemberdata/<int:gid>/', views.delmemberdata, name='delmemberdata'),
    path('editmembershipdata/<int:gid>/', views.editmembershipdata, name='editmembershipdata'),
    path('paynow/<int:user_id>/', views.paynow, name='paynow'),
    path('get_amount/',views.get_amount, name='get_amount'),
    path('delmemberdetails/<int:gid>/', views.delmemberdetails, name='delmemberdetails'),
    path('editmembershipdetails/<int:gid>/', views.editmembershipdetails, name='editmembershipdetails'),

    path('block_user/<int:user_id>/', views.block_user, name='block_user'),
    path('payments/<int:user_id>/', views.payments, name='payments'),



    path('addhomegallery/', views.addhomegallery, name='addhomegallery'),
    path('addhgallery/', views.addhgallery, name='addhgallery'),
    path('edithgallery/<int:gid>/', views.edithgallery, name='edithgallery'),
    path('deletehgallery/<int:gid>/', views.deletehgallery, name='deletehgallery'),


    path('admin-job-posts/', views.admin_services_posts, name='admin_services_posts'),
    path('admin-agency-list/', views.agency_list, name='agency_list'),
    path('agencies/<int:pk>/approve/', views.approve_agency, name='approve_agency'),
    path('agencies/<int:pk>/reject/', views.reject_agency, name='reject_agency'),
    path('agencies/<int:pk>/delete/', views.delete_agency, name='delete_agency'),
    path('agencies/<int:pk>/suspend/', views.suspend_agency, name='suspend_agency'),






















    
]
