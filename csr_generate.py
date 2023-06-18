from OpenSSL import crypto
import json

def main(args):
    # Extract input arguments
    csr_data = args.get("csr_data")
    key_size = args.get("key_size")

    # Extract values from the csr_data dictionary
    common_name = csr_data.get("common_name")
    country = csr_data.get("country")
    state = csr_data.get("state")
    locality = csr_data.get("locality")
    organization = csr_data.get("organization")
    organizational_unit = csr_data.get("organizational_unit")

    # Variables
    TYPE_RSA = crypto.TYPE_RSA
    key = crypto.PKey()

    # Generate the key
    def generate_key():
        key.generate_key(TYPE_RSA, key_size)
        return crypto.dump_privatekey(crypto.FILETYPE_PEM, key).decode()

    # Generate CSR
    def generate_csr():
        req = crypto.X509Req()
        req.get_subject().CN = common_name
        req.get_subject().C = country
        req.get_subject().ST = state
        req.get_subject().L = locality
        req.get_subject().O = organization
        req.get_subject().OU = organizational_unit
        req.set_pubkey(key)
        req.sign(key, "sha256")
        csr = crypto.dump_certificate_request(crypto.FILETYPE_PEM, req).decode()
        return csr

    # Generate the key and CSR
    private_key = generate_key()
    csr = generate_csr()

    # Create the result dictionary
    result = {
        "private_key": private_key,
        "csr": csr
    }

    # Convert the result dictionary to JSON string
    json_result = json.dumps(result, indent=4)

    # Return the JSON result
    return {"result": json_result}