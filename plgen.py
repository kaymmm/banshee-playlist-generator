#!/usr/bin/env python

import sqlite3
from os.path import expanduser
from urllib.parse import unquote

home = expanduser('~')
db_file = home + '/.config/banshee-1/banshee.db'
path_repl = 'file://' + home + '/Music/'
path_playlists = home + '/Playlists/'
playlist_names = ['sync.m3u',
                  'rnb.m3u',
                  'jazz.m3u'
                  ]


common_filters = ["genre NOT LIKE '%rock%'",
                  "genre NOT LIKE '%alternative%'",
                  "genre NOT LIKE '%house%'",
                  "genre NOT LIKE '%pop%'",
                  "genre NOT LIKE '%metal%'",
                  "genre NOT LIKE '%electr%'",
                  "genre NOT LIKE '%dance%'",
                  "Rating > 2",
                  ]
date_filter = " AND (LastPlayedStamp IS NULL OR "\
    + " datetime(LastPlayedStamp,'unixepoch') "\
    + " <= datetime('now','-21 days')) "\
    + " AND (LastSkippedStamp IS NULL OR "\
    + " datetime(LastSkippedStamp, 'unixepoch') "\
    + " <= datetime('now', '-30 days')) "

db_and_cmd = ""
first = True
for filter in common_filters:
    if first:
        first = False
        db_and_cmd += filter
    else:
        db_and_cmd += " AND " + filter

or_filters = [(),
              ("genre LIKE '%r&b%'",
               "genre LIKE '%soul'",
               "genre LIKE '%funk%'"
               ),
              ("genre LIKE '%jazz%'",
               )]

track_limit = (300, 150, 150)

db_cmd_base = "SELECT Name, Title, Duration, Uri "\
    + "FROM CoreTracks "\
    + "LEFT JOIN CoreArtists "\
    + "WHERE "\
    + "CoreTracks.ArtistID=CoreArtists.ArtistID "\
    + "AND TrackID in ("\
    + "SELECT TrackID FROM CoreTracks WHERE "

db = sqlite3.connect(db_file)
c = db.cursor()

for j, playlist in enumerate(playlist_names):
    db_or_cmd = ""
    first_filter = True
    for filter in or_filters[j]:
        if first_filter:
            first_filter = False
            db_or_cmd = " AND (" + filter
        else:
            db_or_cmd += " OR " + filter
    if db_or_cmd:
        db_or_cmd += ") "
    db_sub_cmd = db_and_cmd + date_filter + db_or_cmd
    db_sub_cmd += " ORDER BY RANDOM() "
    db_sub_cmd += "LIMIT " + str(track_limit[j])
    db_cmd = db_cmd_base + db_sub_cmd + ");"

    c.execute(db_cmd)

    f = open(path_playlists + playlist_names[j], 'w')
    print("#EXTM3U", file=f)
    for artist, title, duration, uri in c:
        print("#EXTINF:" + str(int(duration/1000))
              + "," + artist + " - " + title, file=f)
        # print(unquote(uri.replace(path_repl, '')))
        print(unquote(uri.replace(path_repl, '')), file=f)
    f.close()

# :set ts=8 et sw=4 sts=4
