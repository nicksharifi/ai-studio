from .channel import Channel


class TikTokChannel(Channel):
    __mapper_args__ = {
        "polymorphic_identity": "tiktok",
    }


if __name__ == "__main__":
    from .session import make

    db_session = make()
    all_channel = db_session.query(TikTokChannel).all()
    print(all_channel)
    db_session.close()

