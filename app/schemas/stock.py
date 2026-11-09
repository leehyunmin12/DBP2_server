from pydantic import BaseModel, ConfigDict

class StockResponse(BaseModel):
    # pydantic이 DB에서 꺼낸 객체를 읽어서 필드를 채워 줌 / 동작 설정
    model_config = ConfigDict(from_attributes=True)

    market: str
    symbol: str
    name: str