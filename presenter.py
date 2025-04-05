import streamlit as st
from datetime import datetime

class Presenter:
    def __init__(self):
        if 'month_offset' not in st.session_state:
            st.session_state['month_offset'] = 0
            
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
            .stSpinner > div {
                border-color: #1976D2 !important;
                border-bottom-color: transparent !important;
            }
            .main .block-container {
                padding-top: 2rem;
                padding-bottom: 2rem;
            }
            h1 {
                margin-bottom: 1rem !important;
            }
            .month-nav-container {
                display: flex !important;
                flex-direction: row !important;
                align-items: center !important;
                justify-content: space-between !important;
                width: 100% !important;
                margin-bottom: 20px !important;
            }
            .month-nav-button {
                width: 120px !important;
                min-width: 120px !important;
            }
            .month-display {
                text-align: center !important;
                flex-grow: 1 !important;
            }
            /* Mobile specific styles */
            @media (max-width: 768px) {
                .month-nav-container {
                    display: flex !important;
                    flex-direction: row !important;
                    margin-bottom: 10px !important;
                }
                .month-nav-button {
                    width: 100px !important;
                    min-width: 100px !important;
                }
                .month-display {
                    padding: 0 5px !important;
                }
            }
        </style>
        """, unsafe_allow_html=True)
        
        st.title("デカチホ")
        
        st.markdown("""
        <div class="month-nav-container">
            <button id="prev-month" class="month-nav-button stButton">LAST MONTH</button>
            <div class="month-display">
                <h3>{}</h3>
            </div>
            <button id="next-month" class="month-nav-button stButton">NEXT MONTH</button>
        </div>
        """.format(self._get_displayed_month()), unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            prev_btn = st.button("←", key="prev_month_btn", on_click=self._prev_month)
        with col3:
            next_btn = st.button("→", key="next_month_btn", on_click=self._next_month)
            
        st.markdown("""
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                const prevBtn = document.getElementById('prev-month');
                const nextBtn = document.getElementById('next-month');
                const hiddenPrevBtn = document.querySelector('button[data-testid="stButton"]:has(div:contains("←"))');
                const hiddenNextBtn = document.querySelector('button[data-testid="stButton"]:has(div:contains("→"))');
                
                prevBtn.addEventListener('click', function() {
                    hiddenPrevBtn.click();
                });
                
                nextBtn.addEventListener('click', function() {
                    hiddenNextBtn.click();
                });
            });
        </script>
        """, unsafe_allow_html=True)
    
    def _prev_month(self):
        st.session_state['month_offset'] -= 1
    
    def _next_month(self):
        st.session_state['month_offset'] += 1
    
    def _get_displayed_month(self):
        current_date = datetime.now()
        target_month = current_date.month + st.session_state['month_offset']
        target_year = current_date.year
        
        while target_month > 12:
            target_month -= 12
            target_year += 1
        while target_month < 1:
            target_month += 12
            target_year -= 1
            
        return f"{target_year}年{target_month}月"
    
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
                        
                        st.markdown(f"**公演URL**: [{perf.url}]({perf.url})")
        else:
            st.markdown("出演公演情報がありません")
    
    def get_month_offset(self):
        return st.session_state['month_offset']