from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Trade:
    id: int
    symbol: str
    side: str  # 'buy' or 'sell'
    entry_price: float
    exit_price: Optional[float] = None
    size: float = 0.0
    stop_loss: float = 0.0
    take_profit: float = 0.0
    entry_time: datetime = None
    exit_time: Optional[datetime] = None
    pnl: Optional[float] = None
    pnl_percent: Optional[float] = None
    risk_amount: float = 0.0
    status: str = 'open'  # 'open', 'closed', 'cancelled'
    
    def __post_init__(self):
        if self.entry_time is None:
            self.entry_time = datetime.now()