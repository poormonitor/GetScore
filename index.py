import base64
from selenium import webdriver
from PIL import Image
from io import BytesIO
import os
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
    return txt


if __name__ == "__main__":
    with open("config.json", "r") as fp:
        config = json.loads(fp.read())
    driver = webdriver.Firefox()
    driver.set_window_size(1280, 720)
    driver.get("https://pgzy.zjzs.net:4431/login.htm")
    id = config["id"]
    passwd = config["passwd"]
    tencent_id = config["tencent_id"]
    tencent_key = config["tencent_key"]
    driver.find_element_by_name("shenfenzheng").send_keys(id)
    driver.find_element_by_name("mima").send_keys(passwd)
    driver.save_screenshot("screenshot.png")
    image = Image.open("screenshot.png")
    cropped = image.crop((1009, 236, 1128, 288))
    output_buffer = BytesIO()
    cropped.save(output_buffer, format='PNG')
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
    with open("index.html", "w") as fp:
        fp.write(source)
