from django.shortcuts import render,redirect
from django.urls import reverse_lazy
from .forms import *
from .models import *
from order.models import *
from home.models import *
from cart.models import *
from django.db.models import Sum
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from random import randint
import ghasedakpack
from django.http import HttpResponse 
from home.models import *
from django.contrib.auth import views as auth_view

def user_register(request):
    main_categorys = Category.objects.filter(sub_cat=False)
    sub_categorys = Category.objects.filter(sub_cat=True)
    all_category = Category.objects.all()
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = User.objects.create_user(username=data['user_name'],email=data['email'],first_name=data['first_name'],last_name=data['last_name'],password=data['password_1'])
            user.save()
            return redirect('home:home')

            messages.success(request,'حساب کاربری با موفقیت ساخته شد','success')
            
    else:
        form = UserRegisterForm()
    context = {'form':form,'main_categorys':main_categorys,'sub_categorys':sub_categorys,'all_category':all_category}
    return render(request, 'register.html', context)

def user_login(request):
    url = request.META.get('HTTP_REFERER')
    main_categorys = Category.objects.filter(sub_cat=False)
    sub_categorys = Category.objects.filter(sub_cat=True)
    all_category = Category.objects.all()
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            remember = request.POST.get('remember',False)
            try:
                user = authenticate(request, username=User.objects.get(email=data['user']), password=data['password'])
            except:
                user = authenticate(request, username=data['user'], password=data['password'])

            if user is not None:
                login(request,user)
                if not remember:
                    request.session.set_expiry(0)
                else:
                    request.session.set_expiry(10000)
                # messages.success(request,'welcome my site','primary')
                return redirect('home:home')  
            else:
                print ( "invalid login details ")
                return redirect('login')
    else:
        form = UserLoginForm()
    context ={'form':form,'main_categorys':main_categorys,'sub_categorys':sub_categorys,'all_category':all_category}
    return render(request, 'login.html', context)
    

def user_logout(request):
    # url = request.META.get('HTTP_REFERER')
    logout(request)
    return redirect('home:home')


@login_required(login_url='accounts:login')
def user_profile(request):
    order = Order.objects.filter(user_id=request.user.id)
    item_order = ItemOrder.objects.filter(user_id=request.user.id)
    profile = Profile.objects.get(user_id=request.user.id)
    main_categorys = Category.objects.filter(sub_cat=False)
    sub_categorys = Category.objects.filter(sub_cat=True)
    all_category = Category.objects.all()
    nums = Cart.objects.filter(user_id=request.user.id).aggregate(sum=Sum('quantity'))['sum']
    products = Product.objects.all()
    nums_favourite = products.filter(favourite=request.user.id).aggregate(sum=Sum('favourite'))['sum']
    create = Product.objects.all().order_by('-create')[:6]
    context = {'item_order':item_order,'order':order,'main_categorys':main_categorys,'sub_categorys':sub_categorys,'all_category':all_category,'profile':profile,'nums':nums,'create':create,'nums_favourite':nums_favourite}
    return render(request,'profile.html',context)

@login_required(login_url='accounts:login')
def user_update(request):
    profile = Profile.objects.get(user_id=request.user.id)
    main_categorys = Category.objects.filter(sub_cat=False)
    sub_categorys = Category.objects.filter(sub_cat=True)
    all_category = Category.objects.all()
    nums = Cart.objects.filter(user_id=request.user.id).aggregate(sum=Sum('quantity'))['sum']
    nums_favourite = Product.objects.filter(favourite=request.user.id).aggregate(sum=Sum('favourite'))['sum']
    # if request.method == 'POST':
    #     user_form = UserUpdateForm(request.POST,instance=request.user)
    #     profile_form = ProfileUpdateForm(request.POST,request.FILES,instance=request.user.profile)
    #     if user_form and profile_form.is_valid():
    #         user_form.save()
    #         profile_form.save()
    #         messages.success(request,'update successfully','success')
    #         return redirect('accounts:profile')
    # else:
    #     user_form = UserUpdateForm(instance=request.user)
    #     profile_form = ProfileUpdateForm(instance=request.user.profile)
    if request.method == 'POST':
        profile = Profile.objects.filter(user_id=request.user.id).update(phone=request.POST['phone'],address=request.POST['address'])
        user = User.objects.filter(id=request.user.id).update(email=request.POST['email'],first_name=request.POST['f_name'],last_name=request.POST['l_name'])
        messages.success(request,'update successfully','success')
        return redirect('accounts:profile')
    context = {'main_categorys':main_categorys,'sub_categorys':sub_categorys,'all_category':all_category,'profile':profile,'nums':nums,'nums_favourite':nums_favourite}
    return render(request,'accounts/update.html',context)


