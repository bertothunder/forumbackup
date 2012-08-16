forumbackup
===========

Get forum contents using a crawler

Description
===========

Designed initially for running it over our bikers forum in foroactivo.com, so the structure and items have been adapted specifically to the ones from foroactivo structure. 

It will emulates an admin user from the forum, parsing the entire forum and making a backup in a postgreSQL database, by performing next steps:

- Open forum's main page
- Login in the forum as admin by filling in the login form and submit
- A redirection (302) status code is expected and handled as login was fine.
- Open again main form, this time as admin user.
   - Retrieve list of sections (main sections in the forum): name/description and relative url (/f2-xxxxx) of each section
   - Retrieve admin TID (internal field from foroactivo) as this will be used later.
- For each section retrieved:
   - Open that section URL.
   - Retrieve all the threads within given section: description, owner, url
     Foroactivo is paging all the threads in groups of 50 each page. This shall be handled.
   - For each message in section:
     - Open its URL.
     - Get all the posts inside the thread
       foroactivo is paging all the posts in groups of 15 each page. This shall be handled.
     - In order to achieve a correct backup, users involved must be saved as well. So for each user we will check its page as administrator, saving information like number of messages, experience, name, nick, e-mail, etc. etc. Then the post will be linked to this user.

All this information must be saved in the SQL database by using std SQL commands (INSERT, DELETE, UPDATE).

Running
=======

You must have installed python 2.4+ (not v3!) runtime environment, as well as mechanize and BeautifulSoup libraries

A file with name ".credentials" (without the "s) must be created in the same place as the executable (backup.py). This will have one or more sections (each one for a forum):

[forumname]
username=<admin_username>
password=<admin_password>
url=<forum_general_url>

You can find a ready-to-setup credentials file in the source code, just fill it in and change its name to .credentials. Credentials file has been added to .gitignore, so you will be sure your sensible data won't be commited to git by accident.

TO run the backup application, just do:

python backup.py <forumname> <--- Must fit with the forumname in the credentials file!

