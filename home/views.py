from tkinter import PAGES
from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.contrib import messages
from .forms import *
from django.db.models import Q,Max,Min,Count,Sum
from cart.models import *
from cart.views import *
from django.core.mail import EmailMessage
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from .filters import ProductFilter
from urllib.parse import urlencode


def home(request):
    products = Product.objects.all()
    main_categorys = Category.objects.filter(sub_cat=False)
    sub_categorys = Category.objects.filter(sub_cat=True)
    all_category = Category.objects.all()
    gallery = Gallery.objects.all()
    create = Product.objects.all().order_by('-create')[:8]
    data = 'pants'
    create2 = products.filter(Q(name__icontains=data))
    nums = Cart.objects.filter(user_id=request.user.id).aggregate(sum=Sum('quantity'))['sum']
    nums_favourite = products.filter(favourite=request.user.id).aggregate(sum=Sum('favourite'))['sum']
    most_favorite = Product.objects.filter(total_favourite__gte='2')
    if 'search' in request.GET:
        s_form = SearchForm(request.GET)
        print(s_form)
        if s_form.is_valid():
            info = s_form.cleaned_data['search']
            page_obj = products.filter(Q(name__contains=info))
            paginator = Paginator(page_obj, 4)
            page_num = request.GET.get('page')
            data = request.GET.copy()
            if 'page' in data:
                del data['page']
            page_obj = paginator.get_page(page_num)
            return render(request,'product.html',{'products':products,'page_obj':page_obj,'nums':nums,
                    's_form':s_form,'page_num':page_num,'filter':filter,'data':urlencode(data),'nums_favourite':nums_favourite})
    return render(request,'home.html',{'products':products,'main_categorys':main_categorys,'sub_categorys':sub_categorys,'all_category':all_category,'gallery':gallery,'create':create,'create2':create2,'nums':nums,'most_favorite':most_favorite,'nums_favourite':nums_favourite})

def all_product(request,slug=None,id=None):
    products = Product.objects.all()
    main_categorys = Category.objects.filter(sub_cat=False)
    sub_categorys = Category.objects.filter(sub_cat=True)
    all_category = Category.objects.all()
    tags_list=Product.objects.filter(tags__isnull=False).distinct()
    # form = CompareForm()
    nums_favourite = products.filter(favourite=request.user.id).aggregate(sum=Sum('favourite'))['sum']
    nums = Cart.objects.filter(user_id=request.user.id).aggregate(sum=Sum('quantity'))['sum']
    min = Product.objects.aggregate(unit_price=Min('unit_price'))
    min_price = int(min['unit_price'])
    max = Product.objects.aggregate(unit_price=Max('unit_price'))
    max_price = int(max['unit_price'])

    filter = ProductFilter(request.GET,queryset=products)
    products = filter.qs
    
    paginator = Paginator(products,4)
    page_num = request.GET.get('page')
    
    # data using for anything in url consist of page numbers and filter save for another PAGES
    # because when we go another pages filters that we want delete
    data = request.GET.copy()
    if 'page' in data:
        del data['page']

    page_obj = paginator.get_page(page_num)
    category = Category.objects.filter(sub_cat=False)
    if slug and id:
        data = get_object_or_404(Category,slug=slug,id=id)
        page_obj = products.filter(category=data)
        paginator = Paginator(page_obj,8)
        page_num = request.GET.get('page')
        data = request.GET.copy()
        if 'page' in data:
            del data['page']
        page_obj = paginator.get_page(page_num)
    s_form = SearchForm()
    if 'search' in request.GET:
        s_form = SearchForm(request.GET)
        print(s_form)
        if s_form.is_valid():
            info = s_form.cleaned_data['search']
            page_obj = products.filter(Q(name__contains=info))
            paginator = Paginator(page_obj, 4)
            page_num = request.GET.get('page')
            data = request.GET.copy()
            if 'page' in data:
                del data['page']
            page_obj = paginator.get_page(page_num)
    return render(request,'product.html',{'products':products,'main_categorys':main_categorys,'sub_categorys':sub_categorys,'all_category':all_category,'tags_list':tags_list,'page_obj':page_obj,'category':category,'nums':nums,
                    's_form':s_form,'page_num':page_num,'filter':filter,'min_price':min_price,'max_price':max_price,'data':urlencode(data),'nums_favourite':nums_favourite})

