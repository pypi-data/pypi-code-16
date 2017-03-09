from django.conf import settings


def hurumap_settings(request):
    from hurumap.geo import geo_data

    return {
        'HURUMAP': settings.HURUMAP,
        'geo_data': geo_data
    }
