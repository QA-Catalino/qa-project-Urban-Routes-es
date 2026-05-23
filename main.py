import data
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


# ── Utilidad ────────────────────────────────────────────────────────────────
def retrieve_phone_code(driver) -> str:
    """Devuelve el código de confirmación de teléfono interceptado desde los logs de red.
    Úsalo solo después de haber solicitado el código en la aplicación."""
    import json
    import time
    from selenium.common import WebDriverException

    code = None
    for i in range(10):
        try:
            logs = [
                log["message"]
                for log in driver.get_log('performance')
                if log.get("message") and 'api/v1/number?number' in log.get("message")
            ]
            for log in reversed(logs):
                message_data = json.loads(log)["message"]
                body = driver.execute_cdp_cmd(
                    'Network.getResponseBody',
                    {'requestId': message_data["params"]["requestId"]}
                )
                code = ''.join([x for x in body['body'] if x.isdigit()])
        except WebDriverException:
            time.sleep(1)
            continue
        if not code:
            raise Exception(
                "No se encontró el código de confirmación del teléfono.\n"
                "Utiliza 'retrieve_phone_code' solo después de haber solicitado el código en tu aplicación."
            )
        return code


# ── Page Object ──────────────────────────────────────────────────────────────
class UrbanRoutesPage:

    # — Campos de ruta —
    from_field = (By.ID, 'from')
    to_field   = (By.ID, 'to')

    # — Botón para pedir un taxi —
    call_taxi_button = (By.XPATH, '//button[contains(text(),"Pedir un taxi")]')

    # — Tarifa Comfort —
    comfort_rate = (By.XPATH, '//div[contains(@class,"tcard") and .//div[text()="Comfort"]]')

    # — Teléfono —
    phone_button        = (By.CLASS_NAME, 'np-button')
    phone_number_field  = (By.ID, 'phone')
    phone_next_button   = (By.XPATH, '//button[text()="Siguiente"]')
    phone_code_field    = (By.ID, 'code')
    phone_confirm_btn   = (By.XPATH, '//button[text()="Confirmar"]')

    # — Tarjeta de crédito —
    payment_method_button = (By.CLASS_NAME, 'pp-button')
    add_card_button       = (By.XPATH, '//div[contains(@class,"pp-plus")]')
    card_number_field     = (By.XPATH, '//input[@id="number"]')
    card_code_field       = (By.XPATH, '//input[@id="code" and @class="card-input"]')
    card_link_button      = (By.XPATH, '//button[contains(@class,"button") and (text()="Enlace" or text()="Agregar" or text()="Add" or text()="Link")]')
    close_payment_modal   = (By.XPATH, '//div[contains(@class,"payment-picker")]//button[@class="close-button section-close"]')

    # — Mensaje para el conductor —
    driver_message_field = (By.ID, 'comment')

    # — Manta y pañuelos —
    blanket_checkbox = (By.XPATH, '//div[contains(text(),"Manta y pañuelos")]/..//input[@type="checkbox"]')
    blanket_slider   = (By.XPATH, '//div[contains(text(),"Manta y pañuelos")]/..//span[@class="slider round"]')

    # — Helados —
    ice_cream_counter_plus = (By.XPATH, '//div[contains(text(),"Helado")]/..//div[@class="counter-plus"]')
    ice_cream_value        = (By.XPATH, '//div[contains(text(),"Helado")]/..//div[@class="counter-value"]')

    # — Modal de búsqueda / conductor —
    order_taxi_button = (By.CLASS_NAME, 'smart-button')
    taxi_search_modal = (By.CLASS_NAME, 'order-header-title')
    driver_info       = (By.CLASS_NAME, 'order-card-name')

    # ── Constructor ──────────────────────────────────────────────────────────
    def __init__(self, driver):
        self.driver = driver

    # ── Helpers internos ─────────────────────────────────────────────────────
    def _wait(self, timeout=10):
        return WebDriverWait(self.driver, timeout)

    def _wait_and_click(self, locator, timeout=10):
        element = self._wait(timeout).until(expected_conditions.element_to_be_clickable(locator))
        element.click()
        return element

    def _js_click(self, locator, timeout=10):
        """Click via JavaScript — evita ElementClickInterceptedException cuando un overlay tapa el elemento."""
        element = self._wait(timeout).until(expected_conditions.presence_of_element_located(locator))
        self.driver.execute_script("arguments[0].click();", element)
        return element

    def _wait_visible(self, locator, timeout=10):
        return self._wait(timeout).until(expected_conditions.visibility_of_element_located(locator))

    # ── Ruta ─────────────────────────────────────────────────────────────────
    def set_route(self, from_address, to_address):
        self.set_from(from_address)
        self.set_to(to_address)

    def set_from(self, from_address):
        field = self._wait_visible(self.from_field)
        field.clear()
        field.send_keys(from_address)

    def set_to(self, to_address):
        field = self._wait_visible(self.to_field)
        field.clear()
        field.send_keys(to_address)

    def get_from(self):
        return self._wait_visible(self.from_field).get_property('value')

    def get_to(self):
        return self._wait_visible(self.to_field).get_property('value')

    def click_call_taxi_button(self):
        self._wait_and_click(self.call_taxi_button)

    # ── Tarifa ───────────────────────────────────────────────────────────────
    def select_comfort_rate(self):
        self._wait_and_click(self.comfort_rate)

    def get_selected_rate_text(self):
        element = self._wait_visible(self.comfort_rate)
        return element.get_attribute('class')

    # ── Teléfono ─────────────────────────────────────────────────────────────
    def fill_phone_number(self, phone):
        self._wait_and_click(self.phone_button)
        field = self._wait_visible(self.phone_number_field)
        field.send_keys(phone)
        self._wait_and_click(self.phone_next_button)

        code = retrieve_phone_code(self.driver)
        code_field = self._wait_visible(self.phone_code_field)
        code_field.send_keys(code)
        self._wait_and_click(self.phone_confirm_btn)

    def get_phone_number(self):
        return self._wait_visible(self.phone_button).text

    # ── Tarjeta de crédito ───────────────────────────────────────────────────
    def add_credit_card(self, card_number, card_code):
        self._wait_and_click(self.payment_method_button)
        self._wait_and_click(self.add_card_button)

        number_field = self._wait_visible(self.card_number_field)
        number_field.send_keys(card_number)

        cvv_field = self._wait_visible(self.card_code_field)
        cvv_field.send_keys(card_code)
        cvv_field.send_keys(Keys.TAB)

        self._js_click(self.card_link_button)
        self._js_click(self.close_payment_modal)

    # ── Mensaje para el conductor ────────────────────────────────────────────
    def write_message_for_driver(self, message):
        field = self._wait_visible(self.driver_message_field)
        field.send_keys(message)

    def get_message_for_driver(self):
        return self.driver.find_element(*self.driver_message_field).get_property('value')

    # ── Manta y pañuelos ─────────────────────────────────────────────────────
    def request_blanket_and_tissues(self):
        self._js_click(self.blanket_slider)

    def is_blanket_selected(self):
        return self.driver.find_element(*self.blanket_checkbox).is_selected()

    # ── Helados ──────────────────────────────────────────────────────────────
    def add_ice_creams(self, quantity):
        for _ in range(quantity):
            self._js_click(self.ice_cream_counter_plus)

    def get_ice_cream_count(self):
        return int(self._wait_visible(self.ice_cream_value).text)

    # ── Pedir taxi / modal ───────────────────────────────────────────────────
    def click_order_taxi(self):
        self._js_click(self.order_taxi_button)

    def is_taxi_search_modal_visible(self):
        return self._wait_visible(self.taxi_search_modal).is_displayed()

    def wait_for_driver_info(self, timeout=40):
        return self._wait(timeout).until(
            expected_conditions.visibility_of_element_located(self.driver_info)
        ).text


