# TODO list

This is a list where I document simple tasks that are easy to pick up and get going:

1. Debug issue with missing HA sensors -> it looks like this is working now
2. Improve legend on x-axis of graphs

# Doing

References:
* https://docs.python.org/3/library/sqlite3.html#sqlite3-tutorial
* https://towardsdatascience.com/do-you-know-python-has-a-built-in-database-d553989c87bd


# Backlog

Bigger tasks that need to be split in smaller items:

1. When restarting HA, it looks like the add-on tries to connect to the websocket too early. Some retry mechanism needs to be added.
2. Add logo and favicon
3. Package as a proper add-on
4. Reconnect to HA websocket when connection is lost