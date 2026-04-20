"""All DTO to Entity conversions"""
from datetime import datetime
from uuid import uuid4, UUID

# Entities
from src.domain.entities.user import User
from src.domain.entities.address import Address
from src.domain.entities.course import Course
from src.domain.entities.course_component import CourseComponent
from src.domain.entities.class_ import Class
from src.domain.entities.class_session import ClassSession
from src.domain.entities.class_attendance import ClassAttendance
from src.domain.entities.user_class import UserClass
from src.domain.entities.document import Document
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
from src.domain.dtos.user_dto import UserCreateDTO
from src.domain.dtos.address_dto import AddressCreateDTO
from src.domain.dtos.course_dto import CourseCreateDTO
from src.domain.dtos.course_component_dto import CourseComponentCreateDTO
from src.domain.dtos.class_dto import ClassCreateDTO
from src.domain.dtos.class_session_dto import ClassSessionCreateDTO
from src.domain.dtos.class_attendance_dto import ClassAttendanceCreateDTO
from src.domain.dtos.user_class_dto import UserClassEnrollDTO
from src.domain.dtos.document_dto import DocumentCreateDTO
from src.domain.dtos.document_validation_dto import DocumentValidationCreateDTO
from src.domain.dtos.legal_representative_dto import LegalRepresentativeCreateDTO
from src.domain.dtos.user_sex_type_dto import UserSexTypeCreateDTO
from src.domain.dtos.user_gender_type_dto import UserGenderTypeCreateDTO
from src.domain.dtos.user_type_dto import UserTypeCreateDTO
from src.domain.dtos.document_type_dto import DocumentTypeCreateDTO
from src.domain.dtos.document_validation_status_type_dto import DocumentValidationStatusTypeCreateDTO
from src.domain.dtos.shift_type_dto import ShiftTypeCreateDTO
from src.domain.dtos.report_type_dto import ReportTypeCreateDTO

