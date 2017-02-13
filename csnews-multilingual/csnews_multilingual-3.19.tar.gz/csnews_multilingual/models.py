from django.db import models
from django.utils.translation import ugettext_lazy as _
from photologue.models import Photo
from django.http import HttpResponseRedirect
from hvad.models import TranslatableModel, TranslatedFields
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify


class Tag(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(_('Name'), max_length=300),
        slug=models.CharField(_('Slug'), max_length=200, db_index=True)
    )
    added = models.DateField(_('Added'), auto_now_add=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Tag, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')
        ordering = ('-added',)

    def __unicode__(self):
        return u'%s' % self.name


class Article(TranslatableModel):
    published = models.DateTimeField(_('Published'))
    image = models.ForeignKey(Photo, null=True, blank=True, related_name='news_images')
    tags = models.ManyToManyField(Tag, blank=True)

    is_public = models.BooleanField(_('Is public'), default=True)

    added = models.DateField(_('Added'), auto_now_add=True)
    modified = models.DateField(_('Modified'), auto_now=True)

    translations = TranslatedFields(
        title=models.CharField(_('Title'), max_length=200),
        summary=models.TextField(_('Summary'), blank=True),
        body=models.TextField(_('Body')),
        slug = models.CharField(_('Slug'), max_length=200, db_index=True)
    )

    def get_title(self):
        return self.title

    def get_absolute_url(self):
        return reverse('csnews_article', kwargs={'article_slug': self.slug})

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Article, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('Article')
        verbose_name_plural = _('Articles')
        ordering = ('-published',)
        get_latest_by = 'published'

    def __unicode__(self):
        return u'%s' % self.title


class PhotoExtended(TranslatableModel):
    photo = models.OneToOneField(Photo, related_name='extended')

    translations = TranslatedFields(
        caption=models.TextField(_('caption'), blank=True)
    )

    class Meta:
        verbose_name = _('Multilingual Caption')
        verbose_name_plural = _('Multilingual Captions')

    def __unicode__(self):
        return self.photo.title
