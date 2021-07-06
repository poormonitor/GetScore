import base64
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from PIL import Image
from io import BytesIO
import os
import cv2 as cv
import json
import time
import requests


def rec(image, tencent_id, tencent_key):
    from tencentcloud.common import credential
    from tencentcloud.common.profile.client_profile import ClientProfile
    from tencentcloud.common.profile.http_profile import HttpProfile
    from tencentcloud.ocr.v20181119 import ocr_client, models
    cred = credential.Credential(tencent_id, tencent_key)
    httpProfile = HttpProfile()
    httpProfile.endpoint = "ocr.tencentcloudapi.com"

    clientProfile = ClientProfile()
    clientProfile.httpProfile = httpProfile
    client = ocr_client.OcrClient(cred, "ap-shanghai", clientProfile)

    req = models.GeneralBasicOCRRequest()
    params = {"ImageBase64": image}
    req.from_json_string(json.dumps(params))

    resp = client.GeneralBasicOCR(req)
    txt = json.loads(
        resp.to_json_string())["TextDetections"][0]["DetectedText"]
    return txt.replace(" ", "")


def pre_process(image):
    image.save("temp.png")
    img = cv.imread("temp.png")
    blur = cv.pyrMeanShiftFiltering(img, sp=8, sr=60)
    gray = cv.cvtColor(blur, cv.COLOR_BGR2GRAY)
    ret, binary = cv.threshold(gray, 185, 255, cv.THRESH_BINARY_INV)
    cv.bitwise_not(binary, binary)
    cv.imwrite("temp.png", binary)
    processed = Image.open("temp.png")
    return processed


def upload(key, file):
    response = requests.post(url="https://sm.ms/api/v2/upload",
                             files={
                                 "smfile": file
                             },
                             params={
                                 "headers": "Authorization:%s" % key
                             }).text
    try:
        url = json.loads(response)["data"]["url"]
    except:
        url = json.loads(response)["image"]
    return url


def send(key, message):
    s_url = "https://sctapi.ftqq.com/%s.send?title=学考成绩查询&desp=%s" % (key,
                                                                      message)
    requests.get(s_url % message)
    return None


if __name__ == "__main__":
    with open("config.json", "r") as fp:
        config = json.loads(fp.read())
        id = config["id"]
        passwd = config["passwd"]
        tencent_id = config["tencent_id"]
        tencent_key = config["tencent_key"]
        pic_key = config["smms_key"]
        message_key = config["serverchan_key"]
    while True:
        try:
            options = Options()
            options.add_argument('--headless')
            driver = webdriver.Firefox(options=options)
            driver.set_window_size(1366, 768)
            driver.get("https://pgzy.zjzs.net:4431/login.htm")

            driver.find_element_by_name("shenfenzheng").send_keys(id)
            driver.find_element_by_name("mima").send_keys(passwd)
            driver.save_screenshot("screenshot.png")
            image = Image.open("screenshot.png")
            element = driver.find_element_by_id("imgVerify")
            left = element.location['x']
            top = element.location['y']
            right = element.location['x'] + element.size['width']
            bottom = element.location['y'] + element.size['height']
            cropped = image.crop((left, top, right, bottom))
            processed = pre_process(cropped)
            output_buffer = BytesIO()
            processed.save(output_buffer, format='PNG')
            byte_data = output_buffer.getvalue()
            image = base64.b64encode(byte_data).decode('ascii')
            yzm = rec(image, tencent_id, tencent_key)
            driver.find_element_by_name("yzm").send_keys(yzm)
            driver.find_elements_by_id("btnSubmit")[0].click()
            driver.get("https://pgzy.zjzs.net:4431/xklscj.aspx")
        except:
            driver.quit()
            continue
        else:
            break
    source = driver.page_source.replace(" ", "")
    img_name = "result-%s.png" % int(time.time())
    driver.get_screenshot_as_file(img_name)
    driver.quit()
    os.remove("screenshot.png")
    os.remove("temp.png")
    if os.path.exists("index.html"):
        with open("index.html", "r") as fp:
            text = fp.read().replace(" ", "")
            if text == source:
                send(message_key, "成绩：未发布")
                os.remove(img_name)
                exit(0)
    with open("index.html", "w") as fp:
        fp.write(source)
    with open(img_name, "rb") as fp:
        url = upload(pic_key, fp)
    send(message_key, "成绩：" + url)
    os.remove(img_name)