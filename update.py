import requests
import time
import datetime
import dateutil.parser as dp
from os import environ
from dotenv import load_dotenv
load_dotenv()

def get_updates():
  FIGMA_PERSONAL_ACCESS_TOKEN = environ.get('FIGMA_PERSONAL_ACCESS_TOKEN')
  FIGMA_FILE_KEY = environ.get('FIGMA_FILE_KEY')
  FIGMA_API_URL = "https://api.figma.com/v1/files/" + FIGMA_FILE_KEY + "/versions"
  FIGMA_API_HEADERS = { 'X-FIGMA-TOKEN': FIGMA_PERSONAL_ACCESS_TOKEN }

  r = requests.get(url = FIGMA_API_URL, headers = FIGMA_API_HEADERS)
  data = r.json()
  print(data)
  versions = data["versions"]

  now = time.time()
  hours_in_seconds = 1 * 60 * 60

  # Filter out versions that were created more than 24 hours ago, or where the description is empty
  filter_function = lambda x: now - unix_time_from_iso8601(x['created_at']) < hours_in_seconds*24 and x['description'] is not None and len(x['description']) > 0
  todays_versions = list(filter(filter_function, versions))
    
  if len(todays_versions) > 0:
    message = format_message(todays_versions)
    post_message(message)

def format_message(todays_versions):
  date = datetime.datetime.today()
  message = "*Design library updates:* \n\n"

  for version in todays_versions:
    created_at = version["created_at"]
    label = version["label"]
    description = version["description"]
    user = version["user"]["handle"]

    message += "*" + label + "*\n"
    message += "_<!date^" + str(unix_time_from_iso8601(created_at)) + "^{time} {date_short_pretty}|" + created_at + "> by " + user + "_\n"
    message += description + "\n"
    message += "\n-----------\n\n"

  return message

def unix_time_from_iso8601(t):
    parsed_t = dp.parse(t)
    t_in_seconds = parsed_t.strftime('%s')
    return int(t_in_seconds)

def post_message(message):
  SLACK_TEAM_ID = environ.get('SLACK_TEAM_ID')
  SLACK_USER_ID = environ.get('SLACK_USER_ID')
  SLACK_CHANNEL_ID = environ.get('SLACK_CHANNEL_ID')
  SLACK_API_URL = "https://hooks.slack.com/services/" + SLACK_TEAM_ID + "/" + SLACK_USER_ID + "/" + SLACK_CHANNEL_ID

  data = { "text": message }
  r = requests.post(url = SLACK_API_URL, json = data)
  print(message)

get_updates()
