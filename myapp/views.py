from django.shortcuts import render


def home(request):
    return render(request, 'index.html')

def blog(request):
    return render(request, 'blog.html')

def blog_details(request):
    return render(request, 'blog-details.html')

def portfolio_details(request):
    return render(request, 'portfolio-details.html')

def service_details(request):
    return render(request, 'service-details.html')

def starter(request):
    return render(request, 'starter-page.html')