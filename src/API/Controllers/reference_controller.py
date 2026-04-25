"""Reference data controller for lookup tables"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.data.repositories.legal_representative_degree_repository import LegalRepresentativeDegreeRepository
from src.data.repositories.user_sex_type_repository import UserSexTypeRepository
from src.data.repositories.user_gender_type_repository import UserGenderTypeRepository
from src.data.repositories.user_type_repository import UserTypeRepository
from src.data.repositories.document_type_repository import DocumentTypeRepository
from src.data.repositories.document_validation_status_type_repository import DocumentValidationStatusTypeRepository
from src.data.repositories.shift_type_repository import ShiftTypeRepository
from src.data.repositories.report_type_repository import ReportTypeRepository
from src.data.db_context.database import get_db
from src.application.mappers.model_to_view_model_mapper import ModelToViewModelMapper

router = APIRouter(prefix="/reference", tags=["Reference"])

# Sex Types
@router.get("/sex-types")
async def get_sex_types(db: Session = Depends(get_db)):
    """Get all sex types"""
    repo = UserSexTypeRepository(db)
    models = await repo.get_all()
    return [ModelToViewModelMapper.user_sex_type(m) for m in models]

# Gender Types
@router.get("/gender-types")
async def get_gender_types(db: Session = Depends(get_db)):
    """Get all gender types"""
    repo = UserGenderTypeRepository(db)
    models = await repo.get_all()
    return [ModelToViewModelMapper.user_gender_type(m) for m in models]

# User Types
@router.get("/user-types")
async def get_user_types(db: Session = Depends(get_db)):
    """Get all user types"""
    repo = UserTypeRepository(db)
    models = await repo.get_all()
    return [ModelToViewModelMapper.user_type(m) for m in models]

# Legal representative degrees
@router.get("/legal-representative-degrees")
async def get_user_types(db: Session = Depends(get_db)):
    """Get all legal representative degrees"""
    repo = LegalRepresentativeDegreeRepository(db)
    models = await repo.get_all()
    return [ModelToViewModelMapper.user_type(m) for m in models]

# Document Types
@router.get("/document-types")
async def get_document_types(db: Session = Depends(get_db)):
    """Get all document types"""
    repo = DocumentTypeRepository(db)
    models = await repo.get_all()
    return [ModelToViewModelMapper.document_type(m) for m in models]

# Validation Status Types
@router.get("/validation-status-types")
async def get_validation_status_types(db: Session = Depends(get_db)):
    """Get all validation status types"""
    repo = DocumentValidationStatusTypeRepository(db)
    models = await repo.get_all()
    return [ModelToViewModelMapper.document_validation_status_type(m) for m in models]

# Shift Types
@router.get("/shift-types")
async def get_shift_types(db: Session = Depends(get_db)):
    """Get all shift types"""
    repo = ShiftTypeRepository(db)
    models = await repo.get_all()
    return [ModelToViewModelMapper.shift_type(m) for m in models]

# Report Types
@router.get("/report-types")
async def get_report_types(db: Session = Depends(get_db)):
    """Get all report types"""
    repo = ReportTypeRepository(db)
    models = await repo.get_all()
    return [ModelToViewModelMapper.report_type(m) for m in models]