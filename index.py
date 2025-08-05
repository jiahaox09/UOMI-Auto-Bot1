import time
import os
import random
import sys
import shutil
from datetime import datetime
from web3 import Web3
from dotenv import load_dotenv
from colorama import Fore, Style, init as colorama_init

colorama_init(autoreset=True)
load_dotenv()

# Configuration
RPC_URL = os.getenv("RPC_URL", "https://finney.uomi.ai")
w3 = Web3(Web3.HTTPProvider(RPC_URL))
CHAIN_ID = 4386  # Provided chainId

# Load and parse multiple accounts from .env
ACCOUNTS_RAW = os.getenv("ACCOUNTS", "")
if not ACCOUNTS_RAW:
    raise ValueError("请在.env文件中配置ACCOUNTS（格式：私钥1,地址1;私钥2,地址2）")

# Parse accounts list: each account is a dict with private_key and wallet
ACCOUNTS = []
for account_str in ACCOUNTS_RAW.split(";"):
    if not account_str.strip():
        continue
    try:
        pk, addr = account_str.split(",")
        ACCOUNTS.append({
            "private_key": pk.strip(),
            "wallet": Web3.to_checksum_address(addr.strip())
        })
    except ValueError:
        raise ValueError(f"账户格式错误: {account_str}，正确格式应为'私钥,地址'")

if not ACCOUNTS:
    raise ValueError("未解析到有效账户，请检查ACCOUNTS格式")

ROUTER_ADDRESS = Web3.to_checksum_address("0x197EEAd5Fe3DB82c4Cd55C5752Bc87AEdE11f230")
TOKENS = {
    "SYN": Web3.to_checksum_address("0x2922B2Ca5EB6b02fc5E1EBE57Fc1972eBB99F7e0"),
    "SIM": Web3.to_checksum_address("0x04B03e3859A25040E373cC9E8806d79596D70686"),
    "USDC": Web3.to_checksum_address("0xAA9C4829415BCe70c434b7349b628017C59EC2b1"),
    "DOGE": Web3.to_checksum_address("0xb227C129334BC58Eb4d02477e77BfCCB5857D408"),
    "SYN_TO_UOMI": Web3.to_checksum_address("0x2922B2Ca5EB6b02fc5E1EBE57Fc1972eBB99F7e0"),
    "SIM_TO_UOMI": Web3.to_checksum_address("0x04B03e3859A25040E373cC9E8806d79596D70686"),
    "USDC_TO_UOMI": Web3.to_checksum_address("0xAA9C4829415BCe70c434b7349b628017C59EC2b1"),
    "DOGE_TO_UOMI": Web3.to_checksum_address("0xb227C129334BC58Eb4d02477e77BfCCB5857D408"),
    "UOMI_TO_WUOMI": Web3.to_checksum_address("0x5FCa78E132dF589c1c799F906dC867124a2567b2"),
    "WUOMI_TO_UOMI": Web3.to_checksum_address("0x5FCa78E132dF589c1c799F906dC867124a2567b2")  # New pair added
}

ROUTER_ABI = [{
    "inputs": [
        {"internalType": "bytes", "name": "commands", "type": "bytes"},
        {"internalType": "bytes[]", "name": "inputs", "type": "bytes[]"}
    ],
    "name": "execute",
    "outputs": [],
    "stateMutability": "payable",
    "type": "function"
}]
router = w3.eth.contract(address=ROUTER_ADDRESS, abi=ROUTER_ABI)

# Original Banner
BANNER = """
██╗   ██╗     ██████╗     ███╗   ███╗    ██╗
██║   ██║    ██╔═══██╗    ████╗ ████║    ██║
██║   ██║    ██║   ██║    ██╔████╔██║    ██║
██║   ██║    ██║   ██║    ██║╚██╔╝██║    ██║
╚██████╔╝    ╚██████╔╝    ██║ ╚═╝ ██║    ██║
 ╚═════╝      ╚═════╝     ╚═╝     ╚═╝    ╚═╝
"""

VERSION = "Version 1.0 (Multi-Account Support)"
CREDIT = "LETS FUCK THIS TESTNET--Created By Kazuha"
LAST_RUN_FILE = "last_run.txt"

def save_last_run():
    with open(LAST_RUN_FILE, "w") as f:
        f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

