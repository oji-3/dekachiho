import streamlit as st

from config import Config
from repository import Repository
from presenter import Presenter
from use_cases import UseCases

def main():
    config = Config()
    presenter = Presenter()
    repository = Repository(config)
    use_cases = UseCases(repository, presenter)
    
    use_cases.get_member_performances()

if __name__ == "__main__":
    main()