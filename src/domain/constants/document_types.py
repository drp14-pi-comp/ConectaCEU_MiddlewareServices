from enum import Enum

class DocumentTypes(Enum):
    CPF = 1
    RG = 2
    CIN = 3
    PROFILE_PHOTO = 4
    STUDENT_REGISTRY_AUTHORIZATION = 5
    HEALTH_CERTIFICATE = 6
    ABSENCE_JUSTIFICATION = 7
    STUDENT_CARD = 8
    REGISTER_USER_FORM_TEMPLATE = 9
    HEALTH_CERTIFICATE_TEMPLATE = 10
    ATTENDANCE_LIST_TEMPLATE = 11

    @classmethod
    def is_template_type(cls, document_type_id: int) -> bool:
        return document_type_id in [
            cls.REGISTER_USER_FORM_TEMPLATE.value,
            cls.HEALTH_CERTIFICATE_TEMPLATE.value,
            cls.ATTENDANCE_LIST_TEMPLATE.value,
        ]