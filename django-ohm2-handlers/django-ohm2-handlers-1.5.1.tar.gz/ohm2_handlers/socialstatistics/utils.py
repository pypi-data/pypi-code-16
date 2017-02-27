from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.db.models import Q
from ohm2_handlers import utils as h_utils
from . import settings
from . import models as socialstatistics_models
from . import errors as socialstatistics_errors
from .decorators import socialstatistics_safe_request
from .definitions import SocialstatisticsRunException
from dateutil.relativedelta import relativedelta
from dateutil import parser as date_parser
import os, time, random, datetime


random_string = "OACu65TeI1Dbgx1auVOxBWfIr2LqxHLi"




def create_twitter(user, name, account_id, access_token, access_token_secret, **kwargs):
	kwargs["user"] = user
	kwargs["name"] = name.strip()
	kwargs["account_id"] = account_id.strip()
	kwargs["access_token"] = access_token.strip()
	kwargs["access_token_secret"] = access_token_secret.strip()
	return h_utils.db_create(socialstatistics_models.Twitter, **kwargs)

def get_twitter(**kwargs):
	return h_utils.db_get(socialstatistics_models.Twitter, **kwargs)

def get_or_none_twitter(**kwargs):
	return h_utils.db_get_or_none(socialstatistics_models.Twitter, **kwargs)

def filter_twitter(**kwargs):
	return h_utils.db_filter(socialstatistics_models.Twitter, **kwargs)

def delete_twitter(twitter, **kwargs):
	return h_utils.db_update(twitter, deleted = True)

def create_twittersnapshot(twitter, tweets, following, followers, **kwargs):
	kwargs["twitter"] = twitter
	kwargs["tweets"] = tweets
	kwargs["following"] = following
	kwargs["followers"] = followers
	snapshot = h_utils.db_create(socialstatistics_models.TwitterSnapshot, **kwargs)

	last = get_or_none_lasttwittersnapshot(twitter = twitter)
	if last:
		last = h_utils.db_update(last, snapshot = snapshot)
	else:
		last = create_lasttwittersnapshot(twitter, snapshot)

	return snapshot

def create_lasttwittersnapshot(twitter, snapshot, **kwargs):
	kwargs["twitter"] = twitter
	kwargs["snapshot"] = snapshot
	return h_utils.db_create(socialstatistics_models.LastTwitterSnapshot, **kwargs)

def get_lasttwittersnapshot(**kwargs):
	return h_utils.db_get(socialstatistics_models.LastTwitterSnapshot, **kwargs)

def get_or_none_lasttwittersnapshot(**kwargs):
	return h_utils.db_get_or_none(socialstatistics_models.LastTwitterSnapshot, **kwargs)

def filter_lasttwittersnapshot(**kwargs):
	return h_utils.db_filter(socialstatistics_models.LastTwitterSnapshot, **kwargs)

def get_twittersnapshot(**kwargs):
	return h_utils.db_get(socialstatistics_models.TwitterSnapshot, **kwargs)

def get_or_none_twittersnapshot(**kwargs):
	return h_utils.db_get_or_none(socialstatistics_models.TwitterSnapshot, **kwargs)	

def filter_twittersnapshot(**kwargs):
	return h_utils.db_filter(socialstatistics_models.TwitterSnapshot, **kwargs)	

def create_twittersnapshot_from_twitter(twitter, **kwargs):
	api = twitter.get_api()
	me = api.me()

	return create_twittersnapshot(twitter, me.statuses_count, me.friends_count, me.followers_count)


def get_todays_twittersnapshots(twitter, **kwargs):
	now = timezone.now()
	snapshots = filter_twittersnapshot(twitter = twitter,
									   created__year = now.year,
									   created__month = now.month,
									   created__day = now.day)

	return snapshots


def create_facebook(user, name, account_id, access_token, token_type, **kwargs):
	kwargs["user"] = user
	kwargs["name"] = name.strip()
	kwargs["account_id"] = account_id.strip()
	kwargs["access_token"] = access_token.strip()
	kwargs["token_type"] = token_type.strip()
	return h_utils.db_create(socialstatistics_models.Facebook, **kwargs)

