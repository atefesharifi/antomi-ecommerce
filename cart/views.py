from django.shortcuts import render,redirect
from home.models import Product
from .models import *
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from order.models import Order, OrderForm

def cart_detail(request):
    cart = Cart.objects.filter(user_id=request.user.id)
    main_categorys = Category.objects.filter(sub_cat=False)
    sub_categorys = Category.objects.filter(sub_cat=True)
    all_category = Category.objects.all()
    nums_favourite = Product.objects.filter(favourite=request.user.id).aggregate(sum=Sum('favourite'))['sum']
    nums = Cart.objects.filter(user_id=request.user.id).aggregate(sum=Sum('quantity'))['sum']
    user = request.user
    form = OrderForm(instance=request.user.profile)
    total = 0
    try :
        for p in cart:
            if p.product.status != 'None':
                total += p.variant.total_price * p.quantity
            else:
                total += p.product.total_price * p.quantity
    except AttributeError:
        print('attribute does not exist')

    return render(request,'cart.html',{'main_categorys':main_categorys,'sub_categorys':sub_categorys,'all_category':all_category,'cart':cart,'nums':nums,'total':total,'form':form,'user':user,'nums_favourite':nums_favourite})

@login_required(login_url='accounts:login')
def add_cart(request, id):
    print('hiiii')
    url = request.META.get('HTTP_REFERER')
    product = Product.objects.get(id=id)
    print('2hii')
    if product.status != 'None':
        var_id = request.POST.get('select')
        data = Cart.objects.filter(user_id=request.user.id, variant_id=var_id)
        if data:
            check= 'yes'
        else:
            check= 'no'
    else:
        data = Cart.objects.filter(user_id=request.user.id, product_id=id)
        if data:
            check= 'yes'
        else:
            check= 'no'
            
    print(check)
    if request.method == 'POST':
        form = CartForm(request.POST)
        var_id = request.POST.get('select')
        if form.is_valid():
            info = form.cleaned_data['quantity']
            if check == 'yes':
                if product.status != 'None':
                    shop = Cart.objects.get(user_id=request.user.id, product_id=id, variant_id=var_id)
                else:
                    shop = Cart.objects.get(user_id=request.user.id, product_id=id)
                shop.quantity += info
                shop.save()
            else:
                if product.status != 'None':
                    Cart.objects.create(user_id=request.user.id, product_id=id, variant_id=var_id, quantity=info)
                else:
                    Cart.objects.create(user_id=request.user.id, product_id=id, quantity=info)
    else:
        if check == 'yes':
            shop = Cart.objects.get(user_id=request.user.id, product_id=id)
            shop.quantity += 1
            shop.save()
        else:
            Cart.objects.create(user_id=request.user.id, product_id=id, quantity=1)
        
    return redirect(url)

@login_required(login_url='accounts:login')
def remove_cart(request,id):
    url = request.META.get('HTTP_REFERER')
    Cart.objects.filter(id=id).delete()
    return redirect(url)

def add_single(request,id):
    url = request.META.get('HTTP_REFERER')
    cart = Cart.objects.get(id=id)
    if cart.product.status == 'None':
        product = Product.objects.get(id=cart.product.id)
        if product.amount > cart.quantity:
            cart.quantity += 1
    else:
        variant = Variants.objects.get(id=cart.variant.id)
        if variant.amount > cart.quantity:
            cart.quantity += 1
    cart.save()
    return redirect(url)

def remove_single(request,id):
    url = request.META.get('HTTP_REFERER')
    cart = Cart.objects.get(id=id)
    if cart.quantity < 2:
        cart.delete()
    else:
        cart.quantity -= 1
        cart.save()
    return redirect(url)



            
