from selenium import webdriver
import time
import os
import csv
import re

base_dir = os.path.dirname(os.path.abspath(__file__))

class Crawlsystem(object):
  def __init__(self):
    global base_dir
    self.url = "https://twitter.com/asanwal/status/1278829625402146816"

  def set_driver(self):
 
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) ' \
        'Chrome/80.0.3987.132 Safari/537.36'
    chrome_option = webdriver.ChromeOptions()
    chrome_option.add_argument('--no-sandbox')
    chrome_option.add_argument('--disable-dev-shm-usage')
    chrome_option.add_argument('--ignore-certificate-errors')
    chrome_option.add_argument("--disable-blink-features=AutomationControlled")
    chrome_option.add_argument(f'user-agent={user_agent}')
    chrome_option.headless = False
    
    driver = webdriver.Chrome(options = chrome_option)
    return driver

  def main(self):
    # /* Create Driver */
    self.driver = self.set_driver()
    print('----- Created Chrome Driver -----')

    # /* Get URL */
    self.driver.get(self.url)
    
    result_dict = {
        'Author' : '',
        'Title' : '',
        'Date' : '',
        'Comment' : '',
        'Reply_list' : list(),
    }

    author = self.driver.find_element_by_xpath('//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div[1]/div/div/div/section/div/div/div/div[1]/div/div/article/div/div/div/div[2]/div[2]/div/div/div/div[1]/a/div/div[1]/div[1]')
    if author:
      result_dict['Author'] = re.sub('\n|\s+', ' ', author.text)

    title = self.driver.find_element_by_xpath('//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div[1]/div/div/div/section/div/div/div/div[1]/div/div/article/div/div/div/div[3]/div[1]')
    if title:
      result_dict['Title'] = re.sub('\n|\s+', ' ', title.text)

    date = self.driver.find_element_by_xpath('//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div[1]/div/div/div/section/div/div/div/div[1]/div/div/article/div/div/div/div[3]/div[3]')
    if date:
      result_dict['Date'] = re.sub('\n|\s+', ' ', date.text)

    comment = self.driver.find_element_by_xpath('//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div[1]/div/div/div/section/div/div/div/div[1]/div/div/article/div/div/div/div[3]/div[4]')
    if comment:
      result_dict['Comment'] = re.sub('\n|\s+', ' ', comment.text)

    reply_list = list()
    reply_text_list = list()
   

    # /* Scroll Down */
    max_height = self.driver.execute_script("return document.body.scrollHeight")
    max_height_flag = 0

    while True:
      # scroll down
      self.driver.execute_script("window.scrollTo(0, " + str(max_height) + ");")
      time.sleep(10)
      # get current document height
      current_height = self.driver.execute_script("return document.body.scrollHeight")

      if current_height > max_height:
        max_height = current_height
        articles = self.driver.find_elements_by_xpath("//div[@class='css-1dbjc4n r-1iusvr4 r-16y2uox r-1777fci r-1mi0q7o']")
        for article in articles:
          try:
            temp_dict = dict()
            temp_dict['replier'] = re.sub('\n|\s+', ' ', article.find_element_by_xpath("./div[1]").text)
            temp_dict['reply_text'] = re.sub('\s+\@', ' @',article.find_element_by_xpath("./div[2]").text)
            if temp_dict['reply_text'] in reply_text_list:
              continue

            try:
              temp_dict['img_url'] = re.sub('\n|\s+', ' ', article.find_element_by_xpath("./div[2]//img").get_attribute("src"))
            except:
              temp_dict['img_url'] = ''
              pass

            print('------------------------')
            print(temp_dict)
            reply_list.append(temp_dict)
            reply_text_list.append(temp_dict['reply_text'])
          except:
            continue

      else:
        max_height_flag += 1
        if max_height_flag > 3:
            max_height_flag = 0
            break
      continue
    
    result_dict['Reply_list'] = reply_list
    
    with open (base_dir + '/result.csv', 'w', encoding="latin1", newline="", errors="ignore") as result_file:
      writer = csv.writer(result_file)

      row = ["Author", result_dict['Author']]
      writer.writerow(row)

      row = ["Title", result_dict['Title']]
      writer.writerow(row)

      row = ["Date", result_dict['Date']]
      writer.writerow(row)

      row = ["Comment", result_dict['Comment']]
      writer.writerow(row)

      row = ["Conversations", '']
      writer.writerow(row)

      for reply in result_dict['Reply_list']:
        row = ['', reply['replier'], reply['reply_text'], reply['img_url']]
        writer.writerow(row)

    # /* Quit Driver */
    self.driver.quit()

if __name__ == '__main__':
  crawlsystem = Crawlsystem()
  crawlsystem.main()
