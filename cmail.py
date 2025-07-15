import smtplib
from email.message import EmailMessage
def send_mail(to,subject,body):
    server=smtplib.SMTP_SSL('smtp.gmail.com',465)
    server.login('anilkaskani91@gmail.com','oyqr hgek wlig rzsf') #App passcode
    msg=EmailMessage()
    msg['FROM']='anilkaskani91@gmail.com'
    msg['SUBJECT']=subject
    msg['TO']=to
    msg.set_content(body)
    server.send_message(msg)
    server.close()
    
    