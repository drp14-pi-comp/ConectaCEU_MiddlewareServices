from uuid import UUID

class UuidExtender:
    EMPTY = UUID('00000000-0000-0000-0000-000000000000')

    @staticmethod
    def empty() -> UUID:
        return UuidExtender.EMPTY
    
    @staticmethod
    def is_empty(uuid_value: UUID) -> bool:
        return uuid_value == UuidExtender.EMPTY