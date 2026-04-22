"""All SQLAlchemy Model -> ViewModel conversions for reference types (shortcuts)"""
from src.application.mappers.model_to_entity_mapper import ModelToEntityMapper
from src.application.mappers.entity_to_view_model_mapper import EntityToViewModelMapper

# Models
from src.data.models.user_sex_type_model import UserSexTypeModel
from src.data.models.user_gender_type_model import UserGenderTypeModel
from src.data.models.user_type_model import UserTypeModel
from src.data.models.document_type_model import DocumentTypeModel
from src.data.models.document_validation_status_type_model import DocumentValidationStatusTypeModel
from src.data.models.shift_type_model import ShiftTypeModel
from src.data.models.report_type_model import ReportTypeModel

# View models
from src.domain.view_models.user_sex_type_view_model import UserSexTypeViewModel
from src.domain.view_models.user_gender_type_view_model import UserGenderTypeViewModel
from src.domain.view_models.user_type_view_model import UserTypeViewModel
from src.domain.view_models.document_type_view_model import DocumentTypeViewModel
from src.domain.view_models.document_validation_status_type_view_model import DocumentValidationStatusTypeViewModel
from src.domain.view_models.shift_type_view_model import ShiftTypeViewModel
from src.domain.view_models.report_type_view_model import ReportTypeViewModel

class ModelToViewModelMapper:
    """
    Centralized Model -> ViewModel conversions for reference/lookup tables only.
    """
    
    # ========== User Sex Type ==========
    @staticmethod
    def user_sex_type(model: UserSexTypeModel) -> UserSexTypeViewModel:
        """Convert UserSexType Model -> ViewModel"""
        entity = ModelToEntityMapper.user_sex_type(model)
        return EntityToViewModelMapper.user_sex_type(entity)
    
    @staticmethod
    def user_sex_types(models: list[UserSexTypeModel]) -> list[UserSexTypeViewModel]:
        """Convert multiple UserSexType models"""
        return [ModelToViewModelMapper.user_sex_type(m) for m in models]
    
    # ========== User Gender Type ==========
    @staticmethod
    def user_gender_type(model: UserGenderTypeModel) -> UserGenderTypeViewModel:
        """Convert UserGenderType Model -> ViewModel"""
        entity = ModelToEntityMapper.user_gender_type(model)
        return EntityToViewModelMapper.user_gender_type(entity)
    
    @staticmethod
    def user_gender_types(models: list[UserGenderTypeModel]) -> list[UserGenderTypeViewModel]:
        """Convert multiple UserGenderType models"""
        return [ModelToViewModelMapper.user_gender_type(m) for m in models]
    
    # ========== User Type ==========
    @staticmethod
    def user_type(model: UserTypeModel) -> UserTypeViewModel:
        """Convert UserType Model -> ViewModel"""
        entity = ModelToEntityMapper.user_type(model)
        return EntityToViewModelMapper.user_type(entity)
    
    @staticmethod
    def user_types(models: list[UserTypeModel]) -> list[UserTypeViewModel]:
        """Convert multiple UserType models"""
        return [ModelToViewModelMapper.user_type(m) for m in models]
    
    # ========== Document Type ==========
    @staticmethod
    def document_type(model: DocumentTypeModel) -> DocumentTypeViewModel:
        """Convert DocumentType Model -> ViewModel"""
        entity = ModelToEntityMapper.document_type(model)
        return EntityToViewModelMapper.document_type(entity)
    
    @staticmethod
    def document_types(models: list[DocumentTypeModel]) -> list[DocumentTypeViewModel]:
        """Convert multiple DocumentType models"""
        return [ModelToViewModelMapper.document_type(m) for m in models]
    
    # ========== Document Validation Status Type ==========
    @staticmethod
    def document_validation_status_type(model: DocumentValidationStatusTypeModel) -> DocumentValidationStatusTypeViewModel:
        """Convert DocumentValidationStatusType Model -> ViewModel"""
        entity = ModelToEntityMapper.document_validation_status_type(model)
        return EntityToViewModelMapper.document_validation_status_type(entity)
    
    @staticmethod
    def document_validation_status_types(models: list[DocumentValidationStatusTypeModel]) -> list[DocumentValidationStatusTypeViewModel]:
        """Convert multiple DocumentValidationStatusType models"""
        return [ModelToViewModelMapper.document_validation_status_type(m) for m in models]
    
    # ========== Shift Type ==========
    @staticmethod
    def shift_type(model: ShiftTypeModel) -> ShiftTypeViewModel:
        """Convert ShiftType Model -> ViewModel"""
        entity = ModelToEntityMapper.shift_type(model)
        return EntityToViewModelMapper.shift_type(entity)
    
    @staticmethod
    def shift_types(models: list[ShiftTypeModel]) -> list[ShiftTypeViewModel]:
        """Convert multiple ShiftType models"""
        return [ModelToViewModelMapper.shift_type(m) for m in models]
    
    # ========== Report Type ==========
    @staticmethod
    def report_type(model: ReportTypeModel) -> ReportTypeViewModel:
        """Convert ReportType Model -> ViewModel"""
        entity = ModelToEntityMapper.report_type(model)
        return EntityToViewModelMapper.report_type(entity)
    
    @staticmethod
    def report_types(models: list[ReportTypeModel]) -> list[ReportTypeViewModel]:
        """Convert multiple ReportType models"""
        return [ModelToViewModelMapper.report_type(m) for m in models]