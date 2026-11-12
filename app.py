
import json
from pathlib import Path
from datetime import datetime

import pandas as pd
import streamlit as st

from dccf_framework import DCCF


st.set_page_config(
    page_title="DCCF | Secure File Framework",
    page_icon="🔐",
    layout="wide"
)

KEY_DIR = "/content/dccf_keys"

if "dccf" not in st.session_state:
    st.session_state.dccf = DCCF(key_dir=KEY_DIR)

dccf = st.session_state.dccf


st.title("🔐 Dynamic Cryptographic Confidentiality Framework")
st.caption("A multi-tenant secure file encryption and sharing demonstration.")

st.sidebar.title("DCCF Navigation")

page = st.sidebar.radio(
    "Select a feature",
    [
        "Dashboard",
        "Tenant Management",
        "File Encryption",
        "File Decryption",
        "Secure Data Sharing",
        "Key Rotation",
        "Operation Logs"
    ]
)


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

if page == "Dashboard":
    st.header("Project Dashboard")

    tenants = list(dccf.tenants.keys())

    col1, col2, col3 = st.columns(3)

    col1.metric("Configured Tenants", len(tenants))
    col2.metric("Available Keys", sum(
        len(item["keys"]) for item in dccf.tenants.values()
    ))
    col3.metric("Recorded Operations", len(dccf.logs))

    st.subheader("Configured Tenants")

    if tenants:
        st.dataframe(
            pd.DataFrame({"Tenant": tenants}),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No tenants configured. Register a tenant to begin.")

    st.info(
        "Use the sidebar to register tenants, encrypt files, decrypt files, "
        "share data, and rotate encryption keys."
    )


# --------------------------------------------------
# TENANT MANAGEMENT
# --------------------------------------------------

elif page == "Tenant Management":
    st.header("Tenant Management")

    tenant_name = st.text_input(
        "Enter a tenant name",
        placeholder="Example: Tenant_D"
    )

    if st.button("Register Tenant"):
        try:
            if dccf.add_tenant(tenant_name.strip()):
                st.success(f"{tenant_name} registered successfully.")
            else:
                st.warning("This tenant is already registered.")
        except Exception as error:
            st.error(str(error))

    st.subheader("Registered Tenants")

    if dccf.tenants:
        st.write(list(dccf.tenants.keys()))
    else:
        st.info("No tenants registered yet.")


# --------------------------------------------------
# FILE ENCRYPTION
# --------------------------------------------------

elif page == "File Encryption":
    st.header("Encrypt a File")

    if not dccf.tenants:
        st.warning("Register a tenant before encrypting files.")
    else:
        tenant = st.selectbox(
            "Select the tenant",
            list(dccf.tenants.keys())
        )

        uploaded_file = st.file_uploader(
            "Upload a file",
            key="encrypt_upload"
        )

        if st.button("Encrypt File"):
            if uploaded_file is None:
                st.warning("Please upload a file.")
            else:
                try:
                    file_bytes = uploaded_file.getvalue()

                    encrypted_record = dccf.encrypt(
                        tenant,
                        file_bytes
                    )

                    package = {
                        "file_name": uploaded_file.name,
                        "encrypted_data": encrypted_record
                    }

                    encrypted_json = json.dumps(
                        package,
                        indent=4
                    ).encode("utf-8")

                    st.success("File encrypted successfully.")

                    st.download_button(
                        "Download Encrypted File",
                        data=encrypted_json,
                        file_name=uploaded_file.name + ".dccf.json",
                        mime="application/json"
                    )

                    st.write("Encryption Key ID:", encrypted_record["kid"])
                    st.caption(
                        "The encrypted package contains the encrypted data, "
                        "tenant identifier, and key ID. It does not contain "
                        "the encryption key."
                    )

                except Exception as error:
                    st.error(f"Encryption failed: {error}")


# --------------------------------------------------
# FILE DECRYPTION
# --------------------------------------------------

elif page == "File Decryption":
    st.header("Decrypt an Encrypted File")

    encrypted_file = st.file_uploader(
        "Upload a DCCF encrypted JSON file",
        type=["json"],
        key="decrypt_upload"
    )

    if encrypted_file is not None:
        try:
            package = json.loads(
                encrypted_file.getvalue().decode("utf-8")
            )

            encrypted_record = package["encrypted_data"]
            original_name = Path(
                package.get("file_name", "decrypted_file")
            ).name

            tenant = encrypted_record["tenant"]

            st.write("Encrypted for tenant:", tenant)
            st.write("Key ID:", encrypted_record["kid"])

            if st.button("Decrypt File"):
                if tenant not in dccf.tenants:
                    st.error(
                        "The required tenant key is unavailable in this runtime."
                    )
                else:
                    plaintext = dccf.decrypt(
                        tenant,
                        encrypted_record
                    )

                    st.success("File decrypted successfully.")

                    st.download_button(
                        "Download Decrypted File",
                        data=plaintext,
                        file_name=original_name,
                        mime="application/octet-stream"
                    )

        except Exception as error:
            st.error(f"Unable to read or decrypt this file: {error}")


# --------------------------------------------------
# SECURE DATA SHARING
# --------------------------------------------------

elif page == "Secure Data Sharing":
    st.header("Secure Data Sharing")

    tenants = list(dccf.tenants.keys())

    if len(tenants) < 2:
        st.warning("Register at least two tenants to use secure sharing.")
    else:
        source_tenant = st.selectbox(
            "Source Tenant",
            tenants,
            key="share_source"
        )

        target_options = [
            tenant for tenant in tenants
            if tenant != source_tenant
        ]

        target_tenant = st.selectbox(
            "Target Tenant",
            target_options
        )

        shared_file = st.file_uploader(
            "Upload the source tenant's encrypted JSON file",
            type=["json"],
            key="share_upload"
        )

        if st.button("Share Encrypted File"):
            if shared_file is None:
                st.warning("Please upload an encrypted file.")
            else:
                try:
                    package = json.loads(
                        shared_file.getvalue().decode("utf-8")
                    )

                    source_record = package["encrypted_data"]

                    shared_record = dccf.share_data(
                        source_tenant,
                        target_tenant,
                        source_record
                    )

                    shared_package = {
                        "file_name": package.get(
                            "file_name",
                            "shared_file"
                        ),
                        "encrypted_data": shared_record
                    }

                    download_data = json.dumps(
                        shared_package,
                        indent=4
                    ).encode("utf-8")

                    st.success(
                        f"File securely re-encrypted for {target_tenant}."
                    )

                    st.download_button(
                        "Download Shared Encrypted File",
                        data=download_data,
                        file_name="shared_" + Path(
                            package.get("file_name", "file")
                        ).name + ".dccf.json",
                        mime="application/json"
                    )

                    st.caption(
                        "This demonstration uses decrypt-and-re-encrypt "
                        "sharing. It is not proxy re-encryption."
                    )

                except Exception as error:
                    st.error(f"Sharing failed: {error}")


# --------------------------------------------------
# KEY ROTATION
# --------------------------------------------------

elif page == "Key Rotation":
    st.header("Dynamic Key Rotation")

    tenants = list(dccf.tenants.keys())

    if not tenants:
        st.warning("Register a tenant before rotating its key.")
    else:
        tenant = st.selectbox(
            "Select tenant",
            tenants
        )

        current_key = dccf.tenants[tenant]["current_key_id"]

        st.write("Current Key ID:", current_key)

        if st.button("Rotate Encryption Key"):
            try:
                new_key_id = dccf.rotate_key(tenant)

                st.success("Encryption key rotated successfully.")
                st.write("New Key ID:", new_key_id)
                st.info(
                    "Older keys are retained so previously encrypted "
                    "files can still be decrypted."
                )

            except Exception as error:
                st.error(str(error))


# --------------------------------------------------
# OPERATION LOGS
# --------------------------------------------------

elif page == "Operation Logs":
    st.header("Operation Logs")

    if dccf.logs:
        log_df = pd.DataFrame(dccf.logs)

        st.dataframe(
            log_df,
            use_container_width=True,
            hide_index=True
        )

        csv_data = log_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Download Operation Logs",
            data=csv_data,
            file_name="dccf_operation_logs.csv",
            mime="text/csv"
        )
    else:
        st.info("No operations recorded in this application session.")


st.divider()
st.caption(
    "DCCF Academic Demonstration | AES-128-GCM | "
    "Use a managed key service for production deployments."
)
