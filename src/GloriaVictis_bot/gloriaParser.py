import asyncio
import re
import time
import logging

from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

from discordReadWrite import get_tournaments, write_tournaments, get_config_parameter

logger = logging.getLogger("gv")

keywordsLocal = ["[LOKAL]", "[LOCAL]", "[Lokal]", "[Local]", "[lokal]", "[local]"]
keywordsCountry = ["[MASTER]", "[Master]", "[master]"]
regexDay = r"([0-9]{1,2})"
regexMonth = r"([0-9]{1,2})"
regexYear = r"([0-9]{2,4})"
regexSeparator = r"(\.)"
regexDaySeparator = r"([^a-zA-Z0-9\.])"
regOneDay = re.compile(regexDay + regexSeparator + regexMonth + regexSeparator + regexYear)
regTwoDays = re.compile(regexDay + regexSeparator + regexDay + regexSeparator + regexMonth + regexSeparator
                        + regexYear)
page = get_config_parameter("page")


def _load_page(driver, page_l):
    logger.debug(f"Loading page:\r{page_l}")
    driver.get(page_l)
    time.sleep(4)
    logger.debug("Page loaded.")
    return


def _startup():
    opts = Options()
    opts.add_argument('-headless')
    logger.info("Starting selenium driver")
    gloria_driver = webdriver.Firefox(options=opts)
    logger.info("Firefox selenium webdriver started.")
    return gloria_driver


def _teardown(driver):
    logger.info("Starting teardown of selenium driver.")
    driver.close()
    driver.quit()
    logger.info("Selenium driver teardown finished.")


def _find_tournament_list(driver, keyword_list) -> list:
    logger.debug(f"Finding tournament list using keywords:\r{keyword_list}")
    return_list = []
    list2 = []
    for keyword in keyword_list:
        list2.extend(driver.find_elements(By.PARTIAL_LINK_TEXT, keyword))
    for item in list2:
        return_list.append(item.text)
    if len(return_list) > 0:
        logger.debug("Tournaments found. Passing them over for verification.")
        return_list = _verify_tourney_dates(return_list)
        return_list = _sort_list_by_dates(return_list)
    else:
        logger.warning("No tournaments found. It is advised to manually check the site and confirm.")
    return return_list


def _generate_message(tournament_dict) -> str:
    logger.debug("Generating discord message.")
    if not tournament_dict:
        logger.info("Tournament list is empty. Empty message will be generated.")
        return None
    return_string = "Tournament list from " + get_config_parameter("page")
    for name, link in tournament_dict.items():
        return_string = return_string + "\r\r===============================================" + \
                       "===============================================\r\r" + \
                       "**" + name + "**\r" + link
    logger.debug(f"Discord message with tournamets generated:\r{return_string}")
    return return_string


def _get_new_tourney_list() -> dict:
    logger.debug(f"Getting new tournament list from the website: {page}")
    gloria_driver = _startup()
    _load_page(gloria_driver, page)
    links_list = _find_tournament_list(gloria_driver, keywordsLocal + keywordsCountry)
    tourney_dict = _get_tourney_url_dict(gloria_driver, links_list)
    _teardown(gloria_driver)
    return tourney_dict


def _get_tourney_url_dict(driver, tourney_list) -> dict:
    logger.debug("Getting URLs from tournament list.")
    tournament_dict = {}
    for tournament in tourney_list:
        driver.find_element(By.PARTIAL_LINK_TEXT, tournament).click()
        time.sleep(3)
        tournament_dict[tournament] = driver.current_url
        driver.back()
        time.sleep(3)
    logger.debug(f"Getting URLs finished. Returning:\r{tournament_dict}")
    return tournament_dict


def _is_tourney_too_late(tourney_date) -> bool:
    logger.debug(f"Checking if tournament with date: {tourney_date} isn't already finished.")
    t_date = datetime.strptime(tourney_date, "%d.%m.%Y")
    present = datetime.now()
    if t_date.date() < present.date():
        logger.log(5, f"{t_date} is already finished! The tournament is removed from the list.")
        return True
    else:
        logger.log(5, f"{t_date} is not yet passed. The tournament will be added to the list.")
        return False


def _mark_new_tournaments(old_tournament_data, new_tournament_data) -> dict:
    logger.debug("Marking the newly discovered tournaments with appropriate label.")
    return_dict = {}
    for name, link in new_tournament_data.items():
        if name not in old_tournament_data:
            return_dict[":new::exclamation: " + name] = link
        else:
            return_dict[name] = link
    logger.debug("Marking the new tournaments done.")
    return return_dict


