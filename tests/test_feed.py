"""
tests/test_feed.py — Mixtape

Regression tests for Friends Listening Now feed logic.
"""

import pytest
from datetime import datetime, timezone
from app import create_app, db
from models import User, Song, ListeningEvent, friendships
from services.feed_service import get_friends_listening_now


@pytest.fixture
def app():
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


def test_listening_now_does_not_include_yesterday_events(app, monkeypatch):
    """
    Friends Listening Now should only include friends who listened today,
    not friends whose most recent listen was yesterday.
    """
    import services.feed_service as feed_service

    fixed_now = datetime(2024, 6, 10, 0, 30, 0, tzinfo=timezone.utc)

    class FixedDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return fixed_now

    monkeypatch.setattr(feed_service, "datetime", FixedDatetime)

    with app.app_context():
        current_user = User(username="nova", email="nova@example.com")
        today_friend = User(username="darius", email="darius@example.com")
        yesterday_friend = User(username="simone", email="simone@example.com")

        db.session.add_all([current_user, today_friend, yesterday_friend])
        db.session.flush()

        db.session.execute(friendships.insert().values(
            user_id=current_user.id,
            friend_id=today_friend.id,
        ))
        db.session.execute(friendships.insert().values(
            user_id=current_user.id,
            friend_id=yesterday_friend.id,
        ))

        song = Song(
            title="Test Song",
            artist="Test Artist",
            shared_by=current_user.id,
        )
        db.session.add(song)
        db.session.flush()

        today_event = ListeningEvent(
            user_id=today_friend.id,
            song_id=song.id,
            listened_at=datetime(2024, 6, 10, 0, 20, 0, tzinfo=timezone.utc),
        )

        yesterday_event = ListeningEvent(
            user_id=yesterday_friend.id,
            song_id=song.id,
            listened_at=datetime(2024, 6, 9, 23, 45, 0, tzinfo=timezone.utc),
        )

        db.session.add_all([today_event, yesterday_event])
        db.session.commit()

        feed = get_friends_listening_now(current_user.id)

        returned_usernames = [item["friend"]["username"] for item in feed]

        assert "darius" in returned_usernames
        assert "simone" not in returned_usernames
        assert len(feed) == 1