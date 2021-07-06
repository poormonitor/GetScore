import base64
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from PIL import Image
from io import BytesIO
import os
import cv2 as cv
import json


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
    params = {
        "ImageBase64": image
    }
    req.from_json_string(json.dumps(params))

    resp = client.GeneralBasicOCR(req)
    txt = json.loads(resp.to_json_string())[
        "TextDetections"][0]["DetectedText"]
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


if __name__ == "__main__":
    with open("config.json", "r") as fp:
        config = json.loads(fp.read())
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Firefox(options=options)
    driver.set_window_size(1366, 768)
    driver.get("https://pgzy.zjzs.net:4431/login.htm")
    id = config["id"]
    passwd = config["passwd"]
    tencent_id = config["tencent_id"]
    tencent_key = config["tencent_key"]
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
    source = driver.page_source
    driver.get_screenshot_as_file("result.png")
    driver.quit()
    os.remove("screenshot.png")
    os.remove("temp.png")
    with open("index.html", "w") as fp:
        fp.write(source)
