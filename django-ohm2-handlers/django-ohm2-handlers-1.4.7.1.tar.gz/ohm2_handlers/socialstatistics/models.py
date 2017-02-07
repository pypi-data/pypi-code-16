from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.utils.translation import ugettext as _
from ohm2_handlers.models import BaseModel
from . import managers
from . import settings
import facebook as facebook_sdk
import tweepy


class Twitter(BaseModel):
	user = models.ForeignKey(User, on_delete = models.CASCADE)
	name = models.CharField(max_length = settings.STRING_NORMAL)
	account_id = models.CharField(max_length = settings.STRING_NORMAL)
	access_token = models.CharField(max_length = settings.STRING_DOUBLE)
	access_token_secret = models.CharField(max_length = settings.STRING_DOUBLE)

	expiration = models.DateTimeField(null = True, blank = True, default = None)
	deleted = models.BooleanField(default = False)

	def get_auth(self):
		auth = tweepy.OAuthHandler(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)
		auth.set_access_token(self.access_token, self.access_token_secret)
		return auth

	def get_api(self):
		auth = self.get_auth()
		return tweepy.API(auth)

	@property
	def is_expired(self):
		if self.expiration:
			if timezone.now() > self.expiration:
				return True
		return False		

	
class TwitterSnapshot(BaseModel):
	twitter = models.ForeignKey(Twitter, on_delete = models.CASCADE)
	tweets = models.PositiveIntegerField()
	following = models.PositiveIntegerField()
	followers = models.PositiveIntegerField()


class LastTwitterSnapshot(BaseModel):
	twitter = models.OneToOneField(Twitter, on_delete = models.CASCADE)
	snapshot = models.OneToOneField(TwitterSnapshot, on_delete = models.CASCADE)



class Facebook(BaseModel):
	user = models.ForeignKey(User, on_delete = models.CASCADE)
	name = models.CharField(max_length = settings.STRING_NORMAL)
	account_id = models.CharField(max_length = settings.STRING_NORMAL)
	access_token = models.CharField(max_length = settings.STRING_DOUBLE)
	token_type = models.CharField(max_length = settings.STRING_NORMAL)

	expiration = models.DateTimeField(null = True, blank = True, default = None)
	deleted = models.BooleanField(default = False)

	api_version = "2.7"

	@property
	def is_expired(self):
		if self.expiration:
			if timezone.now() > self.expiration:
				return True
		return False

	def get_graph(self):
		return facebook_sdk.GraphAPI(access_token = self.access_token, version = self.api_version)

	def get_object(self, *args, **kwargs):
		return self.get_graph().get_object(*args, **kwargs)


#https://developers.facebook.com/docs/graph-api/reference/page
class FacebookPage(BaseModel):
	facebook = models.ForeignKey(Facebook, on_delete = models.CASCADE)
	name = models.CharField(max_length = settings.STRING_NORMAL)
	page_id = models.CharField(max_length = settings.STRING_DOUBLE)
	deleted = models.BooleanField(default = False)


class FacebookPageSnapshot(BaseModel):
	page = models.ForeignKey(FacebookPage, on_delete = models.CASCADE)
	country_page_likes = models.PositiveIntegerField()
	fan_count = models.PositiveIntegerField()
	new_like_count = models.PositiveIntegerField()
	rating_count = models.PositiveIntegerField()
	talking_about_count = models.PositiveIntegerField()


class LastFacebookPageSnapshot(BaseModel):
	page = models.OneToOneField(FacebookPage, on_delete = models.CASCADE)
	snapshot = models.OneToOneField(FacebookPageSnapshot, on_delete = models.CASCADE)



