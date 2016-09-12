from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from rango.models import Category, Page
#from rango.models import Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
#from rango.forms import PageForm

# def index(request):
#     #return HttpResponse("Rango says Hey There, World!!</br> <a href='/rango/about'>About Rango</a>")
#     context_dict = {'boldmessage' : "I am bold font from the context"}
#     return render(request, 'rango/index.html', context_dict)

def index(request):
    # Query the database for a list of ALL categories currently stored.
    # Order the categories by no. likes in descending order.
    # Retrieve the top 5 only - or all if less than 5.
    # Place the list in our context_dict dictionary which will be passed to the template engine.
    context_dict = {}
    category_list = Category.objects.order_by('-likes')[:5]
    context_dict['categories'] = category_list
    page_list = Page.objects.order_by('-views')[:5]
    context_dict['pages'] = page_list

    # Render the response and send it back!
    return render(request, 'rango/index.html', context_dict)

def about(request):
    context_dict = {'version' : "0.01"}
    return render(request, 'rango/about.html', context_dict)
    #return HttpResponse("Rango says Here is the About page</br><a href='/rango/'>Back Home</a>")

def category(request, category_name_slug):
    context_dict = {}
    print "Here"
    try:
        print "trying : {0}".format(str(category_name_slug))
        # Can we find a category name slug with the given name?
        # If we can't, the .get() method raises a DoesNotExist exception.
        # So the .get() method returns one model instance or raises an exception.
        category = Category.objects.get(slug=category_name_slug)
        context_dict['category_name'] = category.name
        print category.name

        # Retrieve all of the associated pages.
        # Note that filter returns >= 1 model instance.
        pages = Page.objects.filter(category=category)
        context_dict['pages'] = pages# We also add the category object from the database to the context dictionary.
        # We'll use this in the template to verify that the category exists.
        context_dict['category'] = category
        print pages
        print category
    except Category.DoesNotExist:
        print "excepting"
        # We get here if we didn't find the specified category.
        # Don't do anything - the template displays the "no category" message for us.
        pass

    print "rendering"
    return render(request, 'rango/category.html', context_dict)

def add_category(request):
    # a HTTP POST ?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
             # Save the new category to the database.
            form.save(commit=True)

            # Now call the index() view.
            # The user will be shown the homepage.
            return index(request)
        else:
            # The supplied form contained errors - just print them to the terminal
            print form.errors
    else:
        # If the request was not a POST, display the form to enter details.
        form = CategoryForm()

    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any).
    return render(request, 'rango/add_category.html', {'form':form})

def add_page(request, category_name_slug):

    print "In add page in category : {0}".format(str(category_name_slug))
    try:
        cat = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        cat = None

    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if cat:
                page = form.save(commit=False)
                page.category = cat
                page.views = 0
                page.save()
                return category(request, category_name_slug)
        else:
            print form.errors
    else:
        form = PageForm()

    context_dict = {'form':form, 'category':cat}

    return render(request, 'rango/add_page.html', context_dict)


# def register(request):
#     # A boolean value for telling the template whether the registration was successful.
#     # Set to False initially. Code changes value to True when registration succeeds.
#     registered = False
#
#     if request.method == 'POST':
#         # Attempt to grab information from the raw form information.
#         # Note that we make use of both UserForm and UserProfileForm.
#         user_form = UserForm(data=request.POST)
#         profile_form = UserProfileForm(data=request.POST)
#
#         if user_form.is_valid() and profile_form.is_valid():
#             user = user_form.save()
#
#             # Now we hash the password with the set_password method.
#             # Once hashed, we can update the user object.
#             user.set_password(user.password)
#             user.save()
#
#             # Now sort out the UserProfile instance.
#             # Since we need to set the user attribute ourselves, we set commit=False.
#             # This delays saving the model until we're ready to avoid integrity problems.
#             profile = profile_form.save(commit=False)
#             profile.user = user
#
#             # Did the user provide a profile picture?
#             # If so, we need to get it from the input form and put it in the UserProfile model.
#             if 'picture' in request.FILES:
#                 profile.picture = request.FILES['picture']
#
#             profile.save()
#
#             registered = True
#
#         else:
#             print user_form.errors, profile_form.errors
#
#     # Not a HTTP POST, so we render our form using two ModelForm instances.
#     # These forms will be blank, ready for user input.
#     else:
#         user_form = UserForm()
#         profile_form = UserProfileForm()
#
#     return render(request,
#             'rango/register.html',
#             {'user_form':user_form, 'profile_form':profile_form, 'registered':registered})
#
# def user_login(request):
#     if request.method == 'POST':
#         # Gather the username and password provided by the user.
#         # This information is obtained from the login form.
#                 # We use request.POST.get('<variable>') as opposed to request.POST['<variable>'],
#                 # because the request.POST.get('<variable>') returns None, if the value does not exist,
#                 # while the request.POST['<variable>'] will raise key error exception
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#
#         # Use Django's machinery to attempt to see if the username/password
#         # combination is valid - a User object is returned if it is.
#         user = authenticate(username=username, password=password)
#
#         # If we have a User object, the details are correct.
#         # If None (Python's way of representing the absence of a value), no user
#         # with matching credentials was found.
#         if user:
#             # Is the account active? It could have been disabled.
#             if user.is_active:
#                 # If the account is valid and active, we can log the user in.
#                 # We'll send the user back to the homepage.
#                 login(request, user)
#                 return HttpResponseRedirect('/rango/')
#             else:
#                 # An inactive account was used - no logging in!
#                 return HttpResponse("Your Rango account is disabled")
#         else:
#             # Bad login details were provided. So we can't log the user in.
#             print "Invalid login details : {0}, {1}".format(username, password)
#             return HttpResponse("Invalid Login details supplied")
#     # The request is not a HTTP POST, so display the login form.
#     # This scenario would most likely be a HTTP GET.
#     else:
#         # No context variables to pass to the template system, hence the
#         # blank dictionary object...
#         return render(request, 'rango/login.html', {})
#
# @login_required
# def user_logout(request):
#     # Since we know the user is logged in, we can now just log them out.
#     logout(request)
#
#     # Take the user back to the homepage.
#     return HttpResponseRedirect("/rango/")

@login_required
def restricted(request):
    #return HttpResponse("Since you are logged in, you can see this text")
    return render(request, "rango/restricted.html", {} )