def product_detail(request,id):
    product = get_object_or_404(Product,id=id)
    main_categorys = Category.objects.filter(sub_cat=False)
    sub_categorys = Category.objects.filter(sub_cat=True)
    all_category = Category.objects.all()
    user_ip = request.META.get('REMOTE_ADDR')
    view = View.objects.filter(ip=user_ip,product_id=id)
    if not view.exists():
        View.objects.create(ip=user_ip,product_id=id)
        product.num_view += 1
        product.save()
    if request.user.is_authenticated:
        product.views.add(request.user)
    category = Category.objects.filter(sub_cat=False)
    nums = Cart.objects.filter(user_id=request.user.id).aggregate(sum=Sum('quantity'))['sum']
    nums_favourite = Product.objects.filter(favourite=request.user.id).aggregate(sum=Sum('favourite'))['sum']
    images = Images.objects.filter(product_id=id)
    create = Product.objects.all().order_by('-create')[:6]
    comment_form = CommentForm()
    reply_form = ReplyForm()
    cart_form = CartForm()
    comments = Comment.objects.filter(product_id=id,is_reply=False)
    similar = product.tags.similar_objects()[:6]
    is_like = False
    if product.like.filter(id=request.user.id).exists():
        is_like = True

    is_unlike = False
    if product.unlike.filter(id=request.user.id).exists():
        is_unlike = True

    is_favourite = False
    if product.favourite.filter(id=request.user.id).exists():
        is_favourite = True


    if product.status != 'None':
        if request.method == 'POST':
            variant = Variants.objects.filter(product_variant_id=id)
            var_id = request.POST.get('select')
            variants = Variants.objects.get(id=var_id)
            colors = Variants.objects.filter(product_variant_id=id,size_variant_id=variants.size_variant_id)
            # IF USING DBSQLITE FOR AVOIDING ONE SIZE REPEAT
            size = Variants.objects.raw('SELECT * FROM home_variants WHERE product_variant_id=%s GROUP BY size_variant_id', [id])
            # IF USING POSTGRESQL FOR AVOIDING ONE SIZE REPEAT
            # size = Variants.objects.filter(product_variant_id=id.distinct('size_variant_id'))
            
        else:
            variant = Variants.objects.filter(product_variant_id=id)
            variants = Variants.objects.get(id=variant[0].id)
            colors = Variants.objects.filter(product_variant_id=id,size_variant_id=variants.size_variant_id)
            size = Variants.objects.raw('SELECT * FROM home_variants WHERE product_variant_id=%s GROUP BY size_variant_id', [id])

            
        context = {'product':product,'category':category,'main_categorys':main_categorys,'sub_categorys':sub_categorys,'all_category':all_category,'nums':nums,'variant':variant,'variants':variants,'similar':similar, 'is_like':is_like, 'is_unlike':is_unlike,'comments':comments,'comment_form':comment_form,'reply_form':reply_form,'images':images,'cart_form':cart_form,'is_favourite':is_favourite,'colors':colors,'size':size,'create':create,'nums_favourite':nums_favourite}
        return render(request, 'detail.html',context)
    else:
        return render(request,'detail.html',{'product':product,'main_categorys':main_categorys,'sub_categorys':sub_categorys,'all_category':all_category,'category':category,'nums':nums,'nums_comment':nums_comment,'similar':similar, 'is_like':is_like,'is_unlike':is_unlike,'comments':comments,'comment_form':comment_form,'reply_form':reply_form,'images':images,'cart_form':cart_form,'is_favourite':is_favourite,'create':create,'nums_favourite':nums_favourite})

def product_like(request,id):
    url = request.META.get('HTTP_REFERER')
    product = get_object_or_404(Product,id=id)
    is_like = False
    if product.like.filter(id=request.user.id).exists():
        product.like.remove(request.user)
        is_like = False
        messages.success(request,'remove','success')
    else:
        product.like.add(request.user)
        is_like = True
        messages.success(request,'add','success')
    return redirect(url)

def product_unlike(request,id):
    url = request.META.get('HTTP_REFERER')
    product = get_object_or_404(Product,id=id)
    product.unlike.add(request.user)
    messages.success(request,'add like','dark')
    return redirect(url)

