# surf

This is a set of Python classes designed to make surfing easy! Surfing as in surfing on Counter-Strike and other Valve GoldSrc/Source games.

It uses the SQLite database stored in `surf.db`. This will contain your choice of surf servers and maps along with their tier and your personal ratings of them.

A little knowledge of languages like Python and relational databases (you know, MySQL and stuff) will go a long way but hopefully you wont need any. Just remember that if you get stuck and want to get back to the "`>>>`" prompt, press `Ctrl+C`. Also, be careful: it's easy to lose track on what you're doing by using the up and down arrow keys!

## Getting started (Windows)

* If you don't have it already, download Python 2.7 from https://www.python.org/downloads/
* Ensure the path to `python.exe` is in your PATH environment variable
* Make a shortcut on your desktop of `run.bat`

## Getting started (other)

(This should work for Mac and Linux!)

* Create a shortcut to `run.sh`
* What's the likelihood you don't have Python installed and it's not in your `PATH`? Especially on Linux! :]

## Surf servers

### Editable fields on a server (defaults in parentheses):

* `nick' : str
* `addr' : str
* `port' : int (27015)

### Adding a server to your watch list:

    >>> srv = SourceServer.new("<server nickname>", "<server hostname/IP>", <port>)
    >>> srv.insert()

### Updating server details:

    >>> srv = SurfDb.getServer(<server id>)
    >>> srv.nick = "New nickname"
    >>> srv.addr = "<new hostname/IP>"
    >>> srv.port = <new port>
    >>> srv.update()

### Deleting a server:

    >>> srv = SurfDb.getServer(<server id>)
    >>> srv.delete()

## Maps

### Editable fields on a map (defaults in parentheses):

* `tier' : int (-1)
* `rating' : int (-1)
* `stages' : int (-1)
* `bonus' : int (-1)
* `complete' : bool (False)
* `favourite' : bool (False)

Note that map names are always converted to lower case whenever possible, i.e. when servers are pinged, the user enters a map name, *et cetera* as I so far believe the GoldSrc/Source engine does not care. Please let me know if this is not the case!

Also, **note that *maps* are keyed (uniquely identified) by their name**, not an integer ID like servers.

### Add a map:

    >>> m = SurfDb.getMap("surf_pyrism_njv")
    Map not found; returning defaults
    >>> m.rating = 10
    >>> m.tier = 5
    >>> m.insert()

Whenever you call `SurfDb.getMap()` on a map that isn't present in your database, the code will tell you that it is returning a `SurfMap` instance that has all its fields set to their defaults. It is on these maps that you should call `insert()` as opposed to `update()` as the latter is for maps that are *already* present in the database. An `insert()` in that case would result in a constraint error on the database due to duplicate keys (as the map already exists).

### Update a map:

    >>> m = SurfDb.getMap("surf_ez")
    >>> m.complete = True
    >>> m.rating = 1
    >>> m.update()

### Delete a map:

    >>> m = SurfDb.getMap("surf_jizznipples")
    >>> m.delete()
    Are you sure you want to delete map "surf_jizznipples" (y/n)? 

Anything other than a `y` or `Y` will stop the deletion.

## Server list

### One-time server list:

    >>> SurfDb.prettyPrint()

(or)

    >>> SurfDb.pp()

### Continuous monitoring:

    >>> SurfDb.monitor()

(or)

    >>> SurfDb.mon()

`SurfDb.monitor()` and `SurfDb.mon()` have an optional argument which is the delay between refreshes. The default is 180 seconds. Example view of a pretty print:

    ================================================================================================
     ID | Server                  | Game | Map                       | Tier | Rating | Comp  | Ping
    ====|=========================|======|===========================|======|========|=======|======
      0 | DHC                5/42 |  240 | surf_illumination    1/6  |    4 |     -1 | False |   40
    ----|-------------------------|------|---------------------------|------|--------|-------|------
      1 | KSF               27/60 |  240 | surf_kz_protraining 16/4  |    3 |      9 | True  |   90
    ----|-------------------------|------|---------------------------|------|--------|-------|------
      2 | KSF (Europe)      23/40 |  730 | surf_savant_njv      -/-  |    - |      - |   -   |   42
    ----|-------------------------|------|---------------------------|------|--------|-------|------
      3 | GFL               27/64 |  730 | surf_wood            -/-  |    - |      - |   -   |   39
    ----|-------------------------|------|---------------------------|------|--------|-------|------
      4 | KG #1             12/50 |  730 | surf_heaven         -1/-1 |   -1 |     -1 | False |   24
    ----|-------------------------|------|---------------------------|------|--------|-------|------
      5 | KG #2              8/32 |  730 | surf_heaven         -1/-1 |   -1 |     -1 | False |   27
    ----|-------------------------|------|---------------------------|------|--------|-------|------
      6 | KG #3             15/32 |  730 | surf_cubic           -/-  |    - |      - |   -   |   30
    ----|-------------------------|------|---------------------------|------|--------|-------|------
      7 | KG #4              3/32 |  730 | surf_sexyartz_njv    -/-  |    - |      - |   -   |   33
    ----|-------------------------|------|---------------------------|------|--------|-------|------
      8 | KG #5              2/32 |  730 | surf_mesa            1/0  |    1 |      9 | True  |   39
    ----|-------------------------|------|---------------------------|------|--------|-------|------
      9 | Publiclir.se #18  17/50 |  730 | surf_beginner        7/0  |    1 |      8 | True  |   58
    ----|-------------------------|------|---------------------------|------|--------|-------|------
     10 | Coolplay! T1-2    14/32 |  730 | surf_rebel_scaz_njv  1/0  |    1 |     10 | True  |   73
    ----|-------------------------|------|---------------------------|------|--------|-------|------
     11 | Coolplay! T3-4     0/32 |  730 | surf_catalyst_       -/-  |    - |      - |   -   |   65
    ----|-------------------------|------|---------------------------|------|--------|-------|------
     12 | Area of Gaming #1 15/24 |  730 | surf_fruits         10/1  |    2 |      9 | False |   33
    ================================================================================================

### Joining a server:

    >>> SurfDb.join(<server ID>)
    Joining server "XXX" (14/32)

### Joining a full server:

    >>> SurfDb.join(<server ID>)
    Server "XXX" is full (32/32)
    Listening for free space...........
    Space now available (31/32)

When a server is full, the library will rapidly ping the server (every 200ms by default) until it detects that there is at least one free slot available, at which point it will immediately attempt to join. Note that if the game is not running when this happens, the game will open before joining. If the server you aim to join is high-demand, launch the game before doing so or the time the game spends launching may lose you your free slot!

A general optimisation would be to add `-novid` to your launch options.
