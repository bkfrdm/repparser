"""
Python 3.6

3rd party packages:
    - requests
"""

import os
import datetime
from time import sleep

import requests




class Engine:
    """ Persistent requests wrapper.
    Handles all errors except system ones,
    until counter reaches MAX_RETRY value.

    All methods:
    -> requests.Response
    """
    MAX_RETRY = 3
    DELAY = 1.5
    
    def POST(self, *args, **kwargs):
        errors = 0
        while True:
            try:
                sleep(self.DELAY)
                response = requests.post(*args, **kwargs)
                response.raise_for_status()
                return response
            
            except Exception as e:
                if errors == self.MAX_RETRY:
                    raise ConnectionError(e)
                
                print(e.__class__.__name__, e)
                errors += 1


class Scraper(Engine):
    POST_SET = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Length': '452',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Host': 'sinfat.ima.sc.gov.br',
        'Origin': 'http://sinfat.ima.sc.gov.br',
        'Pragma': 'no-cache',
        'Referer': 'http://sinfat.ima.sc.gov.br/relatorio.jsp',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36'
    }

    POST_DOWNLOAD = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Length': '161',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'sinfat.ima.sc.gov.br',
        'Origin': 'http://sinfat.ima.sc.gov.br',
        'Pragma': 'no-cache',
        'Referer': 'http://sinfat.ima.sc.gov.br/relatorio.jsp',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36'
    }

    DATA_SET = {
        'AJAXREQUEST': 'j_id_jsp_1801007148_0',
        'formularioDeEmissaoDeRelatorio': 'formularioDeEmissaoDeRelatorio',
        'javax.faces.ViewState': 'j_id1',
        'formularioDeEmissaoDeRelatorio:j_id_jsp_1801007148_36': 'formularioDeEmissaoDeRelatorio:j_id_jsp_1801007148_36',
    }
    
    DATA_DOWNLOAD = {
        'j_id_jsp_1801007148_253': 'j_id_jsp_1801007148_253',
        'j_id_jsp_1801007148_253:btImprimir.x': '290',
        'j_id_jsp_1801007148_253:btImprimir.y': '508',
        'javax.faces.ViewState': 'j_id1',
    }

    URL = 'http://sinfat.ima.sc.gov.br/publico/relatorios/index_er.jsf'
    MONTHS = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']


    def __init__(self, session_id, reports_types=None, print_state=True):
        self.print_state = print_state

        self.POST_SET['Cookie'] = self.POST_DOWNLOAD['Cookie'] = 'JSESSIONID={}'.format(session_id)

        self.reports_types = range(1, 7) if reports_types is None else reports_types
        self.start_year = 2010
        self.stop_month, self.stop_year = self.current_date()

    def current_date(self) -> (int, int):
        now = datetime.datetime.now()
        return now.month, now.year

    def dates_range(self) -> list:
        dates = [
            (month, month_num, year) for year in range(self.start_year, self.stop_year)
                                         for month_num, month in enumerate(self.MONTHS, start=1)
        ]
        dates.extend(
            [(month, month_num, self.stop_year) for month_num, month in enumerate(self.MONTHS[: self.stop_month], start=1)]
        )

        return dates

    def POST_set_report(self, reports_type, month, month_num, year) -> None:
        self.DATA_SET['formularioDeEmissaoDeRelatorio:inTipoRelatorio'] = str(reports_type)
        self.DATA_SET['formularioDeEmissaoDeRelatorio:j_id_jsp_1801007148_33InputDate'] = '{} 5, {}'.format(month, year)
        self.DATA_SET['formularioDeEmissaoDeRelatorio:j_id_jsp_1801007148_33InputCurrentDate'] = '{:0>2}/{}'.format(month_num, year)
        
        self.POST(self.URL, headers=self.POST_SET, data=self.DATA_SET)
        
    def POST_get_report(self) -> requests.Response:
        return self.POST(self.URL, headers=self.POST_DOWNLOAD, data=self.DATA_DOWNLOAD)

    def exists(self, filepath):
        if os.path.exists(filepath):
            
            if self.print_state:
                print('exists')
                
            return True

    def save(self, file: bytes, filepath) -> None:
        
        if self.print_state:
            print(len(file))
                    
        with open(filepath, 'wb') as OUT:
            OUT.write(file)
    
    def run(self, output_folder):
        dates = self.dates_range()
        
        for reports_type in self.reports_types:
            for month, month_num, year in dates:
                
                if self.print_state:
                    print('Type: {}, date: {}({}) {}, length:'.format(reports_type, month_num, month, year), end=' ')

                filepath = '{}/REL_{}_{}_{}.pdf'.format(output_folder, reports_type, month_num, year)
                if not self.exists(filepath):
                    self.POST_set_report(reports_type, month, month_num, year)
                    response = self.POST_get_report()
                    self.save(response.content, filepath)


def outputs_to(folder_name) -> str:
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)
    return folder_name


def main(session_id, folder_name):
    scraper = Scraper(session_id)
    scraper.run(outputs_to(folder_name))




if __name__ == '__main__':
    main(session_id='6770B1C923A4B663BAF6A40FEFB9877F', folder_name='reports')












