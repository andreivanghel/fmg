from django.db import models
from domain.enums import RunStatus, EventType, EventRelevance

class FinancialModelORM(models.Model):
    model_id = models.AutoField(primary_key = True)

    model_name = models.CharField(max_length = 200)

    description = models.TextField(blank=True)

    is_active   = models.BooleanField(default=False)

    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "financial_models"

class ModelVersionORM(models.Model):
    model_id = models.ForeignKey(
        FinancialModelORM,
        on_delete = models.PROTECT,
        db_column = "model_id",
        related_name = "versions"
    )

    model_version = models.CharField(max_length = 50)

    approved = models.BooleanField(default = False)

    code_version = models.CharField(max_length = 50)

    created_at = models.DateTimeField()

    class Meta:
        db_table = "model_versions"
        constraints = [
            models.UniqueConstraint(
                fields=['model_id', 'model_version'], 
                name='unique_model_version'
            )
        ]

class ParameterVersionORM(models.Model):
    model_id = models.ForeignKey(
        FinancialModelORM,
        on_delete = models.PROTECT,
        db_column = "model_id",
        related_name = "parameter_sets"
    )

    parameter_version = models.AutoField(primary_key = True)

    approved = models.BooleanField(default = False)

    parameter_set = models.JSONField(default = dict)

    created_at = models.DateTimeField()

    class Meta:
        db_table = "model_parameters"

class ModelRunORM(models.Model):
    run_id = models.AutoField(primary_key = True)

    model_id = models.ForeignKey(
        FinancialModelORM,
        on_delete = models.PROTECT,
        db_column = "model_id",
        related_name = "runs"
    )

    model_version = models.CharField(max_length = 50)

    parameter_version = models.ForeignKey(
        ParameterVersionORM,
        on_delete = models.PROTECT,
        db_column = "parameter_version"
    )

    status = models.CharField(
        max_length = 50,
        choices = [(s.value, s.value) for s in RunStatus]
    )

    created_at = models.DateTimeField()

    completed_at = models.DateTimeField(blank = True, null = True)

    outputs = models.JSONField(blank = True, null = True)

    check_results = models.JSONField(blank = True, null = True)

    error_message = models.TextField(blank = True, null = True)

    class Meta:
        db_table = "model_runs"
    
    
class AnyLogORM(models.Model):
    id = models.AutoField(primary_key = True)

    model_id = models.ForeignKey(
        FinancialModelORM,
        on_delete=models.PROTECT,
        db_column="model_id",
        null=True,
        blank=True,
        related_name="events"
    )

    run_id = models.ForeignKey(
        ModelRunORM,
        on_delete=models.PROTECT,
        db_column="run_id",
        null=True,
        blank=True,
        related_name="events"
    )

    event_type = models.CharField(
        max_length=50,
        choices = [(e.value, e.value) for e in EventType]
    )

    author = models.CharField(
        max_length=150,
        default = "ADMIN"
    )

    details = models.JSONField(default = dict)

    relevance = models.CharField(
        max_length=20,
        choices = [(r.value, r.value) for r in EventRelevance]
    )

    timestamp = models.DateTimeField()

    class Meta:
        db_table = "audit_anylog"
        ordering = ["-timestamp"]
