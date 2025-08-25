import time
from datetime import datetime
from typing import Dict, Optional, List
from models.trade import Trade
from config import RISK_PER_TRADE

class TradingService:
    def __init__(self):
        self.trade_history: List[Trade] = []
        self.current_positions: Dict[str, Trade] = {}
        self.next_trade_id = 1
        
    def execute_trade(self, symbol: str, is_buy: bool, entry_price: float, 
                     stop_loss: float, take_profit: float, size: float = None,
                     risk_amount: float = None, current_balance: float = 1000.0) -> Optional[Trade]:
        """Execute a new trade"""
        try:
            if risk_amount is None:
                risk_amount = current_balance * RISK_PER_TRADE
                
            if size is None:
                # Calculate size based on risk
                risk_per_unit = abs(entry_price - stop_loss)
                if risk_per_unit == 0:
                    return None
                size = risk_amount / risk_per_unit
            
            trade = Trade(
                id=self.next_trade_id,
                symbol=symbol,
                side='buy' if is_buy else 'sell',
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                size=size,
                risk_amount=risk_amount,
                entry_time=datetime.now(),
                status='open'
            )
            
            self.current_positions[str(self.next_trade_id)] = trade
            self.next_trade_id += 1
            
            print(f"Trade executed: {trade.side} {trade.symbol} at {trade.entry_price}")
            return trade
            
        except Exception as e:
            print(f"Error executing trade: {e}")
            return None
    
    def close_position(self, trade_id: str, exit_price: float) -> bool:
        """Close an open position"""
        try:
            if trade_id not in self.current_positions:
                return False
                
            trade = self.current_positions[trade_id]
            trade.exit_price = exit_price
            trade.exit_time = datetime.now()
            trade.status = 'closed'
            
            # Calculate P&L
            if trade.side == 'buy':
                trade.pnl = (exit_price - trade.entry_price) * trade.size
            else:
                trade.pnl = (trade.entry_price - exit_price) * trade.size
                
            trade.pnl_percent = (trade.pnl / (trade.entry_price * trade.size)) * 100
            
            # Move to history
            self.trade_history.append(trade)
            del self.current_positions[trade_id]
            
            print(f"Position closed: {trade.side} {trade.symbol} at {exit_price}, P&L: {trade.pnl:.2f}")
            return True
            
        except Exception as e:
            print(f"Error closing position: {e}")
            return False
    
    def check_open_positions(self, current_price: float, 
                             current_balance: float) -> tuple:
        """Check all open positions for stop loss or take profit triggers"""
        closed_trades = []
        total_pnl = 0.0
        
        try:
            positions_to_close = []
            
            for trade_id, trade in self.current_positions.items():
                if trade.status != 'open':
                    continue
                    
                pnl = 0.0
                if trade.side == 'buy':
                    pnl = (current_price - trade.entry_price) * trade.size
                    # Check stop loss and take profit
                    if current_price <= trade.stop_loss:
                        positions_to_close.append((trade_id, trade.stop_loss))
                        print(f"Stop loss triggered for {trade.symbol}")
                    elif current_price >= trade.take_profit:
                        positions_to_close.append((trade_id, trade.take_profit))
                        print(f"Take profit triggered for {trade.symbol}")
                else:  # sell
                    pnl = (trade.entry_price - current_price) * trade.size
                    # Check stop loss and take profit
                    if current_price >= trade.stop_loss:
                        positions_to_close.append((trade_id, trade.stop_loss))
                        print(f"Stop loss triggered for {trade.symbol}")
                    elif current_price <= trade.take_profit:
                        positions_to_close.append((trade_id, trade.take_profit))
                        print(f"Take profit triggered for {trade.symbol}")
                
                total_pnl += pnl
            
            # Close positions
            for trade_id, exit_price in positions_to_close:
                if self.close_position(trade_id, exit_price):
                    closed_trades.append(trade_id)
            
            return closed_trades, total_pnl
            
        except Exception as e:
            print(f"Error checking open positions: {e}")
            return [], 0.0
    
    def get_open_positions(self) -> Dict[str, Trade]:
        """Get all open positions"""
        return self.current_positions.copy()
    
    def get_trade_history(self, limit: int = None) -> List[Trade]:
        """Get trade history"""
        if limit:
            return self.trade_history[-limit:]
        return self.trade_history.copy()
    
    def get_position_by_id(self, trade_id: str) -> Optional[Trade]:
        """Get specific position by ID"""
        return self.current_positions.get(trade_id)
    
    def get_total_pnl(self) -> float:
        """Calculate total P&L from all closed trades"""
        return sum(trade.pnl for trade in self.trade_history if trade.pnl is not None)
    
    def get_win_rate(self) -> float:
        """Calculate win rate from trade history"""
        if not self.trade_history:
            return 0.0
            
        winning_trades = [t for t in self.trade_history if t.pnl and t.pnl > 0]
        return len(winning_trades) / len(self.trade_history) * 100
    
    def get_profit_factor(self) -> float:
        """Calculate profit factor from trade history"""
        if not self.trade_history:
            return 0.0
            
        winning_trades = [t for t in self.trade_history if t.pnl and t.pnl > 0]
        losing_trades = [t for t in self.trade_history if t.pnl and t.pnl <= 0]
        
        total_profit = sum(t.pnl for t in winning_trades)
        total_loss = abs(sum(t.pnl for t in losing_trades))
        
        return total_profit / total_loss if total_loss > 0 else 0.0