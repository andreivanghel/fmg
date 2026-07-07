from rest_framework import serializers
from domain.enums import RunStatus, CheckOutcome, CheckType, CheckSeverity

### decide on the data formats (db)!!!!!!
### IMPORTANT:
### the repository translates from DB to domain
### the serializer translates from domain to JSON
### ---> a serializer is what the client needs!!! <---
###
### max_length is for INPUT VALIDATION!! don't need it for GET


### DO WE NEED POST FOR CHECKS... eventually we will.
### what serializer do we need to that?


class StartRunRequestSerializer(serializers.Serializer):
    model_id = serializers.IntegerField()
    model_version_id = serializers.IntegerField()
    parameter_version_id = serializers.IntegerField()


class RunIdSerializer(serializers.Serializer):
    run_id = serializers.IntegerField(read_only=True)


class CheckResultSerializer(serializers.Serializer):
    check_name = serializers.CharField(read_only=True)
    outcome = serializers.ChoiceField(choices=[(o.value, o.value) for o in CheckOutcome], read_only=True)
    check_type = serializers.ChoiceField(choices=[(t.value, t.value) for t in CheckType], read_only=True)
    check_severity = serializers.ChoiceField(choices=[(s.value, s.value) for s in CheckSeverity], read_only=True)
    message = serializers.CharField(read_only=True)
    details = serializers.DictField(read_only=True)
    started_at = serializers.DateTimeField(read_only=True)
    completed_at = serializers.DateTimeField(read_only=True)


class RunInfoSerializer(serializers.Serializer):
    run_id = serializers.IntegerField(read_only=True)
    model_id = serializers.IntegerField(read_only=True)
    model_version_id = serializers.IntegerField(read_only=True)
    parameter_version_id = serializers.IntegerField(read_only=True)
    status = serializers.ChoiceField(choices=[(s.value, s.value) for s in RunStatus], read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    completed_at = serializers.DateTimeField(allow_null=True, read_only=True)
    outputs = serializers.DictField(allow_null=True, read_only=True)
    check_results = CheckResultSerializer(many=True, allow_null=True, read_only=True)
    error_message = serializers.CharField(allow_null=True, read_only=True)
