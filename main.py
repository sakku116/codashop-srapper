from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from fastapi import Response
from selenium.webdriver.support.ui import WebDriverWait
import uvicorn
from fastapi import FastAPI, APIRouter
from selenium.webdriver.support import expected_conditions as EC

class Main:
    def __init__(self):
        option = webdriver.ChromeOptions()
        option.add_argument('headless')
        self.driver = webdriver.Chrome(service=webdriver.ChromeService("./chromedriver"), options=option)
        self.router = APIRouter()
        self.router.add_api_route("/get-username", self.get_username, methods=["GET"])
        self.router.add_event_handler("shutdown", self.shutdown_app)

    def shutdown_app(self):
        self.driver.close()

    def get_username(self, response: Response, user_id: str):
        self.driver.get("https://www.codashop.com/id-id/higgs-domino")
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#userId')))
        user_id_input = self.driver.find_element(By.CSS_SELECTOR, '#userId')
        user_id_input.clear()
        if not user_id_input:
            response.status_code = 500
            return {
                "message": "user id input not found"
            }
        user_id_input.send_keys(user_id)

        nominal_cards = self.driver.find_elements(By.CSS_SELECTOR, '[id*="denomination_"]')
        first = nominal_cards[0] if nominal_cards else None
        if not first:
            response.status_code = 500
            return {
                "message": "nominal cards not found"
            }
        first.click()

        payment_cards = self.driver.find_elements(By.CSS_SELECTOR, '[class="form-section__pc-container"]')
        first = payment_cards[0] if payment_cards else None
        if not first:
            response.status_code = 500
            return {
                "message": "payment cards not found"
            }
        first.click()

        submit_btn = self.driver.find_element(By.CSS_SELECTOR, '#mdn-submit')
        if not first:
            response.status_code = 500
            return {
                "message": "submit btn not found"
            }
        submit_btn.click()

        # wait for modal
        try:
            WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '[class="modal-container"]')))
        except Exception as e:
            response.status_code = 500
            return {
                "message": "modal not showing (timeout)"
            }

        order_rows = self.driver.find_elements(By.CSS_SELECTOR, '[class="order-info__row"]')
        first = order_rows[0] if order_rows else None
        if not first:
            response.status_code = 500
            return {
                "message": "order rows not found"
            }

        username = first.find_element(By.CSS_SELECTOR, '[class="second-col"]').text
        if not first:
            response.status_code = 500
            return {
                "message": "username not found"
            }

        return {
            "message": "OK",
            "username": username
        }

app = FastAPI()
app.include_router(router=Main().router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)