from django.shortcuts import render, redirect
from .models import *
from cart.models import *
from .forms import CouponForm
from django.views.decorators.http import require_POST
from django.utils import timezone
import jdatetime
from django.contrib import messages
from suds import Client
from django.http import HttpResponse
from django.utils.crypto import get_random_string
from django.db.models import Sum

def order_detail(request,id):
    cart = Cart.objects.filter(user_id=request.user.id)
    main_categorys = Category.objects.filter(sub_cat=False)
    sub_categorys = Category.objects.filter(sub_cat=True)
    all_category = Category.objects.all()
    order = Order.objects.get(id=id)
    nums = Cart.objects.filter(user_id=request.user.id).aggregate(sum=Sum('quantity'))['sum']
    nums_favourite = Product.objects.filter(favourite=request.user).aggregate(sum=Sum('favourite'))['sum']
    form = CouponForm()
    total = 0
    for p in cart:
        if p.product.status != 'None':
            total += p.variant.total_price * p.quantity
        else:
            total += p.product.total_price * p.quantity
            
    context = {'main_categorys':main_categorys,'sub_categorys':sub_categorys,'all_category':all_category,'cart':cart,'order':order,'nums':nums,'form':form,'total':total,'nums_favourite':nums_favourite}
    return render(request,'order.html',context)

def order_create(request):
    if request.method == 'POST':
        print('this is post method')
        # form = OrderForm(request.POST)
        code = get_random_string(length=8)
        order = Order.objects.create(user_id=request.user.id,email=request.POST['email'],f_name=request.POST['f_name'],l_name=request.POST['l_name'],address=request.POST['address'], code=code)
        order.save()
        items = Order.objects.all()
        print(items)
        cart = Cart.objects.filter(user_id=request.user.id)
        for c in cart:
            ItemOrder.objects.create(order_id=order.id,user_id=request.user.id,product_id=c.product_id,variant_id=c.variant_id,quantity=c.quantity)
        return redirect('order:order_detail',order.id)  
    return render(request, "order.html", {})


@require_POST
def coupon_order(request,order_id):
    print('your coupon start')
    form = CouponForm(request.POST)
    time = jdatetime.datetime.now(tz=timezone.utc)
    if form.is_valid():
        code = form.cleaned_data['code']
        try:
            coupon = Coupon.objects.get(code__iexact=code,start__lte=time,end__gte=time,active=True)
        except Coupon.DoesNotExist:
            messages.error(request,'this code wrong','danger')
            return redirect('order:order_detail',order_id)
        print(coupon.code)
        order = Order.objects.get(id=order_id)
        order.discount = coupon.discount
        order.save()
    return redirect('order:order_detail',order_id)

MERCHANT = 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX'
client = Client('https://www.zarinpal.com/pg/services/WebGate/wsdl')
description = "توضیحات مربوط به تراکنش را در این قسمت وارد کنید"  # Required
mobile = '09123456789'  # Optional
CallbackURL = 'http://localhost:8000/order:verify/' # Important: need to edit for realy server.

def send_request(request,price,order_id):
    global amount
    amount = price
    result = client.service.PaymentRequest(MERCHANT, amount, description, request.user.email, mobile, CallbackURL)
    if result.Status == 100:
        return redirect('https://www.zarinpal.com/pg/StartPay/' + str(result.Authority))
    else:
        order = Order.objects.get(id=order_id)
        order.paid = True
        Cart.objects.filter(user_id=request.user.id).delete()
        order.save()
        item = ItemOrder.objects.filter(order_id = order_id)
        for c in item:
            if c.product.status == 'None':
                product = Product.objects.get(id=c.product.id)
                product.sell += c.quantity
                product.amount -= c.quantity
                product.save()
            else:
                variant = Variants.objects.get(id=c.variant.id)
                # product.sell += c.quantity
                variant.amount -= c.quantity
                variant.save()
        return HttpResponse('Error code: ' + str(result.Status))

def verify(request):
    if request.GET.get('Status') == 'OK':
        result = client.service.PaymentVerification(MERCHANT, request.GET['Authority'], amount)
        if result.Status == 100:
            return HttpResponse('Transaction success.')
        elif result.Status == 101:
            return HttpResponse('Transaction submitted : ' + str(result.Status))
        else:
            return HttpResponse('Transaction failed. ' + str(result.Status))
    else:
        return HttpResponse('Transaction failed or canceled by user')

    # if c.product.status == 'None':
    #         product = Product.objects.get(id=c.product.id)
    #         product.amount -= c.quantity
    #         product.save()
    #     else:
    #         variant = Variants.objects.get(id=c.variant.id)
    #         variant.amount -= c.quantity
    #         variant.save()