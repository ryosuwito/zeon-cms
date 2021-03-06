from django.contrib.sites.models import Site
from django.db import models
from django.template.defaultfilters import slugify

from ckeditor.fields import RichTextField

from membership.models import Member

import datetime

class PageModel(models.Model):
    title = models.CharField(max_length=200)
    content = RichTextField(null=True, blank=True)
    slug = models.SlugField(unique=True, db_index=True, blank=True, null=True)
    site = models.ForeignKey(Site, related_name="site_page", on_delete=models.CASCADE,null=True, blank=True)
    owner = models.ForeignKey(Member, null=True, blank=True,
                                on_delete=models.CASCADE, 
                                related_name="page_owner", 
                                verbose_name='owner')
    created_date = models.DateTimeField(db_index=True,default=datetime.datetime.now)
    is_published = models.BooleanField(default=False, db_index=True)
    banner_image_1 = models.ImageField(upload_to = 'cp/user_uploads/banner_images/', null=True, blank=True)
    banner_image_2 = models.ImageField(upload_to = 'cp/user_uploads/banner_images/', null=True, blank=True)
    banner_image_3 = models.ImageField(upload_to = 'cp/user_uploads/banner_images/', null=True, blank=True)

    def __str__(self):
        return self.title.title()
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title.lower())
        super(PageModel, self).save(*args, **kwargs)
    
    def get_banner_image_1_url(self):
        return ("/media/%s"%self.banner_image_1)
    
    def get_banner_image_2_url(self):
        return ("/media/%s"%self.banner_image_2)
    
    def get_banner_image_3_url(self):
        return ("/media/%s"%self.banner_image_3)

    def get_page_url(self):
        return "%s/" % (self.slug)
        