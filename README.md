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

### Flask

1. Create a new Python virtual environment.
2. Activate the environment.
3. `cd powermon-backend`
4. Install the requirements with `pip install -r requirements.txt`.
5. Run the Flask development server with `flask --app powermon run`.

### React

1. Install Node.js and NPM (current development is done using 19.2.0 and 8.19.3, but a wide range of versions should work).
2. `cd powermon-frontend`
3. Install the dependencies with `npm install`.
4. `npm run start`.

A browser window should open with the React development server running. If not, you can access it at `http://localhost:3000`.