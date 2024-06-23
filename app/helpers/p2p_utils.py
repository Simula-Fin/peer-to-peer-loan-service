from math import pow

class ProfitCalculator:
    @staticmethod
    def calculate_profits(investment_amount: float, rate_juros: float, duration: int):
        """
        Calcula o lucro do banco e do investidor.
        
        :param investment_amount: Valor do empréstimo.
        :param rate_juros: Taxa de juros mensal (em porcentagem).
        :param duration: Duração do empréstimo em meses.
        :param bank_profit_rate: Percentual do lucro total que será destinado ao banco.
        :return: Tuple contendo (bank_profit, investor_profit).
        """
        # Taxa de juros mensal
        bank_profit_rate = 0.2
        i = rate_juros / 100

        # Calcular o valor da parcela usando a fórmula da Tabela Price
        monthly_payment = investment_amount * (i * pow(1 + i, duration)) / (pow(1 + i, duration) - 1)

        # Calcular lucro do banco e do investidor
        total_payment = monthly_payment * duration
        total_interest = total_payment - investment_amount
        bank_profit = total_interest * bank_profit_rate
        investor_profit = total_interest - bank_profit

        return bank_profit, investor_profit, monthly_payment