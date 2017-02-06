from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from .managers import UserManager
import random
import string


class User(AbstractBaseUser,PermissionsMixin):
    first_name=models.CharField(max_length=100)
    last_name=models.CharField(max_length=100)
    password=models.CharField(max_length=300)
    is_superuser=models.BooleanField(default=False)
    email=models.EmailField(max_length=200,unique=True)
    is_email_verified=models.BooleanField(default=False)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    objects=UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name','last_name']
    
    class Meta:
        verbose_name=_('user')
        verbose_name_plural=_('users')
        
        
    def get_full_name(self):
        return ('%s %s' % (self.first_name, self.last_name)).strip()
    
    def get_short_name(self):
        return self.first_name
    
  
class ResetPassword(models.Model):
    user=models.ForeignKey(User)
    reset_code=models.CharField(max_length=100)
    date_created=models.DateTimeField(default=timezone.now)


class Code(models.Model): #used for verifications
    #code reasons
    EMAIL_VERIFICATION=1
    REASONS=((EMAIL_VERIFICATION,'Email Verification'),)

    user=models.ForeignKey(User)
    code=models.CharField(max_length=100)
    reason=models.SmallIntegerField(choices=REASONS)
    date_created=models.DateTimeField(default=timezone.now)

    @classmethod
    def generate(cls,user,reason):
        #generate general for now
        code=''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(8))
        return cls.objects.create(user=user,code=code,reason=reason)
            
    @classmethod
    def is_valid(cls,user,reason,code):
        #verify if code is valid for user action
        try:
            return cls.objects.filter(user=user,reason=reason,code=code).first()
        except:
            return False

    
    
    
    
    
    