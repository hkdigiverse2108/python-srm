import httpx
import asyncio

async def test_billing_qr():
    url = "http://localhost:8000/api/billing/generate-qr"
    payload = {
        "payment_type": "BUSINESS_ACCOUNT",
        "gst_type": "WITH_GST",
        "amount": 100,
        "phone": "9999999999"
    }
    headers = {
        "Authorization": "Bearer DEV_TOKEN" # In app.py we have dev mode
    }
    
    print(f"Testing {url} with PhonePe...")
    try:
        async with httpx.AsyncClient() as client:
            # We use the dev mode bypass ?dev=true if we can or just hit it
            # But the router has staff_access Dependency which checks JWT.
            # I'll mock the call or run the app with a bypass.
            
            # Actually, I'll just test the Service method directly in a script.
            pass
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Import service directly to test logic
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
    from app.modules.billing.service import BillingService
    from app.core.config import settings
    
    async def run():
        svc = BillingService()
        try:
            print("--- Testing PhonePe Gateway Initiation ---")
            res = await svc.generate_payment_qr_for_new_invoice(
                payment_type="BUSINESS_ACCOUNT",
                gst_type="WITH_GST",
                amount=100.0,
                phone="9999999999"
            )
            print("Result:", res)
            if res.get("type") == "gateway":
                print("SUCCESS: Gateway URL generated.")
            else:
                print("FAILED: Did not return gateway type.")
        except Exception as e:
            print(f"EXCEPTION: {e}")

    asyncio.run(run())
