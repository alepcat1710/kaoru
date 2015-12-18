# -*- coding: utf-8 -*-

"""
alfred.commands
~~~~~~~~

Command handlers

:copyright: (c) 2015 by Alejandro Ricoveri
:license: MIT, see LICENSE for more details.

"""

import envoy
from telegram import Updater
from . import utils
from . import log
from . import config


# /hello command
def _hello(bot, update):
    """a rather simple ping command"""

    chatter_name = update.message.from_user.first_name
    utils.echo_msg(
        bot, update,
        "Affirmative, {}. I read you. ".format(chatter_name)
    )

# /dryrun command
def _dryrun(bot, update):
    """toggle dry run mode"""
    config.set('dry_run', not config.get('dry_run'))
    if config.get('dry_run'):
        status = "ON"
    else:
        status = "OFF"
    utils.echo_msg(bot, update, "Dry run mode is {}".format(status))

# /lock command:
def _lock(bot, update):
    """
    it basically runs screenlock script resulting
    in the execution of i3lock
    """

    utils.echo_msg(bot, update, "Your screen(s) are now LOCKED")
    envoy.run('screenlock')

# /poweroff command:
def _poweroff(bot, update):
    """turn off your machine(s)"""

    if not config.get('queue_poweroff') and not config.get('queue_reboot'):
        utils.echo_msg(
            bot, update,
            "Your machines are to be shutdown in about {} minute(s)".format(
                config.get('time_poweroff')
            )
        )
        if not config.get('dry_run'):
            envoy.run('sudo shutdown -P +{}'.format(config.get('time_poweroff')))
        config.set('queue_poweroff', True)
    else:
        utils.echo_msg(
            bot, update,
            "Your machines are already going to be shutdown/rebooted"
        )


# /cancel command:
def _cancel(bot, update):
    """Cancel any pending reboot/poweroffs"""

    if not config.get('dry_run'):
        envoy.run("sudo shutdown -c")
    config.set('queue_reboot', False)
    config.set('queue_poweroff', False)
    utils.echo_msg(bot, update, "Operations cancelled")

# /reboot command:
def _reboot(bot, update):
    """reboot your machine(s)"""

    if not config.get('queue_poweroff') and not config.get('queue_reboot'):
        utils.echo_msg(
            bot, update,
            "I'm going to be rebooted in about {} minute(s)".format(
                config.get('time_reboot')
            )
        )
        if not config.get('dry_run'):
            envoy.run('sudo shutdown -r +{}'.format(config.get('time_reboot')))
        config.set('queue_reboot', True)
    else:
        utils.echo_msg(
            bot, update,
            "Your machines are already going to be shutdown/rebooted"
        )


def _unknown(bot, update):
    """default command handler"""

    chatter_name = update.message.from_user.first_name
    utils.echo_msg(
        bot, update,
        "I am sorry {}. I'm afraid I cannot do that ...".format(chatter_name)
    )

def register_commands(updater, dispatcher):
    """register each and every command this bot is going to process"""

    commands = [
        ('hello', _hello),
        ('lock', _lock),
        ('reboot', _reboot),
        ('poweroff', _poweroff),
        ('cancel', _cancel),
        ('dryrun', _dryrun),
    ]

    # register every command there is
    for command, fun in commands:
        dispatcher.addTelegramCommandHandler(command, fun)
        log.msg("/{}: command registered".format(command))

    # and the default one as well ...
    dispatcher.addUnknownTelegramCommandHandler(_unknown)
