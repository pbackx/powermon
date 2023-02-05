# Powermon

## Deployment

Currently, there is no Docker image built for this add-on. To test it out on a Home Assistant OS 
installation:

1. Copy the `powermon` folder to `/addons` on your Home Assistant OS installation. 
2. Go to the Home Assistant Add-on store.
3. Click on the plugin and install it.


## Development

For development purposes, you can copy changes to your Home Assistant server and rebuild the add-on. 
While this works, it is not a very optimal or convenient way to develop.

It is easier to run both the Flask development server and the Create-React-App development server on the
machine you do your development on and connect it to your Home Assistant installation.

### Python aiohttp backend

1. Create a new Python virtual environment.
2. Activate the environment.
3. `cd powermon-backend`
4. Create a .env file with the following contents:

   ```
   CORS_ORIGINS=http://localhost:3000
   SUPERVISOR_TOKEN=<your Home Assistant Supervisor token>
   WEBSOCKET_URL=ws://homeassistant.local:8123/api/websocket
   HA_CORE_API_URL=http://homeassistant.local:8123/api
   POWER_SENSOR=sensor.power_consumption
   DATABASE_FILE=powermon.db
   POWER_AVERAGE_OUT=sensor.powermon_power_average
   POWER_PEAK_OUT=sensor.powermon_power_peak
   ```

5. Install the requirements with `pip install -r requirements.txt`.
6. Run the aio HTTP server with `python powermon.py`.

The supervisor token is a long-lived access token that you can create on your Home Assistant profile page,
by default this is at the bottom of the following page: http://homeassistant.local:8123/profile.

### React frontend

1. Install Node.js and NPM (current development is done using 19.2.0 and 8.19.3, but a wide range of versions should work).
2. `cd powermon-frontend`
3. Install the dependencies with `npm install`.
4. `npm run start`.

A browser window should open with the React development server running. If not, you can access it at `http://localhost:3000`.

### Building and running the Docker image locally

Home Assistant sets the BUILD_FROM environment variable when building the Docker image, so you must specify it:

   docker build -t powermon:local --build-arg BUILD_FROM="homeassistant/amd64-base:latest" .
   docker run --rm -p 8099:8099 --env-file powermon-backend/.env --name powermon powermon:local
 
### Accessing the database on Home Assistant

The database is stored in `/data/powermon.db` on the Home Assistant installation. However this file is inside the
Powermon container, which is not easily accessible.

One option is to make a backup of the add-on and extract the database file from the backup. This is not very convenient
and takes quite a bit of time. However, it is always available and does not require specific permissions.

Another option is to enter the container and access the database directly. This can only be done using an SSH connection
to the Home Assistant Operating System. This does not work through an SSH add-on, but via the 'debug' SSH connection:
https://developers.home-assistant.io/docs/operating-system/debugging/

When this is setup, the easiest procedure is to:

1. Add the remote host to your SSH config file (usually `~/.ssh/config`):
   ```
   Host haroot
       HostName homeassistant.local
       User root
       Port 22222
   ```

2. Create a Docker context for the remote host:
   ```
   docker context create haroot --docker "host=ssh://haroot"
   ```

3. Copy the file using the context:
   ```
   docker --context haroot cp addon_local_powermon:/data/powermon.db ./powermon_remote.db
   ```

If you want to make changes to the database, you can use the above command to copy in the other direction.
However, be careful since the addon is probably running and may have already changed the database.

