from plyer import notification
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.firefox.options import Options


class Alert:
    def __init__(self, region):
        # на веб-сторінці кожна область має свій унікальний id, який буде використовувати програма для відстеження
        # тривог
        self.region_codes = {"Львівська": 27, "Закарпатська": 11, "Івано-Франківська": 13, "Волинська": 8,
                             "Рівненська": 5, "Тернопільська": 21, "Чернівецька": 27, "Хмельницька": 3, "Житомирська":
                                 10, "Вінницька": 4, "Одеська": 18, "Миколаївська": 17, "Кіровоградська": 15,
                             "Черкаська": 24, "Київська": 14, "Чернігівська": 25, "Сумська": 20, "Полтавська": 19,
                             "Дніпропетровська": 9, "Херсонська": 23, "Запорізька": 12, "Донецька": 28, "Луганська":
                                 16, "Харківська": 22, "Київ": 31}
        # знаходимо на сторінці елемент, який відповідає області користувача
        self.region = browser.find_element(By.XPATH, f'//*[@id="{self.region_codes[region]}" and contains(@class, '
                                                     f'"stateObject")]')
        self.name_region = region


# цей клас перевіряє одноразово, чи є тривога зараз у вказаній області
class AlertCheck(Alert):
    def is_alert(self):
        # дамо час сторінці прогрузитися
        time.sleep(1)

        # визначемо статус області
        # в атрибуті class перераховуються класи елементу; якщо тривоги немає, то значення атрибуту дорівнює лише
        # одному класу, а якщо тривога є, то там з'являється значення "regionAlert", яке вказує на факт тривоги
        status = self.region.get_attribute('class')

        if 'regionAlert' in status:
            # перевіряємо, чи id елемента не дорівнює 31 (код міста Києва), бо зміст повідомлення ьуде трохи різнитися
            if self.region.get_attribute('id') == 31:
                return f'Оголошено тривогу в м. {self.name_region}'
            return f'Оголошено тривогу в {self.name_region[:-1]}ій області.'
        else:
            if self.region.get_attribute('id') == 31:
                return f'Тривоги в м. {self.name_region} немає'
            return f'Тривоги в {self.name_region[:-1]}ій області немає.'


# цей клас веде трекінг тривог (відбій/оголошення) та сповіщує користувача повідомленням на комп'ютер
class AlertNotification(Alert):
    def alert_track(self):
        time.sleep(1)
        status = self.region.get_attribute('class')

        # запускаємо бескінечний цикл, який допоможе відслідковувати зміни на сайті
        while True:
            time.sleep(1)
            # перевіряємо кожну секунду статус області та, якщо статус змінився, повідомляємо користувача
            new_status = self.region.get_attribute('class')

            # важливо помітити, що в значенні атрибуту class також з'являються з часом назви інших класів (
            # "regionAlert_60" за приклад), які змінюють колір підсвітки області, якщо тривога там задовга; тому
            # просто перевіряти значення атрибуту не вийде, бо програма буде повідомляти про оголошення тривоги
            # декілька разів (зі зміною підсвітки), тож треба також перевіряти довжину атрибуту class
            if new_status != status and len(new_status.split()) < 3 and new_status is not None:
                status = new_status
                title = 'Увага!' if 'regionAlert' in new_status else 'Інформація'
                if title == 'Увага!':
                    if self.region.get_attribute('id') != 31:
                        message = f'Оголошено тривогу в {self.name_region[:-1]}ій області.'
                    else:
                        message = f'Оголошено тривогу в м. {self.name_region}'
                else:
                    if self.region.get_attribute('id') != 31:
                        message = f'Відбій тривоги в {self.name_region[:-1]}ій області.'
                    else:
                        message = f'Відбій тривоги в м. {self.name_region}'

                # надсилаємо повідомлення на комп'ютер користувачу (завчасно увімкніть сповіщення у системі)
                notification.notify(
                    title=title,
                    message=message,
                    app_name='Повітряні тривоги',
                    timeout=10
                    )


# створюємо клас Options, щоб браузер відкривався у фоновому режимі
firefox_options = Options()
firefox_options.add_argument("--headless")

with webdriver.Firefox(options=firefox_options) as browser:
    browser.get('https://map.ukrainealarm.com/')

    obj = AlertNotification('Дніпропетровська')
    obj.alert_track()
