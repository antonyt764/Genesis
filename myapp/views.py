from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from .models import ContactMessage, NewsletterSubscriber


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


def contact(request):
    
    if request.method == 'POST':
        ContactMessage.objects.create(
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            subject=request.POST.get('subject'),
            message=request.POST.get('message'),
        )
        return redirect('/#contact')
    return redirect('home')


@staff_member_required
def contact_list(request):
    messages = ContactMessage.objects.all()
    return render(request, 'contact-list.html', {'messages': messages})


def newsletter(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            NewsletterSubscriber.objects.get_or_create(email=email)
        return redirect('/#subscribe')
    return redirect('home')