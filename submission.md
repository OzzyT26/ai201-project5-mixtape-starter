# Codebase Map

## Main Files

### app.py

**Module Responsibility**
Creates and configures the Flask application. It initializes the database, loads the application's configuration, registers all route blueprints, and creates the database tables when the application starts.

**Main Functions**
create_app(config=None) -> Flask

Creates and configures the Flask application using the application factory pattern.

### models.py

**Module Responsibility**

**Main Functions**
generate_uuid()

Creates a unique string ID for new database records.

**Association Table Descriptions***

- friendships: Represents friendships between users. Connects one user to another user. Supports a many-to-many relationship.
- song_tags: Represents tags attached to songs. Connects songs and tags. Supports a many-to-many relationship between Song and Tag.
- playlist_entries: Represents songs inside playlists. Connects playlists and songs. Stores each song's playlist position. Stores who added the song. Stores when the song was added.

**Association Table Schemas**

friendships

| Column      | Type         | Constraints / Meaning                 |
| ----------- | ------------ | ------------------------------------- |
| `user_id`   | `String(36)` | Primary key; foreign key to `user.id` |
| `friend_id` | `String(36)` | Primary key; foreign key to `user.id` |


song_tags

| Column    | Type         | Constraints / Meaning                 |
| --------- | ------------ | ------------------------------------- |
| `song_id` | `String(36)` | Primary key; foreign key to `song.id` |
| `tag_id`  | `String(36)` | Primary key; foreign key to `tag.id`  |


playlist_entries

| Column        | Type         | Constraints / Meaning                     |
| ------------- | ------------ | ----------------------------------------- |
| `playlist_id` | `String(36)` | Primary key; foreign key to `playlist.id` |
| `song_id`     | `String(36)` | Primary key; foreign key to `song.id`     |
| `position`    | `Integer`    | Required; stores song order in playlist   |
| `added_by`    | `String(36)` | Required; foreign key to `user.id`        |
| `added_at`    | `DateTime`   | Defaults to current UTC datetime          |

**Model Classes**
User - Represents an app user.
Stores:
-username
-email
-listening streak
-last listened timestamp
-created timestamp
Relationships include:
-shared songs
-ratings
-listening events
-notifications
-playlists
-friends

Tag - Represents a song tag.
Stores:
-tag ID
-tag name

Song - Represents a shared song.
Stores:
-title
-artist
-album
-genre
-user who shared it
-share timestamp
-optional share note
Relationships include:
-ratings
-listening events
-tags

ListeningEvent - Represents a user listening to a song.
Stores:
-user ID
-song ID
-listened timestamp

Rating - Represents a user rating a song.
Stores:
-user ID
-song ID
-score
-rated timestamp
-It also has a uniqueness rule so the same user can only have one rating per song.

Playlist - Represents a playlist.
Stores:
-playlist name
-creator user ID
-created timestamp
-whether it is collaborative
Relationships include:
-songs through playlist_entries

Notification: Represents a user notification.
Stores:
-recipient user ID
-notification type
-message body
-created timestamp
-read/unread status

### seed_data.py

**Module Responsibility**

This module populates the local database with realistic test data so the app has users, songs, friendships, playlists, listening events, ratings, tags, and notifications to work with during development.

**Main Functions**

seed() - Resets and repopulates the database.

## Routes

### routes/feed.py

API Surface
| HTTP Method | Endpoint | Purpose | Service Function Called |
| GET | /feed/<user_id>/listening-now | Returns the user's "Friends Listening Now" feed, including each friend's most recent listening activity. | get_friends_listening_now(user_id) |
| GET | /feed/<user_id>/activity | Returns the user's general activity feed containing recent listening events from friends. | get_activity_feed(user_id) |

### routes/playlists.py

