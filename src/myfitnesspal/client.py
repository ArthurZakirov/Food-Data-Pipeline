import myfitnesspal
import browser_cookie3
import http.cookiejar
import pandas as pd


def load_myfitnesspal_client():
    cj_browser = browser_cookie3.chrome()
    cj = http.cookiejar.CookieJar()
    for cookie in cj_browser:
        cj.set_cookie(cookie)
    client = myfitnesspal.Client(cookiejar=cj, unit_aware=True)
    return client
