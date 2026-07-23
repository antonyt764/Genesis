from django.core.paginator import Paginator
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from .models import Category, ContactMessage, NewsletterSubscriber, Post


def _is_ajax(request):
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'


def home(request):
    recent_posts = Post.objects.order_by('-created_at')[:3]
    return render(request, 'index.html', {'recent_posts': recent_posts})

def _blog_sidebar_context(exclude_pk=None):
    recent_posts = Post.objects.exclude(pk=exclude_pk).order_by('-created_at')[:5]
    categories = Category.objects.annotate(post_count=Count('posts')).order_by('name')
    return {'recent_posts': recent_posts, 'categories': categories}

def blog(request):
    posts = Post.objects.select_related('category').order_by('-created_at')

    category_id = request.GET.get('category')
    if category_id:
        posts = posts.filter(category_id=category_id)

    paginator = Paginator(posts, 4)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {'page_obj': page_obj, 'posts': page_obj.object_list}
    context.update(_blog_sidebar_context())
    return render(request, 'blog.html', context)

def blog_details(request, pk):
    post = get_object_or_404(Post.objects.select_related('category'), pk=pk)
    context = {'post': post}
    context.update(_blog_sidebar_context(exclude_pk=pk))
    return render(request, 'blog-details.html', context)

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
        if _is_ajax(request):
            return HttpResponse('OK')
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
        if _is_ajax(request):
            return HttpResponse('OK')
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
    