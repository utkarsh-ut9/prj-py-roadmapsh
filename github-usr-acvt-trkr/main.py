import os
import sys
import requests
import json
import datetime

TERMINAL_COLS = os.get_terminal_size().columns

def requestAPI(username):
    URL = f'https://api.github.com/users/{username}/events'
    response = requests.get(URL, timeout=10)
    status_code = response.status_code

    if status_code != 200:
        return [], status_code, response.json().get('message', 'Unknown error occurred.')

    jsonData = response.json()
    event_msg = []

    for event in jsonData:
        event_type = event['type']
        created_at = event['created_at']
        repo_name = event['repo']['name']
        dt = datetime.datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
        created_at = dt.strftime("%d-%m-%Y %I:%M:%S %p")

        match event_type:
            case 'IssueCommentEvent':
                event_msg.append(f"{created_at} : Commented on issue {event['payload']['issue']['number']}")
            case 'PushEvent':
                event_msg.append(f"{created_at} : Pushed to {repo_name}")
            case 'IssuesEvent':
                event_msg.append(f"{created_at} : Created issue {event['payload']['issue']['number']}")
            case 'WatchEvent':
                event_msg.append(f"{created_at} : Started watching {repo_name}")
            case 'ForkEvent':
                event_msg.append(f"{created_at} : Forked repository {repo_name}")
            case 'PullRequestEvent':
                event_msg.append(f"{created_at} : Created pull request {event['payload']['pull_request']['number']}")
            case 'PullRequestReviewEvent':
                event_msg.append(f"{created_at} : Reviewed pull request {event['payload']['pull_request']['number']}")
            case 'PullRequestReviewCommentEvent':
                event_msg.append(f"{created_at} : Commented on pull request {event['payload']['pull_request']['number']}")
            case 'CreateEvent':
                event_msg.append(f"{created_at} : Created {repo_name}")
            case _:
                event_msg.append(f"{created_at} : Other event type -> {event_type}")

    with open('logs.log', 'a') as logfile:
        logfile.write(json.dumps(jsonData, indent=4, sort_keys=True))

    return event_msg, status_code, None

def main():
    
    if len(sys.argv) != 2:
        print("Please provide a GitHub username as a command line argument.")
        sys.exit(1)


    user = sys.argv[1].lower().strip()
    events, status_code, msg = requestAPI(user)


    if status_code == 200:
        header = f" GITHUB USER ACTIVITY TRACKER for '{user}' "
        border_length = TERMINAL_COLS - len(header) - 2 

        print("-" * (border_length // 2) + header + "-" * (border_length // 2))

        for idx, evnt in enumerate(events):
            print(f'{idx + 1} - {evnt}')

        print("-" * TERMINAL_COLS)

    else:
        print(f'Error occurred while fetching data -> {status_code}: {msg}')

if __name__ == "__main__":
    main()
