from django.shortcuts import render,redirect
from django.http import HttpResponse
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate,login,logout
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib.auth.decorators import login_required
from datetime import datetime
from rango.bing_search import run_query

def index(request):
    category_list = Category.objects.order_by('-likes')[:5]
    pages_list = Page.objects.order_by('-views')[:5]
    context_dict = {'categories': category_list,'pages': pages_list}
    visits = request.session.get('visits')
    if not visits:
        visits = 1
    reset_last_visit_time = False
    
    
    
    last_visit = request.session.get('last_visit')
    if last_visit:
        last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")
        if (datetime.now() - last_visit_time).seconds > 5:
            visits = visits + 1
            reset_last_visit_time = True
    else:
        reset_last_visit_time = True

    if reset_last_visit_time:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = visits
    context_dict['visits'] = visits
    response = render(request, 'rango/index.html',context_dict)
 
 #  Just playing around....
 #  counter = int(request.COOKIES.get('counter', '1'))
    # if 'test_value' in request.COOKIES:
    #   test_value=request.COOKIES.get('test_value')
    #   initial_value = datetime.strptime(test_value[:-7], "%Y-%m-%d %H:%M:%S")
    #   if (datetime.now() - initial_value).seconds > 5:
    #       counter = counter+1
    #       response.set_cookie('test_value',str(datetime.now()))
    # else:
    #   response.set_cookie('test_value',str(datetime.now()))

    # response.set_cookie('counter',counter)

    return response

def about(request):
    context_dict = {'boldmessage': "ABOUT PAGE!"}
    return render(request,'rango/about.html',context_dict)

def category(request, category_name_slug):
    context_dict = {}
    try:
        category = Category.objects.get(slug=category_name_slug)
        context_dict['category_name'] = category.name
        pages = Page.objects.filter(category=category).order_by('-views')
        context_dict['pages'] = pages

        context_dict['category'] = category
    except Category.DoesNotExist:
        pass
    result_list = []
    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            result_list = run_query(query)
            context_dict['result_list']=result_list
    return render(request,'rango/category.html',context_dict)

@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save(commit = True)
            return index(request)
        else:
            print form.errors
    else:
        form = CategoryForm()
    return render(request, 'rango/add_category.html',{'form':form})

@login_required
def add_page(request,category_name_slug):
    try:
        cat = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        cat = None

    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if cat:
                page = form.save(commit = False)
                page.category = cat
                page.views = 0
                page.save()
                return category(request, category_name_slug)
        else:
            print form.errors
    else:
        form = PageForm()
    context_dict = {'form':form, 'category': cat}
    return render(request, 'rango/add_page.html',context_dict)

# def register(request):
#   registered = False
#   if request.method == 'POST':
#       user_form = UserForm(data = request.POST)
#       profile_form = UserProfileForm(data = request.POST)

#       if user_form.is_valid() and profile_form.is_valid():
#           user = user_form.save()
#           user.set_password(user.password)
#           user.save()

#           profile = profile_form.save(commit = False)
#           profile.user = user

#           if 'picture' in request.FILES:
#               profile.picture = request.FILES['picture']

#           profile.save()
#           registered = True
#       else:
#           print user_form.errors, profile_form.errors
#   else:
#       user_form = UserForm()
#       profile_form = UserProfileForm()
#   return render(request,'rango/register.html',
#       {'user_form':user_form, 'profile_form':profile_form, 'registered':registered})

# def user_login(request):
#   if request.method=='POST':
#       username = request.POST.get('username')
#       password = request.POST.get('password')
        
#       user = authenticate(username=username,password=password)

#       if user:
#           login(request,user)
#           return HttpResponseRedirect('/rango/')
#       else:
#           print "Invalid login details: {0}, {1}".format(username,password)
#           return HttpResponse("Invalid login details supplied.")
#   else:
#       return render(request,'rango/login.html',{})

@login_required
def restricted(request):
    return HttpResponse("Since you're logged in, you can see this.")

# def user_logout(request):
#   logout(request)
#   return HttpResponseRedirect('/rango/')

def search(request):
    result_list = []
    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            result_list = run_query(query)
    return render(request, 'rango/search.html', {'result_list': result_list})

def track_url(request):
    page_id=None
    url = '/rango/'
    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']
            try:
                page=Page.objects.get(id=page_id)
                page.views = page.views+1
                now = datetime.now()
                if not page.first_visit:
                    page.first_visit = now
                page.last_visit = now
                page.save()
                url = page.url
            except:
                pass
    return redirect(url,permanent=True)

def register_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            if request.user.is_authenticated():
                user=request.user
                user_profile = form.save(commit = False)
                user_profile.user=user
                if 'picture' in request.FILES:
                    user_profile.picture = request.FILES['picture']
                user_profile.save()
                return profile(request)
        else:
            print form.errors
    else:
        form = UserProfileForm()
    context_dict = {'form':form}
    return render(request,'rango/profile_registration.html',context_dict)

@login_required
def profile(request):
    context_dict={}
    if request.user.is_authenticated():
        user=request.user
        context_dict['user']=user
    return render(request,'rango/profile.html',context_dict)

@login_required
def like_category(request):
    cat_id = None
    if request.method == 'GET':
        cat_id = request.GET['category_id']
    likes = 0
    if cat_id:
        cat = Category.objects.get(id=int(cat_id))
        if cat:
            likes = cat.likes + 1
            cat.likes=likes
            cat.save()
    return HttpResponse(likes)

def get_category_list(max_results=0, starts_with=''):
        cat_list = []
        if starts_with:
                cat_list = Category.objects.filter(name__istartswith=starts_with)
        else:
            cat_list = Category.objects.all()
        if max_results > 0:
                if len(cat_list) > max_results:
                        cat_list = cat_list[:max_results]

        return cat_list

def suggest_category(request):
    cat_list=[]
    starts_with=''
    if request.method == 'GET':
        starts_with = request.GET['suggestion']
    cat_list = get_category_list(8,starts_with)
    return render(request, 'rango/cats.html',{'cats':cat_list})

@login_required
def auto_add_page(request):
    cat_id = None
    url = None
    title = None
    context_dict = {}
    if request.method == 'GET':
        cat_id = request.GET['category_id']
        url = request.GET['url']
        title = request.GET['title']
        if cat_id:
            category = Category.objects.get(id=int(cat_id))
            p = Page.objects.get_or_create(category=category, title=title, url=url)
            pages = Page.objects.filter(category=category).order_by('-views')
            # Adds our results list to the template context under name pages.
        context_dict = {}
        try:
            #category = Category.objects.get(slug=category_name_slug)
            context_dict['category_name'] = category.name
            pages = Page.objects.filter(category=category).order_by('-views')
            context_dict['pages'] = pages
            context_dict['category'] = category
        except Category.DoesNotExist:
            pass
    return render(request, 'rango/page_list.html', context_dict)