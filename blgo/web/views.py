from django.contrib import auth
from django.contrib.auth import authenticate, login
from django.urls import reverse
from .models import User
from . import models
from django.views import View
from django.http import HttpResponse, JsonResponse
from pure_pagination import PageNotAnInteger, Paginator
from django.shortcuts import render, redirect
from .models import ArticleComment
from .forms import CommentForm
from .form_lg import LoginForm, RegForm
# Create your views here.

#博客主页
def Blog(request):
    articles = models.Article.objects.all().order_by('-created_time')
    count_nums = models.Counts.objects.first()
    user=models.User.objects.first()
    blog_nums = count_nums.blog_nums
    cate_nums = count_nums.category_nums
    tag_nums = count_nums.tag_nums
    count_nums.visit_nums += 1
    count_nums.save()
    all_category = models.Category.objects.all().order_by('id')
    top=models.Article.objects.filter(top=1)
    # 分页
    try:
        page = request.GET.get('page', 1)
    except PageNotAnInteger:
        page = 1

    p = Paginator(articles, 3, request=request)
    articles = p.page(page)

    return render(request, 'index.html', {
        'all_category': all_category,
        'articles': articles,
        'tops':top,
        'avatar':user.avatar,
        'blog_nums': blog_nums,
        'cate_nums': cate_nums,
        'tag_nums': tag_nums

    })

#文章内容
def article(request, article_id):
    contents1 = models.Article.objects.get(pk=article_id)
    all_category = models.Category.objects.all().order_by( 'id' )
    user=models.User.objects.first()
    count_nums = models.Counts.objects.first()
    models.Article.viewed(contents1)
    blog_nums = count_nums.blog_nums
    cate_nums = count_nums.category_nums
    tag_nums = count_nums.tag_nums

    # 获取评论内容
    comments = ArticleComment.objects.filter(blog=contents1,parent=None)
    # 实现博客上一篇与下一篇功能

    has_prev = False
    has_next = False
    id_prev = id_next = int(article_id)
    blog_id_max = models.Article.objects.all().order_by('-id').first()
    id_max = blog_id_max.id
    while not has_prev and id_prev >= 1:
        blog_prev = models.Article.objects.filter(id=id_prev - 1).first()
        if not blog_prev:
            id_prev -= 1
        else:
            has_prev = True
    while not has_next and id_next <= id_max:
        blog_next = models.Article.objects.filter(id=id_next + 1).first()
        if not blog_next:
            id_next += 1
        else:
            has_next = True

    return render(request, 'article_page.html', {
        'all_category': all_category,
        'article': contents1,
        'avatar': user.avatar,
        'comments':comments.order_by('-create_time'),
        'comment_form':CommentForm(initial={'blog_id':article_id,'reply_comment_id': 0}),
        'blog_prev': blog_prev,
        'blog_next': blog_next,
        'has_prev': has_prev,
        'has_next': has_next,
        'blog_nums': blog_nums,
        'cate_nums': cate_nums,
        'tag_nums': tag_nums
    })


#分类显示
def blogs_with_type(request, cate_id):
    cate = models.Category.objects.get(pk=cate_id)
    user = models.User.objects.first()
    articles = models.Article.objects.filter(category=cate)
    count_nums = models.Counts.objects.first()
    blog_nums = count_nums.blog_nums
    cate_nums = count_nums.category_nums
    tag_nums = count_nums.tag_nums
    all_category = models.Category.objects.all().order_by('id')
    # 分页
    try:
        page = request.GET.get('page', 1)
    except PageNotAnInteger:
        page = 1

    p = Paginator(articles, 2, request=request)
    articles = p.page(page)
    return render(request, 'index.html', {
        'all_category': all_category,
        'avatar': user.avatar,
        'articles': articles,
        'blog_nums': blog_nums,
        'cate_nums': cate_nums,
        'tag_nums': tag_nums,
        'cate':1
    })


class ArichiveView(View):
    """
    归档
    """

    def get(self, request):
        all_blog = models.Article.objects.all().order_by('-created_time')
        all_category = models.Category.objects.all().order_by('id')
        user = models.User.objects.first()
        # 博客、标签、分类数目统计
        count_nums = models.Counts.objects.get(id=1)
        blog_nums = count_nums.blog_nums
        cate_nums = count_nums.category_nums
        tag_nums = count_nums.tag_nums
        # 分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(all_blog, 5, request=request)
        all_blog = p.page(page)

        return render(request, 'archive.html', {
            'avatar': user.avatar,
            'all_blog': all_blog,
            'all_category': all_category,
            'blog_nums': blog_nums,
            'cate_nums': cate_nums,
            'tag_nums': tag_nums,

        })



def login(request):
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user = login_form.cleaned_data['user']
            auth.login(request, user)
            return redirect(request.GET.get('from', reverse('home')))
    else:
        login_form = LoginForm()

    context = {}
    context['login_form'] = login_form
    return render(request, 'login.html', context)


def register(request):
    if request.method == 'POST':
        reg_form = RegForm(request.POST)
        if reg_form.is_valid():
            username = reg_form.cleaned_data['username']
            email = reg_form.cleaned_data['email']
            password = reg_form.cleaned_data['password']
            avatar = request.FILES.get("avatar")  # 图片对象
            if avatar == None:
                # 创建用户
                user = User.objects.create_user(username, email, password)
            else:
                user = User.objects.create_user( username, email, password, avatar=avatar )
            user.save()
            # 登录用户
            user = auth.authenticate(username=username, password=password)
            auth.login(request, user)
            return redirect(request.GET.get('from', reverse('home')))
    else:
        reg_form = RegForm()

    context = {}
    context['reg_form'] = reg_form
    return render(request, 'register.html', context)

def update_comment(request):
    referer = request.META.get('HTTP_REFERER', reverse('home'))
    comment_form = CommentForm(request.POST, user=request.user)

    data = {}

    if comment_form.is_valid():
        # 检查通过，保存数据
        comment = ArticleComment()
        a=comment_form.cleaned_data['blog_id']
        comment.user = comment_form.cleaned_data['user']
        comment.content = comment_form.cleaned_data['text']
        comment.blog= models.Article.objects.get(pk=a)
        parent = comment_form.cleaned_data['parent']


        if not parent is None:
            comment.root = parent.root if not parent.root is None else parent
            comment.parent = parent
            comment.reply_to = parent.user
        comment.save()

        # 返回数据
        data['status'] = 'SUCCESS'
        data['username'] = comment.user.username
        data['create_time'] = comment.create_time.strftime('%Y-%m-%d %H:%M:%S')
        data['text'] = comment.content
        if not parent is None:
            data['reply_to'] = comment.reply_to.username
        else:
            data['reply_to'] = ''
        data['pk'] = comment.pk
        data['root_pk'] = comment.root.pk if not comment.root is None else ''
    else:
        #return render(request, 'error.html', {'message': comment_form.errors, 'redirect_to': referer})
        data['status'] = 'ERROR'
        data['message'] = list(comment_form.errors.values())[0][0]
    return JsonResponse(data)

def search(request):
    q = request.GET.get('q')  # 获取关搜索键词
    user = models.User.objects.first()
    contexts = models.Article.objects.all().order_by('created_time')[:5]  # 获取最近五篇文章
    search_list = models.Article.objects.filter(title__icontains=q)  # 根据标题所含关键词搜索
    error_msg = 'No result'
    return render(request, 'search.html', {
            'search_list': search_list,
            'error_msg': error_msg,
            'avatar': user.avatar,
            'contexts': contexts})
