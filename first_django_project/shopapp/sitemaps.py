from django.contrib.sitemaps import Sitemap
from datetime import datetime
from .models import Product


class ShopSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8 # приоритет страницы (1 - самый высокий)

    def items(self):
        return Product.objects.filter(archived__isnull=False).order_by("name")

    def lastmod(self, obj: Product):
        if obj.created_at is not None:
            return obj.created_at
        return datetime.now()



