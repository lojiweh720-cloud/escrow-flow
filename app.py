import hashlib

import streamlit as st
import streamlit.components.v1 as components

# --- HARDCODED PLATFORM CONFIGURATION ---
PLATFORM_WALLET = "9n43d6JU2xxyHJbAFeJmevcBoxvuiGgTatDB5JJgeNDX"
PLATFORM_FEE_PCT = 0.01  # 1% platform fee

st.set_page_config(
    page_title="EscrowFlow Web3 Gateway",
    page_icon="💸",
    layout="wide",
)

# Mock database for escrow transactions
if "escrow_db" not in st.session_state:
    st.session_state.escrow_db = {}


def calculate_fees(amount):
    fee = amount * PLATFORM_FEE_PCT
    net_amount = amount - fee
    return round(fee, 4), round(net_amount, 4)


# --- USER INTERFACE ---
st.title("💸 EscrowFlow: Web3 Cross-Border P2P Gateway")
st.subheader("Secure, instant Solana-powered digital payments for African solopreneurs")

# Phantom wallet connection component
st.write("### 🌐 Live Solana Extension Link")
phantom_button_html = f"""
<div style="text-align: center; margin-top: 10px;">
    <button id="connect_btn" style="
        background-color: #512da8;
        color: white;
        padding: 12px 24px;
        border: none;
        border-radius: 8px;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
        width: 100%;">
        ⚡ Connect Phantom Wallet
    </button>
    <p id="wallet_status" style="color: #888; font-family: sans-serif; margin-top: 10px; font-size: 14px;">
        Status: Disconnected (Treasury linked to {PLATFORM_WALLET[:6]}...)
    </p>
</div>

<script>
    const button = document.getElementById('connect_btn');
    const statusText = document.getElementById('wallet_status');

    button.addEventListener('click', async () => {{
        const isPhantomInstalled = window.solana && window.solana.isPhantom;
        if (!isPhantomInstalled) {{
            statusText.innerText = "❌ Phantom Wallet not found. Please install the browser extension.";
            window.open("https://phantom.app", "_blank");
            return;
        }}

        try {{
            statusText.innerText = "Connecting...";
            const response = await window.solana.connect();
            const publicKey = response.publicKey.toString();
            statusText.style.color = "#00E676";
            statusText.innerText = "✅ Connected Wallet: " + publicKey.slice(0, 6) + "..." + publicKey.slice(-4);
            button.innerText = "Wallet Linked";
            button.style.backgroundColor = "#00E676";
        }} catch (err) {{
            statusText.style.color = "#FF1744";
            statusText.innerText = "❌ Connection request rejected.";
        }}
    }});
</script>
"""
components.html(phantom_button_html, height=120)

# Sidebar information
st.sidebar.header("🔑 Active Platform Rules")
st.sidebar.info(f"**Treasury Destination:**\n`{PLATFORM_WALLET}`")
st.sidebar.write(f"**Platform Fee:** {PLATFORM_FEE_PCT * 100}% per cleared transaction.")

# Application tabs
tab1, tab2, tab3 = st.tabs(
    ["🆕 Create Escrow Payment", "🔐 Manage & Release Funds", "📊 Platform Earnings Ledger"]
)

with tab1:
    st.header("Create a Secure Escrow Contract")
    with st.form("create_escrow_form"):
        project_title = st.text_input(
            "Project Name / Course Title",
            placeholder="e.g., Financial Coaching Course",
        )
        amount_usdc = st.number_input(
            "Amount (USDC / Digital Dollars)",
            min_value=1.0,
            step=0.5,
        )
        vendor_addr = st.text_input(
            "Vendor Solana Wallet Address (Receiver)",
            placeholder="e.g., 4jZq...82wn",
        )
        submit_btn = st.form_submit_button("Initiate Escrow Deposit")

        if submit_btn:
            if not vendor_addr or not project_title:
                st.error("❌ Please supply a project title and receiver address.")
            else:
                fee, net = calculate_fees(amount_usdc)
                tx_id = f"TX-{hashlib.md5(project_title.encode()).hexdigest()[:6].upper()}"
                st.session_state.escrow_db[tx_id] = {
                    "title": project_title,
                    "receiver": vendor_addr,
                    "gross_amount": amount_usdc,
                    "platform_fee": fee,
                    "net_amount": net,
                    "status": "Locked in Escrow 🔒",
                }
                st.success(f"🎉 Escrow initialized! Transaction ID: **{tx_id}**")

with tab2:
    st.header("Release Escrowed Funds")
    tx_to_release = st.text_input(
        "Enter Escrow Transaction ID to clear",
        placeholder="e.g., TX-A1B2C3",
    )

    if tx_to_release in st.session_state.escrow_db:
        tx = st.session_state.escrow_db[tx_to_release]
        st.write(f"**Project:** {tx['title']} | **Payout:** {tx['net_amount']} USDC")
        if tx["status"] == "Locked in Escrow 🔒" and st.button(
            "Confirm & Disburse Funds 🚀"
        ):
            tx["status"] = "Released to Vendor ✅"
            st.success("💵 Success! Cut sent to platform treasury wallet.")
    elif tx_to_release:
        st.error("Transaction code invalid.")

with tab3:
    st.header("📈 API Platform Earnings")
    if st.session_state.escrow_db:
        total_fees = sum(
            tx["platform_fee"]
            for tx in st.session_state.escrow_db.values()
            if tx["status"] == "Released to Vendor ✅"
        )
        st.metric(label="Accumulated Profits (USDC)", value=f"{total_fees} USDC")
        st.write("### App Internal Database State")
        st.json(st.session_state.escrow_db)
    else:
        st.info("No network volume processed yet.")
