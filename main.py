import csv
import re
import urllib.request
from bs4 import BeautifulSoup

BASE_URL = 'http://miet.ru/people/'
MIET_URL = 'http://miet.ru/'

def get_html(url):
    response = urllib.request.urlopen(url)
    return response.read()


def get_letter_link(html):
    soup = BeautifulSoup(html, 'html.parser')
    firstList = soup.find('div', class_ = 'first_list')
    secondList = soup.find('div', class_ = 'second_list')

    letterLinks = []

    for letter in firstList.find_all('a', class_ = 'letter'):
        letterLinks.append({
            'letter': letter.text,
            'link': MIET_URL[:-1] + letter.get('href')
        })

    for letter in secondList.find_all('a', class_ = 'letter'):
        letterLinks.append({
            'letter': letter.text,
            'link': MIET_URL[:-1] + letter.get('href')
        })
    return letterLinks


def get_teacher_link(html):
    soup = BeautifulSoup(html, 'html.parser')
    teachers = soup.find('div', class_ = 'persons')

    teacherLink = []

    for link in teachers.find_all('div', class_ = 'person'):
        teacherLink.append({
            'name': link.h1.text,
            'link': MIET_URL[:-1] + link.a.get('href')
        })
    return teacherLink


def parse(html, link):
    soup = BeautifulSoup(html, 'html.parser')
    information = soup.find('div', class_ = 'person')

    try:
        department = information.find_all('a')[2].text
    except:
        department = 'не указано'

    try:
        occupation = information.find_all('td', class_='pos')[1].text
    except:
        occupation = 'не указана'

    phonePattern = r'\s*(\W\d{3}\W\s\d{3}-\d{2}-\d{2})\s*'
    mailPattern = r'\w+@\w+.\w{1,4}'
    hallPattern = r':\s*(\d{4}\w*)'
    mail = re.search(mailPattern, str(information))
    phone = re.search(phonePattern, str(information))
    hall = re.search(hallPattern, str(information))

    teacherInfo = []

    teacherInfo.append({
        'name': information.h1.text,
        'department': department,
        'occupation': occupation,
        'hall': hall.group(0)[2:] if hall else 'не указана',
        'phone': phone.group(0) if phone else 'не указан',
        'mail': mail.group(0) if mail else 'не указан',
        'link': link,
        'photo': MIET_URL[:-1] + information.find('img').get('src')
      })
    return teacherInfo


def save(teachers, path):
    with open(path, 'w', newline = '') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(('ФИО', 'Подразделение', 'Должность' 'Аудитория', 'Телефон', 'E-mail', 'Ссылка', 'Ссылка на фото'))

        for teacher in teachers:
            writer.writerow((teacher['name'], teacher['department'], teacher['occupation'], teacher['hall'], teacher['phone'], teacher['mail'], teacher['link'], teacher['photo']))


def main():
    letterLink = get_letter_link(get_html(BASE_URL))
    teacherLink = []
    teacherInfo = []

    for link in letterLink:
        teacherLink.extend(get_teacher_link((get_html(link['link']))))

    for teacher in teacherLink:
        teacherInfo.extend(parse(get_html(teacher['link']), teacher['link']))

    save(teacherInfo, "info.csv")


if __name__ == '__main__':
    main()