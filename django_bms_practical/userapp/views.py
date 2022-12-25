from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import session, User, db
# Create your views here.
from sqlalchemy import *
from sqlalchemy.orm import Session
from sqlalchemy import or_
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import time
from django.core.mail import send_mail
from django.conf import settings
metadata = MetaData(bind=db)
session = Session(db)


def send_register_email(email):
    subject = "Welcome to - TestApp"
    user_obj = session.query(User).filter(User.email == email)
    name = [i.first_name for i in user_obj][0]
    message = f"Hi, {name}\n\nThank you for registering with us!!"
    email_from = settings.EMAIL_HOST
    send_mail(subject , message , email_from , [email])

def send_password_change_email(email):
    subject = "Change Password - TestApp"
    user_obj = session.query(User).filter(User.email == email)
    name = [i.first_name for i in user_obj][0]
    message = f"Hi, {name}\n\nYour password has been updated successfully !!"
    email_from = settings.EMAIL_HOST
    send_mail(subject , message , email_from , [email])

def home(request):
    try:
        is_loggedin = request.COOKIES['is_loggedin']
        username = request.session['username']
    except Exception as e:
        is_loggedin = "False"
        username = None
    print(is_loggedin, username)
    if is_loggedin == "True":
        return render(request, 'home.html', {'is_loggedin': is_loggedin, 'username': username})
    return render(request, 'home.html')

def signup(request):
    if request.method == 'POST':
        fname = request.POST.get('firstname')
        lname = request.POST.get('lastname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        confirmpassword = request.POST.get('confirmpassword')
        dob = request.POST.get('dob')
        gender = request.POST.get('gender')
        Usertype = request.POST.get('Usertype')
        users = Table('users', metadata, autoload_with=db)
        unique_user = session.query(User).filter(or_(User.email==email, User.phone==phone))
        conn = db.connect()
        if unique_user:
            for i in unique_user:
                if i.email == email or i.phone == phone:
                    return render(request,'signup.html', {'error': "User with this email or phone already exist!!"})
            else:
                ins = users.insert().values(first_name=fname, last_name=lname, email=email, phone=phone, password=password,
                            confirm_password=confirmpassword, date_of_birth=dob, gender=gender, usertype=Usertype)
                result = conn.execute(ins)
                send_register_email(email)
                return redirect('login')
    return render(request, 'signup.html')

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            unique_user = session.query(User).filter(User.email == email)
            if unique_user:
                for i in unique_user:
                    if i.email == email and i.password == password:
                        response = redirect('home')
                        response.set_cookie('is_loggedin', True)
                        request.session['username'] = email
                        return response
                    return render(request, 'login.html', {'error': 'Email or password does not match!!'})
                return render(request, 'login.html', {'error': 'User with this email does not exist!!'})
        except:
            session.rollback()
    return render(request, 'login.html')


def update_profile(request):
    user = request.session['username']
    unique_user = session.query(User).filter(User.email == user)

    if request.method == 'POST':
        fname = request.POST.get('firstname')
        lname = request.POST.get('lastname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        dob = request.POST.get('dob')
        uid = [i.id for i in unique_user][0]
        session.query(User).filter(User.id == uid).update(
            {'first_name': fname,
             'last_name':lname,
             'email': email,
             'phone': phone,
             'date_of_birth': dob}, synchronize_session=False)
        session.commit()
        return redirect('home')
    lst = [{
        'email': i.email,
        'first_name': i.first_name,
        'last_name': i.last_name,
        'phone': i.phone,
        'gender': i.gender,
        'type': i.usertype,
        'dob': i.date_of_birth.strftime("%Y-%m-%d")
    } for i in unique_user]
    return render(request, 'update_profile.html', {'user': lst[0]})

def view_users(request):
    all_users = session.query(User).all()
    p = Paginator(all_users, 5)
    page_number = request.GET.get('page')
    try:
        page_obj = p.get_page(page_number)  # returns the desired page object
    except PageNotAnInteger:
        # if page_number is not an integer then assign the first page
        page_obj = p.page(1)
    except EmptyPage:
        # if page is empty then return last page
        page_obj = p.page(p.num_pages)
    return render(request, 'view_users.html', {'page_obj': page_obj})

def change_password(request):
    user = request.session['username']
    unique_user = session.query(User).filter(User.email == user)

    if request.method == 'POST':
        password = request.POST.get('password')
        password2 = request.POST.get('confirmpassword')
        if password == password2:
            uid = [i.id for i in unique_user][0]
            email = [i.email for i in unique_user][0]
            session.query(User).filter(User.id == uid).update(
                {'password': password,
                 'confirm_password': password2}, synchronize_session=False)
            session.commit()
            send_password_change_email(email)
            response = redirect('home')
            response.delete_cookie('is_loggedin')
            del request.session['username']
            return response
    return render(request, 'change_password.html')