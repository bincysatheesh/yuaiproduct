

from django.core.mail import send_mail

from django.conf import settings




# token
# 'f5f6d2b0-3526-4059-a16e-af6b070ae0b3'


def send_forget_password_mail(email, token):
   
    subject='Your forget password link'
    message=f'Hi, Click on the link to reset your password http://127.0.0.1:8000/changepassword/{token}'
    email_from = settings.EMAIL_HOST_USER
    # print(email_from)
    recipient_list = [email]
    try:
        send_mail(subject,message,email_from,recipient_list)
        print("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")

    return True




def send_contact_email(name, email, subject, message, admin_email):
    try:
        subject = f'New Enquiry : {subject}'
        message = f'From: {name}\nEmail: {email}\n\n{message}'
        email_from = email
        recipient_list = ['zmcazambia@gmail.com']  # Site admin email

        send_mail(subject, message, email_from, recipient_list, fail_silently=False)

        return True  # Indicate success
    except Exception as e:
        # If an error occurs, print the error for debugging
        print(f"Error sending email: {e}")
        return False  # Indicate failure
    


def send_user_email(name, email, subject, message, admin_email):
    try:
        subject = f'New User Registration : {subject}'
        message = f'From: {name}\nEmail: {email}\n\n{message}'
        email_from = email
        recipient_list = ['zmcazambia@gmail.com']  # Site admin email

        send_mail(subject, message, email_from, recipient_list, fail_silently=False)

        return True  # Indicate success
    except Exception as e:
        # If an error occurs, print the error for debugging
        print(f"Error sending email: {e}")
        return False  # Indicate failure
    