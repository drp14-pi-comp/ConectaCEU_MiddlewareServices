"""All Entity to SQLAlchemy Model conversions"""
from uuid import UUID

from src.data.models.document_validation_model import DocumentValidationModel
from src.data.models.student_absence_justification_model import StudentAbsenceJustificationModel
from src.data.models.user_password_history_model import UserPasswordHistoryModel
from src.domain.entities.document_validation import DocumentValidation
from src.domain.entities.student_absence_justification import StudentAbsenceJustification
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
from src.domain.entities.user_password_history import UserPasswordHistory

class EntityToModelMapper:
    """Centralized Entity to Model conversions"""
    
    @staticmethod
    def _uuid_to_bytes(uuid_obj: UUID) -> bytes:
        return uuid_obj.bytes if uuid_obj else None
    
    # ========== User ==========
    @staticmethod
    def user(entity: User) -> UserModel:
        return UserModel(
            id=entity.id.bytes,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            document=entity.document,
            name=entity.name,
            email=entity.email,
            cellphone_number=entity.cellphone_number,
            contact_cellphone_number=entity.contact_cellphone_number,
            password=entity.password,
            birthdate=entity.birthdate,
            school=entity.school,
            active=entity.active,
            sex_id=entity.sex_id,
            gender_id=entity.gender_id,
            user_type_id=entity.user_type_id,
            email_verified=entity.email_verified if entity.email != '' else None
        )
    
    # ========== Address ==========
    @staticmethod
    def address(entity: Address) -> AddressModel:
        return AddressModel(
            id=entity.id.bytes,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            zip_code=entity.zip_code,
            street=entity.street,
            number=entity.number,
            complement=entity.complement,
            neighborhood=entity.neighborhood,
            user_id=entity.user_id.bytes
        )
    
    # ========== Course ==========
    @staticmethod
    def course(entity: Course) -> CourseModel:
        return CourseModel(
            id=entity.id.bytes,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            name=entity.name,
            total_seat_limit=entity.total_seat_limit,
            workload=entity.workload,
            active=entity.active,
            responsible_educator_1=entity.responsible_educator_1.bytes,
            responsible_educator_2=entity.responsible_educator_2.bytes if entity.responsible_educator_2 else None
        )
    
    # ========== Course Component ==========
    @staticmethod
    def course_component(entity: CourseComponent) -> CourseComponentModel:
        return CourseComponentModel(
            id=entity.id.bytes,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            name=entity.name,
            description=entity.description,
            seat_limit_per_class=entity.seat_limit_per_class,
            active=entity.active,
            course_id=entity.course_id.bytes
        )
    
    # ========== Class ==========
    @staticmethod
    def class_(entity: Class) -> ClassModel:
        return ClassModel(
            id=entity.id.bytes,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            seats_in_use=entity.seats_in_use,
            active=entity.active,
            component_id=entity.component_id.bytes,
            shift_type_id=entity.shift_type_id
        )
    
    # ========== Class Session ==========
    @staticmethod
    def class_session(entity: ClassSession) -> ClassSessionModel:
        return ClassSessionModel(
            id=entity.id.bytes,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            date=entity.date,
            class_id=entity.class_id.bytes
        )
    
    # ========== Attendance ==========
    @staticmethod
    def class_attendance(entity: ClassAttendance) -> ClassAttendanceModel:
        return ClassAttendanceModel(
            id=entity.id.bytes,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            attended=entity.attended,
            user_id=entity.user_id.bytes,
            class_session_id=entity.class_session_id.bytes
        )
    
    # ========== User Class ==========
    @staticmethod
    def user_class(entity: UserClass) -> UserClassModel:
        return UserClassModel(
            id=entity.id.bytes,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            active=entity.active,
            user_id=entity.user_id.bytes,
            class_id=entity.class_id.bytes
        )
    
    # ========== Document ==========
    @staticmethod
    def document(entity: Document) -> DocumentModel:
        return DocumentModel(
            id=entity.id.bytes,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            base64=entity.base64,
            is_front=entity.is_front,
            user_id=entity.user_id.bytes,
            document_type_id=entity.document_type_id,
            legal_representative_id=entity.legal_representative_id.bytes if entity.legal_representative_id else None
        )
    
    # ========== Document Validation ==========
    @staticmethod
    def document_validation(entity: DocumentValidation) -> DocumentValidationModel:
        return DocumentValidationModel(
            id=entity.id.bytes,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            rejection_reason=entity.rejection_reason,
            document_validation_status_type_id=entity.document_validation_status_type_id,
            document_id=entity.document_id.bytes
        )
    
    # ========== Legal Representative ==========
    @staticmethod
    def legal_representative(entity: LegalRepresentative) -> LegalRepresentativeModel:
        return LegalRepresentativeModel(
            id=entity.id.bytes,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            name=entity.name,
            document=entity.document,
            user_id=entity.user_id.bytes,
            legal_representative_degree_id=entity.legal_representative_degree_id
        )
    
    # ========== User Password History ==========
    @staticmethod
    def user_password_history(entity: UserPasswordHistory) -> UserPasswordHistoryModel:
        return UserPasswordHistoryModel(
            id=entity.id.bytes,
            created_at=entity.created_at,
            password=entity.password,
            user_id=entity.user_id.bytes
        )
    
    # ========== Student Abscence Justification ==========
    @staticmethod
    def student_absence_justification(model: StudentAbsenceJustification) -> StudentAbsenceJustificationModel:
        return StudentAbsenceJustificationModel(
            id=UUID(bytes=model.id),
            created_at=model.created_at,
            class_attendance_id=UUID(bytes=model.class_attendance_id),
            document_id=UUID(bytes=model.document_id) if model.document_id else None
        )