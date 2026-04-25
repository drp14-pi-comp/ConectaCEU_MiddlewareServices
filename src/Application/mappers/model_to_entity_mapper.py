"""All SQLAlchemy Model to Entity conversions"""
from uuid import UUID
from xml.dom.minidom import DocumentType

from src.data.models.document_type_model import DocumentTypeModel
from src.data.models.document_validation_model import DocumentValidationModel
from src.data.models.document_validation_status_type_model import DocumentValidationStatusTypeModel
from src.data.models.legal_representative_degree_model import LegalRepresentativeDegreeModel
from src.data.models.report_type_model import ReportTypeModel
from src.data.models.shift_type_model import ShiftTypeModel
from src.data.models.user_gender_type_model import UserGenderTypeModel
from src.data.models.user_password_history_model import UserPasswordHistoryModel
from src.data.models.user_sex_type_model import UserSexTypeModel
from src.data.models.user_type_model import UserTypeModel
from src.data.models.user_model import UserModel
from src.data.models.address_model import AddressModel
from src.data.models.course_model import CourseModel
from src.data.models.course_component_model import CourseComponentModel
from src.data.models.class_model import ClassModel
from src.data.models.class_session_model import ClassSessionModel
from src.data.models.class_attendance_model import ClassAttendanceModel
from src.data.models.user_class_model import UserClassModel
from src.data.models.document_model import DocumentModel
from src.data.models.legal_representative_model import LegalRepresentativeModel

from src.domain.entities.document_validation import DocumentValidation
from src.domain.entities.document_validation_status_type import DocumentValidationStatusType
from src.domain.entities.legal_representative_degree import LegalRepresentativeDegree
from src.domain.entities.report_type import ReportType
from src.domain.entities.shift_type import ShiftType
from src.domain.entities.user import User
from src.domain.entities.address import Address
from src.domain.entities.course import Course
from src.domain.entities.course_component import CourseComponent
from src.domain.entities.class_ import Class
from src.domain.entities.class_session import ClassSession
from src.domain.entities.class_attendance import ClassAttendance
from src.domain.entities.user_class import UserClass
from src.domain.entities.document import Document
from src.domain.entities.legal_representative import LegalRepresentative
from src.domain.entities.user_gender_type import UserGenderType
from src.domain.entities.user_password_history import UserPasswordHistory
from src.domain.entities.user_sex_type import UserSexType
from src.domain.entities.user_type import UserType