class DtoToEntityMapper:
    """Centralized DTO → Entity conversions"""
    
    # ========== User ==========
    @staticmethod
    def user(dto: UserCreateDTO) -> User:
        return User(
            id=uuid4(),
            created_at=datetime.utcnow(),
            updated_at=None,
            document=dto.document,
            name=dto.name,
            email=dto.email,
            cellphone_number=dto.cellphone_number,
            contact_cellphone_number=dto.contact_cellphone_number,
            password=dto.password,
            birthdate=dto.birthdate,
            school=dto.school,
            active=True,
            sex_id=dto.sex_id,
            gender_id=dto.gender_id,
            user_type_id=dto.user_type_id
        )
    
    # ========== Address ==========
    @staticmethod
    def address(dto: AddressCreateDTO) -> Address:
        return Address(
            id=uuid4(),
            created_at=datetime.utcnow(),
            updated_at=None,
            zip_code=dto.zip_code,
            street=dto.street,
            number=dto.number,
            complement=dto.complement,
            neighborhood=dto.neighborhood,
            user_id=UUID(dto.user_id)
        )
    
    # ========== Course ==========
    @staticmethod
    def course(dto: CourseCreateDTO) -> Course:
        return Course(
            id=uuid4(),
            created_at=datetime.utcnow(),
            updated_at=None,
            name=dto.name,
            total_seat_limit=dto.total_seat_limit,
            workload=dto.workload,
            active=True,
            responsible_educator_1=UUID(dto.responsible_educator_1),
            responsible_educator_2=UUID(dto.responsible_educator_2) if dto.responsible_educator_2 else None
        )
    
    # ========== Course Component ==========
    @staticmethod
    def course_component(dto: CourseComponentCreateDTO) -> CourseComponent:
        return CourseComponent(
            id=uuid4(),
            created_at=datetime.utcnow(),
            updated_at=None,
            name=dto.name,
            description=dto.description,
            seat_limit_per_class=dto.seat_limit_per_class,
            active=True,
            course_id=UUID(dto.course_id)
        )
    
    # ========== Class ==========
    @staticmethod
    def class_(dto: ClassCreateDTO) -> Class:
        return Class(
            id=uuid4(),
            created_at=datetime.utcnow(),
            updated_at=None,
            seats_in_use=0,
            active=True,
            component_id=UUID(dto.component_id),
            shift_type_id=dto.shift_type_id
        )
    
    # ========== Class Session ==========
    @staticmethod
    def class_session(dto: ClassSessionCreateDTO) -> ClassSession:
        return ClassSession(
            id=uuid4(),
            created_at=datetime.utcnow(),
            updated_at=None,
            date=dto.date,
            class_id=UUID(dto.class_id)
        )
    
    # ========== Class Attendance ==========
    @staticmethod
    def class_attendance(dto: ClassAttendanceCreateDTO) -> ClassAttendance:
        return ClassAttendance(
            id=uuid4(),
            created_at=datetime.utcnow(),
            updated_at=None,
            attended=False,
            user_id=UUID(dto.user_id),
            class_session_id=UUID(dto.class_session_id)
        )
    
    # ========== User Class ==========
    @staticmethod
    def user_class(dto: UserClassEnrollDTO) -> UserClass:
        return UserClass(
            id=uuid4(),
            created_at=datetime.utcnow(),
            updated_at=None,
            active=True,
            user_id=UUID(dto.user_id),
            class_id=UUID(dto.class_id)
        )
    
    # ========== Document ==========
    @staticmethod
    def document(dto: DocumentCreateDTO) -> Document:
        return Document(
            id=uuid4(),
            created_at=datetime.utcnow(),
            updated_at=None,
            base64=dto.base64,
            is_front=dto.is_front,
            user_id=UUID(dto.user_id),
            document_type_id=dto.document_type_id,
            legal_representative_id=UUID(dto.legal_representative_id) if dto.legal_representative_id else None
        )
    
    # ========== Document Validation ==========
    @staticmethod
    def document_validation(dto: DocumentValidationCreateDTO) -> DocumentValidation:
        return DocumentValidation(
            id=uuid4(),
            created_at=datetime.utcnow(),
            updated_at=None,
            rejection_reason=None,
            document_validation_status_type_id=dto.document_validation_status_type_id,
            document_id=UUID(dto.document_id)
        )
    
    # ========== Legal Representative ==========
    @staticmethod
    def legal_representative(dto: LegalRepresentativeCreateDTO) -> LegalRepresentative:
        return LegalRepresentative(
            id=uuid4(),
            created_at=datetime.utcnow(),
            updated_at=None,
            name=dto.name,
            document=dto.document,
            user_id=UUID(dto.user_id)
        )
    
    # ========== User Sex Type ==========
    @staticmethod
    def user_sex_type(dto: UserSexTypeCreateDTO) -> UserSexType:
        return UserSexType(
            id=0,  # Auto-increment
            description=dto.description
        )
    
    # ========== User Gender Type ==========
    @staticmethod
    def user_gender_type(dto: UserGenderTypeCreateDTO) -> UserGenderType:
        return UserGenderType(
            id=0,
            description=dto.description
        )
    
    # ========== User Type ==========
    @staticmethod
    def user_type(dto: UserTypeCreateDTO) -> UserType:
        return UserType(
            id=0,
            description=dto.description,
            register_user=dto.register_user,
            validate_user_documents=dto.validate_user_documents,
            list_secretaries=dto.list_secretaries,
            list_educators=dto.list_educators,
            list_students=dto.list_students,
            send_broadcast_message=dto.send_broadcast_message,
            add_courses=dto.add_courses,
            add_classes=dto.add_classes,
            emit_user_documents=dto.emit_user_documents
        )
    
    # ========== Document Type ==========
    @staticmethod
    def document_type(dto: DocumentTypeCreateDTO) -> DocumentType:
        return DocumentType(
            id=0,
            description=dto.description
        )
    
    # ========== Document Validation Status Type ==========
    @staticmethod
    def document_validation_status_type(dto: DocumentValidationStatusTypeCreateDTO) -> DocumentValidationStatusType:
        return DocumentValidationStatusType(
            id=0,
            description=dto.description
        )
    
    # ========== Shift Type ==========
    @staticmethod
    def shift_type(dto: ShiftTypeCreateDTO) -> ShiftType:
        return ShiftType(
            id=0,
            description=dto.description
        )
    
    # ========== Report Type ==========
    @staticmethod
    def report_type(dto: ReportTypeCreateDTO) -> ReportType:
        return ReportType(
            id=0,
            description=dto.description
        )