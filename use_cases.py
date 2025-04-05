import streamlit as st

class UseCases:
    def __init__(self, repository, presenter):
        self.repository = repository
        self.presenter = presenter
    
    def get_member_performances(self):
        month_offset = self.presenter.get_month_offset()
        
        with st.spinner("読み込み中..."):
            performances = self.repository.get_performances(month_offset)
            self.presenter.display_performances(performances)