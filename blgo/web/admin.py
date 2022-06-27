from django.contrib import admin
from .models import Article, User, Category, Tag, ArticleComment, Counts


# Register your models here.

admin.AdminSite.site_header='博客管理系统'

admin.AdminSite.site_title = '博客管理系统'

class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'created_time']
    search_fields = ['title']  # 搜索框
    list_filter = ['created_time']  # 过滤器

    def save_model(self, request, obj, form, change):
        obj.save()
        # 统计博客数目
        blog_nums = Article.objects.count()
        count_nums = Counts.objects.get(id=1)
        count_nums.blog_nums = blog_nums
        count_nums.save()
        # 博客分类数目统计
        obj_category = obj.category
        if obj_category is not None:
            obj_category.number = Article.objects.filter(category=obj_category).count()
            obj_category.save()
        # 博客标签数目统计
        obj_tag_list = obj.tags.all()
        for obj_tag in obj_tag_list:
            obj_tag.number = Article.objects.filter(tags=obj_tag).count()
            obj_tag.save()

    def delete_model(self, request, obj):
        # 统计博客数目
        blog_nums = Article.objects.count()
        count_nums = Counts.objects.get(id=1)
        count_nums.blog_nums = blog_nums - 1
        count_nums.save()
        # 博客分类数目统计
        obj_category = obj.category
        category_number = obj_category.blog_set.count()
        obj_category.number = category_number - 1
        obj_category.save()
        # 博客标签数目统计
        obj_tag_list = obj.tag.all()
        for obj_tag in obj_tag_list:
            tag_number = obj_tag.blog_set.count()
            obj_tag.number = tag_number - 1
            obj_tag.save()
        obj.delete()


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'number']

    def save_model(self, request, obj, form, change):
        obj.save()
        category_nums = Category.objects.count()
        count_nums = Counts.objects.get(id=1)
        count_nums.category_nums = category_nums
        count_nums.save()

    def delete_model(self, request, obj):
        obj.delete()
        category_nums = Category.objects.count()
        count_nums = Counts.objects.get(id=1)
        count_nums.category_nums = category_nums
        count_nums.save()


class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'number']

    def save_model(self, request, obj, form, change):
        obj.save()
        tag_nums = Tag.objects.count()
        count_nums = Counts.objects.get(id=1)
        count_nums.tag_nums = tag_nums
        count_nums.save()

    def delete_model(self, request, obj):
        obj.delete()
        tag_nums = Tag.objects.count()
        count_nums = Counts.objects.get(id=1)
        count_nums.tag_nums = tag_nums
        count_nums.save()


# ass ArticleAdmin(admin.ModelAdmin):
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'blog', 'content', 'create_time', 'user']
    search_fields = ['title']  # 搜索框


class CountsAdmin(admin.ModelAdmin):
    list_display = ['blog_nums', 'category_nums', 'tag_nums', 'visit_nums']


admin.site.register(Article, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(User)
admin.site.register(ArticleComment, CommentAdmin)
admin.site.register(Counts, CountsAdmin)
