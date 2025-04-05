import streamlit as st

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
            .stSpinner > div {
                border-color: #1976D2 !important;
                border-bottom-color: transparent !important;
            }
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
            st.markdown("出演公演情報がありません")
