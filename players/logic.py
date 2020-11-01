from background_task import background
from django.core.mail import send_mail


@background
def send_test_email():
    send_mail('Test message','This is a test message','test@worldofcandle.club',['thousandgoblins@gmail.com',])