class ModelToEntityMapper:
    """Centralized Model to Entity conversions"""
    
    @staticmethod
    def _bytes_to_uuid(bytes_obj: bytes) -> UUID:
        return UUID(bytes=bytes_obj) if bytes_obj else None
    
    # ========== User ==========
    @staticmethod
    def user(model: UserModel) -> User:
        return User(
            id=UUID(bytes=model.id),
            created_at=model.created_at,
            updated_at=model.updated_at,
            document=model.document,
            name=model.name,
            email=model.email,
            cellphone_number=model.cellphone_number,
            contact_cellphone_number=model.contact_cellphone_number,
            password=model.password,
            birthdate=model.birthdate,
            school=model.school,
            active=model.active,
            sex_id=model.sex_id,
            gender_id=model.gender_id,
            user_type_id=model.user_type_id
        )
    
    # ========== Address ==========
    @staticmethod
    def address(model: AddressModel) -> Address:
        return Address(
            id=UUID(bytes=model.id),
            created_at=model.created_at,
            updated_at=model.updated_at,
            zip_code=model.zip_code,
            street=model.street,
            number=model.number,
            complement=model.complement,
            neighborhood=model.neighborhood,
            user_id=UUID(bytes=model.user_id)
        )
    
    # ========== Course ==========
    @staticmethod
    def course(model: CourseModel) -> Course:
        return Course(
            id=UUID(bytes=model.id),
            created_at=model.created_at,
            updated_at=model.updated_at,
            name=model.name,
            total_seat_limit=model.total_seat_limit,
            workload=model.workload,
            active=model.active,
            responsible_educator_1=UUID(bytes=model.responsible_educator_1),
            responsible_educator_2=UUID(bytes=model.responsible_educator_2) if model.responsible_educator_2 else None
        )
    
    # ========== Course Component ==========
    @staticmethod
    def course_component(model: CourseComponentModel) -> CourseComponent:
        return CourseComponent(
            id=UUID(bytes=model.id),
            created_at=model.created_at,
            updated_at=model.updated_at,
            name=model.name,
            description=model.description,
            seat_limit_per_class=model.seat_limit_per_class,
            active=model.active,
            course_id=UUID(bytes=model.course_id)
        )
    
    # ========== Class ==========
    @staticmethod
    def class_(model: ClassModel) -> Class:
        return Class(
            id=UUID(bytes=model.id),
            created_at=model.created_at,
            updated_at=model.updated_at,
            seats_in_use=model.seats_in_use,
            active=model.active,
            component_id=UUID(bytes=model.component_id),
            shift_type_id=model.shift_type_id
        )
    
    # ========== Class Session ==========
    @staticmethod
    def class_session(model: ClassSessionModel) -> ClassSession:
        return ClassSession(
            id=UUID(bytes=model.id),
            created_at=model.created_at,
            updated_at=model.updated_at,
            date=model.date,
            class_id=UUID(bytes=model.class_id)
        )
    
    # ========== Attendance ==========
    @staticmethod
    def attendance(model: ClassAttendanceModel) -> ClassAttendance:
        return ClassAttendance(
            id=UUID(bytes=model.id),
            created_at=model.created_at,
            updated_at=model.updated_at,
            attended=model.attended,
            user_id=UUID(bytes=model.user_id),
            class_session_id=UUID(bytes=model.class_session_id)
        )
    
    # ========== User Class ==========
    @staticmethod
    def user_class(model: UserClassModel) -> UserClass:
        return UserClass(
            id=UUID(bytes=model.id),
            created_at=model.created_at,
            updated_at=model.updated_at,
            active=model.active,
            user_id=UUID(bytes=model.user_id),
            class_id=UUID(bytes=model.class_id)
        )
    
    # ========== Document ==========
    @staticmethod
    def document(model: DocumentModel) -> Document:
        return Document(
            id=UUID(bytes=model.id),
            created_at=model.created_at,
            updated_at=model.updated_at,
            base64=model.base64,
            is_front=model.is_front,
            user_id=UUID(bytes=model.user_id),
            document_type_id=model.document_type_id,
            legal_representative_id=UUID(bytes=model.legal_representative_id) if model.legal_representative_id else None
        )
    
    # ========== Legal Representative ==========
    @staticmethod
    def legal_representative(model: LegalRepresentativeModel) -> LegalRepresentative:
        return LegalRepresentative(
            id=UUID(bytes=model.id),
            created_at=model.created_at,
            updated_at=model.updated_at,
            name=model.name,
            document=model.document,
            user_id=UUID(bytes=model.user_id)
        )
    
    # ========== User Password History ==========
    @staticmethod
    def user_password_history(model: UserPasswordHistoryModel) -> UserPasswordHistory:
        return UserPasswordHistory(
            id=UUID(bytes=model.id),
            created_at=model.created_at,
            password=model.password,
            user_id=UUID(bytes=model.user_id)
        )
    
    # ========== Reference Entities ==========
    @staticmethod
    def user_sex_type(model: UserSexTypeModel) -> UserSexType:
        """Convert UserSexType Model → Entity"""
        return UserSexType(
            id=model.id,
            description=model.description
        )

    @staticmethod
    def user_gender_type(model: UserGenderTypeModel) -> UserGenderType:
        """Convert UserGenderType Model → Entity"""
        return UserGenderType(
            id=model.id,
            description=model.description
        )

    @staticmethod
    def user_type(model: UserTypeModel) -> UserType:
        """Convert UserType Model → Entity"""
        return UserType(
            id=model.id,
            description=model.description,
            register_user=model.register_user,
            validate_user_documents=model.validate_user_documents,
            list_secretaries=model.list_secretaries,
            list_educators=model.list_educators,
            list_students=model.list_students,
            send_broadcast_message=model.send_broadcast_message,
            add_courses=model.add_courses,
            add_classes=model.add_classes,
            emit_user_documents=model.emit_user_documents
        )

    @staticmethod
    def document_type(model: DocumentTypeModel) -> DocumentType:
        """Convert DocumentType Model → Entity"""
        return DocumentType(
            id=model.id,
            description=model.description
        )

    @staticmethod
    def document_validation_status_type(model: DocumentValidationStatusTypeModel) -> DocumentValidationStatusType:
        """Convert DocumentValidationStatusType Model → Entity"""
        return DocumentValidationStatusType(
            id=model.id,
            description=model.description
        )

    @staticmethod
    def document_validation(model: DocumentValidationModel) -> DocumentValidation:
        """Convert DocumentValidation Model → Entity"""
        return DocumentValidation(
            id=UUID(bytes=model.id),
            created_at=model.created_at,
            updated_at=model.updated_at,
            rejection_reason=model.rejection_reason,
            document_validation_status_type_id=model.document_validation_status_type_id,
            document_id=UUID(bytes=model.document_id)
        )

    @staticmethod
    def shift_type(model: ShiftTypeModel) -> ShiftType:
        """Convert ShiftType Model → Entity"""
        return ShiftType(
            id=model.id,
            description=model.description
        )

    @staticmethod
    def report_type(model: ReportTypeModel) -> ReportType:
        """Convert ReportType Model → Entity"""
        return ReportType(
            id=model.id,
            description=model.description
        )

    @staticmethod
    def legal_representative_degree(model: LegalRepresentativeDegreeModel) -> LegalRepresentativeDegree:
        """Convert LegalRepresentativeDegree Model → Entity"""
        return LegalRepresentativeDegree(
            id=model.id,
            description=model.description
        )