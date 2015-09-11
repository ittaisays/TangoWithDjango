from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User

class Category(models.Model):
	name = models.CharField(max_length=128, unique=True)
	likes = models.IntegerField(default = 0)
	views = models.IntegerField(default = 0)
	slug = models.SlugField(unique = True)

	def save(self, *args, **kwargs):
		self.slug = slugify(self.name)
		if self.views<0:
			self.views=0
		super(Category, self).save(*args, **kwargs)

	def __unicode__(self):
		return self.name

class Page(models.Model):
	category = models.ForeignKey(Category)
	title = models.CharField(max_length=128)
	url = models.URLField()
	views = models.IntegerField(default=0)
	last_visit = models.DateTimeField(null=True)
	first_visit = models.DateTimeField(null=True)

	def __unicode__(self):
		return self.title

class UserProfile(models.Model):
	user = models.OneToOneField(User)
	website = models.URLField(blank=True)
	picture = models.ImageField(upload_to='profile_images', blank=True)

	def __unicode__(self):
		return self.user.username