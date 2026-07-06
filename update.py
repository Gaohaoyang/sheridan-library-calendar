#!/usr/bin/env python3
"""Refetch Sheridan Library activities from ActiveMississauga and rewrite
the data block in index.html (between /*__DATA_START__*/ and /*__DATA_END__*/).

Search filter: center 46 (Sheridan Library), ages 0-6, department 5 (Library).
Uses only the Python standard library.
"""
import json
import re
import html
import datetime
import time
import urllib.request
from pathlib import Path

BASE = "https://anc.ca.apm.activecommunities.com/activemississauga/rest"
SEARCH = {
    "activity_search_pattern": {
        "skills": [], "time_after_str": "", "days_of_week": None,
        "activity_select_param": 2, "center_ids": [46], "time_before_str": "",
        "open_spots": None, "activity_id": None, "activity_category_ids": [],
        "date_before": "", "min_age": 0, "date_after": "", "activity_type_ids": [],
        "site_ids": [], "for_map": False, "geographic_area_ids": [],
        "season_ids": [], "activity_department_ids": [5],
        "activity_other_category_ids": [], "child_season_ids": [],
        "activity_keyword": "", "instructor_ids": [], "max_age": 6,
        "custom_price_from": "", "custom_price_to": "",
    },
    "activity_transfer_pattern": {},
}


def call(url, body=None):
    req = urllib.request.Request(url, headers={
        "Accept": "application/json",
        "Content-Type": "application/json;charset=utf-8",
        "page_info": '{"order_by":"","page_number":1,"total_records_per_page":100}',
        "User-Agent": "Mozilla/5.0",
    }, data=json.dumps(body).encode() if body else None)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def clean(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def fetch():
    items = call(f"{BASE}/activities/list?locale=en-US", SEARCH)["body"]["activity_items"]
    out = []
    for li in items:
        aid = li["id"]
        d = call(f"{BASE}/activity/detail/{aid}?locale=en-US")["body"]["detail"]
        m = call(f"{BASE}/activity/detail/meetingandregistrationdates/{aid}?locale=en-US")
        pats = m["body"]["meeting_and_registration_dates"]["activity_patterns"]
        if len(pats) != 1 or len(pats[0]["pattern_dates"]) != 1:
            print(f"WARNING: {aid} {d['activity_name']} has an unusual pattern shape; "
                  f"check manually: {pats}")
        pat = pats[0]
        pd = pat["pattern_dates"][0]
        center = d["centers"][0]
        out.append({
            "id": aid,
            "name": d["activity_name"].strip(),
            "number": d["activity_number"],
            "desc": clean(d["catalog_description"]),
            "category": d["category"],
            "subCategory": d["sub_category"],
            "type": d["activity_type"],
            "ages": d["age_description"].strip().rstrip(","),
            "season": d["season_name"],
            "firstDate": d["first_date"],
            "lastDate": d["last_date"],
            "sessions": d["other_info"]["sessions"],
            "weekday": pd["weekdays"],
            "startTime": pd["starting_time"],
            "endTime": pd["ending_time"],
            "exceptions": pat["exception_dates"],
            "timeRange": li["time_range"],
            "spaceStatus": d["space_status"],
            "totalOpen": li["total_open"],
            "facility": d["facilities"][0]["name"] if d["facilities"] else "",
            "center": {
                "name": center["name"],
                "address": f"{center['address1']}, {center['city']}, "
                           f"{center['state']} {center['zip_code']}",
                "phone": center["phone"],
            },
            "url": li["detail_url"],
        })
        print(f"  {aid} {d['activity_name']}")
        time.sleep(0.3)
    return out


def main():
    page = Path(__file__).parent / "index.html"
    activities = fetch()
    today = datetime.date.today().isoformat()
    data_json = json.dumps(activities, ensure_ascii=False, separators=(",", ":"))
    block = (
        "/*__DATA_START__*/\n"
        f'const DATA_UPDATED = "{today}";\n'
        f"const ACTIVITIES = {data_json};\n"
        "/*__DATA_END__*/"
    )
    src = page.read_text()
    cur = re.search(r"const ACTIVITIES = (.*?);\n", src)
    if cur and cur.group(1) == data_json:
        print("No data changes; leaving index.html untouched.")
        return
    new, n = re.subn(r"/\*__DATA_START__\*/.*?/\*__DATA_END__\*/", block, src, flags=re.S)
    if n != 1:
        raise SystemExit("data markers not found in index.html")
    page.write_text(new)
    print(f"Updated {page} with {len(activities)} activities (as of {today}).")
    new_ids = {a["id"] for a in activities}
    colors = set(map(int, re.findall(r"^  (\d+): \{", new, flags=re.M)))
    missing = new_ids - colors
    if missing:
        print(f"NOTE: add COLORS entries in index.html for new activities: {sorted(missing)}")


if __name__ == "__main__":
    main()
