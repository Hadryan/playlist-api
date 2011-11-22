 ... From rsms documents, forked by me 
https://raw.github.com/krakelin/playlist-api/master/README.md
...
## Outline

These are the currently available requests (we're still in the progress of
determining what the base URL should look like).

    GET /user/{username}/playlists/regular -> ordered list of {playlist}s
    GET /user/{username}/playlists/special/starred -> ordered list of {playlist}s
    GET /user/{username}/playlists/special/purchases -> ordered list of {playlist}s
    GET /playlist/{id} -> {playlist}

    POST /playlist <- {playlist}
    POST /playlist/{id}/add?index <- list of track URIs
    POST /playlist/{id}/move?src-index&count&dst-index
    POST /playlist/{id}/remove?index&count
    POST /playlist/{id}/collaborative?enabled
    POST /playlist/{id}/image <- image data
    POST /playlist/{id}/annotation <- text

Each request is described in detail in `API methods`.


## Error responses

As the API is restricted to HTTP we make use of the HTTP protocol when it comes
to error indication. The status of any HTTP response is represented by a
standard status code. The ranges are as follows:

See [Status Code Definitions, RFC 2616](http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html)
for further details.

The response entity of an error (unless in the case of "bodyless" responses, as
defined by [HTTP/1.1](http://www.w3.org/Protocols/rfc2616/rfc2616.html))
contains a simple human-readable message, primarily aiding development.

XSPF response:

    HTTP/1.1 400 Bad Request
    
    <error message="The foo argument is empty" />

JSON response:

    HTTP/1.1 400 Bad Request
    
    {"message":"The foo argument is empty"}


# API methods

---

## Querying playlists

### GET /user/{username}/playlists/regular -> ordered list of {playlist}s

Retrieve the list of regular playlists for a `user`.

**Authorization:** required

    GET /user/smedjan/playlists/regular.json

JSON response:

    {
      "playlists":[
        {
          "version": "XYZ123",
          "uri": "spotify:user:smedjan:playlist:6welunS19b7RD9lodXrhuG",
          "title": "Spotify playlist",
          "creator": "smedjan"
        }
        ...
      ]
    }

XSPF response:

    <?xml version="1.0" encoding="utf-8"?>
    <playlist xmlns="http://xspf.org/ns/0/" xmlns:sp="http://www.spotify.com/ns/music/1" 
        version="1" sp:version="4">
      <trackList>
        <track>
          <identifier>spotify:user:smedjan:playlist:6welunS19b7RD9lodXrhuG</identifier>
          <title>Spotify playlist</title>
          <creator>smedjan</creator>
        </track>
        ...
      </trackList>
    </playlist>


### GET /user/{username}/playlists/special/starred -> ordered list of {playlist}s

Retrieve `user`s special "Starred" playlist, containing all tracks a user have "starred".

**Authorization:** required, same owner

The response is the same as for any playlist.


### GET /user/{username}/playlists/special/purchases -> ordered list of {playlist}s

Retrieve `user`s special "Purchases" playlist, containing all tracks a user has purchased.

**Authorization:** required, same owner

The response is the same as for any playlist.


### GET /playlist/{id} -> {playlist}

Retrieve any playlist by identifier `{id}`.

**Authorization:** no


---

## Manipulating playlists

As we perform server-side merging of modifications, a modification request might
result in a few different status codes:

- `200 OK` -- Modifications applied and your version is the latest.

- `201 Created` -- The playlist was created.

- `205 Reset Content` -- The modification was accepted but resulted in a dirty state. See below for details.

You will *never* get a `409 Conflict`, since conflicts are resolved automagically.

**Modifications implying incorporation of remote edits:**

If a modification was accepted but resulted in a dirty state, you will get a
205 Reset Content response, indication your client should reload the playlist
from the server.

Example:

    > GET /playlists/xyz123
    # Some time passes and the playlist is modified by another client.
    > POST /playlists/xyz123
    < 205 Reset Content
    > GET /playlists/xyz123


### POST /playlist <- {playlist}

Create a new playlist as the authenticated user.

**Authorization:** required

**Request entity**:

A {playlist} object, except the `version` and `identifier` members should not be present.


### POST /playlist/{id}/add?index <- list of track URIs

Insert one or more tracks into playlist `{id}` at `{index}`.

**Authorization:** required, same owner or collaborator

- `index` -- The position in the list where to insert the tracks. Indices are 0-based.

**Request entity**:

List of tracks URIs

Example:

    POST /playlist/6welunS19b7RD9lodXrhuG/add?index=4
    Content-type: application/json
    
    ["spotify:track:5xft6jBZvMHRD1jyTDPQXx","spotify:track:1MD4tX2g5hx0D2WQ6JsC2m"]


### POST /playlist/{id}/move?src-index&count&dst-index

Move `{count}` tracks in playlist `{id}` from `{src-index}` to `{dst-index}`.

**Authorization:** required, same owner or collaborator

- `src-index` -- The start position of the tracks to move.
- `count` -- The number of tracks, starting at `src-index`, to move (or "select").
- `dst-index` -- The position where to move (or "land") the tracks, expressed in your versions coordinates.

Example -- move the first two tracks down past the next two tracks:

List before the modification:

    0: Track A
    1: Track B
    2: Track C
    3: Track D
    4: Track E

POSTing:

    POST /playlist/6welunS19b7RD9lodXrhuG/move?src-index=0&count=2&dst-index=2

List after the modification:

    0: Track C
    1: Track D
    2: Track A
    3: Track B
    4: Track E


### POST /playlist/{id}/remove?index&count

Remove `{count}` tracks from playlist `{id}` starting at `{index}`.

**Authorization:** required, same owner or collaborator

- `index` -- The start position of the tracks to remove.
- `count` -- The number of tracks to delete, starting at `index`.

Example -- remove the first two tracks:

List before the modification:

    0: Track A
    1: Track B
    2: Track C
    3: Track D
    4: Track E

POSTing:

    POST /playlist/6welunS19b7RD9lodXrhuG/remove?index=0&count=2

List after the modification:

    0: Track C
    1: Track D
    2: Track E


### POST /playlist/{id}/collaborative?enabled

Toggle collaborative mode for playlist `{id}`.

**Authorization:** required, same owner

- `enabled` -- `true` to enable other people to edit the contents of the playlist,
  or false to only allow the ower to edit the playlist.


### POST /playlist/{id}/image <- image data

Assign a custom image to playlist `{id}`.

**Authorization:** required, same owner

**Request entity**:

The image data. An empty request entity means "clear the image".

Example:

    POST /playlist/6welunS19b7RD9lodXrhuG/image
    Content-type: image/jpeg
    Content-length: 22355
    
    <JPEG data>


### POST /playlist/{id}/annotation <- text

Edit the free-text description of playlist `{id}`.

**Authorization:** required, same owner

**Request entity**:

UTF-8 encoded text.

Example:

    POST /playlist/6welunS19b7RD9lodXrhuG/annotation
    Content-type: text/plain
    Content-length: 21
    
    Latest French nu-jazz