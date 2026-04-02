from domain.entities import ParameterSet
from application.interfaces.repositories_interfaces import IParametersRepository


class CreateParametersSetService:

    def __init__(
            self, 
            model_repository: 
            parameters_repository: IParametersRepository
    ) -> None:
        self.parameters_repository = parameters_repository
    
    def execute(
            self,
            model_id: int,
            parameter_version: str,
            parameter_set: dict
    ) -> int:
        
