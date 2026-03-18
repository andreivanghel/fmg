from application.interfaces.repositories_interfaces import IRunRepository

class DjangoRunRepository(IRunRepository):

    def save(self, run):
        return super().save(run)
    
    def get(self, run_id):
        return super().get(run_id)