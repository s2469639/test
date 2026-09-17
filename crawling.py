import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import time

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.kotra.or.kr/subList/20000020753',
    'Origin': 'https://www.kotra.or.kr',
    'X-Requested-With': 'XMLHttpRequest',
    'Accept': '*/*'
})

# 세션 초기화
session.get('https://www.kotra.or.kr/subList/20000020753', timeout=10)

api_url = 'https://www.kotra.or.kr/module/subhome/bizAply/selectBmBizRcritYListNewAjax.do'

all_items = []
max_pages = 5

for page in range(1, max_pages + 1):
    print(f"[{page}페이지 수집 중...]")
    
    # 필수 메뉴 파라미터 보완
    payload = {
        'pageIndex': page,
        'recordCountPerPage': 10,
        'subhomeSeq': '',
        'searchCondition': '',
        'searchKeyword': '',
        'menuNo': '20000020753'
    }
    
    try:
        response = session.post(api_url, data=payload, timeout=10)
        response.raise_for_status()
        
        # [디버깅] 1페이지에서 서버가 실제로 내려준 내용 앞부분 확인
        if page == 1:
            print("--- [서버 응답 앞 300자 미리보기] ---")
            print(response.text[:300])
            print("-------------------------------------")
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # class="card" 뿐만 아니라 card를 포함하는 class 모두 검색
        cards = soup.find_all('div', class_=re.compile(r'\bcard\b'))
        
        if not cards:
            # card 태그가 없을 경우 대체 구조(li 등) 탐색
            cards = soup.select('.card-list > li') or soup.find_all('div', class_='item')
            
        if not cards:
            print(f"-> {page}페이지에 공고 카드를 찾지 못했습니다.")
            break
            
        for card in cards:
            title_tag = card.find('a', class_='card-tit') or card.find('strong', class_='tit')
            title = title_tag.get_text(strip=True) if title_tag else "정보 없음"
            
            card_text = card.get_text(separator='\n')
            
            period_match = re.search(r'신청기간\s*[:]?\s*([0-9.\-~ ]+)', card_text)
            period = period_match.group(1).strip() if period_match else "정보 없음"
            
            tel_match = re.search(r'전화번호\s*[:]?\s*([+0-9\- /]+)', card_text)
            tel = tel_match.group(1).strip() if tel_match else "정보 없음"
            
            email_match = re.search(r'이메일\s*[:]?\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', card_text)
            email = email_match.group(1).strip() if email_match else "정보 없음"
            
            all_items.append({
                '사업명': title,
                '신청기간': period,
                '전화번호': tel,
                '이메일': email
            })
            
    except Exception as e:
        print(f"오류 발생: {e}")
        break
        
    time.sleep(1.2)

df = pd.DataFrame(all_items)
print(f"\n총 {len(df)}건 수집 완료!")
if not df.empty:
    print(df.head())
    df.to_csv('kotra_biz_list.csv', index=False, encoding='utf-8-sig')