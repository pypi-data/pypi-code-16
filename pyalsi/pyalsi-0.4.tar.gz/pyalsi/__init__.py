#! /usr/bin/python2

import click
import platform

from pyalsi.logos import logos
from colors import normal, bold
from pyalsi.hardware.disks.disk import DiskGroup
from pyalsi.hardware.vga.vga import VgaCard, Pci
from pyalsi.system.system import System
from window_managers import window_manager_definitions
from pyalsi.hardware.cpu.cpu import Cpu
from pyalsi.hardware.ram.ram import Ram
from pyalsi.utils.strings import colorize, colorize_usage, colorize_percent, Colors

DEFAULT_DISTRO_LOGO = {'Arch Linux': 'Archey',
                       'Debian': 'Below',
                       'Fedora': 'Screenfetch',
                       'Apricity OS': 'Below',
                       'Ubuntu': 'Archey'}

cpu, ram, system, vga, disks = Cpu(), Ram(), System(), Pci(), DiskGroup()
colors = Colors()


def set_color_one(ctx, p, n):
    if n not in normal:
        invalid_colour_warning()
    colors.set('c1', normal[n])


def set_color_two(ctx, p, b):
    if b not in bold:
        invalid_colour_warning()
    colors.set('c2', bold[b])


def invalid_colour_warning():
    raise click.UsageError('color must be one of {}'.format(', '.join(normal)))


def validate_logo(ctx, p, logo):
    if logo is not None:
        if logo not in logos[system.distro]:
            valid_logos = "Please pick either: {}".format(", ".join(logos[system.distro].keys()))
            if logo != 'help':
                valid_logos = "Invalid logo. {}".format(valid_logos)
            raise click.UsageError(valid_logos)
    else:
        logo = DEFAULT_DISTRO_LOGO[system.distro]
    return logo


def set_distro(ctx, p, distro):
    if distro is not None:
        system.distro = distro


@click.command()
@click.option('-n', '--normal-colour', default="white", callback=set_color_one)
@click.option('-b', '--bold-colour', default="dgrey", callback=set_color_two)
@click.option('-l', '--info-below', is_flag=True)
@click.option('-d', '--distro', help="choose: " + ", ".join(logos.keys()),
              callback=set_distro)
@click.option('--logo', help="type 'pyAlsi --logo help' to see valid logos for your distro",
              default=None, callback=validate_logo)
def cli(normal_colour, bold_colour, info_below, distro, logo):
    if logo == 'Below':
        info_below = True

    a = system.get_last_login()
    info = [colorize("OS", "{} {}".format(system.distro, platform.machine())),
            colorize("Hostname", platform.node()),
            colorize("Last Login From", '{} At {}'.format(a['ip'], a['at'])),
            colorize("Uptime", system.get_uptime()),
            colorize("Kernel", platform.release()),
            colorize("Shell", system.shell),
            colorize("Packages", system.count_packages()),
            colorize("Window Manager", system.get_window_manager()),
            colorize("RAM", "{} ({})".format(
                colorize_usage(ram.get_used().to_megabytes(), ram.get_total().to_megabytes(), ram.percent, "M"),
                colorize_percent(ram.percent, "%"))),
            colorize("CPU", cpu.to_info_string())
            ]

    info.extend(colorize("VGA Cards", card) for card in vga.get_vga_devices())
    info.extend(colorize(key, value) for key, value in system.get_package_stats().iteritems())
    info.extend(disk.to_info_string() for disk in disks.disks)

    if info_below:
        click.echo("\n".join([line.format(**colors.colors) for line in logos[system.distro][logo].splitlines()]))
        click.echo("\n\n")
        click.echo("\n".join(["   " + line.format(**colors.colors) for line in info]))
    else:
        for i, line in enumerate((logos[system.distro][logo]).splitlines()):
            click.echo("{}".format(line + (info[i] if (i < len(info)) else "")).format(**colors.colors))

