




from django.core.mail import send_mail
from django.conf import settings


def sendapprovemail(email):
    try:
        subject = 'ZMCA Registration Approval'
        message = 'Hi, your registration with ZMCA has been approved. You can now log in to your account.Click here to go to the website: http://127.0.0.1:8000/'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email]

        # Print for debugging purposes
        print("Email From:", email_from)
        print("Recipient List:", recipient_list)

        # Check if the email address is not empty or None before sending the email
        if recipient_list[0]:
            send_mail(subject, message, email_from, recipient_list)
            print("Email sent successfully.")
        else:
            print("Invalid email address. Email not sent.")
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