def get_last_run():
    try:
        with open(LAST_RUN_FILE, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "Never"

def center_text(text, terminal_width=None):
    if terminal_width is None:
        terminal_width = shutil.get_terminal_size().columns
    lines = text.strip().split('\n')
    centered_lines = [line.center(terminal_width) for line in lines]
    return '\n'.join(centered_lines)

def loading_animation(message, duration=1.5):
    terminal_width = shutil.get_terminal_size().columns
    frames = ["[◇◇◇◇]", "[◆◇◇◇]", "[◆◆◇◇]", "[◆◆◆◇]", "[◆◆◆◆]"]
    print(f"\n{Fore.CYAN + Style.BRIGHT + message.center(terminal_width)}")
    for _ in range(int(duration * 2)):
        for frame in frames:
            print(f"{Fore.BLUE + frame.center(terminal_width)}", end="\r")
            sys.stdout.flush()
            time.sleep(0.2)
    print(f"{Fore.GREEN + Style.BRIGHT + 'DONE'.center(terminal_width)}")

def select_account():
    terminal_width = shutil.get_terminal_size().columns
    print(f"\n{Fore.CYAN + Style.BRIGHT + '选择操作的账户'.center(terminal_width)}")
    print(f"{Fore.BLUE + '-' * 50}".center(terminal_width))
    for i, account in enumerate(ACCOUNTS, 1):
         print(f"{Fore.WHITE + f'[{i}] 账户: {account['wallet'][:6]}...{account['wallet'][-4:]}'.center(terminal_width)}")
    print(f"{Fore.WHITE + f'[{len(ACCOUNTS) + 1}] 所有账户'.center(terminal_width)}")
    print(f"{Fore.BLUE + '-' * 50}".center(terminal_width))
    
    while True:
        try:
            choice = int(input(f"{Fore.GREEN + '>> 请选择账户 (1-{len(ACCOUNTS)+1}): '}"))
            if 1 <= choice <= len(ACCOUNTS) + 1:
                return choice
            else:
                print(f"{Fore.RED + '无效选择，请重新输入'}")
        except ValueError:
            print(f"{Fore.RED + '请输入数字'}")

def show_swap_menu(wallet):
    terminal_width = shutil.get_terminal_size().columns
    print(f"\n{Fore.WHITE + Style.BRIGHT + 'UOMI DEX Swap Terminal'.center(terminal_width)}")
    print(f"{Fore.CYAN + f'Wallet: {wallet[:6]}...{wallet[-4:]} | Time: {datetime.now().strftime("%H:%M:%S %d-%m-%Y")}'.center(terminal_width)}")
    print(f"{Fore.BLUE + '-' * 50}".center(terminal_width))
    print(f"{Fore.CYAN + 'Swap Options:'.center(terminal_width)}")
    for i, token in enumerate(TOKENS.keys(), 1):
        if token.endswith("_TO_UOMI"):
            option = f"[{i}] {token.split('_TO_')[0]} → UOMI"
        elif token == "UOMI_TO_WUOMI":
            option = f"[{i}] UOMI → WUOMI"
        else:
            option = f"[{i}] UOMI → {token}"
        print(f"{Fore.WHITE + option.center(terminal_width)}")
    print(f"{Fore.WHITE + f'[{len(TOKENS) + 1}] Auto Swap All Pairs'.center(terminal_width)}")
    print(f"{Fore.BLUE + '-' * 50}".center(terminal_width))

def do_swap(token_name, token_addr, is_token_to_uomi=False, private_key=None, wallet=None):
    terminal_width = shutil.get_terminal_size().columns
    # Random amount between 0.001 and 0.004 for UOMI_TO_WUOMI, 0.01 for others
    amount = w3.to_wei(random.uniform(0.001, 0.004), "ether") if token_name == "UOMI_TO_WUOMI" else w3.to_wei(0.01, "ether")
    
    if token_name == "UOMI_TO_WUOMI":
        amount_display = w3.from_wei(amount, "ether")
        print(f"\n{Fore.YELLOW + f'账户: {wallet[:6]}...{wallet[-4:]}'.center(terminal_width)}")
        print(f"{Fore.WHITE + Style.BRIGHT + f'Initiating Swap: {amount_display:.6f} UOMI → WUOMI'.center(terminal_width)}")
        loading_animation("Preparing Transaction")
        try:
            base_fee = w3.eth.get_block("latest").get("baseFeePerGas", w3.to_wei(1, "gwei"))
            gas_price = int(w3.to_wei(0.000000533, "gwei") * 1.5)  # 1.5x provided gasPrice
            tx = {
                "chainId": CHAIN_ID,
                "from": wallet,
                "to": token_addr,
                "value": amount,
                "data": "0xd0e30db0",  # Deposit function selector
                "nonce": w3.eth.get_transaction_count(wallet),
                "gas": 42242,  # Provided gas limit
                "maxFeePerGas": base_fee + w3.to_wei(2, "gwei"),
                "maxPriorityFeePerGas": w3.to_wei(2, "gwei")
            }
            signed = w3.eth.account.sign_transaction(tx, private_key)
            txh = w3.eth.send_raw_transaction(signed.raw_transaction)
            print(f"{Fore.GREEN + f'TX SENT: https://explorer.uomi.ai/tx/{w3.to_hex(txh)}'.center(terminal_width)}")
            w3.eth.wait_for_transaction_receipt(txh)
            print(f"{Fore.GREEN + Style.BRIGHT + 'SWAP EXECUTED'.center(terminal_width)}")
        except Exception as e:
            print(f"{Fore.RED + Style.BRIGHT + f'SWAP ERROR: {str(e)[:50]}...'.center(terminal_width)}")
        return

    # Uniswap V3-style command for other swaps, including WUOMI_TO_UOMI
    SWAP_EXACT_INPUT = bytes([0x00])
    
    if is_token_to_uomi:
        token_symbol = token_name.split('_TO_')[0]
        print(f"\n{Fore.YELLOW + f'账户: {wallet[:6]}...{wallet[-4:]}'.center(terminal_width)}")
        print(f"{Fore.WHITE + Style.BRIGHT + f'Initiating Swap: 0.01 {token_symbol} → UOMI'.center(terminal_width)}")
        loading_animation("Approving Token")
        
        # Approve ERC20 token
        token_contract_abi = [
            {
                "constant": False,
                "inputs": [
                    {"name": "_spender", "type": "address"},
                    {"name": "_value", "type": "uint256"}
                ],
                "name": "approve",
                "outputs": [{"name": "", "type": "bool"}],
                "type": "function"
            }
        ]
        token_contract = w3.eth.contract(address=token_addr, abi=token_contract_abi)
        try:
            approve_tx = token_contract.functions.approve(ROUTER_ADDRESS, amount).build_transaction({
                "from": wallet,
                "nonce": w3.eth.get_transaction_count(wallet),
                "gas": 100000,
                "maxFeePerGas": w3.eth.get_block("latest").get("baseFeePerGas", w3.to_wei(1, "gwei")) + w3.to_wei(2, "gwei"),
                "maxPriorityFeePerGas": w3.to_wei(2, "gwei")
            })
            signed_approve = w3.eth.account.sign_transaction(approve_tx, private_key)
            approve_txh = w3.eth.send_raw_transaction(signed_approve.raw_transaction)
            w3.eth.wait_for_transaction_receipt(approve_txh)
            print(f"{Fore.GREEN + f'APPROVED: https://explorer.uomi.ai/tx/{w3.to_hex(approve_txh)}'.center(terminal_width)}")
        except Exception as e:
            print(f"{Fore.RED + Style.BRIGHT + f'APPROVAL ERROR: {str(e)[:50]}...'.center(terminal_width)}")
            return
        
        # Define output token as UOMI (assumed as SYN)
        output_token = TOKENS["SYN"]
        commands = SWAP_EXACT_INPUT
        inputs = [
            Web3.to_bytes(hexstr=Web3.to_hex(
                Web3.solidity_keccak(['address', 'address', 'uint24', 'address', 'uint256', 'uint256', 'uint160'],
                    [token_addr, output_token, 3000, wallet, amount, 0, 0])
            ))
        ]
        value = 0
    else:
        print(f"\n{Fore.YELLOW + f'账户: {wallet[:6]}...{wallet[-4:]}'.center(terminal_width)}")
        print(f"{Fore.WHITE + Style.BRIGHT + f'Initiating Swap: 0.01 UOMI → {token_name}'.center(terminal_width)}")
        commands = SWAP_EXACT_INPUT
        inputs = [
            Web3.to_bytes(hexstr=Web3.to_hex(
                Web3.solidity_keccak(['address', 'address', 'uint24', 'address', 'uint256', 'uint256', 'uint160'],
                    [TOKENS["SYN"], token_addr, 3000, wallet, amount, 0, 0])
            ))
        ]
        value = amount

    loading_animation("Executing Swap")
    try:
        base_fee = w3.eth.get_block("latest").get("baseFeePerGas", w3.to_wei(1, "gwei"))
        tx = router.functions.execute(commands, inputs).build_transaction({
            "chainId": CHAIN_ID,
            "from": wallet,
            "value": value,
            "nonce": w3.eth.get_transaction_count(wallet),
            "gas": 300000,
            "maxFeePerGas": base_fee + w3.to_wei(2, "gwei"),
            "maxPriorityFeePerGas": w3.to_wei(2, "gwei")
        })
        signed = w3.eth.account.sign_transaction(tx, private_key)
        txh = w3.eth.send_raw_transaction(signed.raw_transaction)
        print(f"{Fore.GREEN + f'TX SENT: https://explorer.uomi.ai/tx/{w3.to_hex(txh)}'.center(terminal_width)}")
        w3.eth.wait_for_transaction_receipt(txh)
        print(f"{Fore.GREEN + Style.BRIGHT + 'SWAP EXECUTED'.center(terminal_width)}")
    except Exception as e:
        print(f"{Fore.RED + Style.BRIGHT + f'SWAP ERROR: {str(e)[:50]}...'.center(terminal_width)}")

def main():
    terminal_width = shutil.get_terminal_size().columns
    print(center_text(Fore.CYAN + Style.BRIGHT + BANNER))
    print(center_text(Fore.GREEN + Style.BRIGHT + VERSION))
    print(center_text(Fore.YELLOW + CREDIT))
    print(center_text(Fore.WHITE + f"Last Run: {get_last_run()}"))
    print(center_text(Fore.BLUE + "-" * 50))

    while True:
        # Select account first
        account_choice = select_account()
        target_accounts = []
        if account_choice == len(ACCOUNTS) + 1:
            target_accounts = ACCOUNTS  # All accounts
        else:
            target_accounts = [ACCOUNTS[account_choice - 1]]  # Single account

        # Show swap menu with first account's info (for display only)
        show_swap_menu(target_accounts[0]["wallet"])
        swap_choice = input(f"{Fore.GREEN + '>> 选择操作 (1-' + str(len(TOKENS) + 1) + '): '}")

        # Parse swap choice
        token_name = None
        token_addr = None
        is_token_to_uomi = False
        auto_swap_all = False

        try:
            swap_choice_int = int(swap_choice)
            if swap_choice_int == len(TOKENS) + 1:
                auto_swap_all = True
            elif 1 <= swap_choice_int <= len(TOKENS):
                token_name = list(TOKENS.keys())[swap_choice_int - 1]
                token_addr = TOKENS[token_name]
                is_token_to_uomi = token_name.endswith("_TO_UOMI")
            else:
                print(f"{Fore.RED + '无效的选择，请重试'}")
                continue
        except ValueError:
            print(f"{Fore.RED + '请输入有效的数字'}")
            continue

        # Get number of swaps
        try:
            num_swaps = int(input(f"{Fore.GREEN + '>> 输入执行次数: '}"))
            if num_swaps < 1:
                print(f"{Fore.RED + '次数必须大于0'}")
                continue
        except ValueError:
            print(f"{Fore.RED + '请输入有效的数字'}")
            continue

        # Execute swaps for target accounts
        for account in target_accounts:
            print(f"\n{Fore.MAGENTA + Style.BRIGHT + f'===== 开始处理账户: {account["wallet"][:6]}...{account["wallet"][-4:]} ====='.center(terminal_width)}")
            if auto_swap_all:
                # Auto swap all pairs
                for _ in range(num_swaps):
                    print(f"\n{Fore.CYAN + f'===== 第 {_+1}/{num_swaps} 轮自动交换 ====='.center(terminal_width)}")
                    for token in TOKENS:
                        addr = TOKENS[token]
                        to_uomi = token.endswith("_TO_UOMI")
                        do_swap(token, addr, to_uomi, account["private_key"], account["wallet"])
                        time.sleep(random.uniform(2, 5))
            else:
                # Single swap type
                for i in range(num_swaps):
                    print(f"\n{Fore.CYAN + f'===== 第 {i+1}/{num_swaps} 次交换 ====='.center(terminal_width)}")
                    do_swap(token_name, token_addr, is_token_to_uomi, account["private_key"], account["wallet"])
                    time.sleep(random.uniform(2, 5))

        save_last_run()
        print(f"\n{Fore.GREEN + Style.BRIGHT + '所有操作已完成'.center(terminal_width)}")
        continue_choice = input(f"{Fore.GREEN + '是否继续? (y/n): '}").lower()
        if continue_choice != 'y':
            print(f"{Fore.CYAN + '感谢使用，再见!'}")
            break

if __name__ == "__main__":
    main()
