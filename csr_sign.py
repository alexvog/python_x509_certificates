import json
from datetime import datetime
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.x509.oid import NameOID
import random


def main(args):
    # Extract input arguments
    cacrt = args.get("cacrt")
    cakey = args.get("cakey")
    csr_data = args.get("csr_data")
    
    # Extract values from the csr_data dictionary
    csr_text = csr_data.get("csr")
    not_valid_before = csr_data.get("not_valid_before")
    not_valid_after = csr_data.get("not_valid_after")

    # Load the CA certificate and private key
    ca_cert = x509.load_pem_x509_certificate(cacrt.encode(), default_backend())
    ca_key = serialization.load_pem_private_key(cakey.encode(), None, default_backend())

    # Remove unnecessary whitespace characters from CSR text
    csr_text = csr_text.strip()

    # Load the CSR
    csr = x509.load_pem_x509_csr(csr_text.encode(), default_backend())
    builder = x509.CertificateBuilder().subject_name(csr.subject)

    # Parse the validity dates
    not_valid_before = datetime.strptime(not_valid_before, "%Y-%m-%d")
    not_valid_after = datetime.strptime(not_valid_after, "%Y-%m-%d")

    # Set the certificate's validity period
    builder = builder.not_valid_before(not_valid_before)
    builder = builder.not_valid_after(not_valid_after)

    # Set the certificate's public key
    builder = builder.public_key(csr.public_key())

    # Add the common name (CN) to the subject
    common_name = csr.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
    builder = builder.add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName(common_name)
        ]),
        critical=False
    )

    # Add the CA certificate as the issuer
    builder = builder.issuer_name(ca_cert.subject)

    # Generate a random serial number for the certificate
    builder = builder.serial_number(random.randint(1, 2 ** 32))

    # Sign the certificate with the CA private key
    certificate = builder.sign(
        private_key=ca_key,
        algorithm=hashes.SHA256(),
        backend=default_backend()
    )

    # Prepare the signed CSR JSON response
    signed_csr = {
        'certificate': certificate.public_bytes(serialization.Encoding.PEM).decode(),
        'common_name': common_name
    }
    
    return signed_csr
