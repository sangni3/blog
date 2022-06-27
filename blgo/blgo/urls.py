"""blgo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blgo/', include('blgo.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from web import views
from web.views import ArichiveView
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from sitemap.BlogSitemap import BlogSitemap

blog_sitemap={
    'recipe':BlogSitemap
}

urlpatterns = [
    path( '',  views.Blog, name='home' ),
    path('admin/', admin.site.urls),
    path( 'index/', views.Blog, name='home' ),
    path( 'article/<article_id>', views.article,name='article' ),
    path( 'type/<cate_id>', views.blogs_with_type, name='blogs_with_type' ),
    path( 'update_comment', views.update_comment, name='update_comment' ),
    url( r'^archive/$', ArichiveView.as_view(), name='archive' ),
    path( 'ckeditor', include( 'ckeditor_uploader.urls' ) ),
    path( 'login/', views.login, name='login' ),
    path( 'register/', views.register, name='register' ),
    path( 'search/', views.search, name='search' ),
    url( r'^blog_sitemap\.xml$', sitemap, {'sitemaps': blog_sitemap},
         name='django.contrib.sitemaps.views.sitemap' ),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