def _normalize_date(date_string, reverse=False, is_two_days=False) -> str:
    logger.log(5, f"Normalizing tournament date: {date_string} to comply with date checking functions.")
    # Add a step in group checking in case of two-days tournament date format
    if is_two_days:
        increment = 2
        reg = regTwoDays
    else:
        increment = 0
        reg = regOneDay
    return_value: str = ""
    if not re.match(reg, date_string):
        logger.debug(fr"Couldn't normalize date: {date_string} with application regex. Returning empty string!")
        return return_value
    str2 = re.search(reg, date_string)
    if len(str2.group(1)) == 1:
        return_value = return_value + "0" + str2.group(1) + "."
    else:
        return_value = return_value + str2.group(1) + "."
    if len(str2.group(3 + increment)) == 1:
        return_value = return_value + "0" + str2.group(3 + increment) + "."
    else:
        return_value = return_value + str2.group(3 + increment) + "."
    if len(str2.group(5 + increment)) == 2:
        return_value = return_value + "20" + str2.group(5 + increment)
    elif len(str2.group(5 + increment)) == 4:
        return_value = return_value + str2.group(5 + increment)
    logger.log(5, f"Tournament date: {date_string} normalized to: {return_value} - returning.")
    return return_value

def _normalize_date_reversed(date_string, is_two_days=False) -> str:
    logger.log(5, f"Normalizing tournament date in reversed mode: {date_string}"
                  f"to comply with date checking functions.")
    if is_two_days:
        increment = 2
        reg = regTwoDays
    else:
        increment = 0
        reg = regOneDay
    return_value: str = ""
    if not re.match(reg, date_string):
        logger.debug(fr"Couldn't normalize date: {date_string} with application regex. Returning empty string!")
        return return_value
    str2 = re.search(reg, date_string)
    if len(str2.group(5 + increment)) == 2:
        return_value = return_value + "20" + str2.group(5 + increment)
    elif len(str2.group(5 + increment)) == 4:
        return_value = return_value + str2.group(5 + increment)
    if len(str2.group(3 + increment)) == 1:
        return_value = return_value + "0" + str2.group(3 + increment)
    else:
        return_value = return_value + str2.group(3 + increment)
    if len(str2.group(1)) == 1:
        return_value = return_value + "0" + str2.group(1)
    else:
        return_value = return_value + str2.group(1)
    logger.log(5, f"Tournament date: {date_string} normalized to: {return_value} - returning.")
    return return_value


def _sort_list_by_dates(tournament_list) -> list:
    logger.debug(f"Sorting the tournament list by dates:\r{tournament_list}")
    tourney_date_map = {}
    dates_list_sorted = []
    return_list = []
    for tournament in tournament_list:
        date = re.search(regOneDay, tournament)
        date2 = _normalize_date(date.group(0), True)
        tourney_date_map[tournament] = date2
    for date in tourney_date_map.values():
        if date not in dates_list_sorted:
            dates_list_sorted.append(date)
    dates_list_sorted.sort()
    for d in dates_list_sorted:
        tmp_list = [tournament for tournament, date in tourney_date_map.items() if date == d]
        return_list.extend(tmp_list)
    logger.debug(f"Returning sorted tournament list:\r{return_list}")
    return return_list


def _verify_tourney_dates(link_list) -> list:
    logger.debug(f"Verifying tournaments dates for links:")
    logger.debug("\r".join(link_list))
    new_list = []

    for link in link_list:
        date = re.search(regOneDay, link)
        if date is not None:
            date2 = _normalize_date(date.group(0))
        else:
            date = re.search(regTwoDays, link)
            if date is not None:
                date2 = _normalize_date(date.group(0), is_two_days=True)
            else:
                logger.debug(f"There is no valid date provided to the link: {link}! Skipping.")
                continue
        if _is_tourney_too_late(date2):
            continue
        new_list.append(link)

    logger.debug(f"Date verification completed. The links will be added:\r{link_list}")
    return new_list


def run() -> str:
    new_tourneys = _get_new_tourney_list()
    old_tourneys = get_tournaments()
    write_tournaments(new_tourneys)
    new_tourneys = _mark_new_tournaments(old_tourneys, new_tourneys)
    message = _generate_message(new_tourneys)
    return message
