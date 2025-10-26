import logging

from db.channel import Channel
from db.youtube_channel import YouTubeChannel

# Optional platforms. These modules may not exist in older deployments.
try:
    from db.tiktok_channel import TikTokChannel
except Exception:
    TikTokChannel = None  # type: ignore

try:
    from db.instagram_channel import InstagramChannel
except Exception:
    InstagramChannel = None  # type: ignore

from publisher_youtube import PublisherYoutube

logger = logging.getLogger(__name__)


def create_publisher_for_channel(channel: Channel):
    """Return a Publisher instance suitable for the given Channel row.

    Falls back to None for unknown channel types so callers can skip gracefully.
    """
    if isinstance(channel, YouTubeChannel):
        return PublisherYoutube(channel.id)

    # Defer imports of platform publishers to avoid hard dependency explosions
    if TikTokChannel and isinstance(channel, TikTokChannel):
        from publisher_tiktok import PublisherTikTok

        return PublisherTikTok(channel.id)

    if InstagramChannel and isinstance(channel, InstagramChannel):
        from publisher_instagram import PublisherInstagram

        return PublisherInstagram(channel.id)

    logger.warning(f"No publisher available for channel id={channel.id}, type={type(channel)}")
    return None

