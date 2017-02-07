import yaml
import aalam_common.utils as zutils


def get_yaml_dict(settings_map):
    with open(settings_map, "r") as fd:
        return yaml.load(fd)


def uninstall_settings(provider, app):
    zutils.request_local_server(
        "DELETE",
        "/aalam/base/settings/%s/%s" % (provider, app))


def install_settings(provider, app, settings_map):
    doc = get_yaml_dict(settings_map)
    data = None
    for x in doc:
        data[x['code']] = x['type']
    resp = zutils.request_local_server(
        "PUT",
        "/aalam/base/settings/%s/%s" % (provider, app),
        json={"settings": data})
    if resp.status_code != 200:
        uninstall_settings(provider, app)
