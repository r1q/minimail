# Minimail

A simple webapp to manage your email campaigns and subscribers. Using AWS SES for mail delivery.

## Features

**List management:**

* Hosted newletter homepage
* Embed-able newsletter signup form
* Ajax friendly API to signup subscribers
* Confirmation via email for each new subscribers
* Import subscribers from Mailchimp CSV
* import subscriebrs from copy/pasting emails and names
* Unsubscribe/Delete subscribers 

**Email management:**

* Custom `Reply-To:` address
* Live HTML preview while writing or pasting the email content
* HTML email preview before sending
* Send test email before sending to the list
* Auto-CSS inlining for greated email client support
* Auto-minifying of HTML email to prevent cut message (gmail impose a length limit to emails)
* Auto-generation of text email from the HTML (keeping the links and heading hierarchies)
* Auto-generation/inclusion of an unsubscribe link for each email sent

## No-features:

    > Things Minimail will not provide for now
    
* Drag and drop HTML email builder (you’ll need to write or copy/paste your HTML email)

## Tech stack

* Python 3.5
* Django 1.10
* Twitter Bootstrap 3.3.7

For Python libraries in use, see `requirements.txt`.

## Setup dev env

1. `virtualenv --python=python3.5 . && source bin/activate`
2. `pip install -r requirements.txt`
3. `./manage.py makemigrations && ./manage.py migrate`
4. `./manage.py runserver`

## Setup prod env

1. `export MINIMAIL_ENV=prod`
2. `virtualenv --python=python3.5 . && source bin/activate`
3. `pip install -r requirements.txt`
4. `./manage.py makemigrations && ./manage.py migrate`
5. Start the app with gunicorn: `./server_conf/start_stop_django_app.sh`
6. Link the app nginx configuration file to nginx default conf folder: `sudo ln -s /path/to/repo/server_conf/minimail.nginx.conf /path/to/nginx/main/conf/minimail.nginx.conf`
7. Test and reload nginx: `sudo nginx -t && nginx -s reload`

## systemd

1. create the service description in `/etc/systemd/system/minimail.service`

```
[Unit]
Description=app
After=network.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=<your app directory>/minimail
ExecStart=<your app directory>/minimail/server_conf/start.sh

[Install]
WantedBy=multi-user.target
```

2. `sudo systemctl daemon-reload`
3. `sudo systemctl start minimail`
4. `sudo systemctl enable minimail` to launch minimail on startup

## Code syntax

### Python

Check for code syntax with `pylint -r no -f colorized minimail`. Add this command in `.git/hooks/pre-commit` to auto-check as you commit.

## Frontend framework

We use [Twitter Bootstrap](http://getbootstrap.com/customize/?id=8c2854b0c5b8e7607cea7f997c40c761), customized with system fonts.

## License

MIT License - Copyright (c) 2016 Julien Buty

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
