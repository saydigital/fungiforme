from discord import Embed


def has_gif_element(message):
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
    if has_gif_element(message) \
            and message.reference \
            and original_message \
            and message.reference.message_id == original_message.id:
        if has_gif_element(original_message):
            # users cannot reply to another GIF
            return False
        elif original_message.author == message.author:
            # users cannot reply to their own messages
            return False
        else:
            return True
    else:
        return False
        

def is_valid_gif_message(message, original_message):
    if is_valid_reply_gif(message, original_message) and message.reactions:
        return True
    else:
        return False


def get_message_gif_url(message):
    if message.embeds and message.embeds[0].type == 'gifv':
        return message.embeds[0].thumbnail.url
    elif message.attachments and message.attachments[0].filename.lower().endswith('.gif'):
        return message.attachments[0].url
    else:
        return Embed.Empty
