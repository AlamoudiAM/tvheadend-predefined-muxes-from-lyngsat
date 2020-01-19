# NOTE: THIS CODE IS ONLY TESTED AGAINST DVB-S MUXES, YOU ARE FREE TO FORK IT AND MODIFY IT

import requests
from bs4 import BeautifulSoup
import re


# filter row's cells based on specific regular expression and remove html tags
def target_and_remove_html(cell, regx):
    cell = filter(lambda x: re.match(regx, x.text), cell)
    cell = map(lambda x: x.text, cell)
    return list(cell)


# parse html and get muxes out of it
def get_muxes(r):
    soup = BeautifulSoup(r.text, 'html.parser')
    muxes = []
    for table in soup.select('table'):
        for row in table.select('tr'):
            # e.g. 'DVB-S', 'DVB-S2'
            delivery_re = '^DVB-S.*'
            delivery = row.select('td:nth-child(6) > font > font')
            delivery = target_and_remove_html(delivery, delivery_re)

            # e.g. '11727\xa0H', '11747\xa0V'
            freq_and_polarization_re = '\d{5}'
            freq_and_polarization = row.select('td:nth-child(2) > font > font:nth-child(1) > b')
            freq_and_polarization = target_and_remove_html(freq_and_polarization, freq_and_polarization_re)

            # e.g. '30000-3/48PSK', '27500-5/6'
            symbol_rate_and_fec_and_modulation_re = '\d+-'
            symbol_rate_and_fec_and_modulation = row.select('td:nth-child(7) > font')
            symbol_rate_and_fec_and_modulation = target_and_remove_html(
                symbol_rate_and_fec_and_modulation,
                symbol_rate_and_fec_and_modulation_re
            )

            if delivery and freq_and_polarization and symbol_rate_and_fec_and_modulation:
                delivery = delivery[0]
                freq = freq_and_polarization[0].split('\xa0')[0]
                polarization = freq_and_polarization[0].split('\xa0')[1]
                symbol_rate = symbol_rate_and_fec_and_modulation[0].split('-')[0]
                fec = symbol_rate_and_fec_and_modulation[0].split('-')[1][:3]
                modulation = symbol_rate_and_fec_and_modulation[0].split('-')[1][3:]
                modulation = modulation.split('\xa0')[0]
                muxes.append([delivery, freq, polarization, symbol_rate, fec, modulation])

    return muxes


def get_page(url):
    # header is from my chrome console
    return requests.get(url, headers={
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'www.lyngsat.com',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
    })


# write muxes as predefined muxes file to be used for for tvheadend
def write_muxes_to_file(muxes, file_name):
    file_string = ''

    for mux in muxes:
        file_string += '[CHANNEL]\n'
        file_string += '\tDELIVERY_SYSTEM = {}\n'.format(mux[0].replace('-', ''))
        file_string += '\tFREQUENCY = {}000\n'.format(mux[1])

        if mux[2] == 'V':
            file_string += '\tPOLARIZATION = VERTICAL\n'
        else:
            file_string += '\tPOLARIZATION = HORIZONTAL\n'

        file_string += '\tSYMBOL_RATE = {}000\n'.format(mux[3])
        file_string += '\tINNER_FEC = {}\n'.format(mux[4])

        if mux[5]:
            if '8PSK' in mux[5]:
                file_string += '\tINVERSION = PSK/8\n\n'
            elif 'QPSK' in mux[5]:
                file_string += '\tINVERSION = QPSK\n\n'
            else:
                file_string += '\tINVERSION = {}\n\n'.format(mux[5])

        else:
            file_string += '\tINVERSION = AUTO\n\n'

    with open('./output/' + file_name, 'w') as file:
        file.write(file_string)


if __name__ == '__main__':

    # contains urls from lyngsat and the output file names
    muxes_meta = {
        'nilesat': {
            'url': 'https://www.lyngsat.com/Nilesat-201.html',
            'file_name': 'Nilesat101+102-7.0W'
        },
        'nilesat_hd': {
            'url': 'https://www.lyngsat.com/hd/Nilesat-201.html',
            'file_name': 'NilesatHD101+102-7.0W'
        },
        'eutelsat7': {
            'url': 'https://www.lyngsat.com/Eutelsat-7-West-A.html',
            'file_name': 'Eutelsat7West-7.3W'
        },
        'eutelsat7_hd': {
            'url': 'https://www.lyngsat.com/hd/Eutelsat-7-West-A.html',
            'file_name': 'EutelsatHD7WestA-7.3W'
        },
        'eutelsat8': {
            'url': 'https://www.lyngsat.com/Eutelsat-8-West-B.html',
            'file_name': 'Eutelsat8WestB-8.0W'
        },
        'eutelsat8_hd': {
            'url': 'https://www.lyngsat.com/hd/Eutelsat-8-West-B.html',
            'file_name': 'EutelsatHD8WestB-8.0W'
        }
    }

    # loop through urls > parse them > generate muxes > save them
    for mux_meta in muxes_meta.values():
        request = get_page(mux_meta['url'])
        mux = get_muxes(request)
        write_muxes_to_file(mux, mux_meta['file_name'])
