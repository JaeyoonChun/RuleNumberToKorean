import re
import json


class NumToWord:
    def __init__(self):
        # 숫자 앞 뒤 한 어절만 잘라서 숫자 읽기 방식을 정한다.
        self.pat_base = re.compile(
            r'([가-힣A-Za-z.,ε_\]]*\s?)([\+\-\–\±$＄￦￥]*\d[^\]가-힣\nε]*[^\]가-힣 \nε]*)(\s?[가-힣A-Za-z.,ε\]]*)')
        
        self.pat_num = re.compile(r'(\d+(?:,\d{3})*(?:\.\d+)?)')
        self.pat_not_num = re.compile(r'[^\d.,]')
        self.kor_clf = re.compile(
            r'^(?:시간|군데|마리|가지|사람|개사|보루|경기|글자|번째|박스|조각|켤레|상자|봉지|통|잔|곡|자리|째|분께|단어|정거장|좌석|석|컵|골|벌|겹|세트|달(?!러)|시(?!즌|리즈|접|속)|개(?![년월국])|매|건(?!조)|구(?!역)|장(?!비|기)|차례|종류|종목|바늘|[명줄살잔해곳배갑병발척권])')
        self.format = re.compile('εε (.*) εε')
        self.space = re.compile('\s{2,}')
        self.sign = re.compile(
            r'([^일이삼사오육칠팔구십백천만억조]\s)([\+\-\–\±])(\s?[영일이삼사오육칠팔구십백천만억조])')

        self.exc = (
            ('대', 3, re.compile(r'(?:차량|객차|전기차|수소차|버스|헬리콥터|비행기|항공기|택시|외관|제품|장비|전투기|컴퓨터|기계|차|기기).*? 대(?!책)')),
            ('번째', 2, re.compile('번째')),
            ('폰기종', 0, re.compile(
                r'(?<![a-zA-Z])(?:인보이스|아이폰|갤|갤럭시|홍미|홍노|노트|놋|s|g|v|q|a|j|k)\s?$', re.IGNORECASE)),
            ('통신망', 1, re.compile(r'[345]\s?g(?![a-zA-Z]|/[a-zA-Z])', re.IGNORECASE)),
            ('전화번호', 1, re.compile(r'(?:\d{2,3}\s?-\s?\d{3,4}\s?-\s?\d{4}|(?<![],\.\d-])010\s)')),
            ('화폐', 3, re.compile(r'[$＄￦￥€]')),
            ('월', 3, re.compile(r'(?:6|10) 월')),
            ('기념일', 1, re.compile(r'\b\d{1}\s?[·∙]\s?\d{2}')),
            ('날짜', 1, re.compile(r'\b\d{4}(?:\.|-)\d{1,2}(?:\.|-)\d{1,2}\b')),
            ('만', 3, re.compile(r'(?<!의) 1 [십백천만]')),
            ('영어', 3, re.compile(r'[12345679]\s?(?:season|D(?![a-zA-Z])|K(?![a-zA-Z])|아웃|-way|스타(?!쉽)|샷)', re.IGNORECASE)),
            ('비행기', 3, re.compile(r'(?:행|비행기|[a-zA-Z]|항공) \d+ 편?')),
            ('모델명', 3, re.compile(r'([a-zA-Z]|\d{3,})-\d')),
            ('예약번호', 3, re.compile(r'(번호|전화|코드).{0,4}\d{3,}')),
            ('버전번호', 3, re.compile(r'(?<!\d)\d{1}\.\d{1,}\.\d')),
            ('원쁠원', 1, re.compile(r'1\+1'))
        )

        self.sign_dict = {'+': '플러스', '-': '마이너스', '–': '마이너스', '±': '플러스마이너스'}
        self.ccy_dict = {'$': '달러', '＄': '달러', '￦': '원', '￥': '엔', '€': '유로'}
        self.eng_dict = {'0': '제로', '1': '원', '2': '투', '3': '쓰리', '4': '포', '5': '파이브',
                         '6': '식스', '7': '세븐', '8': '에잇', '9': '나인', '10': '텐', '11': '일레븐'}

        self.chi_dict = {'0': '공', '1': '일', '2': '이', '3': '삼', '4': '사',
                         '5': '오', '6': '육', '7': '칠', '8': '팔', '9': '구'}

        self.unit_dict = {'0': '',
                          '1': '', '2': '십', '3': '백', '4': '천',
                          '5': '만', '6': '십', '7': '백', '8': '천',         # 만
                          '9': '억', '10': '십', '11': '백', '12': '천',      # 억
                          '13': '조', '14': '십', '15': '백', '16': '천'}

        self.kor_dict = {'0': '영', '1': ['한', '첫'], '2': '두', '3': '세', '4': '네',
                         '5': '다섯', '6': '여섯', '7': '일곱', '8': '여덟', '9': '아홉'}
        self.kor_unit_dict = {'0': '', '1': '열',
                              '2': '스물', '3': '서른', '4': '마흔'}

    def convert_kor(self, num, first=False):
        """고유어로 읽어야 하는 숫자를 처리하는 메서드"""
        if '.' in num or ',' in num or int(num) >= 50:
            word = self.pat_num.sub(
                repl=lambda m: self.convert_chi(m.group()), string=num)
        elif num == '20':
            word = '스무'
        else:
            word = ''
            num_len = len(num)
            for char in num:
                if char == '0' and word != '':
                    num_len = num_len - 1
                    continue
                elif char == '1' and num_len == 1:
                    word += self.kor_dict[char][1] if first else self.kor_dict[char][0]
                else:
                    if num_len == 2:
                        word += self.kor_unit_dict[char]
                    else:
                        word += self.kor_dict[char]
                num_len = num_len - 1
        return word
    
    def convert_unit(self, num):
        word = ''
        cnt = 0
        a = num
        while(True):
            if a == 0: break
            a, b = divmod(a, 10)
            if b == 0:
                cnt += 1
                continue
            if cnt == 0:
                word += self.chi_dict[str(b)]
            elif cnt == 1:
                if b == 1:
                    word = '십' + word
                else:
                    word = self.chi_dict[str(b)] + '십' + word
            elif cnt == 2:
                if b == 1:
                    word = '백' + word
                else:
                    word = self.chi_dict[str(b)] + '백' + word
            elif cnt == 3:
                if b == 1:
                    word = '천' + word
                else:
                    word = self.chi_dict[str(b)] + '천' + word
            cnt += 1
        return word

    def convert_chi(self, num):
        """한자어로 읽어야 하는 숫자를 처리하는 메서드"""
        n1 = num
        n1_word, n2_word = '', ''

        if '.' in num:
            n1, n2 = num.split('.')
            n2_word = '쩜'
            for char in n2:
                if char == '0':
                    n2_word += '영'
                else:
                    n2_word += self.chi_dict[char]

        n1 = n1.replace(',', '')
        if n1.count('0') == len(n1):
            n1_word = '영' * n1.count('0')
            return n1_word + n2_word
        if n1[0] == '0':
            n1_word = re.sub('\d', lambda m:self.chi_dict[m.group()], n1)
            return n1_word + n2_word
        cnt = 0
        a = int(n1)
        while(True):
            if a == 0:
                break
            a, b = divmod(a, 10**4)
            if b == 0:
                cnt += 1
                continue
            w = self.convert_unit(b)
            if cnt == 0:
                n1_word += w
            elif cnt == 1:
                if w[-1] == '일' and len(w) == 1:
                    w = ''
                n1_word = w + '만' + n1_word
            elif cnt == 2:
                n1_word = w + '억' + n1_word
            elif cnt == 3:
                n1_word = w + '조' + n1_word
            elif cnt == 4:
                n1_word = w + '경' + n1_word
            elif cnt == 5:
                n1_word = w + '해' + n1_word
            cnt += 1

        return n1_word + n2_word

    def exc_handling(self, text, match_res, total, key):
        """숫자 읽기에서 예외사항을 처리하는 메서드"""
        m1, m2, m3 = match_res
        while self.pat_num.search(m2):
            if key == '대':
                m2 = self.pat_num.sub(
                    repl=lambda m: self.convert_kor(m.group()), string=m2)
                continue
            elif key == '번째':
                m2 = self.pat_num.sub(repl=lambda m: self.convert_kor(
                    m.group(), first=True), string=m2)
                continue
            elif key == '폰기종' or key == '통신망':
                n = self.pat_num.search(m2).group()
                if re.search(f'[가-힣] {n}\s?[a-zA-Z]', m2) or '.' in n or ',' in n:
                    m2 = re.sub(n, self.convert_chi(n), m2)
                elif int(n) > 11 or (n[0] == '0'):
                    m2 = re.sub('\d', repl=lambda m:self.chi_dict[m.group()], string=m2)
                    continue
                else:
                    m2 = re.sub(n, f'{self.eng_dict[n]}', m2)
                    continue
            elif key == '전화번호' or key == '비행기' or key == '모델명' or key == '예약번호':
                m2 = re.sub('\d', repl=lambda m:self.chi_dict[m.group()], string=m2)
                continue
            elif key == '화폐':
                m2 = self.pat_num.sub(
                    repl=lambda m: self.convert_chi(m.group()), string=m2)
                cur = re.search('[$＄￦￥€]', m2).group()
                m2 = re.sub(re.escape(cur), '', m2)
                continue
            elif key == '월':
                n = self.pat_num.search(m2).group()
                if n == '6' or n == '10':
                    word = '유' if '6' in m2 else '시'
                    m2 = re.sub(n, word, m2)
                else:
                    m2 = re.sub(n, self.convert_chi(n), m2)
            elif key == '기념일':
                n = self.pat_num.search(m2).group()
                if len(n) == 2:
                    m2 = re.sub(
                        n, f'{self.chi_dict[n[0]]}{self.chi_dict[n[1]]}', m2)
                else:
                    m2 = re.sub(n, self.convert_chi(n), m2)
            elif key == '날짜':
                date = self.exc[8][2].search(m2).group()
                if '.' in date : n = date.split('.')
                else: n = date.split('-')
                if n[1] == '6' or n[1] == '10':
                    word = '유' if '.6.' in m2 else '시'
                else:
                    word = re.sub(n[1], self.convert_chi(self.pat_num.search(n[1]).group()), n[1])
                m2 = re.sub(f'{n[0]}.', f'{self.convert_chi(self.pat_num.search(n[0]).group())} 년 ', string=m2, count=1)
                m2 = re.sub(f'{n[1]}.', f'{word} 월 ', string=m2, count=1)
                m2 = re.sub(f'{n[2]}', f'{self.convert_chi(self.pat_num.search(n[2]).group())} 일 ', string=m2, count=1)
                return re.sub(re.escape(total), f'{m1}{m2}{m3}', text, count=1)
                continue
            elif key == '만':
                n = self.pat_num.search(m2).group()
                if n == '1':
                    m2 = re.sub(n, '', m2, count=1)
                else:
                    m2 = re.sub(n, self.convert_chi(n), m2, count=1)
            elif key == '버전번호':
                m2 = re.sub('\d', repl=lambda m:'영' if m.group()=='0' else self.chi_dict[m.group()], string=m2)
                m2 = re.sub('\.', '쩜', m2)
                continue
            elif key == '영어':
                m2 = re.sub('\d', repl=lambda m:self.eng_dict[m.group()], string=m2)
                continue
            elif key == '원쁠원':
                m2 = re.sub('\d', repl=lambda m:self.eng_dict[m.group()], string=m2)
                m2 = m2.replace('+', ' 플러스 ')
                continue
        if key == '화폐':
            return re.sub(re.escape(total), f'{m1}{m2} {self.ccy_dict[cur]} {m3}', text, count=1)
        return re.sub(re.escape(total), f'{m1}{m2}{m3}', text, count=1)

    def convert(self, text):
        """한국어 숫자 읽기 함수
        예외 처리 > 고유어 > 한자어 순서로 숫자를 변환한다.
        """
        text = f'εε {text} εε'

        while self.pat_base.search(text):
            match_res = self.pat_base.search(text).groups()
            total = ''.join(match_res)
            m1, m2, m3 = match_res
            exc_flag = False
            
            try:    
                for key, idx, val in self.exc:
                    if idx != 3:
                        if val.search(match_res[idx]):
                            if key == '폰기종':
                                if 'A' in m1 and re.search('(?:블록|블럭|%)', total):
                                    break
                            text = self.exc_handling(text, match_res, total, key)
                            exc_flag = True
                            break
                    else:
                        if val.search(total):
                            if key == '예약번호':
                                if re.search('(?:대|호|번|후반)', m3):
                                    if self.pat_num.search(m2).group()[0] != 0:
                                        break
                            text = self.exc_handling(text, match_res, total, key)
                            exc_flag = True
                            break
            except:
                print(text)
                exit()
            if exc_flag:
                continue

            if self.kor_clf.search(m3):
                if self.kor_clf.search(m3).group() == '시':
                    m2_ = self.pat_num.findall(m2)
                    for n in m2_:
                        n = n.replace(',', '')
                        try:
                            if float(n) > 12:
                                m2 = re.sub(n, self.convert_chi(n), m2)
                        except:
                            print(text)
                            exit()
                elif self.kor_clf.search(m3).group() == '시간':
                    if self.pat_num.search(m2).group() == '24':
                        m2 = re.sub('24', '이십사', m2)
                elif '장' in m3:
                    if '제' in m1:
                        m2 = self.pat_num.sub(repl=lambda m:self.convert_chi(m.group()), string=m2)       
                m2 = self.pat_num.sub(
                    repl=lambda m: self.convert_kor(m.group()), string=m2)
            else:
                try:
                    m2 = self.pat_num.sub(
                        repl=lambda m: self.convert_chi(m.group()), string=m2)
                except:
                    print(text)
                    raise
                    exit()

            text = re.sub(re.escape(total), f'{m1}{m2}{m3}', text, count=1)

        text = self.sign.sub(
            repl=lambda m: f'{m.group(1)}{self.sign_dict[m.group(2)]} {m.group(3)}', string=text)
        text = self.format.sub(r'\1', text)
        text = self.space.sub(' ', text)
        return text


if __name__ == '__main__':
    t = '공인 연비는 13.6 km/l, 17.2 m/l이며, 1~2개, 내 휴대폰은 갤8'
    a = NumToWord()
    print(a.convert(t))