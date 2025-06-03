from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from faker import Faker
import time
import os
import requests
from PIL import Image, ImageDraw
from webdriver_manager.microsoft import EdgeChromiumDriverManager

# إعداد البيانات الوهمية
fake = Faker()

# إعداد متصفح Edge بشكل بسيط
options = Options()
options.use_chromium = True
options.add_argument('--start-maximized')
options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
options.add_experimental_option('useAutomationExtension', False)

def get_next_account_number():
    try:
        with open("last_account_number.txt", "r") as file:
            return int(file.read().strip()) + 1
    except FileNotFoundError:
        return 1

def save_account_number(account_number):
    with open("last_account_number.txt", "w") as file:
        file.write(str(account_number))

def wait_and_find_element(driver, by, value, timeout=20):
    try:
        print(f"انتظار ظهور العنصر: {value}")
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        time.sleep(1)
        print(f"تم العثور على العنصر: {value}")
        return element
    except Exception as e:
        print(f"لم يتم العثور على العنصر {value}: {e}")
        return None

def enter_date(driver, date_field):
    """دالة خاصة لإدخال التاريخ"""
    try:
        # تنظيف الحقل
        date_field.click()
        time.sleep(1)
        date_field.clear()
        time.sleep(1)        # إدخال التاريخ بعدة طرق
        
        # الطريقة الأولى: استخدام JavaScript
        driver.execute_script("arguments[0].value = '01/01/1990';", date_field)
        driver.execute_script("arguments[0].dispatchEvent(new Event('change', { 'bubbles': true }));", date_field)
        time.sleep(2)
        
        # التحقق من القيمة
        actual_value = date_field.get_attribute('value')
        if not actual_value or len(actual_value) < 10:
            # الطريقة الثانية: استخدام send_keys مباشرة
            date_field.clear()
            date_field.send_keys("01011990")
            time.sleep(2)
            
            # إذا لم تنجح، نجرب الطريقة الثالثة
            if not date_field.get_attribute('value'):
                actions = ActionChains(driver)
                actions.click(date_field)
                actions.send_keys(Keys.HOME)
                actions.send_keys("01011990")
                actions.perform()
                time.sleep(2)

        print("تم إدخال التاريخ")
        time.sleep(2)

        # التحقق من القيمة
        actual_value = date_field.get_attribute('value')
        print(f"القيمة المدخلة: {actual_value}")

        # إذا لم يتم إدخال السنة بشكل صحيح
        if "1990" not in actual_value:
            print("جاري المحاولة بطريقة بديلة...")
            date_field.clear()
            time.sleep(1)
            
            # محاولة باستخدام JavaScript
            driver.execute_script("arguments[0].value = '01011990'", date_field)
            time.sleep(1)
            driver.execute_script("arguments[0].dispatchEvent(new Event('change'))", date_field)
            
            # محاولة باستخدام Actions
            if "1990" not in date_field.get_attribute('value'):
                actions = ActionChains(driver)
                actions.click(date_field).key_down(Keys.HOME).send_keys("01011990").perform()

        return True
    except Exception as e:
        print(f"خطأ في إدخال التاريخ: {e}")
        return False

def verify_page_loaded(driver):
    try:
        WebDriverWait(driver, 30).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        username_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "signup_displayname_input"))
        )
        return True
    except Exception as e:
        print(f"خطأ في تحميل الصفحة: {e}")
        return False

def create_account():
    try:
        print("بدء عملية إنشاء الحساب...")
        account_number = get_next_account_number()
        username = f"elitbotnew{account_number}"
        email = f"elitbotnew{account_number}@dsf.com"
        password = "Moammedmax34"
        
        print(f"تم تجهيز البيانات: {username}, {email}")

        print("جاري فتح صفحة التسجيل...")
        driver.get("https://ar.secure.imvu.com/welcome/ftux/account/")
        print("انتظار تحميل الصفحة...")
        time.sleep(10)

        if not verify_page_loaded(driver):
            print("إعادة تحميل الصفحة...")
            driver.refresh()
            time.sleep(10)
            if not verify_page_loaded(driver):
                raise Exception("فشل في تحميل الصفحة")

        print("الصفحة جاهزة للتفاعل")
        time.sleep(3)

        # ملء النموذج
        fields = {
            ("CLASS_NAME", "signup_displayname_input"): username,
            ("NAME", "signup_email"): email,
            ("NAME", "signup_password"): password,
            ("NAME", "confirm_password"): password
        }

        for (by_type, locator), value in fields.items():
            element = wait_and_find_element(driver, getattr(By, by_type), locator)
            if element:
                print(f"إدخال البيانات في حقل {locator}")
                element.clear()
                for char in value:
                    element.send_keys(char)
                    time.sleep(0.1)
                time.sleep(2)

        # إدخال تاريخ الميلاد
        print("محاولة إدخال تاريخ الميلاد...")
        date_field = wait_and_find_element(driver, By.XPATH, "//input[@class='date-picker-input']")
        if date_field:
            enter_date(driver, date_field)

        time.sleep(3)

        # الضغط على زر التسجيل
        submit = wait_and_find_element(driver, By.ID, "registration-submit")
        if submit:
            print("الضغط على زر التسجيل")
            time.sleep(2)
            submit.click()
            time.sleep(5)        # التعامل مع الكابتشا
        print("انتظار ظهور الكابتشا...")
        time.sleep(3)
        try:
            # العثور على الـ iframe الخاص بالكابتشا
            iframe = wait_and_find_element(driver, By.CSS_SELECTOR, "iframe[title='reCAPTCHA']", timeout=15)
            if iframe:
                print("تم العثور على إطار الكابتشا")
                # التبديل إلى إطار الكابتشا
                driver.switch_to.frame(iframe)
                
                # البحث عن مربع الكابتشا والضغط عليه
                captcha_checkbox = wait_and_find_element(driver, By.CSS_SELECTOR, "div.recaptcha-checkbox-border")
                if captcha_checkbox:
                    print("جاري الضغط على مربع الكابتشا...")
                    time.sleep(1)
                    captcha_checkbox.click()
                    print("تم الضغط على مربع الكابتشا، يمكنك الآن حل الكابتشا يدوياً")
                    # انتظار لمدة طويلة للحل اليدوي
                    time.sleep(3600)  # انتظار ساعة كاملة
                
                driver.switch_to.default_content()
            else:
                print("لم يتم العثور على إطار الكابتشا")
        except Exception as e:
            print(f"خطأ في الكابتشا: {e}")
            driver.switch_to.default_content()

        save_account_number(account_number)
        print("تم حفظ رقم الحساب")

    except Exception as e:
        print(f"خطأ في إنشاء الحساب: {e}")

if __name__ == "__main__":
    try:
        print("جاري تهيئة المتصفح...")
        service = Service(EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(service=service, options=options)
        driver.set_page_load_timeout(30)
        print("تم تهيئة المتصفح بنجاح")
        
        create_account()
        
        print("اكتملت العملية")
        
    except Exception as e:
        print(f"حدث خطأ: {e}")
    finally:
        time.sleep(5)
        if 'driver' in locals():
            driver.quit()
        print("تم إغلاق المتصفح")
