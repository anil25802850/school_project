import random

uc =[chr(i) for i in range(ord ('A'),ord('Z') +1)]
uc =[chr(i) for i in range(ord ('a'),ord('z') +1)]

def genotp():
    otp=''
    for i in range(2):
        otp+=otp+random.choice(uc)
        otp = otp+random.choice(uc)
        otp = otp+str(random.randint(0,9))
    return otp
    