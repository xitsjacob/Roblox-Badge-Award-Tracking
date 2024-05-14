import asyncio
import json
import requests
from datetime import datetime
from dateutil import tz

from roblox import Client

USER_ID = "INSERT_RBLX_ID"
FILENAME = f"{USER_ID}_badges.json"

client = Client()

badges = []

async def grab_badges():
    url = f"https://badges.roblox.com/v1/users/{USER_ID}/badges"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    
    params = {"cursor": None, "limit": 100}
    
    while url:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            badges_data = response.json()
            for badge in badges_data["data"]:
                awarded_date = await date_format(badge["id"])
                badges.append({"badgeId": badge["id"], "badgeName": badge["name"], "dateAwarded": awarded_date})
                await asyncio.sleep(0.5)
            next_page_cursor = badges_data.get("nextPageCursor")
            params["cursor"] = next_page_cursor
            if not next_page_cursor:
                break
        else:
            print(f"Failed to fetch badges for user {USER_ID}. Status code: {response.status_code}")
            return None
    
    return badges

async def find_date(badge_id):
    user = await client.get_user(USER_ID)
    badge_data = client.get_base_badge(badge_id)
    awarded_data = await user.get_badge_awarded_dates([badge_data])

    return awarded_data
    

async def date_format(badge_id):
    try:
        date_time = await find_date(badge_id)

        awarded_date_str = str(date_time)
        # Extracting date and time from the given string
        awarded_date = awarded_date_str.split('=')[2].split()[0]  # Extracting '2024-04-29'
        awarded_time = awarded_date_str.split('=')[2].split()[1]  # Extracting '01:25:28.475657+00:00'

        # Remove timezone information
        awarded_time = awarded_time.split('+')[0]

        # Converting date and time strings into datetime object
        awarded_datetime = datetime.strptime(awarded_date + ' ' + awarded_time.split('.')[0], '%Y-%m-%d %H:%M:%S')

        # Converting datetime to the desired format
        formatted_awarded_datetime = awarded_datetime.astimezone(tz.gettz('EST')).strftime("[%B %d, %Y at %I:%M:%S %p %Z]")

        return formatted_awarded_datetime
    except Exception as e:
        print(e)

async def write_badges_to_file(badges, filename):
    user_data = await client.get_user(USER_ID)
    data_sets = {
        "user_id": int(USER_ID),
        "username": user_data.name,
        "display_name": user_data.display_name,
        "badges": badges
    }

    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data_sets, file, indent=4)

async def main():
    badges = await grab_badges()
    if badges:
        await write_badges_to_file(badges, FILENAME)
        print(f"User badges written to {FILENAME}")

asyncio.run(main())