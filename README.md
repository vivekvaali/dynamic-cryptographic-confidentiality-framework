# Dynamic Cryptographic Confidentiality Framework (DCCF)

A multi-tenant data confidentiality framework using AES-128-GCM encryption, dynamic key rotation, tenant isolation, and secure cross-tenant data sharing.

## 1. Project Overview

The Dynamic Cryptographic Confidentiality Framework (DCCF) demonstrates how sensitive data can be protected in a multi-tenant cloud environment.

Each tenant has an independent encryption key. The framework supports secure encryption and decryption, detects unauthorized access and data tampering, and allows controlled data sharing between tenants.

## 2. Key Features

- **AES-128-GCM Encryption:** Provides authenticated encryption for data confidentiality and integrity.
- **Tenant Isolation:** Maintains separate encryption keys for individual tenants.
- **Dynamic Key Rotation:** Generates new keys while retaining previous keys for decrypting existing data.
- **Secure Data Sharing:** Transfers data between tenants through decryption and re-encryption.
- **Tampering Detection:** Detects unauthorized modifications to encrypted data.
- **Performance Evaluation:** Measures encryption time, decryption time, throughput, and ciphertext overhead.
- **Streamlit Interface:** Provides an interactive interface for demonstrating framework operations.

## 3. Technologies Used

- Python
- Cryptography
- AES-128-GCM
- Streamlit
- Pandas
- NumPy
- Matplotlib
- Google Colab

## 4. System Workflow

1. Register tenants in the framework.
2. Generate and maintain an independent encryption key for each tenant.
3. Encrypt data using the selected tenant's key.
4. Decrypt data after validating the tenant and authentication tag.
5. Rotate tenant keys when required.
6. Share data securely by decrypting it for the source tenant and re-encrypting it for the destination tenant.
7. Evaluate encryption and decryption performance.

## 5. Performance Evaluation

The framework was evaluated using programmatically generated test files of different sizes.

The evaluation measures:

- Encryption time
- Decryption time
- Encryption throughput
- Ciphertext overhead

### Performance Charts

**Encryption and Decryption Time**

![Encryption and Decryption Time](results/charts/encryption_decryption_time.png)

**Encryption Throughput**

![Encryption Throughput](results/charts/encryption_throughput.png)

**Ciphertext Overhead**

![Ciphertext Overhead](results/charts/ciphertext_overhead.png)

The measured results are available in:

`results/performance_results.csv`

## 6. Automated Testing

The project includes automated tests covering:

- Encryption and decryption
- Tenant isolation
- Key rotation
- Cross-tenant data sharing
- Tampering detection
- Tenant registration

Run the tests from the project directory:

```bash
python -m unittest discover -s tests -v
```

## 7. Installation and Execution

### Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd <YOUR_REPOSITORY_FOLDER>
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the Streamlit Application

```bash
streamlit run app.py
```

## 8. Repository Structure

```text
Dynamic-Cryptographic-Confidentiality-Framework/
│
├── app.py
├── dccf_framework.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── notebooks/
│   └── DCCF_Final_Project.ipynb
│
├── tests/
│   └── test_dccf.py
│
└── results/
    ├── performance_results.csv
    └── charts/
        ├── ciphertext_overhead.png
        ├── encryption_decryption_time.png
        └── encryption_throughput.png
```

## 9. Security Considerations and Limitations

- AES-GCM provides authenticated encryption.
- Each tenant uses an independent encryption key.
- Previous keys are retained to support decryption of existing encrypted data after key rotation.
- Cross-tenant sharing uses a decrypt-and-re-encrypt approach.
- This project is an academic demonstration and is not intended as a production-ready key management system.
- Production deployments should use a dedicated Key Management Service (KMS) or Hardware Security Module (HSM), along with appropriate access controls and secure key backup procedures.

## 10. Conclusion

DCCF demonstrates a practical approach to protecting data in a multi-tenant environment through authenticated encryption, tenant-level key management, dynamic key rotation, and controlled data sharing.

The project also evaluates encryption performance and provides an interactive Streamlit interface for demonstrating its functionality.

---

**Project:** Dynamic Cryptographic Confidentiality Framework  
**Implementation:** Python | AES-128-GCM | Streamlit
