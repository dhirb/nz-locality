#!/usr/bin/python
# -*- coding: utf-8 -*-

from selenium.webdriver import ChromeOptions, Chrome
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
import time
import json


def sanitize_option(option):
    """
    Format the given string by stripping the trailing parentheses
    eg. Auckland City (123) -> Auckland City
    :param option: String to be formatted
    :return: Substring without the trailing parentheses
    """
    return ' '.join(option.split(' ')[:-1]).strip()


# Output mappings
region_list = []
region_district_map = {}
district_suburb_map = {}

# Setup Selenium Chrome browser
chrome_options = ChromeOptions()
chrome_options.add_argument('--incognito')
browser = Chrome(chrome_options=chrome_options)

try:
    # Launch browser and navigate to TradeMe Property page
    browser.get('https://www.trademe.co.nz/property')

    # Wait until dropdowns are ready in DOM
    WebDriverWait(browser, 10).until(ec.presence_of_element_located((By.ID, 'PropertyRegionSelect')))
    region_dropdown = browser.find_element_by_id('PropertyRegionSelect')
    region_options = [x for x in region_dropdown.find_elements_by_tag_name('option')]

    # Get the regions
    region_list = [r.get_attribute('innerHTML') for r in region_options]
    region_list.pop(0)  # Discard 'All' option

    for i in range(0, len(region_list)):
        region = region_list[i]

        # Select a region to start populating the district list
        Select(region_dropdown).select_by_index(i + 1)
        time.sleep(1)

        # Get the district list
        district_dropdown = browser.find_element_by_id('PropertyDistrictSelect')
        district_options = Select(district_dropdown).options
        districts = [sanitize_option(d.get_attribute('innerHTML')) for d in district_options]
        districts.pop(0)  # Discard 'All' option

        # Populate region-district mapping
        region_district_map[region] = {}
        region_district_map[region]['districts'] = districts

        # Iterate the districts
        for j in range(0, len(districts)):
            district = districts[j]
            # Select a district to start populating the suburb list
            Select(district_dropdown).select_by_index(j + 1)
            time.sleep(1)

            # Get the suburb list
            suburb_dropdown = browser.find_element_by_id('PropertySuburbSelect')
            suburb_options = Select(suburb_dropdown).options

            # Populate district-suburb mapping
            district_suburb_map[district] = {}
            district_suburb_map[district]['region'] = region
            district_suburb_map[district]['suburbs'] = [
                sanitize_option(s.get_attribute('innerHTML')) for s in suburb_options]

    # Convert result to JSON
    with open('output/region.json', 'w+') as region_file:
        region_file.write(json.dumps(region_list))
    with open('output/region_district.json', 'w+') as region_district_file:
        region_district_file.write(json.dumps(region_district_map))
    with open('output/district_suburb.json', 'w+') as district_suburb_file:
        district_suburb_file.write(json.dumps(district_suburb_map))

finally:
    browser.quit()