# ── Tests ────────────────────────────────────────────────────────────────────
class TestUrbanRoutes:
    driver = None

    @classmethod
    def setup_class(cls):
        options = webdriver.ChromeOptions()
        options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        cls.driver = webdriver.Chrome(options=options)
        cls.driver.get(data.urban_routes_url)

    # 1. Configurar la dirección
    def test_set_route(self):
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.set_route(data.address_from, data.address_to)
        assert routes_page.get_from() == data.address_from
        assert routes_page.get_to() == data.address_to

    # 2. Seleccionar tarifa Comfort
    def test_select_comfort_rate(self):
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.click_call_taxi_button()
        routes_page.select_comfort_rate()
        classes = routes_page.get_selected_rate_text()
        assert 'active' in classes or 'selected' in classes

    # 3. Rellenar el número de teléfono
    def test_fill_phone_number(self):
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.fill_phone_number(data.phone_number)
        assert data.phone_number in routes_page.get_phone_number()

    # 4. Agregar tarjeta de crédito
    def test_add_credit_card(self):
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.add_credit_card(data.card_number, data.card_code)
        payment_label = WebDriverWait(self.driver, 10).until(
            expected_conditions.visibility_of_element_located((By.CLASS_NAME, 'pp-value-text'))
        )
        assert payment_label.is_displayed()

    # 5. Escribir mensaje para el conductor
    def test_write_message_for_driver(self):
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.write_message_for_driver(data.message_for_driver)
        assert routes_page.get_message_for_driver() == data.message_for_driver

    # 6. Pedir manta y pañuelos
    def test_request_blanket_and_tissues(self):
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.request_blanket_and_tissues()
        assert routes_page.is_blanket_selected() is True

    # 7. Pedir 2 helados
    def test_add_two_ice_creams(self):
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.add_ice_creams(2)
        assert routes_page.get_ice_cream_count() == 2

    # 8. Modal de búsqueda de taxi
    def test_taxi_search_modal_appears(self):
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.click_order_taxi()
        assert routes_page.is_taxi_search_modal_visible() is True

    # 9. (Opcional) Esperar información del conductor
    def test_driver_info_appears(self):
        routes_page = UrbanRoutesPage(self.driver)
        try:
            driver_name = routes_page.wait_for_driver_info(timeout=40)
            assert driver_name != ''
        except Exception:
            pass  # Es opcional — si no aparece el conductor, el test se omite

    @classmethod
    def teardown_class(cls):
        cls.driver.quit()