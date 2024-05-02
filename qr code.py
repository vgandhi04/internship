import qrcode
from pyzbar.pyzbar import decode
from PIL import Image

# Define a list of URLs
urls = [
    "https://www.example.com",
    "https://www.google.com",
    "https://www.github.com",
    "https://www.python.org"
]

# Create a QR code instance
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)

# Add a placeholder data to the QR code
qr.add_data("placeholder")
qr.make(fit=True)

# Generate the QR code image
img = qr.make_image(fill_color="black", back_color="white")
img.save("qr_code.png")

print("QR code saved as 'qr_code.png'. Please scan the code.")

# Wait for the user to scan the QR code
decoded = decode(Image.open("qr_code.png"))
if decoded:
    print("QR code scanned. Select a URL to redirect to:")
    for i, url in enumerate(urls):
        print(f"{i+1}. {url}")

    user_input = int(input("Enter the number of the URL you want to use: "))
    selected_url = urls[user_input - 1]

    print(f"Redirecting to: {selected_url}")
    # Add code here to open the selected URL or perform any other actions
else:
    print("No QR code detected.")