def get_facebook(**kwargs):
	return h_utils.db_get(socialstatistics_models.Facebook, **kwargs)

def get_or_none_facebook(**kwargs):
	return h_utils.db_get_or_none(socialstatistics_models.Facebook, **kwargs)	

def filter_facebook(**kwargs):
	return h_utils.db_filter(socialstatistics_models.Facebook, **kwargs)	

def delete_facebook(facebook, **kwargs):
	return h_utils.db_update(facebook, deleted = True)

def create_facebookpage(facebook, name, page_id, **kwargs):
	kwargs["facebook"] = facebook
	kwargs["name"] = name.strip()
	kwargs["page_id"] = page_id.strip()
	return h_utils.db_create(socialstatistics_models.FacebookPage, **kwargs)

def get_facebookpage(**kwargs):
	return h_utils.db_get(socialstatistics_models.FacebookPage, **kwargs)

def get_or_none_facebookpage(**kwargs):
	return h_utils.db_get_or_none(socialstatistics_models.FacebookPage, **kwargs)	

def filter_facebookpage(**kwargs):
	return h_utils.db_filter(socialstatistics_models.FacebookPage, **kwargs)

def delete_facebookpage(page, **kwargs):
	return h_utils.db_update(page, deleted = True)

def create_facebookpagesnapshot(page, country_page_likes, fan_count, new_like_count, rating_count, talking_about_count, **kwargs):
	kwargs["page"] = page
	kwargs["country_page_likes"] = country_page_likes
	kwargs["fan_count"] = fan_count
	kwargs["new_like_count"] = new_like_count
	kwargs["rating_count"] = rating_count
	kwargs["talking_about_count"] = talking_about_count
	snapshot = h_utils.db_create(socialstatistics_models.FacebookPageSnapshot, **kwargs)

	last = get_or_none_lastfacebookpagesnapshot(page = page)
	if last:
		last = h_utils.db_update(last, snapshot = snapshot)
	else:
		last = create_lastfacebookpagesnapshot(page, snapshot)

	return snapshot

def create_facebookpagesnapshot_from_facebookpage(page, **kwargs):
	fields = "country_page_likes,fan_count,new_like_count,rating_count,talking_about_count"
	ret = page.facebook.get_object(id = page.page_id, fields = fields)


	return create_facebookpagesnapshot(page, ret["country_page_likes"], ret["fan_count"], ret.get("new_like_count", 0),
									   ret.get("rating_count", 0), ret.get("talking_about_count", 0))


def create_lastfacebookpagesnapshot(page, snapshot, **kwargs):
	kwargs["page"] = page
	kwargs["snapshot"] = snapshot
	return h_utils.db_create(socialstatistics_models.LastFacebookPageSnapshot, **kwargs)

def get_lastfacebookpagesnapshot(**kwargs):
	return h_utils.db_get(socialstatistics_models.LastFacebookPageSnapshot, **kwargs)

def get_or_none_lastfacebookpagesnapshot(**kwargs):
	return h_utils.db_get_or_none(socialstatistics_models.LastFacebookPageSnapshot, **kwargs)

def filter_lastfacebookpagesnapshot(**kwargs):
	return h_utils.db_filter(socialstatistics_models.LastFacebookPageSnapshot, **kwargs)

def get_facebookpagesnapshot(**kwargs):
	return h_utils.db_get(socialstatistics_models.FacebookPageSnapshot, **kwargs)

def get_or_none_facebookpagesnapshot(**kwargs):
	return h_utils.db_get_or_none(socialstatistics_models.FacebookPageSnapshot, **kwargs)	

def filter_facebookpagesnapshot(**kwargs):
	return h_utils.db_filter(socialstatistics_models.FacebookPageSnapshot, **kwargs)

def get_todays_facebookpagesnapshot(page, **kwargs):
	now = timezone.now()
	snapshots = filter_facebookpagesnapshot(page = page,
										    created__year = now.year,
										    created__month = now.month,
										    created__day = now.day)

	return snapshots