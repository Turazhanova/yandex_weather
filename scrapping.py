from bs4 import BeautifulSoup as bs
from selenium import webdriver
import csv

def find_element_safe(element, no_need_text):
    try:
        if no_need_text and element:
            return element
        if element:
            return element.text
        else:
            return 'N/A'
    except AttributeError:
        return 'N/A'


def extract_data_from_column(calendar_item):
    day = find_element_safe(calendar_item.find("div", attrs={'climate-calendar-day__day'}), False)
    
    day_climate_tag = find_element_safe(calendar_item.find("div", attrs={'temp climate-calendar-day__temp-day'}), True)
    day_climate = find_element_safe(day_climate_tag.find("span", attrs={'temp__value temp__value_with-unit'}), False)
    
    night_climate_tag = find_element_safe(calendar_item.find("div", attrs={'temp climate-calendar-day__temp-night'}), True)
    night_climate = find_element_safe(night_climate_tag.find("span", attrs={'temp__value temp__value_with-unit'}), False)
    
    feel_like_climate_tag = find_element_safe(calendar_item.find("div", attrs={'climate-calendar-day__detailed-feels-like'}), True)
    feel_like_climate = find_element_safe(feel_like_climate_tag.find("span", attrs={'temp__value temp__value_with-unit'}), False)
    
    new_table = find_element_safe(calendar_item.find("table", attrs={'climate-calendar-day__detailed-data-table'}), True)
    new_table_rows = new_table.find_all("tr", attrs={'climate-calendar-day__detailed-data-table-row'})
    if len(new_table_rows) >= 2:
        pressure = find_element_safe(new_table_rows[0].find_all("td", attrs={'climate-calendar-day__detailed-data-table-cell climate-calendar-day__detailed-data-table-cell_value_yes'})[0], False)
        humidity = find_element_safe(new_table_rows[0].find_all("td", attrs={'climate-calendar-day__detailed-data-table-cell climate-calendar-day__detailed-data-table-cell_value_yes'})[1], False)
        wind_speed = find_element_safe(new_table_rows[1].find_all("td", attrs={'climate-calendar-day__detailed-data-table-cell climate-calendar-day__detailed-data-table-cell_value_yes'})[0], False)
    
    return day, day_climate, night_climate, feel_like_climate, pressure, humidity, wind_speed




URL_YANDEX_WEATHER = "https://yandex.kz/pogoda/month?lat=43.273564&lon=76.914851&via=hnav"
driver = webdriver.Chrome()
driver.get(URL_YANDEX_WEATHER)
content = driver.page_source
soup = bs(content, 'html.parser')
climate_calendar_table = soup.find("table", class_="climate-calendar")
climate_calendar_list = []
if climate_calendar_table:
    calendar_item_rows = climate_calendar_table.find("tbody").find_all("tr", attrs={'class': 'climate-calendar__row'})
    if len(calendar_item_rows) > 0:
        for i in range(1, len(calendar_item_rows)):
            calendar_item_columns = calendar_item_rows[i].find_all("td", attrs={'class': 'climate-calendar__cell'})
            for calendar_item in calendar_item_columns:
                day, day_climate, night_climate, feel_like_climate, pressure, humidity, wind_speed = extract_data_from_column(calendar_item)
                climate_calendar_list.append([day, day_climate, night_climate, feel_like_climate, pressure, humidity, wind_speed])


with open('weather_month.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(['Day', 'Day-climate', 'Night-climate', 'Feel-like-climate', 'Pressure', 'Humidity', 'Wind-speed'])
    csvwriter.writerows(climate_calendar_list)
driver.close()