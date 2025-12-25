from collections import defaultdict
import calendar
import requests
import json

def get_current_year_waste_summary():
    post_data = {"number": 224, "schedulegroup": "j", "streetId": 25924460}
    response = requests.post("https://pluginssl.ecoharmonogram.pl/api/v1/plugin/v1/schedules", data=post_data)
    text = response.content.decode("utf-8-sig")
    return json.loads(text)



def group_waste_schedules_by_type_and_month(year_schedule_response)-> dict:
    scheduler_categories = year_schedule_response["scheduleDescription"]
    all_current_year_schedules = list(year_schedule_response["schedules"])

    waste_schedule_by_category_month = defaultdict(dict)

    for waste_category in scheduler_categories:
        category = waste_category["name"]
        waste_schedule_by_category_month[category] = defaultdict(dict)

        for schedule in all_current_year_schedules:
            if schedule["scheduleDescriptionId"] == waste_category["id"]:
                month_as_str = calendar.month_name[int(schedule["month"])]
                waste_schedule_by_category_month[category][month_as_str] = str(schedule["days"]).split(";")

    return waste_schedule_by_category_month

current_year_waste_schedule = group_waste_schedules_by_type_and_month(get_current_year_waste_summary())
for category, month_days in current_year_waste_schedule.items():
    for month, days in month_days.items():
        print(f"W miesiacu {month} odpady {category} są brane w dniach {days}")