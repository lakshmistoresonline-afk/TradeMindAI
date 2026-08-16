class RiskEngine:
    @staticmethod
    def calculate_position_size(capital: float, risk_per_trade_pct: float, stop_loss_pct: float):
        # Risk Amount = Capital * Risk%
        # Position Size = Risk Amount / Stop Loss%
        risk_amount = capital * (risk_per_trade_pct / 100)
        position_size = risk_amount / (stop_loss_pct / 100)
        return position_size

    @staticmethod
    def kelly_criterion(win_prob: float, win_loss_ratio: float):
        # K = (p*b - q) / b
        # p = probability of win
        # q = probability of loss (1-p)
        # b = win/loss ratio (avg win / avg loss)
        k = (win_prob * win_loss_ratio - (1 - win_prob)) / win_loss_ratio
        return k
