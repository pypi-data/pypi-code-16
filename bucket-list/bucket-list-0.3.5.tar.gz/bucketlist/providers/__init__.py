import sys
from bucketlist import appconfig, speedyio, SUPPORTED_PROVIDERS
from bucketlist.errors import BucketlistError
from bucketlist.providers.wunderlist import Wunderlist
from bucketlist.providers.localfs import LocalFS


def get_current_provider():
    try:
        provider = appconfig.get_provider_name()
    except BucketlistError as e:
        provider = None

    if provider is None:
        speedyio.error("Provider is not set or is invalid.")

        speedyio.plain_print("\nSuppoted providers are:")
        for provider_name in SUPPORTED_PROVIDERS:
            speedyio.bold_print(" - {}".format(provider_name))

        speedyio.plain_print("\n"+
            "For changing the provider or setting one please run following command.\n" +
            "    bucket-list config --set-provider <provider_name>")
        sys.exit(0)

    return {
        'wunderlist': Wunderlist,
        'localfs': LocalFS
    }.get(provider)
