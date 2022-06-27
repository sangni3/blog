from web.models import Article

from django.contrib.sitemaps import Sitemap

from django.db.models import Sum

class BlogSitemap(Sitemap):

    changefreq = "weekly"

#priority = 0.5

    def items(self):

        return Article.objects.filter(status="p")

    def lastmod(self, obj):

        if obj.created_time:

            return obj.created_time

        return obj.created_time

    def priority(self, obj):

        if obj.views:

            allReadCount = Article.objects.all().aggregate(Sum('views'))['views__sum']

            curPriority = obj.views / float(allReadCount)

            return '%.2f' % (curPriority / 2.0 + 0.5)

        return 0.50
