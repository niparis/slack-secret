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


@click.group()
@click.version_option(version=__version__)
@click.argument("token", type=str)
def main(token):
    global client
    client = WebClient(token=token)


@click.group()
def no_token():
    pass


@no_token.command(help="Shows version")
def version():
    print(__version__)


@main.command(help="save all users as json and download the images")
def save_users():
    from slack_secret.users import save_users

    save_users(client)


@main.command(
    help="Lists all the private channels that your token can access. You'll need the channel ID for any othe action"
)
def list_private_channels():
    from slack_secret.channels import list_private_channels

    list_private_channels(client)


@main.command(help="Downloads all the messages and images from the supplied channelID")
@click.argument("channel_id", type=str)
def save_private_channel(channel_id):
    from slack_secret.channels import save_private_channel

    save_private_channel(client, channel_id=channel_id)


@main.command(help="Downloads all the messages and images from all channels")
def save_all_private_channels():
    from slack_secret.channels import save_all_private_channels

    save_all_private_channels(client)


@main.command(help="Deletes all the messages and from the supplied channelID")
@click.argument("channel_id", type=str)
def delete_private_channel(channel_id):
    from slack_secret.channels import delete_private_channel

    delete_private_channel(client, channel_id=channel_id)


cli = click.CommandCollection(sources=[main, no_token])

if __name__ == "__main__":
    cli()
