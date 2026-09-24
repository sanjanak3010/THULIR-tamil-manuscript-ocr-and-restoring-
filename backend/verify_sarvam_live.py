import os
import time
from dotenv import load_dotenv
from sarvamai import SarvamAI

# Load backend/.env
load_dotenv()

api_key = os.getenv("SARVAM_API_KEY")

if not api_key:
    print("❌ SARVAM_API_KEY not found")
    exit()

print("✅ API key found")
print("Key length:", len(api_key))

client = SarvamAI(
    api_subscription_key=api_key
)

test_image = "test_manuscript.jpeg"

print("✅ Real Tamil manuscript image selected:", test_image)

try:
    print("📤 Sending image to Sarvam Document AI...")

    with open(test_image, "rb") as f:
        job = client.doc_ai.digitise(
            file=[("test_manuscript.jpeg", f, "image/jpeg")],
            language="ta-IN",
            output_format="md"
        )

    print("✅ Job created")
    print("Job ID:", job.job_id)
    print("Status:", job.status)

    terminal_states = {
        "completed",
        "partially_completed",
        "failed",
        "rejected"
    }

    while True:
        status = client.doc_ai.get_status(job_id=job.job_id)

        print("Current status:", status.status)

        if status.status.lower() in terminal_states:
            break

        time.sleep(5)

    if status.status.lower() in {"completed", "partially_completed"}:
        print("🎉 SARVAM OCR IS WORKING!")
        
        result = client.doc_ai.get_results(job_id=job.job_id)
        print("Result:")
        print(result)

    else:
        print("❌ Sarvam job failed")
        print(status)

except Exception as e:
    print("❌ ERROR:")
    print(type(e).__name__)
    print(str(e))