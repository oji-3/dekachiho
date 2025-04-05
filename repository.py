import requests
from bs4 import BeautifulSoup
import re
import time
import random
import concurrent.futures
from functools import partial
from datetime import datetime

from entities import Performance

class Repository:
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3',
        })
        self.cache = {}
    
    def get_performances(self, month_offset=0):
        # Only fetch for the specified month
        url = self.config.schedule_url if month_offset == 0 else self._get_url_for_month_offset(month_offset)
        performances = self._fetch_performances(url)
        return self._process_performances_in_batches(performances)
    
    def _get_url_for_month_offset(self, month_offset):
        # Get current date
        current_date = datetime.now()
        
        # Calculate target month and year based on offset
        target_month = current_date.month + month_offset
        target_year = current_date.year
        
        # Adjust for year boundaries
        while target_month > 12:
            target_month -= 12
            target_year += 1
        while target_month < 1:
            target_month += 12
            target_year -= 1
        
        # Try to detect and replace any existing year/month pattern
        pattern = re.compile(r'(/\d{4}/\d{1,2}/)')
        match = pattern.search(self.config.schedule_url)
        
        if match:
            # Replace existing pattern
            return self.config.schedule_url.replace(match.group(1), f"/{target_year}/{target_month}/")
        else:
            # Append new pattern
            base_url = self.config.schedule_url.rstrip('/')
            return f"{base_url}/{target_year}/{target_month}/"
    
    def _fetch_performances(self, url):
        try:
            res = self.session.get(url, timeout=self.config.request_timeout)
            res.raise_for_status()
        except Exception:
            return []

        soup = BeautifulSoup(res.text, "html.parser")
        year_month = self._get_year_month(soup)

        performance_data = []
        entries = soup.select("li.schedule_entry_box.clearfix")
        
        for entry in entries:
            date_and_week = self._get_date_and_week(entry)
            entry_performances = self._get_performances(entry, self.config.base_url)
            
            for performance in entry_performances:
                title = performance["title"]
                url = performance["url"]
                
                if url:
                    performance_data.append({
                        "date": f"{year_month}{date_and_week}",
                        "title": title,
                        "url": url
                    })
        
        return performance_data
    
    def _process_performances_in_batches(self, performance_data):
        performances = []
        total_performances = len(performance_data)
        
        for i in range(0, total_performances, self.config.batch_size):
            batch = performance_data[i:i + self.config.batch_size]
            batch_results = self._process_batch(batch)
            performances.extend(batch_results)
            
            time.sleep(random.uniform(0.5, 1.0))
        
        return performances
    
    def _process_batch(self, batch):
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            check_func = partial(self._check_performance_worker, 
                                target_member=self.config.target_member,
                                keyword=self.config.keyword)
            
            future_to_perf = {
                executor.submit(check_func, perf): perf 
                for perf in batch
            }
            
            for future in concurrent.futures.as_completed(future_to_perf):
                perf = future_to_perf[future]
                try:
                    is_appearing, members = future.result()
                    if is_appearing:
                        performance_info = Performance(
                            date=perf["date"],
                            title=perf["title"],
                            url=perf["url"],
                            member=self.config.target_member,
                            members=members
                        )
                        results.append(performance_info)
                except Exception:
                    pass
        
        return results

    def _check_performance_worker(self, performance, target_member, keyword):
        url = performance["url"]
        
        if url in self.cache:
            return self.cache[url]
            
        for attempt in range(self.config.retry_count + 1):
            try:
                result = self._check_member_in_performance(url, target_member)
                self.cache[url] = result
                return result
            except Exception:
                if attempt < self.config.retry_count:
                    time.sleep(random.uniform(0.5, 1.5))
                else:
                    self.cache[url] = (False, [])
                    return False, []
    
    def _get_year_month(self, soup):
        month = soup.select_one("p.month").contents[0].strip() if soup.select_one("p.month") else ""
        year = soup.select_one("span.year").text.strip() if soup.select_one("span.year") else ""
        return f"{year}年{month}月"
    
    def _get_date_and_week(self, entry):
        date = entry.select_one("p.date span.md").text if entry.select_one("p.date span.md") else ""
        week = entry.select_one("p.date span.week").text if entry.select_one("p.date span.week") else ""
        
        for eng, jpn in self.config.weekday_conversion.items():
            week = week.replace(eng, jpn)
            
        return f"{date}日({week})"
    
    def _get_performances(self, entry, base_url):
        performances = []
        for performance in entry.select("div.entry.live02.cat17"):
            title = performance.select_one("p.tit").text if performance.select_one("p.tit") else ""
            url_tag = performance.select_one("a")
            url = base_url + url_tag['href'] if url_tag and 'href' in url_tag.attrs else ""
            performances.append({
                "title": title,
                "url": url
            })
        return performances
    
    def _extract_members_from_html(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        member_spans = []
        
        spans = soup.find_all('span')
        for span in spans:
            if 'メンバー：' in span.text:
                member_spans.append(span)
        
        if member_spans:
            members_text = member_spans[0].text
            members_text = members_text.replace('メンバー：', '')
            members_text = re.sub(r'<.*?>', '', members_text)
            members_list = [name.strip() for name in members_text.split('・')]
            
            cleaned_members = []
            for member in members_list:
                member = re.sub(r'\s+', ' ', member).strip()
                if member and not re.search(r'o:p|EN-US', member):
                    cleaned_members.append(member)
            
            return cleaned_members
        
        text = soup.get_text()
        member_pattern = re.compile(r'メンバー：(.*?)(?:\n|※|【|\[)', re.DOTALL)
        match = member_pattern.search(text)
        
        if match:
            members_text = match.group(1).strip()
            members_list = [name.strip() for name in members_text.split('・')]
            return [m for m in members_list if m and len(m) > 0]
        
        return []
    
    def _check_member_in_performance(self, url, member_name):
        try:
            res = self.session.get(url, timeout=self.config.request_timeout)
            res.raise_for_status()
            
            members = self._extract_members_from_html(res.text)
            
            for member in members:
                if member_name in member or self.config.keyword in member:
                    return True, members
                    
            if self.config.keyword in res.text:
                return True, members
            return False, members
            
        except Exception as e:
            raise Exception(f"ページの取得エラー: {str(e)}")