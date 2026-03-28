import os
import re
import urllib.request
import json

USERNAME = "algorithnicmind"
TOKEN = os.environ.get("GITHUB_TOKEN")

query = """
{
  user(login: "%s") {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            contributionCount
            weekday
          }
        }
      }
    }
  }
}
""" % USERNAME

req = urllib.request.Request(
    'https://api.github.com/graphql',
    data=json.dumps({'query': query}).encode('utf-8'),
    headers={'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'}
)

try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode('utf-8'))
except Exception as e:
    print(f"Error checking GitHub API: {e}")
    exit(1)

calendar = data['data']['user']['contributionsCollection']['contributionCalendar']
weeks = calendar['weeks']

day_counts = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 0:0}

for week in weeks:
    for day in week['contributionDays']:
        day_counts[day['weekday']] += day['contributionCount']

day_names = {1:"Monday", 2:"Tuesday", 3:"Wednesday", 4:"Thursday", 5:"Friday", 6:"Saturday", 0:"Sunday"}

total = sum(day_counts.values()) or 1

output = "```text\n📊 Weekly Contribution Activity (Last 365 Days)\n\n"

ordered_days = [1, 2, 3, 4, 5, 6, 0]

for day_idx in ordered_days:
    count = day_counts[day_idx]
    pct = (count / total) * 100
    blocks_count = int((pct / 100) * 25)
    bar = "█" * blocks_count + "░" * (25 - blocks_count)
    name = day_names[day_idx].ljust(10)
    count_str = f"{count} commits".ljust(13)
    output += f"{name} {count_str}   {bar}   {pct:5.1f}%\n"

output += "```"

with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

pattern = r"(<!-- START_SECTION:weekly_stats -->\n).*?(\n<!-- END_SECTION:weekly_stats -->)"
readme = re.sub(pattern, r"\1" + output + r"\2", readme, flags=re.DOTALL)

with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme)
