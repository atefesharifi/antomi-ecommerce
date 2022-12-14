from django import forms
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout

error ={
    'min_length':'* حداقل باید 5 کاراکتر باشد',
    'required':'* این فیلد اجباری است',
    'invalid':'* ایمیل شما نامعتبر است',
}

class UserRegisterForm(forms.Form):
    user_name = forms.CharField(max_length=50,error_messages=error,widget=forms.TextInput(attrs={'placeholder':'نام کاربری ', 'class':'form-control'}),label=False)
    email = forms.EmailField(error_messages=error,widget=forms.EmailInput(attrs={'placeholder':' ایمیل ','class':'form-control'}),label=False)
    first_name = forms.CharField(max_length=50,min_length=5,error_messages=error,widget=forms.TextInput(attrs={'placeholder':' نام ','class':'form-control'}),label=False)
    last_name = forms.CharField(max_length=50,widget=forms.TextInput(attrs={'placeholder':' نام خانوادگی ','class':'form-control'}),label=False)
    password_1 = forms.CharField(max_length=50,widget=forms.PasswordInput(attrs={'placeholder':' رمز ورود ','class':'form-control'}),label=False)
    password_2 = forms.CharField(max_length=50,widget=forms.PasswordInput(attrs={'placeholder':' تکرار رمز ورود ','class':'form-control'}),label=False)

    
    def clean_user_name(self):
        user = self.cleaned_data['user_name']
        if User.objects.filter(username=user).exists():
            raise forms.ValidationError('* نام کاربری موجود است')
        return user

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('* ایمبل موجود است')
        return email

    def clean_password_2(self):
        password1 = self.cleaned_data['password_1']
        password2 = self.cleaned_data['password_2']
        if password1 != password2:
            raise forms.ValidationError('* رمز عبور با تکرار رمز یکسان نیست')
        elif len(password2) < 5:
            raise forms.ValidationError('* پسورد باید حداقل 5 کاراکتر باشد ')
        elif not any(x.isupper() for x in password2):
            raise forms.ValidationError('* پسورد حداقل باید یک حرف بزرگ داشته باشد.')
        return password1

class UserLoginForm(forms.Form):
    user = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'نام کاربری...', 'class':'form-control'}),label=False)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'رمز عبور...', 'class':'form-control'}),label=False)
    # remember = forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={'placeholder':'مرا به خاطر بسپار'}))
    
    # def clean(self):
    #     username = self.cleaned_data.get('username')
    #     password = self.cleaned_data.get('password')
    #     user = authenticate(username=username, password=password)
    #     if not user or not user.is_active:
    #         raise forms.ValidationError("* اطلاعات نامعتبر است, لطفا دوباره تلاش کنید")
    #     return self.cleaned_data
    
    

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email','first_name','last_name']
        labels = {
        "email": "ایمیل","first_name": "نام","last_name": "نام خانوادگی"
    }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone','address','profile_image']
        labels = {
        "phone": "تلفن","address": "آدرس","profile_image": "عکس کاربر"
    }

class PhoneForm(forms.Form):
    phone = forms.IntegerField()

class CodeForm(forms.Form):
    code = forms.IntegerField()