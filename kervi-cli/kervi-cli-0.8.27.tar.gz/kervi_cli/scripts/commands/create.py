"""" Cli module that creates application and modules """
import os
import uuid
from shutil import copyfile
import kervi.utility.nethelper as nethelper

import click
from kervi_cli.scripts.template_engine import SuperFormatter
import kervi_cli

@click.group()
def create():
    pass

@create.command()
@click.argument('app_id', "Id of application, used in code to identify app")
@click.argument('app_name', 'Name of app, used at title in UI')
@click.option('--platform', default=None, help='RPI')
def application(app_name, app_id, platform):
    template_engine = SuperFormatter()

    cli_path = os.path.dirname(kervi_cli.__file__)
    template_path = os.path.join(cli_path, "templates/")

    web_ports = [80, 8080, nethelper.get_free_port()]
    web_port = 0
    for port in web_ports:
        if nethelper.is_port_free(port):
            web_port = port
            break

    app_template = open(template_path+"app_tmpl.py", 'r').read()
    app_file_content = template_engine.format(
        app_template,
        id=app_id,
        name=app_name,
        log=app_id,
        base_port=9500,
        websocket_port=nethelper.get_free_port(),
        ui_port=web_port,
        secret=uuid.uuid4()
    )

    if not os.path.exists(app_id+".py"):
        app_file = open(app_id+".py", "w")
        app_file.write(app_file_content)
        app_file.close()

    if not os.path.exists("web_assets"):
        os.makedirs("web_assets")

    #dashboards
    if not os.path.exists("dashboards"):
        os.makedirs("dashboards")
    if not os.path.exists("dashboards/__init__.py"):
        copyfile(template_path+"dashboard_init_tmpl.py", "dashboards/__init__.py")

    #cams
    if not os.path.exists("cams"):
        os.makedirs("cams")

    if not os.path.exists("cams/__init__.py"):
        copyfile(template_path+"cams_init_tmpl.py", "cams/__init__.py")

    if not os.path.exists("cams/cam1.py"):
        copyfile(template_path+"cam_tmpl.py", "cams/cam1.py")

    #controllers
    if not os.path.exists("controllers"):
        os.makedirs("controllers")

    if not os.path.exists("controllers/__init__.py"):
        copyfile(template_path+"controllers_init_tmpl.py", "controllers/__init__.py")

    if not os.path.exists("controllers/my_controller.py"):
        copyfile(template_path+"controller_tmpl.py", "controllers/my_controller.py")

    if not os.path.exists("controllers/system_controller.py"):
        copyfile(template_path+"system_controller_tmpl.py", "controllers/system_controller.py")

    #sensors
    if not os.path.exists("sensors"):
        os.makedirs("sensors")

    if not os.path.exists("sensors/my_sensor.py"):
        copyfile(template_path+"sensor_tmpl.py", "sensors/my_sensor.py")
        copyfile(template_path+"system_sensors_tmpl.py", "sensors/system_sensors.py")

    if not os.path.exists("sensors/__init__.py"):
        copyfile(template_path+"sensors_init_tmpl.py", "sensors/__init__.py")


    click.echo('Your app is ready')
    click.echo("start it with python "+app_id+".py")
