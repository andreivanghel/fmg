from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models import Q
from domain.enums import RunStatus, EventType, EventRelevance

class FinancialModelORM(models.Model):
    model_id = models.AutoField(primary_key = True)

    model_name = models.CharField(max_length = 200, unique = True)

    description = models.TextField(blank=True)

    is_active   = models.BooleanField(default=False)

    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "financial_models"
        indexes = [
            models.Index(fields=["is_active"])
        ]



class ModelVersionORM(models.Model):
    version_id = models.AutoField(primary_key = True)

    model = models.ForeignKey(
        FinancialModelORM,
        on_delete = models.PROTECT,
        db_column = "model_id",
        related_name = "versions"
    )

    version = models.CharField(max_length = 50)

    code_version = models.CharField(max_length = 50, unique = True)

    approved = models.BooleanField(default = False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "model_versions"
        constraints = [
            models.UniqueConstraint(
                fields=['model_id', 'version'], 
                name='unique_model_version'
            )
        ]
        indexes = [
            models.Index(fields=["approved"]),
        ]



class ParameterVersionORM(models.Model):
    parameter_version_id = models.AutoField(primary_key = True)

    model = models.ForeignKey(
        FinancialModelORM,
        on_delete = models.PROTECT,
        db_column = "model_id",
        related_name = "parameter_sets"
    )

    parameter_version = models.CharField(max_length = 50)

    parameter_set = models.JSONField(encoder=DjangoJSONEncoder, default = dict)

    approved = models.BooleanField(default = False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "model_parameters"
        constraints = [
            models.UniqueConstraint(
                fields=['model_id', 'parameter_version'], 
                name='unique_parameter_version'
            ),
            models.CheckConstraint(
                condition=Q(approved=False) | Q(parameter_version_id__isnull=False),
                name="prevent_insert_as_approved"
            )
        ]
        indexes = [
            models.Index(fields=["approved"]),
        ]



class ModelRunORM(models.Model):
    run_id = models.AutoField(primary_key = True)

    model = models.ForeignKey(
        FinancialModelORM,
        on_delete = models.PROTECT,
        db_column = "model_id",
        related_name = "runs"
    )

    model_version = models.ForeignKey(
        ModelVersionORM,
        on_delete = models.PROTECT,
        db_column = "model_version_id",
        related_name = "runs"
    )

    parameter_version = models.ForeignKey(
        ParameterVersionORM,
        on_delete = models.PROTECT,
        db_column = "parameter_version_id",
        related_name = "runs"
    )

    status = models.CharField(
        max_length = 50,
        choices = [(s.value, s.value) for s in RunStatus]
    )

    created_at = models.DateTimeField(auto_now_add=True)

    completed_at = models.DateTimeField(blank = True, null = True)

    outputs = models.JSONField(encoder=DjangoJSONEncoder, blank = True, null = True)

    check_results = models.JSONField(encoder=DjangoJSONEncoder, blank = True, null = True)

    error_message = models.TextField(blank = True, null = True)

    class Meta:
        db_table = "model_runs"
        indexes = [
            models.Index(fields=["model_id", "status", "created_at"]),
            models.Index(fields=["model_id", "model_version_id", "parameter_version_id"]),
            models.Index(fields=["status", "created_at"]),
        ]




class OutboxEventORM(models.Model):
    id          = models.AutoField(primary_key=True)

    event_type  = models.CharField(max_length=100)

    payload     = models.JSONField(encoder=DjangoJSONEncoder)

    created_at  = models.DateTimeField(auto_now_add=True)

    processed   = models.BooleanField(default=False)

    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "outbox_events"

        #   The outbox workes performs many queries on this table, 
        #   looking for processed=False events. 
        #   This composite index makes the query faster.
        indexes = [
            models.Index(fields=["processed", "created_at"]) 
        ]
    
    
    
class AnyLogORM(models.Model):
    id = models.AutoField(primary_key = True)

    model = models.ForeignKey(
        FinancialModelORM,
        on_delete=models.PROTECT,
        db_column="model_id",
        null=True,
        blank=True,
        related_name="events"
    )

    run = models.ForeignKey(
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
        default = "SYSTEM"
    )

    details = models.JSONField(encoder=DjangoJSONEncoder,default = dict)

    relevance = models.CharField(
        max_length=20,
        choices = [(r.value, r.value) for r in EventRelevance]
    )

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "audit_anylog"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["run_id", "timestamp"]),
            models.Index(fields=["model_id", "timestamp"]),
            models.Index(fields=["relevance", "timestamp"]),
        ]
