# TODO list

This is a list where I document simple tasks that are easy to pick up and get going:

1. Create script to start a SQLlite database and create a table for storing power data
2. Set up debug access so I can manipulate (=delete) the database if I need to https://developers.home-assistant.io/docs/operating-system/debugging/
3. Store power data in the database
4. Return stored data when powermon page is loaded


# Doing

1. Decide on DB tech and store energy usage

References:
* https://docs.python.org/3/library/sqlite3.html#sqlite3-tutorial
* https://towardsdatascience.com/do-you-know-python-has-a-built-in-database-d553989c87bd


# Backlog

Bigger tasks that need to be split in smaller items:

1. Use WebSocket API to capture and display current energy usage
   1. Limit the graph to only show the last hour (maybe make it configurable?)
2. Calculate 15 minutes power usage and expose as new sensor
3. Calculate peak power usage per month and expose as new sensor
4. Ask fiverr to design a nice favicon/logo for the project
