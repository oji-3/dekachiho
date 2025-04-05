import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()
        self.schedule_url = os.getenv("SCHEDULE_URL")
        self.base_url = os.getenv("BASE_URL")
        self.keyword = os.getenv("KEYWORD")
        self.target_member = os.getenv("TARGET_MEMBER")
        self.weekday_conversion = {
            "MON": "月",
            "TUE": "火",
            "WED": "水",
            "THU": "木",
            "FRI": "金",
            "SAT": "土",
            "SUN": "日"
        }

class Entities:
    class Performance:
        def __init__(self, date, title, url, member, members):
            self.date = date
            self.title = title
            self.url = url
            self.member = member
            self.members = members

class UseCases:
    def __init__(self, repository, presenter):
        self.repository = repository
        self.presenter = presenter
    
    def get_member_performances(self):
        performances = self.repository.get_performances()
        self.presenter.display_performances(performances)

class Repository:
    def __init__(self, config):
        self.config = config
    
    def get_performances(self):
        try:
            res = requests.get(self.config.schedule_url)
            res.raise_for_status()
        except Exception as e:
            return []

        soup = BeautifulSoup(res.text, "html.parser")
        year_month = self._get_year_month(soup)
        performances = []
        
        entries = soup.select("li.schedule_entry_box.clearfix")
        
        for idx, entry in enumerate(entries):
            date_and_week = self._get_date_and_week(entry)
            entry_performances = self._get_performances(entry, self.config.base_url)
            
            for performance in entry_performances:
                title = performance["title"]
                url = performance["url"]
                
                if url:
                    is_appearing, members = self._check_member_in_performance(url, self.config.target_member)
                    if is_appearing:
                        performance_info = Entities.Performance(
                            date=f"{year_month}{date_and_week}",
                            title=title,
                            url=url,
                            member=self.config.target_member,
                            members=members
                        )
                        performances.append(performance_info)
        
        return performances
    
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
            res = requests.get(url, timeout=10)
            res.raise_for_status()
            
            members = self._extract_members_from_html(res.text)
            
            for member in members:
                if member_name in member or self.config.keyword in member:
                    return True, members
                    
            if self.config.keyword in res.text:
                return True, members
            return False, members
            
        except Exception:
            return False, []

class Presenter:
    def __init__(self):
        self._setup_ui()
    
    def _setup_ui(self):
        st.set_page_config(
            page_title="デカチホ",
            layout="wide"
        )
        
        st.markdown("""
        <style>
            .performer {
                padding: 4px 8px;
                margin: 2px;
                border-radius: 4px;
                background-color: #ffffff !important;
                color: #000000 !important;
                display: inline-block;
                border: 1px solid #e0e0e0;
            }
            .performer.highlighted {
                background-color: #ffeb3b !important;
                color: #000000 !important;
                font-weight: bold;
                border: 1px solid #ffc107;
            }
            /* モダンなローディングスタイル */
            .stSpinner > div {
                border-color: #1976D2 !important;
                border-bottom-color: transparent !important;
            }
            /* モダンなアプリスタイル */
            .main .block-container {
                padding-top: 2rem;
                padding-bottom: 2rem;
            }
            h1 {
                margin-bottom: 2rem !important;
            }
        </style>
        """, unsafe_allow_html=True)
        
        st.title("デカチホ")
    
    def _generate_members_html(self, members, target_member):
        html_output = '<div style="margin-top: 10px; margin-bottom: 15px;">'
        
        for member in members:
            if target_member in member:
                html_output += f'<span class="performer highlighted">{member}</span>'
            else:
                html_output += f'<span class="performer">{member}</span>'
        
        html_output += '</div>'
        return html_output
    
    def display_performances(self, performances):
        if performances:
            for i, perf in enumerate(performances):
                with st.container():
                    with st.expander(f"**{perf.date}**　　{perf.title}"):
                        if perf.members and len(perf.members) > 0:
                            members_html = self._generate_members_html(perf.members, perf.member)
                            st.markdown(members_html, unsafe_allow_html=True)
                        else:
                            st.markdown("**出演メンバー情報を取得できませんでした**")
                        
                        st.markdown(f"**公演詳細URL**: [{perf.url}]({perf.url})")
        else:
            st.markdown("デカチホの出演公演情報がありません")

def main():
    config = Config()
    presenter = Presenter()
    repository = Repository(config)
    use_cases = UseCases(repository, presenter)
    
    loading_placeholder = st.empty()
    
    with loading_placeholder.container():
        with st.spinner("データを読み込み中..."):
            if 'performances' not in st.session_state:
                st.session_state.performances = repository.get_performances()
            
            use_cases.get_member_performances()

if __name__ == "__main__":
    main()