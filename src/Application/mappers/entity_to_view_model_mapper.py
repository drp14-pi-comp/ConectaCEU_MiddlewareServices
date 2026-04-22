"""All Entity to ViewModel conversions"""
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

from src.domain.entities.user_password_history import UserPasswordHistory
from src.domain.view_models.user_password_history_view_model import UserPasswordHistoryViewModel
from src.domain.view_models.user_view_model import UserViewModel
from src.domain.view_models.address_view_model import AddressViewModel
from src.domain.view_models.course_view_model import CourseViewModel
from src.domain.view_models.course_component_view_model import CourseComponentViewModel
from src.domain.view_models.class_view_model import ClassViewModel
from src.domain.view_models.class_session_view_model import ClassSessionViewModel
from src.domain.view_models.class_attendance_view_model import ClassAttendanceViewModel
from src.domain.view_models.user_class_view_model import UserClassViewModel
from src.domain.view_models.document_view_model import DocumentViewModel
from src.domain.view_models.legal_representative_view_model import LegalRepresentativeViewModel

class EntityToViewModelMapper:
    """Centralized Entity to ViewModel conversions"""
    
    # ========== User ==========
    @staticmethod
    def user(entity: User) -> UserViewModel:
        return UserViewModel(
            id=entity.id,
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
            user_type_id=entity.user_type_id
        )
    
    # ========== Address ==========
    @staticmethod
    def address(entity: Address) -> AddressViewModel:
        return AddressViewModel(
            id=entity.id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            zip_code=entity.zip_code,
            street=entity.street,
            number=entity.number,
            complement=entity.complement,
            neighborhood=entity.neighborhood,
            user_id=entity.user_id
        )
    
    # ========== Course ==========
    @staticmethod
    def course(entity: Course) -> CourseViewModel:
        return CourseViewModel(
            id=entity.id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            name=entity.name,
            total_seat_limit=entity.total_seat_limit,
            workload=entity.workload,
            active=entity.active,
            responsible_educator_1=entity.responsible_educator_1,
            responsible_educator_2=entity.responsible_educator_2
        )
    
    # ========== Course Component ==========
    @staticmethod
    def course_component(entity: CourseComponent) -> CourseComponentViewModel:
        return CourseComponentViewModel(
            id=entity.id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            name=entity.name,
            description=entity.description,
            seat_limit_per_class=entity.seat_limit_per_class,
            active=entity.active,
            course_id=entity.course_id
        )
    
    # ========== Class ==========
    @staticmethod
    def class_(entity: Class) -> ClassViewModel:
        return ClassViewModel(
            id=entity.id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            seats_in_use=entity.seats_in_use,
            active=entity.active,
            component_id=entity.component_id,
            shift_type_id=entity.shift_type_id
        )
    
    # ========== Class Session ==========
    @staticmethod
    def class_session(entity: ClassSession) -> ClassSessionViewModel:
        return ClassSessionViewModel(
            id=entity.id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            date=entity.date,
            class_id=entity.class_id
        )
    
    # ========== Attendance ==========
    @staticmethod
    def attendance(entity: ClassAttendance) -> ClassAttendanceViewModel:
        return ClassAttendanceViewModel(
            id=entity.id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            attended=entity.attended,
            user_id=entity.user_id,
            class_session_id=entity.class_session_id
        )
    
    # ========== User Class ==========
    @staticmethod
    def user_class(entity: UserClass) -> UserClassViewModel:
        return UserClassViewModel(
            id=entity.id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            active=entity.active,
            user_id=entity.user_id,
            class_id=entity.class_id
        )
    
    # ========== Document ==========
    @staticmethod
    def document(entity: Document) -> DocumentViewModel:
        return DocumentViewModel(
            id=entity.id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            base64=entity.base64,
            is_front=entity.is_front,
            user_id=entity.user_id,
            document_type_id=entity.document_type_id,
            legal_representative_id=entity.legal_representative_id
        )
    
    # ========== Legal Representative ==========
    @staticmethod
    def legal_representative(entity: LegalRepresentative) -> LegalRepresentativeViewModel:
        return LegalRepresentativeViewModel(
            id=entity.id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            name=entity.name,
            document=entity.document,
            user_id=entity.user_id
        )
    
    # ========== User Password History ==========
    @staticmethod
    def user_password_history(entity: UserPasswordHistory) -> UserPasswordHistoryViewModel:
        return UserPasswordHistoryViewModel(
            id=entity.id,
            created_at=entity.created_at,
            password=entity.password,
            user_id=entity.user_id
        )