API Surface
| HTTP Method | Endpoint | Purpose | Service Function Called |
| POST | /playlists/ | Create a new playlist. | create_playlist(name, created_by, is_collaborative) |
| GET | /playlists/<playlist_id> | Retrieve a playlist's metadata. | get_playlist(playlist_id) |
| GET | /playlists/<playlist_id>/songs | Retrieve the ordered list of songs in a playlist. | get_playlist_songs(playlist_id) |
| POST | /playlists/<playlist_id>/songs | Add a song to a playlist. | add_to_playlist(playlist_id, song_id, added_by) |

### routes/songs.py

API Surface
| HTTP Method | Endpoint | Purpose | Service Function Called |
| GET | /songs/search?q=<query> | Search for songs by title or artist. | search_songs(query) |
| GET | /songs/<song_id> | Retrieve the details of a specific song. | get_song(song_id) |
| POST | /songs/<song_id>/rate | Submit or update a user's rating for a song. | rate_song(user_id, song_id, score) |
| POST | /songs/<song_id>/listen | Record that a user listened to a song and update their listening streak. | record_listening_event(user_id, song_id) |


## Services

### feed_service.py

**Module Responsibility**

This module is responsible for building the app’s feed-related views, especially:
- Friends Listening Now
- General friend activity feed

**Main Functions**

- get_friends_listening_now(user_id: str) -> list[dict]: Returns a list of the current user’s friends who listened to something recently.
- get_activity_feed(user_id: str, limit: int = 20) -> list[dict]: Returns a broader feed of recent listening events from the user’s friends.

### notification_service.py

**Module Responsibility**

This module is responsible for creating, updating, and retrieving user notifications. It handles notifications related to interactions with shared songs, along with notification read status.

**Main Functions**

- create_notification(user_id: str, notification_type: str, body: str) -> Notification: Creates a new notification for a user.
- add_to_playlist(playlist_id: str, song_id: str, added_by_user_id: str) -> None: Handles the event where a user adds a song to a playlist.
- rate_song(user_id: str, song_id: str, score: int) -> Rating: Creates or updates a user’s rating for a song.
- get_notifications(user_id: str, unread_only: bool = False) -> list[dict]: Retrieves notifications for a user.
- mark_as_read(notification_id: str) -> None: Marks a notification as read.

### playlist_service.py

**Module Responsibility**

This module is responsible for playlist-related database logic. It handles creating playlists, retrieving playlist metadata, retrieving songs inside a playlist, and getting all playlists created by a specific user.

**Main Functions**

- create_playlist(name: str, created_by_user_id: str, is_collaborative: bool = True) -> Playlist: Creates a new playlist.
- get_playlist_songs(playlist_id: str) -> list[dict]: Returns the songs in a playlist.
- get_playlist(playlist_id: str) -> dict: Returns playlist metadata without the song list.
- get_user_playlists(user_id: str) -> list[dict]: Returns all playlists created by a specific user.

### search_service.py
**Module Responsibility**

This module is responsible for song search and retrieval. It provides functions for searching songs by title or artist and for retrieving the details of a single song.

**Main Functions**

- search_songs(query: str) -> list[dict]: Searches for songs whose title or artist matches a given search string.
- get_song(song_id: str) -> dict: Retrieves a single song by its ID.

### streak_service.py

**Module Responsibility**

This module is responsible for recording when users listen to songs and maintaining each user’s listening streak.

A listening streak is based on consecutive calendar days where the user listened to at least one song.

**Main Functions**

- record_listening_event(user_id: str, song_id: str) -> ListeningEvent: Records that a user listened to a song.
- update_listening_streak(user: User, now: datetime) -> None: Updates a user’s listening streak based on their previous listening date.
- get_streak(user_id: str) -> int: Returns a user’s current listening streak.


# Example Data Flows

## User Rates A Song

User sends POST request to /songs/<song_id>/rate
→ routes/songs.py rate(song_id) receives the request
→ route reads JSON body
→ route extracts user_id and score
→ route checks that user_id and score are present
→ route calls notification_service.rate_song(user_id, song_id, int(score))
→ rate_song() validates that score is between 1 and 5
→ rate_song() retrieves the Song by song_id
→ rate_song() retrieves the User by user_id
→ rate_song() checks whether this user already rated this song
→ if rating exists, update existing score
→ if rating does not exist, create a new Rating record
→ commit database changes
→ return Rating instance to route
→ route converts rating to dict
→ route returns rating JSON with status 201

