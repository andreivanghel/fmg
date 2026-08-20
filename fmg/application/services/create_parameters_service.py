from fmg.application.exceptions import ModelNotFoundError
from fmg.application.interfaces.repositories_interfaces import (
    IModelRepository,
    IParametersRepository,
)
from fmg.domain.entities import ParameterSet


class CreateParametersSetService:
    def __init__(
        self, model_repository: IModelRepository, parameters_repository: IParametersRepository
    ) -> None:
        self.model_repository = model_repository
        self.parameters_repository = parameters_repository

    def execute(self, model_id: int, parameter_version: str, parameter_set: dict) -> int:

        all_models = self.model_repository.get_all_models_ids()
        if model_id not in all_models:
            raise ModelNotFoundError(model_id=model_id)

        p_set = ParameterSet.create(
            model_id=model_id, parameter_version=parameter_version, parameter_set=parameter_set
        )

        p_set_id = self.parameters_repository.create(p_set)

        return p_set_id
