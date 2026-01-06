class AttackReference:
    def __init__(self, reference_id: int, source_name: str, description: str, url: str) -> None:
        self.reference_id: int = reference_id
        self.source_name: str = source_name
        self.description: str = description
        self.url: str = url
