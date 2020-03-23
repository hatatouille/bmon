import sys
import re
import time
from enum import Enum
import datetime as dt
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

driver = webdriver.Chrome("./chromedriver")
ignored_exceptions = (NoSuchElementException, StaleElementReferenceException,)
wait = WebDriverWait(driver, 10, ignored_exceptions=ignored_exceptions)


class Studio(Enum):
    GINZA = "0001"
    AOYAMA = "0002"
    EBISU = "0003"
    SHINJUKU = "0004"
    SAKAE = "0005"
    IKEBUKURO = "0006"
    HANEDA = "0007"
    UMEDA = "0008"
    OMIYA = "0009"

def login():
    id = driver.find_element_by_id("your-id")
    id.send_keys("<ここにあなたのb-monster IDを入れてください>")

    password = driver.find_element_by_id("your-password")
    password.send_keys("<ここにあなたのb-monster passwordを入れてください>")

    login = driver.find_element_by_id("login-btn")
    login.click()
    wait.until(EC.presence_of_all_elements_located)
    return

def latest_reserve(_after_hour):
    driver.get("https://www.b-monster.jp")

    trigger = driver.find_element_by_xpath("//*[@id='g-console']/li[1]/button")
    trigger.click()


    wait.until(EC.presence_of_element_located((By.ID, 'login-modal')))
    login()
    time.sleep(1)

    driver.get("https://www.b-monster.jp/reserve/?studio_code=" + Studio.EBISU.value)
    wait.until(EC.presence_of_all_elements_located)

    now = dt.datetime.now()

    print("現在時刻は " + now.strftime("%Y/%m/%d %H:%M:%S") + "です")

    for i in driver.find_elements_by_class_name("flex-no-wrap"):
        for j in i.find_elements_by_css_selector(".daily-panel"):
            for k in j.find_elements_by_css_selector(".panel.whats-program-panel"):
                tttime = k.find_element_by_css_selector("a:first-child > .panel-content > .tt-time").text
                ttinstructor = k.find_element_by_css_selector("a:first-child > .panel-content > .tt-instructor").text
                timearr = tttime[:5].split(":")
                timearr_end = tttime[-5:]
                start_time = dt.datetime(now.year, now.month, now.day, int(timearr[0]), int(timearr[1]), 0)
                if start_time > now + dt.timedelta(hours=_after_hour):
                    print("本日の" + Studio.EBISU.value + "スタジオ: " + ttinstructor + "の" + timearr[0] + ":" + timearr[1] + "~" + timearr_end + "の回の予約を試みます。")
                    anchor = k.find_element_by_css_selector("a:first-child")
                    anchor.click()
                    break
            break
        break

    time.sleep(1)
    return

def fixed_reserve(_url):
    print(_url)
    driver.get(_url)
    wait.until(EC.presence_of_all_elements_located)

    if driver.find_element_by_id('login-modal'): login()
    time.sleep(1)
    return

def has_vacancy():
    wait.until(EC.presence_of_element_located((By.ID, 'select-bag')))
    time.sleep(1)
    _parent = driver.find_element_by_id('select-bag')
    try:
        if _parent.find_elements_by_css_selector('.form-box'):
            print("空きがあります(*・ω・)ノ")
            return True
        else:
            print("満員です(;´д｀) ")
            return False
    except StaleElementReferenceException as e:
        print(e)
        return False

def get_vacant_bags():
    print("空きバッグ検索")
    vacancy_list = []
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'bag-list')))
    for i in driver.find_elements_by_class_name('bag-list'):
        # i ∈ <div class="bag-list bag-list5">
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'bag-check')))
        for j in i.find_elements_by_css_selector('.bag-check:not(.hidden):not(.bag-blank)'):
            # j ∈ <label for="bag65" class="bag-check  bag65  box-master">
            k = j.get_attribute('for')
            if re.match('bag\d{1,2}', k): bag_no = k
            print(bag_no)
            wait.until(EC.presence_of_element_located((By.ID, bag_no)))
            if j.find_element_by_id(bag_no).is_enabled():
                #j.find_element_by_id(bag_no) ∈ <input type="checkbox" id="bag65" disabled="disabled">
                vacancy_list.append(bag_no[3:].zfill(2))
    print(vacancy_list)
    return vacancy_list

def choose_bag(_vac_bags):
    print("サンドバッグ選択")
    # ここには、選んだStudio.Enumのサンドバッグ番号を自分の優先度順に並べてください
    fav_bags = ["46","48","49","51","38","36","34","32","30","43","63","61","59","57","55","40","25","23","21","19","17","15","52","67","42","27","74","72","76","70","80","68","02","04","07","92","94","14"]
    # e.g.) _vac_bags = ["03", "05", "04", "02", "01", "36"]

    candidate = min((s for s in range(len(fav_bags)) if fav_bags[s] in _vac_bags), default=-1)
    return fav_bags[candidate]

def activate_bag(_dec_bag):
    print(_dec_bag + "番を予約します")
    target_id = "bag" + _dec_bag.lstrip("0")
    print(target_id)
    target_dom = driver.find_element_by_xpath('//*[@id="' + target_id + '"]')
    driver.execute_script("arguments[0].scrollIntoView(true);", target_dom)
    target_dom.send_keys(Keys.SPACE)
    return target_dom.get_attribute('checked')

def reserve():
    print("プランで予約する")
    _confirm = driver.find_element_by_xpath('//*[@id="your-reservation"]/button[1]')
    if _confirm.is_enabled(): _confirm.click()
    time.sleep(1)
    wait.until(EC.presence_of_all_elements_located)
    if "confirm" in driver.current_url:
        _complete = driver.find_element_by_xpath('//*[@id="main-container"]/div[2]/button')
        _complete.click()
        return True
    else:
        return False

def reload_page(_interval):
    print(str(_interval) + "秒おきにページをリロードします")
    driver.refresh()
    wait.until(EC.presence_of_all_elements_located)
    return

# mainスレッド
if __name__ == '__main__':
    args = sys.argv
    if len(args) < 2:
        hour = 1
        print("直近" + str(hour) + "時間以降の予約が可能か確認します")
        latest_reserve(hour)
    else:
        pattern = "https?://[\w/:%#\$&\?\(\)~\.=\+\-]+"
        if re.match(pattern, args[1]):
            # e.g.) python3 bmon.py 'https://www.b-monster.jp/reserve/punchbag?lesson_id=107686&studio_code=0003'
            print("引数で指定された回の予約が可能か確認します")
            fixed_reserve(args[1])
        else:
            print("正しいURL形式で引数に渡してください")
            quit()

    threshold = 0
    while not has_vacancy():
        reload_interval = 5 # 3秒に1回更新 => 12回で1分
        reload_page(reload_interval)
        threshold += 1
        print("リロード回数" + str(threshold))
        # time.sleep(5)
        dot = 0
        while dot < reload_interval:
            print(".", end = "")
            dot += 1
            time.sleep(1)
        print("\n")
        if threshold >= 360: break # 最大30分間繰り返す

    wait.until(EC.presence_of_element_located((By.ID, 'select-bag')))
    vac_bags = get_vacant_bags()
    dec_bag = choose_bag(vac_bags)
    if activate_bag(dec_bag): result = reserve()
    quit(result)
