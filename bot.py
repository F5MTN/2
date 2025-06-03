from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from faker import Faker
import time
import os
import requests
from PIL import Image, ImageDraw
from webdriver_manager.chrome import ChromeDriverManager
import zipfile
import urllib.request

# إعداد البيانات الوهمية
fake = Faker()

# دالة لتحميل وتثبيت إضافة Buster Captcha Solver
def download_buster_extension():
    extension_dir = "buster_extension"
    if not os.path.exists(extension_dir):
        os.makedirs(extension_dir)
        print("تحميل إضافة Buster Captcha Solver...")
        
        # رابط تحميل الإضافة من Chrome Web Store
        extension_id = "mpbjkejclgfgadiemmefgebjfooflfhl"
        extension_url = f"https://clients2.google.com/service/update2/crx?response=redirect&prodversion=91.0.4472.124&acceptformat=crx2,crx3&x=id%3D{extension_id}%26uc"
        
        try:
            # تحميل ملف الإضافة
            urllib.request.urlretrieve(extension_url, f"{extension_dir}/buster.crx")
            
            # استخراج الإضافة
            with zipfile.ZipFile(f"{extension_dir}/buster.crx", 'r') as zip_ref:
                zip_ref.extractall(extension_dir)
            
            print("تم تحميل وتثبيت إضافة Buster Captcha Solver بنجاح")
            return extension_dir
        except Exception as e:
            print(f"فشل في تحميل الإضافة: {e}")
            return None
    else:
        print("إضافة Buster Captcha Solver موجودة بالفعل")
        return extension_dir

# إعداد المتصفح مع إضافة Buster
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

# تحميل وإضافة إضافة Buster
buster_path = download_buster_extension()
if buster_path:
    options.add_argument(f"--load-extension={buster_path}")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# إخفاء أن المتصفح يتم التحكم فيه بواسطة أتمتة
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

# بيانات API الخاصة بحل Captcha
CAPTCHA_API_KEY = "a67d3ce22ef5749d70ee34da412c5f32d998462a"
CAPTCHA_API_URL = "https://api.zenrows.com/v1/"

# استرجاع الرقم التالي للحساب
def get_next_account_number():
    try:
        with open("last_account_number.txt", "r") as file:
            return int(file.read().strip()) + 1
    except FileNotFoundError:
        return 1

# حفظ الرقم الأخير
def save_account_number(account_number):
    with open("last_account_number.txt", "w") as file:
        file.write(str(account_number))

# إعداد مجلد لحفظ لقطات الشاشة
if not os.path.exists("screenshots"):
    os.makedirs("screenshots")

# عداد الصور
screenshot_counter = 1

# حفظ لقطات الشاشة
def save_screenshot(step_name):
    global screenshot_counter
    screenshot_path = f"screenshots/{screenshot_counter:04d}_{step_name}.png"
    driver.save_screenshot(screenshot_path)
    screenshot_counter += 1
    print(f"تم حفظ لقطة الشاشة: {screenshot_path}")

# حفظ لقطة شاشة عند الضغط على المكان المحدد
def save_click_location_screenshot(element, step_name):
    global screenshot_counter
    location = element.location
    size = element.size
    x = int(location["x"] + size["width"] / 2)
    y = int(location["y"] + size["height"] / 2)

    # التقاط لقطة الشاشة
    screenshot_path = f"screenshots/{screenshot_counter:04d}_{step_name}.png"
    driver.save_screenshot(screenshot_path)

    # فتح الصورة ورسم دائرة على مكان الضغط
    image = Image.open(screenshot_path)
    draw = ImageDraw.Draw(image)
    radius = 10
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), outline="red", width=3)
    image.save(screenshot_path)
    screenshot_counter += 1
    print(f"تم حفظ لقطة الشاشة مع تحديد الضغط: {screenshot_path}")

# دالة لحل الكابتشا باستخدام API
def solve_captcha(captcha_image_url):
    try:
        # إرسال طلب لحل الكابتشا باستخدام API
        response = requests.post(CAPTCHA_API_URL, data={
            'apikey': CAPTCHA_API_KEY,
            'url': captcha_image_url
        })
        result = response.json()
        if 'solution' in result:
            return result['solution']
        else:
            print("فشل في حل الكابتشا:", result)
            return ""
    except Exception as e:
        print(f"حدث خطأ أثناء حل الكابتشا: {e}")
        return ""


