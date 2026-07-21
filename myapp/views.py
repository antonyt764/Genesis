from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
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


@staff_member_required
@require_POST
def contact_delete(request, pk):
    message = get_object_or_404(ContactMessage, pk=pk)
    message.delete()
    return redirect('contact_list')


def newsletter(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            NewsletterSubscriber.objects.get_or_create(email=email)
        return redirect('/#subscribe')
    return redirect('home')


@staff_member_required
def contact_edit(request,pk):
    message = get_object_or_404(ContactMessage,pk=pk)
    
    
    if request.method == "POST":
        message.name = request.POST.get("name")
        message.email = request. POST.get("email")
        message.subject = request.POST.get("subject")
        message.message = request.POST.get("message")
        message.save()

        return redirect("contact_list")
    return render(request,"contact-edit.html",{
        "message":message
    })
    