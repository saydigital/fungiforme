# Copyright 2022-TODAY Rapsodoo Italia S.r.L. (www.rapsodoo.com)
# # License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

from discord import Embed


CODE_BASE_URL = "https://github.com/saydigital/fungiforme"
ISSUE_BASE_URL = f"{CODE_BASE_URL}/issues"
ISSUE_NEW_URL = f"{ISSUE_BASE_URL}/new?"


def has_gif_element(message):
    """
    Returns True if the message has a gif element (embed or attach).
    """
    if message.embeds and message.embeds[0].type == 'gifv':
        has_embed_gif = True
    else:
        has_embed_gif = False

    if message.attachments and message.attachments[0].filename.lower().endswith('.gif'):
        has_attachment_gif = True
    else:
        has_attachment_gif = False

    return has_embed_gif or has_attachment_gif


def is_valid_reply_gif(message, original_message):
    """
    Returns True if the message is a valid GIF reply to an original message.
    """
    if has_gif_element(message) \
            and message.reference \
            and original_message \
            and message.reference.message_id == original_message.id:
        if has_gif_element(original_message):
            # users cannot reply to another GIF
            return False
        if original_message.author == message.author:
            # users cannot reply to their own messages
            return False
        return True
    return False


def is_valid_gif_message(message, original_message):
    """
    Returns True if the message is a valid GIF message.
    """
    if is_valid_reply_gif(message, original_message) and message.reactions:
        return True
    else:
        return False


def get_message_gif_url(message):
    """
    Returns the GIF URL of the message.
    """
    if message.embeds and message.embeds[0].type == 'gifv':
        return message.embeds[0].thumbnail.url
    if message.attachments and message.attachments[0].filename.lower().endswith('.gif'):
        return message.attachments[0].url
    return Embed.Empty
