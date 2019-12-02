import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import OffForm, LoginForm, RegistrationForm
from .models import Category, Product
from .constants import *


def home(request):
    """ homepage, when the user performs a search, if the desired product is not in the database,
     use the openfoodfact API to find it and save it in the database """
    if request.method == 'POST':
        form = OffForm(request.POST)
        if form.is_valid():
            search_terms = form.cleaned_data['nom']
            mini_search_terms = search_terms.lower()
            first_maj_search_terms = search_terms.capitalize()
            if len(Product.objects.filter(name=mini_search_terms)) == 0:
                all_products = []
                for category in CATEGORIES_LIST:
                    api = 'https://fr.openfoodfacts.org/cgi/search.pl'
                    config = {
                        'action': 'process',
                        'search_terms': first_maj_search_terms,
                        'tagtype_0': 'categories',
                        'tag_contains_0': 'contains',
                        'tag_0': category,
                        'page_size': 1,
                        'json': 1
                    }
                    response = requests.get(api, params=config)
                    results = response.json()
                    recovered_product = results['products']
                    all_products.extend(recovered_product)

                good_product = []
                for product in all_products:
                    if 'product_name_fr' in product:
                        if product['product_name_fr'] == first_maj_search_terms and len(
                                clean_cat(product['categories'].split(","), CATEGORIES_LIST)) > 0:
                            good_product.append(product)
                selected_products = []

                if len(good_product) > 0:
                    if len(good_product) > 1:
                        good_product = [good_product[0]]

                    for product in good_product:
                        if valid_product(KEYS, product):
                            cat = clean_cat(product['categories'].split(","), CATEGORIES_LIST)
                            nutriscore = product['nutrition_grade_fr']
                            name = product['product_name_fr'].lower()
                            url_picture = product['image_url']
                            url_link = product['url']

                            key = [nutriscore, name, cat, url_picture, url_link]
                            selected_products.append(key)
                    if len(selected_products) > 0:
                        product_to_insert = selected_products[0]
                        element = Product.objects.create(name=product_to_insert[1].lower(), nutriscore=product_to_insert[0],
                                                         url_image=product_to_insert[3],
                                                         url_link=product_to_insert[4])

                        for cat in product_to_insert[2]:
                            element.category.add(Category.objects.get(name=cat))
                            element.save()

            return redirect('off:article', search=search_terms)

    else:
        form = OffForm()
    return render(request, 'off/home.html', locals())

# Access information account
@login_required(login_url='off:registration')  # redirect when user is not logged in
def account(request):
    user = User.objects.get(id=request.user.id)
    form = OffForm()
    return render(request, 'off/account.html', locals())


@login_required(login_url='off:registration')  # redirect when user is not logged in
def my_products(request):
    # Access to saved products
    user = User.objects.get(id=request.user.id)
    products = user.product_set.all().order_by('nutriscore')
    form = OffForm()
    paginate = True
    paginator = Paginator(products, 9)
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        products = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        products = paginator.page(paginator.num_pages)
    return render(request, 'off/myproducts.html', locals())


def article(request, search):
    # Returns products in the same category with a higher nutritional rating
    search = search.lower()
    researched_product = get_object_or_404(Product, name=search)
    nutriscore_researched_product = researched_product.nutriscore
    categories = Category.objects.filter(product__name=search).values_list('id', flat=True)
    products = Product.objects.filter(category__id__in=categories).filter(
        nutriscore__lt=nutriscore_researched_product).distinct().exclude(name=researched_product.name).order_by('nutriscore')

    paginate = True
    paginator = Paginator(products, 9)
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        products = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        products = paginator.page(paginator.num_pages)

    form = OffForm()

    # Product backup
    if request.method == 'POST':
        product = request.POST.get('id_product', False)
        user = User.objects.get(id=request.user.id)
        product_to_save = Product.objects.get(id=product)
        product_to_save.user.add(user)
        product_to_save.save()

    # Products saved by a user
    if request.user.is_authenticated:
        user = User.objects.get(id=request.user.id)
        memory = user.product_set.all()

    return render(request, 'off/articles.html', locals())


def login_registration(request):
    """ Display two forms, the first to register, the second to connect """
    login_error = False
    registration_error = False
    form = OffForm()
    if request.method == 'POST':
        login_form = LoginForm(request.POST)

        if login_form.is_valid():

            username = login_form.cleaned_data["username"]
            password = login_form.cleaned_data["password"]
            user = authenticate(username=username,
                                password=password)  # Check if data are correct
            if user:  # If the returned object is not None
                login(request, user)  # we connect user
                return redirect('home')
            else:  # otherwise an error is displayed
                login_error = True
                registration_form = RegistrationForm()

        else:
            registration_form = RegistrationForm(request.POST)
            if registration_form.is_valid():
                username = registration_form.cleaned_data["pseudo"]
                email = registration_form.cleaned_data["email"]
                password = registration_form.cleaned_data["password"]
                if User.objects.filter(email=email):
                    registration_error = True
                else:
                    user = User.objects.create_user(username, email, password)
                    login(request, user)
                    return redirect('home')

    else:
        login_form = LoginForm()
        registration_form = RegistrationForm()

    return render(request, 'off/login.html', locals())


def log_out(request):
    logout(request)
    return redirect('home')


def detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product_nutriscore = product.nutriscore
    form = OffForm()
    nutriscores = ['a', 'b', 'c', 'd', 'e']
    return render(request, 'off/detail.html', locals())


def mentions(request):
    return render(request, 'off/mentions.html')


def valid_product(keys, all_products):
    """ Returns true if all the desired keys are in the dictionary  """

    for key in keys:
        if key not in all_products:
            return False
    return True


def clean_list(products_list):
    """ Removes white space in front of the name of each category  """
    for i, elt in enumerate(products_list):
        if elt[0] == " ":
            elt = elt[1:]
            products_list[i] = elt
    return products_list


def clean_cat(list_categories_product, list_categories):
    """ Returns a list which contains the categories present in the two lists placed in parameter  """
    final_list = []
    list_cat = clean_list(list_categories_product)
    for category in list_cat:
        if category in list_categories:
            final_list.append(category)
    return final_list
