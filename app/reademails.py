"""
Source https://www.geeksforgeeks.org/how-to-read-emails-from-gmail-using-gmail-api-in-python/
"""

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os.path
import subprocess
import datetime
from time import sleep

# Define the SCOPES. If modifying it, delete the token.pickle file.
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
HOME = "/home/dockerpi"
ALEXA_DEVICE_NAME = "Rushi's Echo Dot"
# Check for emails every REFRESH_RATE mins
REFRESH_RATE = 15 
# Number of times to read the same email before it automatically marks it as read
MAX_TIMES_REPEAT = 3

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
shortdays = [x.lower()[:3] for x in days]


class WarningCounter:
    def __init__(self):
        self.counter = {}

    def add(self, key):
        if key in self.counter.keys():
            self.counter[key] = self.counter[key] + 1
        else:
            self.counter[key] = 0

    def get_count(self, key):
        return self.counter[key]


def getEmails():
    # Variable creds will store the user access token.
    # If no valid token found, we will create one.
    creds = None
    warning_counter = WarningCounter()

    # The file token.pickle contains the user access token.
    # Check if it exists
    if os.path.exists(f"{HOME}/.homeassistant/token.pickle"):

        # Read the token from the file and store it in the variable creds
        with open(f"{HOME}/.homeassistant/token.pickle", "rb") as token:
            creds = pickle.load(token)

    # If credentials are not available or are invalid, ask the user to log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                f"{HOME}/.homeassistant/credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=8000)

    # Save the access token in token.pickle file for the next run
    with open(f"{HOME}/.homeassistant/token.pickle", "wb") as token:
        pickle.dump(creds, token)

    # Connect to the Gmail API
    service = build("gmail", "v1", credentials=creds)

    labels = service.users().labels().list(userId="me").execute()
    RSOLabelid = list(filter(lambda x: x["name"] == "RSO", labels["labels"]))[0]["id"]

    while True:
        # request a list of all the messages
        # messages is a list of dictionaries where each dictionary contains a message id.
        messages = (
            service.users()
            .messages()
            .list(userId="me", labelIds=["UNREAD", RSOLabelid], maxResults=10)
            .execute()
            .get("messages", [])  # dict.get
        )

        # iterate through all the messages
        for msg in messages:
            if msg:
                warning_counter.add(msg["id"])
                # Get the message from its id
                txt = (
                    service.users().messages().get(userId="me", id=msg["id"]).execute()
                )

                # Use try-except to avoid any Errors
                try:
                    # Get value of 'payload' from dictionary 'txt'
                    payload = txt["payload"]
                    headers = payload["headers"]

                    # Look for Subject and Sender Email in the headers
                    for d in headers:
                        if d["name"] == "Subject":
                            subject = d["value"]
                        if d["name"] == "From":
                            sender = d["value"]
                    print("Subject: ", subject)
                    print("From: ", sender)
                    subjectwords = subject.lower().split(" ")
                    cleanlist = []
                    for word in subjectwords:
                        word = word.strip(".:")
                        if word == "wk":
                            cleanlist.append("week")
                        elif word == "fw":
                            pass
                        elif "/" in word:
                            num1 = word.split("/")[0]
                            strmonth = datetime.date(1900, int(num1), 1).strftime("%B")
                            num2 = word.split("/")[1] + "th"
                            cleanlist.append(strmonth + num2)
                        elif word == "due":
                            cleanlist.append(f"{word},")
                        elif len(word) == 3:
                            try:
                                cleanlist.append(f"{days[shortdays.index(word)]}.")
                            except:
                                cleanlist.append(word)
                        else:
                            cleanlist.append(word)

                    message = f'subject: {" ".join(cleanlist)}'
                    # print("message:", message)

                    # notify three times before marking as read
                    print(warning_counter.get_count(msg["id"]))
                    if warning_counter.get_count(msg["id"]) < MAX_TIMES_REPEAT:
                        subprocess.check_call(
                            args=[
                                'sh alexa_remote_control.sh  -d "%s" -e speak:"%s"'
                                % (ALEXA_DEVICE_NAME, message)
                            ],
                            shell=True,
                        )
                    else:
                        # mark email as read
                        service.users().messages().modify(
                            userId="me",
                            id=msg["id"],
                            body={"removeLabelIds": ["UNREAD", RSOLabelid]},
                        ).execute()
                        print("\n")
                except:
                    pass
                # sleep for (for and if) iteration
                sleep(8)
        # wait REFRESH_RATE mins
        sleep(60 * REFRESH_RATE)

getEmails()
