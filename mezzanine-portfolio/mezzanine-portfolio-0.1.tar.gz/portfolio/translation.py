from modeltranslation.translator import translator
from mezzanine.core.translation import (TranslatedSlugged,
                                        TranslatedDisplayable,
                                        TranslatedRichText,
                                        TranslationOptions)
from portfolio.models import PortfolioCategory, PortfolioPost, PortfolioImage


class TranslatedPortfolioPost(TranslatedDisplayable, TranslatedRichText):
    fields = ()


class TranslatedPortfolioCategory(TranslatedSlugged):
    fields = ()


class TranslatedPortfolioImage(TranslationOptions):
    fields = ('description',)

translator.register(PortfolioCategory, TranslatedPortfolioCategory)
translator.register(PortfolioPost, TranslatedPortfolioPost)
translator.register(PortfolioImage, TranslatedPortfolioImage)