## User Creates A Playlist

User sends POST request to /playlists/
→ routes/playlists.py create() receives the request
→ route reads JSON body
→ route extracts name, created_by, and is_collaborative
→ route checks that name and created_by are present
→ route calls playlist_service.create_playlist(name, created_by, is_collaborative)
→ create_playlist() retrieves the creating User by created_by_user_id
→ if user does not exist, raise ValueError
→ create_playlist() creates a new Playlist record
→ add Playlist to database session
→ commit database changes
→ return Playlist instance to route
→ route converts playlist to dict
→ route returns playlist JSON with status 201

## User Searches For A Song

User sends GET request to /songs/search?q=<query>
→ routes/songs.py search() receives the request
→ route reads the q query parameter
→ route checks that q is present
→ route calls search_service.search_songs(query)
→ search_songs() queries the Song table
→ search_songs() matches songs where title or artist contains the query string
→ matching is case-insensitive
→ search_songs() converts each matching Song to a dictionary
→ route receives the list of song dictionaries
→ route returns JSON with results and count

# Root Cause Analyses

## Bug #1

**Issue number and title**

Issue Number: 1
Title: My listening streak keeps resetting

**How you reproduced it**

I ran the test_streaks.py tests and saw that the test_streak_increments_on_sunday test failed.  All of the other tests including test_streak_starts_at_1_for_new_user, test_streak_increments_on_consecutive_day, test_streak_does_not_double_count_same_day, and test_streak_resets_after_skipped_day passed.

The failing test first grabs a test user from the database and creates one datetime for Saturday and one for Sunday. The test then calls update_listening_streak with the test user and the datetime created for Saturday.  It runs a test asserting that the listening streak should be 1 for the test user, and the test passes.

However, when update_listening_streak is called for the test user and the datetime for Sunday, and the test asserts that the listening streak should be 2,  the test fails and the terminal feedback for the test case states that the number returned by listening_streak is 1. 

What this means: It appears the listening_streak has reset to 1.
Conditions: This happens when the second day of a listening streak occurs on a Sunday.

**How you found the root cause**

From the test, it is clear that the update_listening_streak function is responsible for updating the listening streak, so I first investigated there. I opened streak_service.py and examined the update_listening_streak function. I read the docstring to confirm the functions intended behavior. I noted that the docstring doesn’t specify any different logic for streaks involving Sundays.

I read the intended behavior in the docstring and found the section that handles each specification to see if it matches.  The doc string states “If the user listened yesterday: streak increments by 1”. Lines 73-74 appear to attempt to implement this logic, but line 73 contains an additional condition that the docstring didn’t specify. Line 73 also requires that the user listened yesterday, but also requires that today is not Sunday:

Line 73: elif days_since_last == 1 and today.weekday() != 6:

**The root cause**

The update logic in streak_service.py’s update_listening_streak is incorrect. The doc string specifies, “If the user listened yesterday: streak increments by 1”, however, in line 73 of the code implemented conditions are “if a user listened yesterday and today is not Sunday: streak increments by 1."

Lines 73 - 74:

elif days_since_last == 1 and today.weekday() != 6:
        user.listening_streak += 1

**Your fix and side-effect check**

I removed the extra condition today.weekday() != 6 on line 73. This fixes the root cause, because, according to the test suite, the bug was appearing when Sunday was the second day in the streak. This condition was causing the streak count to not increment on Sundays. 

Before: 

elif days_since_last == 1 and today.weekday() != 6:
        user.listening_streak += 1

After:

elif days_since_last == 1:
        user.listening_streak += 1

To confirm that there weren’t any side effects caused by the change, I reran the test_streaks.py test suite. Now, all 5 tests  are passing, so no other branches of the listening streak logic were affected.