# إنشاء حساب
def create_account():
    try:
        # استرجاع الرقم التالي وإنشاء الاسم والإيميل
        account_number = get_next_account_number()
        username = f"elitbotnew{account_number}"
        email = f"elitbotnew{account_number}@dsf.com"
        password = "Moammedmax34"
        birthdate = "1990-01-01"

        # فتح صفحة التسجيل
        driver.get("https://ar.secure.imvu.com/welcome/ftux/account/")
        time.sleep(5)
        save_screenshot("page_loaded")

        # تعبئة الحقول
        try:
            username_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "signup_displayname_input"))
            )
            username_field.send_keys(username)
            save_click_location_screenshot(username_field, "username_filled")
        except Exception as e:
            print(f"خطأ أثناء العثور على حقل اسم المستخدم: {e}")
            save_screenshot("username_field_error")

        try:
            email_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "signup_email"))
            )
            email_field.send_keys(email)
            save_click_location_screenshot(email_field, "email_filled")
        except Exception as e:
            print(f"خطأ أثناء العثور على حقل البريد الإلكتروني: {e}")
            save_screenshot("email_field_error")

        try:
            password_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "signup_password"))
            )
            password_field.send_keys(password)
            save_click_location_screenshot(password_field, "password_filled")
        except Exception as e:
            print(f"خطأ أثناء العثور على حقل كلمة المرور: {e}")
            save_screenshot("password_field_error")

        try:
            confirm_password_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "confirm_password"))
            )
            confirm_password_field.send_keys(password)
            save_click_location_screenshot(confirm_password_field, "confirm_password_filled")
        except Exception as e:
            print(f"خطأ أثناء العثور على حقل تأكيد كلمة المرور: {e}")
            save_screenshot("confirm_password_field_error")

        # إدخال تاريخ الميلاد
        try:
            date_picker = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@class='date-picker-input']"))
            )
            date_picker.send_keys(birthdate)
            save_click_location_screenshot(date_picker, "birthdate_filled")
        except Exception as e:
            print(f"خطأ أثناء العثور على حقل تاريخ الميلاد: {e}")
            save_screenshot("birthdate_field_error")

        # الضغط على زر "Create Account"
        try:
            submit_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "registration-submit"))
            )
            submit_button.click()
            save_click_location_screenshot(submit_button, "submit_clicked")

            # الانتظار 3 ثواني قبل متابعة الخطوات
            time.sleep(3)

        except Exception as e:
            print(f"خطأ أثناء العثور على زر الإرسال: {e}")
            save_screenshot("submit_button_error")

        # الانتظار حتى يظهر مربع Captcha
        print("الانتظار حتى يظهر مربع Captcha...")
        try:
            # الانتظار حتى يظهر العنصر الذي يحتوي على مربع الكابتشا داخل الـ iframe
            iframe = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.NAME, "a-6dardm6osdhq"))
            )
            # التبديل إلى الإطار
            driver.switch_to.frame(iframe)

            # الانتظار حتى يظهر مربع الكابتشا
            captcha_checkbox = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.recaptcha-checkbox"))
            )
            # الضغط على مربع الكابتشا
            captcha_checkbox.click()
            save_click_location_screenshot(captcha_checkbox, "captcha_clicked")

            # استرجاع رابط صورة الكابتشا
            captcha_image_url = driver.find_element(By.CSS_SELECTOR, "img[alt='captcha']").get_attribute("src")
            captcha_solution = solve_captcha(captcha_image_url)
            print(f"تم حل الكابتشا: {captcha_solution}")

            # إدخال الحل في النموذج
            captcha_input = driver.find_element(By.ID, "captcha_solution_input")
            captcha_input.send_keys(captcha_solution)

            # العودة إلى الصفحة الرئيسية بعد التفاعل مع الكابتشا
            driver.switch_to.default_content()

            # الانتظار 5 ثواني بعد حل الكابتشا
            time.sleep(5)

        except Exception as e:
            print(f"لم يتم العثور على مربع Captcha أو حدث خطأ: {e}")
            save_screenshot("captcha_not_found")

        # حفظ البيانات
        save_account_number(account_number)

    except Exception as e:
        print(f"حدث خطأ أثناء إنشاء الحساب: {e}")
        save_screenshot("error")

# تشغيل الكود
create_account()

# دالة محسنة لحل الكابتشا مع استخدام إضافة Buster
def solve_captcha_with_buster():
    try:
        print("محاولة حل الكابتشا باستخدام إضافة Buster...")
        
        # البحث عن زر Buster في الصفحة
        buster_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[title*='Buster']"))
        )
        buster_button.click()
        print("تم الضغط على زر Buster")
        
        # انتظار حل الكابتشا
        time.sleep(10)
        
        return True
    except Exception as e:
        print(f"فشل في استخدام إضافة Buster: {e}")
        return False

# تشغيل الكود
create_account()

