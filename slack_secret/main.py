import logging
import os

import click

from slack import WebClient

from . import __version__


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = None
OUTPUT_FOLDER = "output"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


@click.group(invoke_without_command=True)
@click.version_option(version=__version__)
@click.argument("token", type=str)
@click.pass_context
def main(ctx, token):
    ctx.ensure_object(dict)
    if ctx.invoked_subcommand is None:
        click.echo(__version__)
    else:
        click.echo(f"slacksecrets {__version__}")
        ctx.obj["client"] = WebClient(token=token)


####
# Users
###


@main.command(help="save all users as json and download the images")
@click.pass_context
def save_users(ctx):
    from slack_secret.users import save_users

    click.echo(f"Saving all users information.")
    save_users(ctx.obj["client"])


####
# Private Channels
###


@main.command(
    help="Lists all the private channels that your token can access. You'll need the channel ID for any othe action"
)
@click.pass_context
def list_private_channels(ctx):
    from slack_secret.channels import list_private_channels

    click.echo(f"Listing all private channels:")
    list_private_channels(ctx.obj["client"])


@main.command(help="Downloads all the messages and images from the supplied channelID")
@click.pass_context
@click.argument("channel_id", type=str)
def save_private_channel(ctx, channel_id):
    from slack_secret.channels import save_private_channel

    click.echo(f"Saving the private channel with id {channel_id}")
    save_private_channel(ctx.obj["client"], channel_id=channel_id)


@main.command(help="Downloads all the messages and images from all channels")
@click.pass_context
def save_all_private_channels(ctx):
    from slack_secret.channels import save_all_private_channels

    click.echo(f"Saving all private channels")
    save_all_private_channels(ctx.obj["client"])


@main.command(help="Deletes all the messages and from the supplied channelID")
@click.pass_context
@click.argument("channel_id", type=str)
def delete_private_channel(ctx, channel_id):
    from slack_secret.channels import delete_private_channel

    click.echo(f"Deleting private channels with id {channel_id}")
    delete_private_channel(ctx.obj["client"], channel_id=channel_id)


####
# Instant Messages
###


@main.command(help="Lists all im ")
@click.pass_context
def list_all_im(ctx):
    from slack_secret.im import list_all_im

    click.echo(f"List all instant messages")
    list_all_im(ctx.obj["client"])


@main.command(help="Save a single im ")
@click.argument("username", type=str)
@click.pass_context
def save_single_im(ctx, username):
    from slack_secret.im import save_single_im

    click.echo(f"Saves a the instant messages conversation for {username} (text and images)")
    save_single_im(ctx.obj["client"], username)


@main.command(help="Saves all im, one folder for each conversation.")
@click.pass_context
def save_all_im(ctx):
    from slack_secret.im import save_all_im

    click.echo(f"Saves all instant messages conversations (text and images)")
    save_all_im(ctx.obj["client"])


@main.command(help="Deletes all of your messages in a single im ")
@click.argument("username", type=str)
@click.pass_context
def delete_single_im(ctx, username):
    from slack_secret.im import delete_single_im

    click.echo(f"Deletes instant messages conversations with {username}")
    delete_single_im(ctx.obj["client"], username)


if __name__ == "__main__":
    main()
