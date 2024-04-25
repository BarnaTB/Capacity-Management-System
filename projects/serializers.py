from rest_framework import serializers

from accounts.serializers import (DeveloperProfileSerializer,
                                  UserConfigSerializer)
from projects.models import Project
from utils.general import get_date_from_string


class ProjectSerializer(serializers.ModelSerializer):
    members = DeveloperProfileSerializer(many=True, read_only=True)
    created_by = UserConfigSerializer(read_only=True)

    class Meta:
        model = Project
        fields = "__all__"
        extra_kwargs = {"slug": {"required": False}, "name": {"required": True}, }

    def validate(self, data):
        start_date = data.get("start_date", "")
        end_date = data.get("end_date", "")
        if start_date:
            start_date = get_date_from_string(str(start_date))
        if end_date:
            end_date = get_date_from_string(str(end_date))
        if end_date and start_date and end_date < start_date:
            raise serializers.ValidationError("End date must be greater than start date.")

        data.update({"start_date": start_date, "end_date": end_date})
        return data


class AssignProjectSerializer(serializers.ModelSerializer):
    members = DeveloperProfileSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = "__all__"
