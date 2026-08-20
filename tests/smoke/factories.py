import factory

from fmg.infra.django.models import (
    FinancialModelORM,
    ModelVersionORM,
    ParameterVersionORM,
)


class FinancialModelORMFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FinancialModelORM

    model_name = factory.Sequence(lambda n: f"portfolio-var-{n}")
    description = "test model"
    is_active = True


class ModelVersionORMFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ModelVersionORM

    model = factory.SubFactory(FinancialModelORMFactory)
    version = "v1"
    code_version = factory.Sequence(lambda n: f"code-v{n}")  # è unique=True, serve univoco
    approved = True


class ParameterVersionORMFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ParameterVersionORM

    model = factory.SubFactory(FinancialModelORMFactory)
    parameter_version = "v1"
    parameter_set = {"confidence": 0.95}
    approved = True
