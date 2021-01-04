# Comrade - Python Module
This folder stores the Python code on which the majority of Comrade operates. Runs on Python 3.8+.

It is written using `discord.py`, and houses several different modules:

## Folder Manifest

### `client`
Code for the Discord client running the bot

### `components`
Bot commands, and the code required to execute the commands; contains the bulk of the code for the bot

### `config`
Code for parsing the configuration file and making it visible to other modules

### `db`
Code for connecting to the two databases Comrade users, and interfaces with other modules

### `static`
Static (non-changing) assets which are used by the bot, such as a fancy text border which is used in the `news` command

### `utils`
Utility and convenience functions called upon by other parts of the bot

## Files in this Directory
### `cfg.ini`
User-editable configuration for the bot. This is parsed by the bot at runtime. Changes to the file require a bot restart to update.

### `main.py`
main program


# Self-Hosting Comrade
If you want to host Comrade on your own system, here an outline of what you need to do.

These steps are just a general outline; searching things up on the web is the best way to go for detailed information.

## 1. Discord Bot Account
We need to create an account for the bot to log into. This type of account is different from a regular Discord user account, made specifically for bots.

* Go to [the Discord Developer page](https://discord.com/developers/applications), and create a bot account.

* Save your **bot token** for step 3.

**Keep this bot token private; treat it as if it were your Discord password**.

* __Add the bot to your Discord server__. Make sure the bot has permissions to `read messages, send messages, embed links, attach files, create webhooks` at the very least.

## 2. Databases
Comrade uses two database services to operate. You need to supply login information for these two databases to the bot. Both of these services are free to use. The bot will set up these databases automatically once it connects to them.

### A) MongoDB
MongoDB is used for server-side configuration, and persisting information. It is critical to many core features of the bot.

* Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) and create an account, or login to your existing account.
* Create a **Project** on which you will have a cluster
* Create a **Cluster** on which you will host your database (Comrade is designed to work within the limits of the Free Tier M0 Cluster plan)
* Create a database on the cluster.
* Obtain the **connection string** for your database, and save it for step 3. (Don't forget to include your password)

**Keep this connection string private; treat it as if it were your bank login**.

### B) Google Cloud Storage
Google Cloud Storage is used for the emotes system.

* Go to [Google Cloud Storage](https://console.cloud.google.com/storage/). Sign up for an account if you don't already have one (it's free, just need a credit card of some sort)
* Create a **Project**.
* Create a [Service Account](https://cloud.google.com/docs/authentication/getting-started) and download the **JSON key file**. Save the contents of this file for step 3.

**Keep this file private; treat it as if it were your bank login**.

## 3. Create the .env file
Comrade has a method of loading private data, using a file called `.env`. In the same folder as this file (`src/Comrade`), create a file called `.env`.

Make the following entries in your file:
* TOKEN = \<discord token>
* MONGOKEY = \<MongoDB Connection string>
* GC = \<JSON String>

It should have the form:
```
TOKEN = AbC1234.....
MONGOKEY = mongodb+srv://.....
GC = {"type": "service_account","project_id":.......}
```

## 4. Install Dependencies
In the root folder of the Git repository, run:
```
pip install -r requirements.txt
```
and let things install.

## 5. Start the Bot
You can now start the bot by running
```
python main.py
```

## 6. First-Time Setup (Optional)
Once the bot has started up, you can do some things to configure the bot for your server. However, this is not required for the bot to work properly.

### Channel Mappings
Comrade relies on the server owner to feed text channels into Comrade for some of its funtionality. This includes:
- announcements-channel: A place for the bot to make daily announcements
- log-channel: A place for the bot to log internal status
- meme-channel: A place in which all newly posted image or videos are "reviewed"
- png-channel: A channel to spawn pngs
- vault-channel: A place where users can vote to "pin" a message. Make this restricted such that only Comrade can post.
- custom-channel-group: (Optional) category under which custom channels can be created

You can set them using the command
```
setchannel <channel name> <channel mention>
ex. $c setchannel "vault-channel" #meme-vault
```

## Hosting the Bot Externally
You can also host Comrade externally on sites like repl.it. As an example, you can look at the repl I set up [here](https://repl.it/@itchono/Comrade). repl.it also has a nice feature of keeping your `.env` file private.

Comrade features tools to automatically keep the repl alive (repl.it tries to kill your code if it is running for too long)

