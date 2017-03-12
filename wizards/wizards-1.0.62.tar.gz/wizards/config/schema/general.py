import ea.schema

from wizards.config.schema.base import BaseConfigSchema


class GeneralSettingsSchema(BaseConfigSchema):
    """Loads and validates the general user-settings for SG
    generated applications.
    """

    # Specifies the working directory of the application.
    workdir = ea.schema.fields.String(
        required=False,
        missing='/'
    )

    # The directory holding inversion-of-control configuration
    # files, relative to the file that this schema parsed.
    iocdir = ea.schema.fields.String(
        required=False,
        missing="ioc.d/"
    )

    @ea.schema.post_load
    def post_load(self, dto):
        dto['iocdirs'] = ["%s/*.ioc" % dto.pop('iocdir').rstrip('/')]