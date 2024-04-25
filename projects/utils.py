from django.db.models import QuerySet

from accounts.serializers import DeveloperProfileSerializer
from projects.models import Project


def get_suggested_profiles(project: Project, developer_profiles: QuerySet) -> list:
    """Helper function to calculate the percentage by which
    a developer matches a project's required skills

    Args:
        project (Project): The project against a match is supposed to be
        computed
        developer_profile (DeveloperProfile): The developer profile that is
        supposed to be matched

    Returns:
        _type_: _description_
    """
    suggested_profiles = []

    for profile in developer_profiles:
        required_skills = set(project.required_skills.all())
        developer_skills = set(profile.skills.all())
        matching_skills = required_skills.intersection(developer_skills)
        match_percentage = round(len(matching_skills) / len(required_skills) * 100, 1)

        developer_data = {
            "developer_profile": DeveloperProfileSerializer(profile).data,
            "match_percentage": match_percentage,
        }

        suggested_profiles.append(developer_data)
    return suggested_profiles