def product_comment(request,id):
    url = request.META.get('HTTP_REFERER')
    product = Product.objects.get(id=id)
    if request.method == 'POST':
        # comment_form = CommentForm(request.POST)
        # if comment_form.is_valid():
        #     data = comment_form.cleaned_data
        comment = Comment.objects.create(comment=request.POST['comment'],rate=request.POST['rate'],user_id=request.user.id,product_id =id)
        comment.save()
        product.total_comment +=1
        product.save()
        return redirect(url)


def product_reply(request,id,comment_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        reply_form = ReplyForm(request.POST)
        if reply_form.is_valid():
            data = reply_form.cleaned_data
            Comment.objects.create(comment=data['comment'],user_id=request.user.id,product_id =id,reply_id=comment_id,is_reply=True)
            messages.success(request,'tnx for reply','primary')
            return redirect(url)

def comment_like(request,id):
    url = request.META.get('HTTP_REFERER')
    comment = Comment.objects.get(id=id)
    if comment.comment_like.filter(id=request.user.id).exists():
        comment.comment_like.remove(request.user)
    else:
        comment.comment_like.add(request.user)
        messages.success(request,'tnx for like comment','warning')
    return redirect(url)

# def product_search(request):
#     products = Product.objects.all()
#     if request.method == 'POST':
#         form = SearchForm(request.POST)
#         if form.is_valid():
#             data = form.cleaned_data['search']
#             if data.is_digit():
#                 products = products.filter(Q(discount__exact=data)|Q(unit_price__exact=data))
#             else:
#                 products = products.filter(Q(name__contains=data))
#             return render(request,'home/product.html',{'products':products,'form':form})

def favourite_product(request,id):
    url = request.META.get('HTTP_REFERER')
    product = Product.objects.get(id=id)
    is_favourite = False
    if product.favourite.filter(id=request.user.id).exists():
        product.favourite.remove(request.user)
        product.total_favourite -= 1
        product.save()
        is_favourite = False
    else:
        product.favourite.add(request.user)
        product.total_favourite += 1
        product.save()
        is_favourite = True

    return redirect(url)

def favourite_remove(request,id):
    url = request.META.get('HTTP_REFERER')
    product = Product.objects.get(id=id)
    product.favourite.remove(request.user)
    return redirect(url)
 
def contact(request):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        # subject = request.POST['subject']
        email = request.POST['email']
        # msg = request.POST['message']
        # body = subject + '\n' + email + '\n' + msg
        form = EmailMessage(
            'contact form',
            'اشتراک شما انجام شد',
            'atefesharifi86@gmail.com',
            (email,),
            
        )
        form.send(fail_silently=False)
        print('eshteke anjam shdo')
    return redirect(url)

def about(request):
    main_categorys = Category.objects.filter(sub_cat=False)
    sub_categorys = Category.objects.filter(sub_cat=True)
    all_category = Category.objects.all()
    nums = Cart.objects.filter(user_id=request.user.id).aggregate(sum=Sum('quantity'))['sum']
    nums_favourite = Product.objects.filter(favourite=request.user.id).aggregate(sum=Sum('favourite'))['sum']
    return render(request, 'about.html',{'main_categorys':main_categorys,'sub_categorys':sub_categorys,'all_category':all_category,'nums':nums,'nums_favourite':nums_favourite})


def blog(request):
    blogs = Blog.objects.all()
    products = Product.objects.all()
    main_categorys = Category.objects.filter(sub_cat=False)
    sub_categorys = Category.objects.filter(sub_cat=True)
    all_category = Category.objects.all()
    tags_list=Product.objects.filter(tags__isnull=False).distinct()
    # form = CompareForm()
    nums_favourite = products.filter(favourite=request.user.id).aggregate(sum=Sum('favourite'))['sum']
    nums = Cart.objects.filter(user_id=request.user.id).aggregate(sum=Sum('quantity'))['sum']    
    paginator = Paginator(blogs,2)
    page_num = request.GET.get('page')
    
    # data using for anything in url consist of page numbers and filter save for another PAGES
    # because when we go another pages filters that we want delete
    data = request.GET.copy()
    if 'page' in data:
        del data['page']

    page_obj = paginator.get_page(page_num)
    category = Category.objects.filter(sub_cat=False)
    return render(request,'blog.html',{'products':products,'blogs':blogs,'main_categorys':main_categorys,'sub_categorys':sub_categorys,'all_category':all_category,'tags_list':tags_list,'page_obj':page_obj,'category':category,'nums':nums,
                    'page_num':page_num,'data':urlencode(data),'nums_favourite':nums_favourite})
    

