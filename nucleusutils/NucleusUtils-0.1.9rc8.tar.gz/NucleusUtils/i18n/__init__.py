import warnings

with warnings.catch_warnings():
    warnings.simplefilter("always")
    warnings.warn("Module NucleusUtils.i18n is deprecated! Use NucleusUtils.translations", DeprecationWarning)
