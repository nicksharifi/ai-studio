from .channel import Channel


class YouTubeChannel(Channel):
    __mapper_args__ = {
        "polymorphic_identity": "youtube",
    }


if __name__ == "__main__":
    from session import make

    db_session = make()
    all_channel = db_session.query(YouTubeChannel).all()
    print(all_channel)
    # PublisherYoutube

    # Close the session
    db_session.close()
