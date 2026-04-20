"""All update operations (DTO → existing Entity)"""
from datetime import datetime
from uuid import UUID

# Entities
from src.domain.entities.user import User
from src.domain.entities.address import Address
from src.domain.entities.course import Course
from src.domain.entities.course_component import CourseComponent
from src.domain.entities.class_ import Class
from src.domain.entities.class_attendance import ClassAttendance
from src.domain.entities.document_validation import DocumentValidation
from src.domain.entities.legal_representative import LegalRepresentative
from src.domain.entities.user_sex_type import UserSexType
from src.domain.entities.user_gender_type import UserGenderType
from src.domain.entities.user_type import UserType
from src.domain.entities.document_type import DocumentType
from src.domain.entities.document_validation_status_type import DocumentValidationStatusType
from src.domain.entities.shift_type import ShiftType
from src.domain.entities.report_type import ReportType

# DTOs
from src.domain.dtos.user_dto import UserUpdateDTO
from src.domain.dtos.address_dto import AddressUpdateDTO
from src.domain.dtos.course_dto import CourseUpdateDTO
from src.domain.dtos.course_component_dto import CourseComponentUpdateDTO
from src.domain.dtos.class_dto import ClassUpdateDTO
from src.domain.dtos.class_attendance_dto import ClassAttendanceUpdateDTO
from src.domain.dtos.document_validation_dto import DocumentValidationUpdateDTO
from src.domain.dtos.legal_representative_dto import LegalRepresentativeUpdateDTO
from src.domain.dtos.user_sex_type_dto import UserSexTypeUpdateDTO
from src.domain.dtos.user_gender_type_dto import UserGenderTypeUpdateDTO
from src.domain.dtos.user_type_dto import UserTypeUpdateDTO
from src.domain.dtos.document_type_dto import DocumentTypeUpdateDTO
from src.domain.dtos.document_validation_status_type_dto import DocumentValidationStatusTypeUpdateDTO
from src.domain.dtos.shift_type_dto import ShiftTypeUpdateDTO
from src.domain.dtos.report_type_dto import ReportTypeUpdateDTO

class UpdateMapper:
    """Centralized update operations"""
    
    # ========== User ==========
    @staticmethod
    def user(entity: User, dto: UserUpdateDTO) -> User:
        update_data = dto.model_dump(exclude_none=True)
        for field, value in update_data.items():
            if hasattr(entity, field):
                setattr(entity, field, value)
        entity.updated_at = datetime.now(datetime.timezone.utc)
        return entity
    
    # ========== Address ==========
    @staticmethod
    def address(entity: Address, dto: AddressUpdateDTO) -> Address:
        update_data = dto.model_dump(exclude_none=True)
        for field, value in update_data.items():
            if hasattr(entity, field):
                setattr(entity, field, value)
        entity.updated_at = datetime.now(datetime.timezone.utc)
        return entity
    
    # ========== Course ==========
    @staticmethod
    def course(entity: Course, dto: CourseUpdateDTO) -> Course:
        update_data = dto.model_dump(exclude_none=True)
        for field, value in update_data.items():
            if field in ['responsible_educator_1', 'responsible_educator_2'] and value:
                value = UUID(value)
            if hasattr(entity, field):
                setattr(entity, field, value)
        entity.updated_at = datetime.now(datetime.timezone.utc)
        return entity
    
    # ========== Course Component ==========
    @staticmethod
    def course_component(entity: CourseComponent, dto: CourseComponentUpdateDTO) -> CourseComponent:
        update_data = dto.model_dump(exclude_none=True)
        for field, value in update_data.items():
            if hasattr(entity, field):
                setattr(entity, field, value)
        entity.updated_at = datetime.now(datetime.timezone.utc)
        return entity
    
    # ========== Class ==========
    @staticmethod
    def class_(entity: Class, dto: ClassUpdateDTO) -> Class:
        update_data = dto.model_dump(exclude_none=True)
        for field, value in update_data.items():
            if hasattr(entity, field):
                setattr(entity, field, value)
        entity.updated_at = datetime.now(datetime.timezone.utc)
        return entity
    
    # ========== Class Attendance ==========
    @staticmethod
    def class_attendance(entity: ClassAttendance, dto: ClassAttendanceUpdateDTO) -> ClassAttendance:
        entity.attended = dto.attended
        entity.updated_at = datetime.now(datetime.timezone.utc)
        return entity
    
    # ========== Document Validation ==========
    @staticmethod
    def document_validation(entity: DocumentValidation, dto: DocumentValidationUpdateDTO) -> DocumentValidation:
        entity.document_validation_status_type_id = dto.document_validation_status_type_id
        if dto.rejection_reason:
            entity.rejection_reason = dto.rejection_reason
        entity.updated_at = datetime.now(datetime.timezone.utc)
        return entity
    
    # ========== Legal Representative ==========
    @staticmethod
    def legal_representative(entity: LegalRepresentative, dto: LegalRepresentativeUpdateDTO) -> LegalRepresentative:
        update_data = dto.model_dump(exclude_none=True)
        for field, value in update_data.items():
            if hasattr(entity, field):
                setattr(entity, field, value)
        entity.updated_at = datetime.now(datetime.timezone.utc)
        return entity
    
    # ========== User Sex Type ==========
    @staticmethod
    def user_sex_type(entity: UserSexType, dto: UserSexTypeUpdateDTO) -> UserSexType:
        update_data = dto.model_dump(exclude_none=True)
        for field, value in update_data.items():
            if hasattr(entity, field):
                setattr(entity, field, value)
        return entity
    
    # ========== User Gender Type ==========
    @staticmethod
    def user_gender_type(entity: UserGenderType, dto: UserGenderTypeUpdateDTO) -> UserGenderType:
        update_data = dto.model_dump(exclude_none=True)
        for field, value in update_data.items():
            if hasattr(entity, field):
                setattr(entity, field, value)
        return entity
    
    # ========== User Type ==========
    @staticmethod
    def user_type(entity: UserType, dto: UserTypeUpdateDTO) -> UserType:
        update_data = dto.model_dump(exclude_none=True)
        for field, value in update_data.items():
            if hasattr(entity, field):
                setattr(entity, field, value)
        return entity
    
    # ========== Document Type ==========
    @staticmethod
    def document_type(entity: DocumentType, dto: DocumentTypeUpdateDTO) -> DocumentType:
        update_data = dto.model_dump(exclude_none=True)
        for field, value in update_data.items():
            if hasattr(entity, field):
                setattr(entity, field, value)
        return entity
    
    # ========== Document Validation Status Type ==========
    @staticmethod
    def document_validation_status_type(entity: DocumentValidationStatusType, dto: DocumentValidationStatusTypeUpdateDTO) -> DocumentValidationStatusType:
        update_data = dto.model_dump(exclude_none=True)
        for field, value in update_data.items():
            if hasattr(entity, field):
                setattr(entity, field, value)
        return entity
    
    # ========== Shift Type ==========
    @staticmethod
    def shift_type(entity: ShiftType, dto: ShiftTypeUpdateDTO) -> ShiftType:
        update_data = dto.model_dump(exclude_none=True)
        for field, value in update_data.items():
            if hasattr(entity, field):
                setattr(entity, field, value)
        return entity
    
    # ========== Report Type ==========
    @staticmethod
    def report_type(entity: ReportType, dto: ReportTypeUpdateDTO) -> ReportType:
        update_data = dto.model_dump(exclude_none=True)
        for field, value in update_data.items():
            if hasattr(entity, field):
                setattr(entity, field, value)
        return entity