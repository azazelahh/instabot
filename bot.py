import os
import time
import random
import datetime
import lexicon
import emoji
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
import smtplib, ssl


class InstaBot:

    def __init__(self, username, password):
        self.username = username
        self.password = password

        self.comment_success_count = 0

        # GOOGLE_CHROME_BIN = os.environ.get('GOOGLE_CHROME_BIN')
        # CHROMEDRIVER_PATH = os.environ.get('CHROMEDRIVER_PATH')
        # chrome_options = webdriver.ChromeOptions()
        # chrome_options.binary_location = GOOGLE_CHROME_BIN
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-gpu')
        # chrome_options.add_argument('--no-sandbox')
        # self.driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=chrome_options)  
        self.driver = webdriver.Chrome('./chromedriver')
       

    def login(self):
        self.driver.get('https://www.instagram.com/accounts/login/')
        time.sleep(2)
        username_element = self.driver.find_element_by_name('username')
        username_element.clear()
        username_element.send_keys(self.username)
        password_element = self.driver.find_element_by_name('password')
        password_element.clear()
        password_element.send_keys(self.password)
        password_element.send_keys(Keys.RETURN)
        time.sleep(4)

        
    def run(self):
        top_posts = self.get_top_posts(11)
        for post in top_posts:
            try:
                print('Accessing post {}'.format(post))
                self.engage(post)
            except Exception as e:
                log(post)
                log(str(e))


    def engage(self, post):

        self.driver.get(post)
        time.sleep(1)

        self.like()
        time.sleep(2)

        self.comment()
        time.sleep(1)

        self.comment_success_count = self.comment_success_count + 1
        sleep_time = random.randint(28, 34)
        time.sleep(sleep_time)


    def get_top_posts(self, n):
        top_posts = []

        for hashtag in lexicon.HASHTAGS:
            self.driver.get('https://www.instagram.com/explore/tags/' + hashtag + '/')
            time.sleep(2)

            links = self.driver.find_elements_by_tag_name('a')

            for i in range(0, n):
                if i < len(links):
                    link = links[i].get_attribute('href')
                    if link not in top_posts:
                        top_posts.append(link)

        return top_posts


    def like(self):
        like_button = self.driver.find_element_by_xpath("//span[@aria-label='Like']")
        like_button.click()
        print('Post was liked')


    def comment(self):

        comment_area = lambda: self.driver.find_elements_by_tag_name('textarea')[0]
        comment_area().click()
        comment_area().clear()

        comment = random.choice(lexicon.COMMENTS)

        try:

            for letter in comment:
                comment_area().send_keys(letter)
                key_press_delay = random.randint(1, 7) / 30
                time.sleep(key_press_delay)

            comment_area().send_keys(Keys.RETURN)
            print('Post was commented on {0}'.format(comment))

        except Exception as e:
            print("Failed to comment {0}".format(comment))
            print(str(e))

def send_email(subject, message, sender_email, receiver_email, password):
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"  
    message = 'Subject: {}\n\n{}'.format(subject, message)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)

def log(message):

    log_file = open('log.txt', 'a+')
    log_file.write(message + '\n')
    log_file.close()


if __name__ == '__main__':

   

    print("Just woke up at {0}".format(datetime.datetime.now()))
    comment_success_count = 0

    try:
        username = os.environ.get('INSTAGRAM_USERNAME')
        password = os.environ.get('INSTAGRAM_PASSWORD')
        bot = InstaBot(username, password)
        bot.login()
        bot.run()
        comment_success_count = bot.comment_success_count
        
    except WebDriverException as e:
        log(str(e.msg))
        ##send failure text notification

    finally:
        bot.driver.close()

    message = "Finished execution at {0} \n Successful comment count {1}".format(datetime.datetime.now(), comment_success_count)
    log(message)
    print(message)
