# -*- coding: utf-8 -*-


class WTError(Exception):
    """Base WT exception"""


class UrlNotFoundError(WTError):
    """Url not found error"""


class BadPaginatorUrlError(WTError):
    """Bad paginator url error"""


class BadPaginatorPageError(WTError):
    """Bad paginator page error"""


class InvalidLocalLinkError(WTError):
    """Invalid local link error"""
