FROM python:3.10.1-bullseye

RUN pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
RUN apt update && apt install jq -y

ARG user=dockerpi

RUN adduser --home /home/$user  --disabled-password $user 

USER $user
RUN mkdir /home/$user/app
RUN mkdir /home/$user/.homeassistant

COPY ./app /home/$user/app
COPY ./homeassistant/* /home/$user/.homeassistant/
COPY ./cookies/cookies.txt /tmp/.alexa.cookie
COPY . .

WORKDIR /home/$user/app

CMD [ "python", "/home/dockerpi/app/reademails.py"]