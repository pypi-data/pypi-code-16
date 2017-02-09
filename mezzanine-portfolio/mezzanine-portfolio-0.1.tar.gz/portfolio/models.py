from future.builtins import str

from string import punctuation

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from django.utils.encoding import force_text

from mezzanine.conf import settings
from mezzanine.core.fields import FileField
from mezzanine.core.models import Displayable, Ownable, RichText, Slugged, Orderable
from mezzanine.generic.fields import CommentsField, RatingField
from mezzanine.utils.models import AdminThumbMixin, upload_to



class PortfolioPost(Displayable, Ownable, RichText, AdminThumbMixin):
    """
    A Portfolio post.
    """

    categories = models.ManyToManyField("PortfolioCategory",
                                        verbose_name=_("Categories"),
                                        blank=True, related_name="portfolioposts")
    
    rating = RatingField(verbose_name=_("Rating"))
    featured_image = FileField(verbose_name=_("Featured Image"),
        upload_to=upload_to("portfolio.PortfolioPost.featured_image", "portfolio"),
        format="Image", max_length=255, null=True, blank=True)
    admin_thumb_field = "featured_image"

    class Meta:
        verbose_name = _("Portfolio post")
        verbose_name_plural = _("Portfolio posts")
        ordering = ("-publish_date",)

    def get_absolute_url(self):
        """
        URLs for Portfolio posts can either be just their slug, or prefixed
        with a portion of the post's publish date, controlled by the
        setting ``Portfolio_URLS_DATE_FORMAT``, which can contain the value
        ``year``, ``month``, or ``day``. Each of these maps to the name
        of the corresponding urlpattern, and if defined, we loop through
        each of these and build up the kwargs for the correct urlpattern.
        The order which we loop through them is important, since the
        order goes from least granular (just year) to most granular
        (year/month/day).
        """
        url_name = "portfolio_post_detail"
        kwargs = {"slug": self.slug}
        date_parts = ("year", "month", "day")
        if settings.BLOG_URLS_DATE_FORMAT in date_parts:
            url_name = "portfolio_post_detail_%s" % settings.BLOG_URLS_DATE_FORMAT
            for date_part in date_parts:
                date_value = str(getattr(self.publish_date, date_part))
                if len(date_value) == 1:
                    date_value = "0%s" % date_value
                kwargs[date_part] = date_value
                if date_part == settings.BLOG_URLS_DATE_FORMAT:
                    break
        return reverse(url_name, kwargs=kwargs)
        #return ''


class PortfolioCategory(Slugged):
    """
    A category for grouping Portfolio posts into a series.
    """

    class Meta:
        verbose_name = _("Portfolio Category")
        verbose_name_plural = _("Portfolio Categories")
        ordering = ("title",)

    @models.permalink
    def get_absolute_url(self):
        return ("portfolio_post_list_category", (), {"category": self.slug})


@python_2_unicode_compatible
class PortfolioImage(Orderable):

    portfolio_post = models.ForeignKey("PortfolioPost", related_name="images")
    file = FileField(_("File"), max_length=200, format="Image",
        upload_to=upload_to("portfolio.PortfolioImage.file", "portfolio"))
    description = models.CharField(_("Description"), max_length=1000,
                                                           blank=True)

    class Meta:
        verbose_name = _("Image")
        verbose_name_plural = _("Images")

    def __str__(self):
        return self.description

    def save(self, *args, **kwargs):
        """
        If no description is given when created, create one from the
        file name.
        """
        if not self.id and not self.description:
            name = force_text(self.file)
            name = name.rsplit("/", 1)[-1].rsplit(".", 1)[0]
            name = name.replace("'", "")
            name = "".join([c if c not in punctuation else " " for c in name])
            # str.title() doesn't deal with unicode very well.
            # http://bugs.python.org/issue6412
            name = "".join([s.upper() if i == 0 or name[i - 1] == " " else s
                            for i, s in enumerate(name)])
            self.description = name
        super(PortfolioImage, self).save(*args, **kwargs)