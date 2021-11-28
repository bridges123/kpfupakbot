import re
import datetime
import requests
import lxml
import json
from bs4 import BeautifulSoup


url = 'https://abiturient.kpfu.ru/entrant/abit_entrant_originals_list?'


def get_info(data):
    req = requests.get(f'{url}p_faculty={data["faculty"]}&p_speciality={data["speciality"]}&p_inst={data["inst"]}&'
                       f'p_typeofstudy={data["study_type"]}&p_category={data["category"]}').text
    soup = BeautifulSoup(req, 'lxml')
    guys_html = soup.find('table', {'id': 't_common'})
    if guys_html is not None:
        guys_html = guys_html.find_all('tr', {'bgcolor': '#ffffff'})
        stolbs_html = soup.find('table', {'id': 't_common'}).find('tr', {'bgcolor': '#ffff80'})
        guys = []
        stolbs = [i.text.strip().replace('\n', '') for i in stolbs_html.find_all('td')]
        guys.append(stolbs)
        for guy_html in guys_html:
            info = [i.text.strip().replace('\n', '') for i in guy_html.find_all('td')]
            guys.append(info)
        p = soup.find('p').find('b').text
        try:
            kolvo = re.search(r'План приема: (\d+)', p).group(1)
        except Exception as ex:
            kolvo = 0
            print(ex)
        guys.append(kolvo)
        guys.append(int(datetime.datetime.now().timestamp()))
        return guys
    return False


def get_all_info():
    i = 0
    all_info = {}
    vuzes = [['0', 'КФУ (Казань)'], ['1', 'КФУ (Наб. Челны)'], ['5', 'КФУ (Елабуга)']]
    institutes = []
    specialities = []
    categories = [['1', 'Бюджет'], ['2', 'Внебюджет']]
    typeofstudies = []
    for vuz in vuzes:
        all_info[vuz[0]] = {}
        req = requests.get(f'{url}p_inst={vuz[0]}').text
        soup = BeautifulSoup(req, 'lxml')
        institutes_html = soup.find('select', {'name': 'p_faculty'}).find_all('option')
        for inst in institutes_html:
            inst_value, inst_name = inst.get('value'), inst.text
            all_info[vuz[0]][inst_value] = {}
            if len(inst_value) > 0:
                institutes.append([inst_value, inst_name])
                req = requests.get(f'{url}p_inst={vuz[0]}&p_faculty={inst_value}').text
                soup = BeautifulSoup(req, 'lxml')
                specialities_html = soup.find('select', {'name': 'p_speciality'}).find_all('option')
                for spec in specialities_html:
                    spec_value, spec_name = spec.get('value'), spec.text
                    all_info[vuz[0]][inst_value][spec_value] = {}
                    if len(spec_value) > 0:
                        specialities.append([spec_value, spec_name])
                        req = requests.get(f'{url}p_inst={vuz[0]}&p_faculty={inst_value}&p_speciality={spec_value}').text
                        soup = BeautifulSoup(req, 'lxml')
                        typeofstudies_html = soup.find('select', {'name': 'p_typeofstudy'}).find_all('option')
                        for type in typeofstudies_html:
                            type_value, type_name = type.get('value'), type.text
                            all_info[vuz[0]][inst_value][spec_value][type_value] = {}
                            if len(type_value) > 0:
                                typeofstudies.append([type_value, type_name])
                                for category in categories:
                                    info = get_info({
                                        'faculty': inst_value,
                                        'speciality': spec_value,
                                        'inst': vuz[0],
                                        'study_type': type_value,
                                        'category': category[0]
                                    })
                                    if info:
                                        all_info[vuz[0]][inst_value][spec_value][type_value][category[0]] = info
                                        print(i)
                                        i += 1
    with open('stolbs.json', 'w') as f:
        json.dump({'vuzes': vuzes, 'institutes': institutes, 'specialities': specialities, 'categories': categories, 'typeofstudies': typeofstudies}, f,
                  indent=4, ensure_ascii=False)
    with open('info.json', 'w') as f:
        json.dump(all_info, f, ensure_ascii=False, indent=4)


def find_guy(id):
    with open('info.json', 'r') as f:
        returns = []
        all_info = json.load(f)
        for vuz in all_info:
            for inst in all_info[vuz]:
                if inst != '':
                    for spec in all_info[vuz][inst]:
                        if spec != '':
                            for type in all_info[vuz][inst][spec]:
                                if type != '':
                                    for category in all_info[vuz][inst][spec][type]:
                                        if category != '':
                                            for chel in all_info[vuz][inst][spec][type][category]:
                                                try:
                                                    if id == chel[1]:
                                                        if (int(datetime.datetime.now().timestamp()) - all_info[vuz][inst][spec][type][category][-1]) > 900:
                                                            info = get_info({
                                                                'faculty': inst,
                                                                'speciality': spec,
                                                                'inst': vuz,
                                                                'study_type': type,
                                                                'category': category
                                                            })
                                                            if info:
                                                                for chelik in info:
                                                                    if chelik[1] == id:
                                                                        all_info[vuz][inst][spec][type][category] = info
                                                                        returns.append({'info': chelik, 'blanks': info[0], 'stolbs': [vuz, inst, spec, type, category], 'other': [all_info[vuz][inst][spec][type][category][-2], all_info[vuz][inst][spec][type][category][-3][0]]})
                                                        else:
                                                            returns.append({'info': chel, 'blanks': all_info[vuz][inst][spec][type][category][0], 'stolbs': [vuz, inst, spec, type, category], 'other': [all_info[vuz][inst][spec][type][category][-2], all_info[vuz][inst][spec][type][category][-3][0]]})
                                                except:
                                                    pass
    with open('info.json', 'w') as f:
        json.dump(all_info, f, indent=4, ensure_ascii=False)
    return returns