def change_password(request):
    profile = Profile.objects.get(user_id=request.user.id)
    category = Category.objects.filter(sub_cat=False)
    nums = Cart.objects.filter(user_id=request.user.id).aggregate(sum=Sum('quantity'))['sum']
    nums_favourite = Product.objects.filter(favourite=request.user.id).aggregate(sum=Sum('favourite'))['sum']
    
    if request.method == 'POST':
        form = PasswordChangeForm(request.user,request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request,form.user)
            messages.success(request,'passwor successfully changed','success')
            return redirect('accounts:profile')
        else:
            messages.error(request,'password not correct','danger')
            return redirect('accounts:change')
    else:
        form = PasswordChangeForm(request.user)

    return render(request,'accounts/change.html',{'form':form,'category':category,'profile':profile,'nums':nums,'nums_favourite':nums_favourite})

def phone(request):
    if request.method == 'POST':
        form = PhoneForm(request.POST)
        if form.is_valid():
            global random_code,phone
            data = form.cleaned_data
            phone = f"0{data['phone']}"
            random_code = randint(100,1000)
            sms = ghasedakpack.Ghasedak("3f269a0a1b77f8f09813f2476e8105367d612c824154b3acc221030ae5ef05f9")
            sms.send({'message':random_code,'receptor':phone,'linenumber':"10008566"})
            return redirect('accounts:verify')
    else:
        form = PhoneForm()
    return render(request,'phone.html',{'form':form})

def verify(request):
    if request.method == 'POST':
        form = CodeForm(request.POST)
        if form.is_valid():
            if random_code == form.cleaned_data['code']:
                profile = Profile.objects.get(phone=phone)
                user = User.objects.get(profile__id=profile.id)
                login(request,user)
                messages.success(request,'hi user')
                return redirect('home:home')
            else:
                messages.error(request,'error code')
    else:
        form = CodeForm()
    return render(request,'accounts/code.html',{'form':form})

def favourite(request):
    profile = Profile.objects.get(user_id=request.user.id)
    main_categorys = Category.objects.filter(sub_cat=False)
    sub_categorys = Category.objects.filter(sub_cat=True)
    all_category = Category.objects.all()
    nums_favourite = Product.objects.filter(favourite=request.user.id).aggregate(sum=Sum('favourite'))['sum']
    nums = Cart.objects.filter(user_id=request.user.id).aggregate(sum=Sum('quantity'))['sum']
    product = request.user.fa_user.all()
    return render(request,'favourite.html',{'product':product,'main_categorys':main_categorys,'sub_categorys':sub_categorys,'all_category':all_category,'profile':profile,'nums':nums,'nums_favourite':nums_favourite})

def history(request):
    profile = Profile.objects.get(user_id=request.user.id)
    main_categorys = Category.objects.filter(sub_cat=False)
    sub_categorys = Category.objects.filter(sub_cat=True)
    all_category = Category.objects.all()
    nums = Cart.objects.filter(user_id=request.user.id).aggregate(sum=Sum('quantity'))['sum']
    nums_favourite = Product.objects.filter(favourite=request.user.id).aggregate(sum=Sum('favourite'))['sum']
    data = ItemOrder.objects.filter(user_id = request.user.id)
    return render(request,'history.html',{'data':data,'main_categorys':main_categorys,'sub_categorys':sub_categorys,'all_category':all_category,'profile':profile,'nums':nums,'nums_favourite':nums_favourite})

def product_view(request):
    views = View.objects.filter(ip=request.META.get('HTTP_ADDR')).order_by('-create')[:2]
    return render(request, 'accounts/view.html', {'views':views})

class ResetPassword(auth_view.PasswordResetView):
    template_name = 'reset.html'
    success_url = reverse_lazy('accounts:reset_done')
    email_template_name = 'link.html'
    

class DonePassword(auth_view.PasswordResetDoneView):
    template_name = 'done.html'

class ConfirmPassword(auth_view.PasswordResetConfirmView):
    template_name = 'confirm.html'
    success_url = reverse_lazy('accounts:complete')

class Complete(auth_view.PasswordResetCompleteView):
    template_name = 'complete.html'