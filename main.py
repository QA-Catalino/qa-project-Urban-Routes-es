import data
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys


# no modificar
def retrieve_phone_code(driver) -> str:
    """Este código devuelve un número de confirmación de teléfono y lo devuelve como un string."""
    import json
    import time
    from selenium.common import WebDriverException
    code = None
    for i in range(10):
        try:
            logs = [log["message"] for log in driver.get_log('performance') if log.get("message")
                    and 'api/v1/number?number' in log.get("message")]
            for log in reversed(logs):
                message_data = json.loads(log)["message"]
                body = driver.execute_cdp_cmd('Network.getResponseBody',
                                              {'requestId': message_data["params"]["requestId"]})
                code = ''.join([x for x in body['body'] if x.isdigit()])
        except WebDriverException:
            time.sleep(1)
            continue
        if not code:
            raise Exception("No se encontró el código de confirmación del teléfono.")
        return code


class UrbanRoutesPage:
    # Localizadores existentes
    from_field = (By.ID, 'from')
    to_field = (By.ID, 'to')

    # Nuevos Localizadores
    order_button = (By.XPATH, "//button[contains(text(), 'Pedir un taxi')]")
    comfort_tariff = (By.XPATH, "//div[@class='tfast-container']//div[text()='Comfort']/..")
    tariff_card_title = (By.XPATH, "//div[@class='tfast-container']//div[text()='Comfort']")

    phone_field_trigger = (By.CLASS_NAME, 'np-text')
    phone_input = (By.ID, 'phone')
    phone_next_button = (By.XPATH, "//button[contains(text(), 'Siguiente')]")
    phone_code_input = (By.ID, 'code')
    phone_confirm_button = (By.XPATH, "//button[contains(text(), 'Confirmar')]")

    payment_method_trigger = (By.CLASS_NAME, 'pp-text')
    add_card_button = (By.XPATH, "//div[contains(text(), 'Agregar tarjeta')]")
    card_number_input = (By.ID, 'number')
    card_cvv_input = (By.XPATH, "//div[@class='card-code-input']//input[@id='code']")
    card_link_button = (By.XPATH, "//button[contains(text(), 'Enlazar')]")
    close_payment_modal = (By.XPATH, "//div[@id='payment-method-modal']//button[@class='close-button']")

    driver_message_input = (By.ID, 'comment')
    blanket_tissue_checkbox = (By.XPATH, "//div[contains(text(), 'Manta y pañuelos')]/../span[@class='slider round']")
    blanket_switch_state = (By.XPATH, "//div[contains(text(), 'Manta y pañuelos')]/../input[@class='switch-input']")

    ice_cream_plus_button = (By.XPATH,
                             "//div[contains(text(), 'Helado')]/../div[@class='counter']//div[@class='counter-plus']")
    ice_cream_count = (By.XPATH,
                       "//div[contains(text(), 'Helado')]/../div[@class='counter']//div[@class='counter-value']")

    submit_order_button = (By.CLASS_NAME, 'smart-button')
    order_modal = (By.CLASS_NAME, 'order-body')
    driver_info_header = (By.XPATH, "//div[contains(@class, 'order-number')]")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)

    def set_from(self, from_address):
        self.driver.find_element(*self.from_field).send_keys(from_address)

    def set_to(self, to_address):
        self.driver.find_element(*self.to_field).send_keys(to_address)

    def get_from(self):
        return self.driver.find_element(*self.from_field).get_property('value')

    def get_to(self):
        return self.driver.find_element(*self.to_field).get_property('value')

    def set_route(self, from_address, to_address):
        self.set_from(from_address)
        self.set_to(to_address)
        self.wait.until(EC.element_to_be_clickable(self.order_button)).click()

    def select_comfort_tariff(self):
        comfort_element = self.wait.until(EC.element_to_be_clickable(self.comfort_tariff))
        comfort_element.click()

    def check_comfort_selected(self):
        # Verifica si el elemento del título de la tarifa Comfort está presente o activo
        return self.wait.until(EC.presence_of_element_located(self.tariff_card_title)).is_displayed()

    def fill_phone_number(self, phone_number):
        self.wait.until(EC.element_to_be_clickable(self.phone_field_trigger)).click()
        self.wait.until(EC.visibility_of_element_located(self.phone_input)).send_keys(phone_number)
        self.driver.find_element(*self.phone_next_button).click()

    def enter_phone_code(self, code):
        code_input_field = self.wait.until(EC.visibility_of_element_located(self.phone_code_input))
        code_input_field.send_keys(code)
        self.driver.find_element(*self.phone_confirm_button).click()

    def get_phone_text(self):
        return self.wait.until(EC.presence_of_element_located(self.phone_field_trigger)).text

    def add_credit_card(self, card_number, card_code):
        self.wait.until(EC.element_to_be_clickable(self.payment_method_trigger)).click()
        self.wait.until(EC.element_to_be_clickable(self.add_card_button)).click()

        self.wait.until(EC.visibility_of_element_located(self.card_number_input)).send_keys(card_number)
        cvv_field = self.driver.find_element(*self.card_cvv_input)
        cvv_field.send_keys(card_code)

        # Simular des-enfoque presionando TAB para activar el botón Enlazar
        cvv_field.send_keys(Keys.TAB)

        self.wait.until(EC.element_to_be_clickable(self.card_link_button)).click()
        self.wait.until(EC.element_to_be_clickable(self.close_payment_modal)).click()

    def get_payment_method_text(self):
        return self.wait.until(EC.presence_of_element_located(self.payment_method_trigger)).text

    def write_driver_message(self, message):
        message_field = self.wait.until(EC.visibility_of_element_located(self.driver_message_input))
        message_field.send_keys(message)

    def get_driver_message(self):
        return self.driver.find_element(*self.driver_message_input).get_property('value')

    def order_blanket_and_tissues(self):
        self.wait.until(EC.element_to_be_clickable(self.blanket_tissue_checkbox)).click()

    def is_blanket_ordered(self):
        return self.driver.find_element(*self.blanket_switch_state).is_selected()

    def order_ice_creams(self, quantity):
        plus_button = self.wait.until(EC.element_to_be_clickable(self.ice_cream_plus_button))
        for _ in range(quantity):
            plus_button.click()

    def get_ice_cream_count(self):
        return self.driver.find_element(*self.ice_cream_count).text

    def submit_car_order(self):
        self.wait.until(EC.element_to_be_clickable(self.submit_order_button)).click()

    def is_order_modal_displayed(self):
        return self.wait.until(EC.visibility_of_element_located(self.order_modal)).is_displayed()

    def wait_for_driver_info(self):
        # Espera de hasta 60 segundos a que el contador cambie o aparezca información del conductor
        return WebDriverWait(self.driver, 60).until(
            EC.visibility_of_element_located(self.driver_info_header)).is_displayed()

    class TestUrbanRoutes:
        driver = None
        routes_page = None  # Definimos la variable a nivel de clase

        @classmethod
        def setup_class(cls):
            from selenium.webdriver.chrome.options import Options
            options = Options()
            options.set_capability("goog:loggingPrefs", {'performance': 'ALL'})
            cls.driver = webdriver.Chrome(options=options)
            cls.driver.maximize_window()

        def test_set_route(self):
            self.driver.get(data.urban_routes_url)
            # Inicializamos la página asignándola a self.routes_page para que esté disponible en los siguientes tests
            TestUrbanRoutes.routes_page = UrbanRoutesPage(self.driver)

            address_from = data.address_from
            address_to = data.address_to

            # 1. Configurar la dirección
            TestUrbanRoutes.routes_page.set_route(address_from, address_to)
            assert TestUrbanRoutes.routes_page.get_from() == address_from
            assert TestUrbanRoutes.routes_page.get_to() == address_to

        def test_select_comfort_tariff(self):
            # 2. Hacemos clic en el botón "Pedir un taxi" para desplegar las tarifas
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC

            # Esperamos y hacemos clic en el botón inicial
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(TestUrbanRoutes.routes_page.order_button)
            ).click()

            # 3. Ahora seleccionamos la tarifa Comfort
            TestUrbanRoutes.routes_page.select_comfort_tariff()
            assert TestUrbanRoutes.routes_page.check_comfort_selected() is True

    def test_fill_phone_number(self):
        # 3. Rellenar el número de teléfono
        self.routes_page.fill_phone_number(data.phone_number)
        phone_code = retrieve_phone_code(self.driver)
        self.routes_page.enter_phone_code(phone_code)
        assert self.routes_page.get_phone_text() == data.phone_number

    def test_add_credit_card(self):
        # 4. Agregar una tarjeta de crédito
        self.routes_page.add_credit_card(data.card_number, data.card_code)
        assert "Tarjeta" in self.routes_page.get_payment_method_text()

    def test_write_driver_message(self):
        # 5. Escribir un mensaje para el controlador
        self.routes_page.write_driver_message(data.message_for_driver)
        assert self.routes_page.get_driver_message() == data.message_for_driver

    def test_order_blanket_and_tissues(self):
        # 6. Pedir una manta y pañuelos
        self.routes_page.order_blanket_and_tissues()
        assert self.routes_page.is_blanket_ordered() is True

    def test_order_ice_creams(self):
        # 7. Pedir 2 helados
        self.routes_page.order_ice_creams(2)
        assert self.routes_page.get_ice_cream_count() == "2"

    def test_submit_car_order(self):
        # 8. Aparece el modal para buscar un taxi
        self.routes_page.submit_car_order()
        assert self.routes_page.is_order_modal_displayed() is True

    def test_wait_for_driver_info(self):
        # 9. Esperar a que aparezca la información del conductor (Opcional)
        assert self.routes_page.wait_for_driver_info() is True

    @classmethod
    def teardown_class(cls):
        cls.driver.quit()
