import myfitnesspal
import browser_cookie3
import http.cookiejar

cj_browser = browser_cookie3.chrome()

# Step 2: Create a new cookiejar
cj = http.cookiejar.CookieJar()

# Step 3: Transfer cookies from cj_browser to cj
for cookie in cj_browser:
    cj.set_cookie(cookie)

client = myfitnesspal.Client(cookiejar=cj)
client.get_date(2024, 4, 14)