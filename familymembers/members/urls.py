from django.contrib.auth import views as auth_views
from django.urls import path,include
from .import views
urlpatterns = [  
   
    path('memberlogin/',views.memberlogin,name='memberlogin'),
    path('mlogin',views.mlogin,name='mlogin'),
    path('membersignup/',views.membersignup,name='membersignup'),
    path('msignup/',views.msignup,name='msignup'),

    path('welcome/', views.welcome, name='welcome'),
    path('aboutus/',views.aboutus, name='aboutus'),
    path('gallerycategory/',views.gallerycategory,name='gallerycategory'),
    path('adminaboutus/',views.adminaboutus, name='adminaboutus'),
    path('memberaboutus/',views.memberaboutus, name='memberaboutus'),
    path('membersview1/',views.members_view1, name='members_view1'),
    path('childrenview/',views.childrenview, name='childrenview'),
    path('otherview/',views.otherview, name='otherview'),
    path('cevents/', views.cevents, name='cevents'),



    path('famview1/',views.fam_view1, name='fam_view1'),
    path('view-family1/<int:user_id>/',views.view_family1, name='view_family1'),
    path('committemembers/',views.committemembers, name='committemembers'),
    path('birthdaydetails/',views.birthdaydetails, name='birthdaydetails'),
    path('bloodgroup/',views.bloodgroup, name='bloodgroup'),




    




    # path('',views.loadindex,name='loadindex'), 
    path('customerindex/',views.customerindex,name='customerindex'),

    path('memberindex/',views.memberindex,name='memberindex'),
    path('save_owner/',views.save_owner, name='save_owner'),
    path('save_spouse/',views.save_spouse, name='save_spouse'),
    path('deletechild/<int:c_id>/',views.deletechild, name='deletechild'),
    path('deletespouse/<int:sp_id>/',views.deletespouse, name='deletespouse'),
    path('deleteother/<int:o_id>/',views.deleteother, name='deleteother'),
    path('deleteimage/<int:fp_id>/',views.deleteimage, name='deleteimage'),
    path('deleteowner/<int:pid>/',views.deleteowner, name='deleteowner'),
    path('edit_owner/<int:owner_id>/',views.edit_owner, name='edit_owner'),
    path('edit_child/<int:child_id>/',views.edit_child, name='edit_child'),
    path('edit_image/<int:fp_id>/',views.edit_image, name='edit_image'),
    path('edit_other/<int:o_id>/',views.edit_other, name='edit_other'),
    path('edit_spouse/<int:spouse_id>/',views.edit_spouse, name='edit_spouse'),
    # path('update_owner/', views.update_owner, name='update_owner'),
    path('familyview/',views.familyview, name='familyview'),
    path('submitfamilyview/',views.submitfamilyview, name='submitfamilyview'),
    path('submit_status/',views.submit_status, name='submit_status'),


    path('save_children/',views.save_children, name='save_children'),
    path('save_other/',views.save_other, name='save_other'),
    path('save_fp/',views.save_fp, name='save_fp'),
    path('finish/',views.finish, name='finish'),
    path('fr/',views.fr, name='fr'),
    path('complete/',views.complete, name='complete'),
    # path('generate_pdf/', views.generate_pdf, name='generate_pdf'),
    path('logout/', views.loadlogout, name='logout'),
    path('changepassword/<token>/',views.changepassword,name='changepassword'),
    path('forgetpassword/',views.forgetpassword,name='forgetpassword'),
    path('payments1/', views.payments1, name='payments1'),






    # path('password_reset/',auth_views.PasswordResetView.as_view(),name='password_reset'),

    # path('password_reset/done/',auth_views.PasswordResetDoneView.as_view(),name='password_reset_done'),

    # path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(),name='password_reset_confirm'),

    # path('reset/done/',auth_views.PasswordResetCompleteView.as_view(),name='password_reset_complete'),
    path('job-posts/', views.job_posts, name='job_posts'),
    path('create-job-post/', views.create_job_post, name='create_job_post'),

    path('community-services/', views.community_services, name='community_services'),

]
