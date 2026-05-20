"""All Entity to ViewModel conversions"""
from src.domain.entities.profiles_to_exclude import ProfilesToExclude
from src.domain.entities.student_absence_justification import StudentAbsenceJustification
from src.domain.entities.user import User
from src.domain.entities.address import Address
from src.domain.entities.course import Course
from src.domain.entities.course_component import CourseComponent
from src.domain.entities.class_ import Class
from src.domain.entities.class_attendance import ClassAttendance
from src.domain.entities.user_course import UserCourse
from src.domain.entities.document import Document
from src.domain.entities.legal_representative import LegalRepresentative
from src.domain.entities.user_password_history import UserPasswordHistory
from src.domain.entities.user_sex_type import UserSexType
from src.domain.entities.user_gender_type import UserGenderType
from src.domain.entities.user_type import UserType
from src.domain.entities.document_type import DocumentType
from src.domain.entities.document_validation_status_type import DocumentValidationStatusType
from src.domain.entities.document_validation import DocumentValidation
from src.domain.entities.shift_type import ShiftType
from src.domain.entities.report_type import ReportType
from src.domain.entities.legal_representative_degree import LegalRepresentativeDegree

from src.domain.view_models.profiles_to_exclude_view_model import ProfilesToExcludeViewModel
from src.domain.view_models.student_absence_justification_view_model import StudentAbsenceJustificationViewModel
from src.domain.view_models.user_password_history_view_model import UserPasswordHistoryViewModel
from src.domain.view_models.user_view_model import UserViewModel
from src.domain.view_models.address_view_model import AddressViewModel
from src.domain.view_models.course_view_model import CourseViewModel
from src.domain.view_models.course_component_view_model import CourseComponentViewModel
from src.domain.view_models.class_view_model import ClassViewModel
from src.domain.view_models.class_attendance_view_model import ClassAttendanceViewModel
from src.domain.view_models.user_course_view_model import UserCourseViewModel
from src.domain.view_models.document_view_model import DocumentViewModel
from src.domain.view_models.legal_representative_view_model import LegalRepresentativeViewModel
from src.domain.view_models.user_sex_type_view_model import UserSexTypeViewModel
from src.domain.view_models.user_gender_type_view_model import UserGenderTypeViewModel
from src.domain.view_models.user_type_view_model import UserTypeViewModel
from src.domain.view_models.document_type_view_model import DocumentTypeViewModel
from src.domain.view_models.document_validation_status_type_view_model import DocumentValidationStatusTypeViewModel
from src.domain.view_models.document_validation_view_model import DocumentValidationViewModel
from src.domain.view_models.shift_type_view_model import ShiftTypeViewModel
from src.domain.view_models.report_type_view_model import ReportTypeViewModel
from src.domain.view_models.legal_representative_degree_view_model import LegalRepresentativeDegreeViewModel

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
            user_type_id=entity.user_type_id,
            student_sequential=entity.student_sequential
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
            responsible_educator_2=entity.responsible_educator_2,
            shift_type_id=entity.shift_type_id
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
            date=entity.date,
            component_id=entity.course_component_id
        )
    
    # ========== Class Attendance ==========
    @staticmethod
    def class_attendance(entity: ClassAttendance) -> ClassAttendanceViewModel:
        return ClassAttendanceViewModel(
            id=entity.id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            attended=entity.attended,
            user_id=entity.user_id,
            class_id=entity.class_id
        )
    
    # ========== User Course ==========
    @staticmethod
    def user_course(entity: UserCourse) -> UserCourseViewModel:
        return UserCourseViewModel(
            id=entity.id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            active=entity.active,
            user_id=entity.user_id,
            course_id=entity.course_id
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
            user_id=entity.user_id,
            legal_representative_degree_id=entity.legal_representative_degree_id
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
    
    # ========== Profile To Exclude ==========
    @staticmethod
    def profiles_to_exclude(entity: ProfilesToExclude) -> ProfilesToExcludeViewModel:
        return ProfilesToExcludeViewModel(
            id=entity.id,
            created_at=entity.created_at,
            user_id=entity.user_id
        )
    
    # ========== Student Abscence Justification ==========
    @staticmethod
    def student_absence_justification(entity: StudentAbsenceJustification) -> StudentAbsenceJustificationViewModel:
        return StudentAbsenceJustificationViewModel(
            id=entity.id,
            created_at=entity.created_at,
            class_attendance_id=entity.class_attendance_id,
            document_id=entity.document_id
        )
    
    # ========== User Sex Type ==========
    @staticmethod
    def user_sex_type(entity: UserSexType) -> UserSexTypeViewModel:
        return UserSexTypeViewModel(id=entity.id, description=entity.description)

    # ========== User Gender Type ==========
    @staticmethod
    def user_gender_type(entity: UserGenderType) -> UserGenderTypeViewModel:
        return UserGenderTypeViewModel(id=entity.id, description=entity.description)

    # ========== User Type ==========
    @staticmethod
    def user_type(entity: UserType) -> UserTypeViewModel:
        return UserTypeViewModel(
            id=entity.id,
            description=entity.description,
            register_user=entity.register_user,
            validate_user_documents=entity.validate_user_documents,
            list_secretaries=entity.list_secretaries,
            list_educators=entity.list_educators,
            list_students=entity.list_students,
            send_broadcast_message=entity.send_broadcast_message,
            add_courses=entity.add_courses,
            add_classes=entity.add_classes,
            emit_user_documents=entity.emit_user_documents
        )

    # ========== Document Type ==========
    @staticmethod
    def document_type(entity: DocumentType) -> DocumentTypeViewModel:
        return DocumentTypeViewModel(id=entity.id, description=entity.description)

    # ========== Document Validation Status Type ==========
    @staticmethod
    def document_validation_status_type(entity: DocumentValidationStatusType) -> DocumentValidationStatusTypeViewModel:
        return DocumentValidationStatusTypeViewModel(id=entity.id, description=entity.description)

    # ========== Document Validation ==========
    @staticmethod
    def document_validation(entity: DocumentValidation) -> DocumentValidationViewModel:
        return DocumentValidationViewModel(
            id=entity.id, created_at=entity.created_at, updated_at=entity.updated_at,
            rejection_reason=entity.rejection_reason,
            document_validation_status_type_id=entity.document_validation_status_type_id,
            document_id=entity.document_id
        )

    # ========== Shift Type ==========
    @staticmethod
    def shift_type(entity: ShiftType) -> ShiftTypeViewModel:
        return ShiftTypeViewModel(id=entity.id, description=entity.description)

    # ========== Report Type ==========
    @staticmethod
    def report_type(entity: ReportType) -> ReportTypeViewModel:
        return ReportTypeViewModel(id=entity.id, description=entity.description)

    # ========== Legal Representative Degree ==========
    @staticmethod
    def legal_representative_degree(entity: LegalRepresentativeDegree) -> LegalRepresentativeDegreeViewModel:
        return LegalRepresentativeDegreeViewModel(id=entity.id, description=entity.description)