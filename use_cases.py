class UseCases:
    def __init__(self, repository, presenter):
        self.repository = repository
        self.presenter = presenter
    
    def get_member_performances(self):
        performances = self.repository.get_performances()
        self.presenter.display_performances(performances)
