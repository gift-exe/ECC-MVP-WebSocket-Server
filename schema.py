from pydantic import BaseModel

class ClientPayload(BaseModel):
    answer: str
    from_phone: str
    question: str
    severity_level: int
    sid: str

    class Config:
        from_attributes = True
        orm_mode = True
    @classmethod
    def to_dict(cls, payload):
        return {
            'answer': payload.answer,
            'from_phone':payload.from_phone,
            'question':payload.question,
            'severity_level':payload.severity_level,
            'sid':payload.sid
        }