# إغلاق المتصفح
driver.quit()

        # الانتظار حتى يظهر مربع Captcha
        print("الانتظار حتى يظهر مربع Captcha...")
        try:
            # الانتظار حتى يظهر العنصر الذي يحتوي على مربع الكابتشا داخل الـ iframe
            iframe = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.NAME, "a-6dardm6osdhq"))
            )
            # التبديل إلى الإطار
            driver.switch_to.frame(iframe)

            # الانتظار حتى يظهر مربع الكابتشا
            captcha_checkbox = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.recaptcha-checkbox"))
            )
            # الضغط على مربع الكابتشا
            captcha_checkbox.click()
            save_click_location_screenshot(captcha_checkbox, "captcha_clicked")

            # العودة إلى الصفحة الرئيسية
            driver.switch_to.default_content()
            
            # محاولة حل الكابتشا باستخدام إضافة Buster
            if solve_captcha_with_buster():
                print("تم حل الكابتشا بنجاح باستخدام إضافة Buster")
            else:
                # في حالة فشل Buster، استخدام الطريقة القديمة
                driver.switch_to.frame(iframe)
                captcha_image_url = driver.find_element(By.CSS_SELECTOR, "img[alt='captcha']").get_attribute("src")
                captcha_solution = solve_captcha(captcha_image_url)
                print(f"تم حل الكابتشا بالطريقة القديمة: {captcha_solution}")
                
                captcha_input = driver.find_element(By.ID, "captcha_solution_input")
                captcha_input.send_keys(captcha_solution)
                driver.switch_to.default_content()

            # الانتظار 5 ثواني بعد حل الكابتشا
            time.sleep(5)

        except Exception as e:
            print(f"لم يتم العثور على مربع Captcha أو حدث خطأ: {e}")
            save_screenshot("captcha_not_found")

        # حفظ البيانات
        save_account_number(account_number)

    except Exception as e:
        print(f"حدث خطأ أثناء إنشاء الحساب: {e}")
        save_screenshot("error")

# تشغيل الكود
create_account()

# إغلاق المتصفح
driver.quit()

# دالة محسنة لحل الكابتشا مع استخدام إضافة Buster
def solve_captcha_with_buster():
    try:
        print("محاولة حل الكابتشا باستخدام إضافة Buster...")
        
        # البحث عن زر Buster في الصفحة
        buster_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[title*='Buster']"))
        )
        buster_button.click()
        print("تم الضغط على زر Buster")
        
        # انتظار حل الكابتشا
        time.sleep(10)
        
        return True
    except Exception as e:
        print(f"فشل في استخدام إضافة Buster: {e}")
        return False

        # الانتظار حتى يظهر مربع Captcha
        print("الانتظار حتى يظهر مربع Captcha...")
        try:
            # الانتظار حتى يظهر العنصر الذي يحتوي على مربع الكابتشا داخل الـ iframe
            iframe = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.NAME, "a-6dardm6osdhq"))
            )
            # التبديل إلى الإطار
            driver.switch_to.frame(iframe)

            # الانتظار حتى يظهر مربع الكابتشا
            captcha_checkbox = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.recaptcha-checkbox"))
            )
            # الضغط على مربع الكابتشا
            captcha_checkbox.click()
            save_click_location_screenshot(captcha_checkbox, "captcha_clicked")

            # العودة إلى الصفحة الرئيسية
            driver.switch_to.default_content()
            
            # محاولة حل الكابتشا باستخدام إضافة Buster
            if solve_captcha_with_buster():
                print("تم حل الكابتشا بنجاح باستخدام إضافة Buster")
            else:
                # في حالة فشل Buster، استخدام الطريقة القديمة
                driver.switch_to.frame(iframe)
                captcha_image_url = driver.find_element(By.CSS_SELECTOR, "img[alt='captcha']").get_attribute("src")
                captcha_solution = solve_captcha(captcha_image_url)
                print(f"تم حل الكابتشا بالطريقة القديمة: {captcha_solution}")
                
                captcha_input = driver.find_element(By.ID, "captcha_solution_input")
                captcha_input.send_keys(captcha_solution)
                driver.switch_to.default_content()

            # الانتظار 5 ثواني بعد حل الكابتشا
            time.sleep(5)

        except Exception as e:
            print(f"لم يتم العثور على مربع Captcha أو حدث خطأ: {e}")
            save_screenshot("captcha_not_found")

        # حفظ البيانات
        save_account_number(account_number)

    except Exception as e:
        print(f"حدث خطأ أثناء إنشاء الحساب: {e}")
        save_screenshot("error")

# تشغيل الكود
create_account()

# إغلاق المتصفح
driver.quit()

# دالة محسنة لحل الكابتشا مع استخدام إضافة Buster
def solve_captcha_with_buster():
    try:
        print("محاولة حل الكابتشا باستخدام إضافة Buster...")
        
        # البحث عن زر Buster في الصفحة
        buster_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[title*='Buster']"))
        )
        buster_button.click()
        print("تم الضغط على زر Buster")
        
        # انتظار حل الكابتشا
        time.sleep(10)
        
        return True
    except Exception as e:
        print(f"فشل في استخدام إضافة Buster: {e}")
