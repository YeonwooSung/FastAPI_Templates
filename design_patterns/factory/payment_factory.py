from fastapi import FastAPI, HTTPException

class PaymentProcessor:
    def process_payment(self, amount: float):
        pass

class CreditCardProcessor(PaymentProcessor):
    def process_payment(self, amount: float):
        return f"Processing credit card payment for {amount} dollars."

class PayPalProcessor(PaymentProcessor):
    def process_payment(self, amount: float):
        return f"Processing PayPal payment for {amount} dollars."

class PaymentProcessorFactory:
    @staticmethod
    def create_processor(processor_type: str) -> PaymentProcessor:
        if processor_type == "credit_card":
            return CreditCardProcessor()
        elif processor_type == "paypal":
            return PayPalProcessor()
        else:
            raise HTTPException(status_code=400, detail="Invalid payment processor type.")

app = FastAPI()

@app.post("/process_payment/{processor_type}")
def process_payment(processor_type: str, amount: float):
    processor = PaymentProcessorFactory.create_processor(processor_type)
    return processor.process_payment(amount)
