from application.interfaces.repositories_interfaces import IParametersRepository

class DjangoParametersRepository(IParametersRepository):

    def save(self, parameter_set):
        return super().save(parameter_set)
    
    def get(self, model_id, parameters_id):
        return super().get(model_id, parameters_id)