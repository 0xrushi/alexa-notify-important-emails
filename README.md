# Alexa AI for reminding important emails and reminders

## Motivation :-

It was the third time I missed reading my email and picking up shifts for my oncampus job. I did try creating labels and filtering them but that didn't show any progress in improvement. It's really stressful when I get the notification that something needs a response from me right away. I had to make sure that I was not missing this next time. It is then when I decided I need to build a system to process and remind me this.

### High level view:-

- Create a rule in your work email to filter out the emails by text content/subject/sender's email and forward it to a personal email address
- The rule should look something like 

![2021-12-19_18-04](https://user-images.githubusercontent.com/6279035/146694347-2c18cb5e-7493-4b09-a2b8-8a1908995dba.png)

- Create a rule in the personal email address to add a label to those emails. eg. I labelled as (RSO).
- Parsing and cleaning of the emails with the assigned labels :-)

## Setting up alexa_remote_control.sh (secrets.yaml)

The alexa request is based on https://github.com/walthowd/ha-alexa-tts,
There is a minor change make sure to add these https://github.com/rushic24/ha-alexa-tts/commit/e9b145a01c0792b82076554579fc46e6b60a3347 if you want to try that script. I have aleady included that in this repo.

Add your login credentials to the `homeassistant/secrets.yaml` file, with the keys alexa_email and alexa_password. I have kept a template to make those changes.

Run the script interactively to pull your devices:

`./alexa_remote_control.sh -a`

And set that in `ALEXA_DEVICE_NAME` in `reademails.py`

If login fails look at `/tmp/.alexa.login`. Search for "password" and see if you are being prompted for the captcha. If so, you can attempt to login to Alexa manually from a browser (from the same IP) and see if that fixes the issue for you. It never did for me, so I logged in to https://alexa.amazon.com with Chrome and used the cookies.txt 

[Chrome cookies downloader extension](https://chrome.google.com/webstore/detail/cookiestxt/njabckikapfpffapmjgojcnbfjonfjfg?hl=en) \
[Firefox cookies downloader extension](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/)

to export my amazon cookies to /tmp/.alexa.cookie. Other individuals have reported success using the same procedure, but only when using Firefox.

Once you have `./alexa_remote_control.sh -a` returning your devices you can test TTS by running:

``` {bash}
./alexa_remote_control.sh -d "My Dot Name" -e speak:This_is_a_test!
```

**Note:** When trying out this script make sure to change the home directory (`HOME="/home/dockerpi"` to your home) in `alexa_remote_control.sh`, and restore ie back to `HOME="/home/dockerpi"` and also place a copy of that cookies.txt in `cookies/cookies.txt` for using it inside docker.

## Setting up Gmail API credentials (credentials.json and token.pickle)  

[Go through this geekforgeeks link](https://www.geeksforgeeks.org/how-to-read-emails-from-gmail-using-gmail-api-in-python/) to set up Gmail API and downloading credentials.json. Use their template script to generate a **token.pickle** file. Move that to `homeassistant/token.pickle` for using in docker.

## Testing docker

Build and run the docker container to test if everything works

```{bash}
docker run --rm -it $(docker build -q .)
```

## Making the docker container as service

Create a service in ` /etc/systemd/system/docker.reademails.service ` with the template below

```{bash}
[Unit]
Description=read emails with RSO tag
After=docker.service
Requires=docker.service

[Service]
TimeoutStartSec=0
Restart=never
ExecStartPre=docker build -t reademails_docker /home/pi/Documents/alexa-notify-important-emails
ExecStart=docker run -t reademails_docker

[Install]
WantedBy=multi-user.target
```

### To start this service:-

`sudo systemctl start docker.reademails.service `

### To start this service at every boot:-

`sudo systemctl enable docker.reademails.service`

## Wrapping things up, before reaching this stage you might need to configure :-

- secrets.yaml
- cookies.txt
- credentials.json
- token.pickle
- HOME (only during generation of secrets/tokens)
- HOME (when creating a service)
- ALEXA_DEVICE_NAME, REFRESH_RATE, MAX_TIMES_REPEAT in `reademails.py`
- The label variable (RSOLabelid), you can add a print statement `print(labels)` at the line above and select label accordingly in `reademails.py`

```{python}
labels = service.users().labels().list(userId="me").execute()
RSOLabelid = list(filter(lambda x: x["name"] == "RSO", labels["labels"]))[0]["id"]
```

## See it in action :)

https://user-images.githubusercontent.com/6279035/146694731-f55ce539-a4ba-40ea-a0eb-b2236114d9c6.mp4

# Cool! isn't it? What's next?

## I don't like the voice of alexa, Lets build something like [CorentinJ Real-Time-Voice-Cloning](https://github.com/CorentinJ/Real-Time-Voice-Cloning) and get my emails read in Morgan Freeman's voice :D
