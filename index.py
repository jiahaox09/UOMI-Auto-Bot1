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
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
WALLET = Web3.to_checksum_address(os.getenv("WALLET_ADDRESS"))
w3 = Web3(Web3.HTTPProvider(RPC_URL))
CHAIN_ID = 4386  # Provided chainId

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

VERSION = "Version 1.0"
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

def show_swap_menu():
    terminal_width = shutil.get_terminal_size().columns
    print(f"\n{Fore.WHITE + Style.BRIGHT + 'UOMI DEX Swap Terminal'.center(terminal_width)}")
    print(f"{Fore.CYAN + f'Wallet: {WALLET[:6]}...{WALLET[-4:]} | Time: {datetime.now().strftime("%H:%M:%S %d-%m-%Y")}'.center(terminal_width)}")
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

def do_swap(token_name, token_addr, is_token_to_uomi=False):
    terminal_width = shutil.get_terminal_size().columns
    # Random amount between 0.001 and 0.004 for UOMI_TO_WUOMI, 0.01 for others
    amount = w3.to_wei(random.uniform(0.001, 0.004), "ether") if token_name == "UOMI_TO_WUOMI" else w3.to_wei(0.01, "ether")
    
    if token_name == "UOMI_TO_WUOMI":
        amount_display = w3.from_wei(amount, "ether")
        print(f"\n{Fore.WHITE + Style.BRIGHT + f'Initiating Swap: {amount_display:.6f} UOMI → WUOMI'.center(terminal_width)}")
        loading_animation("Preparing Transaction")
        try:
            base_fee = w3.eth.get_block("latest").get("baseFeePerGas", w3.to_wei(1, "gwei"))
            gas_price = int(w3.to_wei(0.000000533, "gwei") * 1.5)  # 1.5x provided gasPrice
            tx = {
                "chainId": CHAIN_ID,
                "from": WALLET,
                "to": token_addr,
                "value": amount,
                "data": "0xd0e30db0",  # Deposit function selector
                "nonce": w3.eth.get_transaction_count(WALLET),
                "gas": 42242,  # Provided gas limit
                "maxFeePerGas": base_fee + w3.to_wei(2, "gwei"),
                "maxPriorityFeePerGas": w3.to_wei(2, "gwei")
            }
            signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
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
        print(f"\n{Fore.WHITE + Style.BRIGHT + f'Initiating Swap: 0.01 {token_symbol} → UOMI'.center(terminal_width)}")
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
                "from": WALLET,
                "nonce": w3.eth.get_transaction_count(WALLET),
                "gas": 100000,
                "maxFeePerGas": w3.eth.get_block("latest").get("baseFeePerGas", w3.to_wei(1, "gwei")) + w3.to_wei(2, "gwei"),
                "maxPriorityFeePerGas": w3.to_wei(2, "gwei")
            })
            signed_approve = w3.eth.account.sign_transaction(approve_tx, PRIVATE_KEY)
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
                    [token_addr, output_token, 3000, WALLET, amount, 0, 0])
            ))
        ]
        value = 0
    else:
        print(f"\n{Fore.WHITE + Style.BRIGHT + f'Initiating Swap: 0.01 UOMI → {token_name}'.center(terminal_width)}")
        commands = SWAP_EXACT_INPUT
        inputs = [
            Web3.to_bytes(hexstr=Web3.to_hex(
                Web3.solidity_keccak(['address', 'address', 'uint24', 'address', 'uint256', 'uint256', 'uint160'],
                    [TOKENS["SYN"], token_addr, 3000, WALLET, amount, 0, 0])
            ))
        ]
        value = amount

    loading_animation("Executing Swap")
    try:
        base_fee = w3.eth.get_block("latest").get("baseFeePerGas", w3.to_wei(1, "gwei"))
        tx = router.functions.execute(commands, inputs).build_transaction({
            "chainId": CHAIN_ID,
            "from": WALLET,
            "value": value,
            "nonce": w3.eth.get_transaction_count(WALLET),
            "gas": 300000,
            "maxFeePerGas": base_fee + w3.to_wei(2, "gwei"),
            "maxPriorityFeePerGas": w3.to_wei(2, "gwei")
        })
        signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        txh = w3.eth.send_raw_transaction(signed.raw_transaction)
        print(f"{Fore.GREEN + f'TX SENT: https://explorer.uomi.ai/tx/{w3.to_hex(txh)}'.center(terminal_width)}")
        w3.eth.wait_for_transaction_receipt(txh)
        print(f"{Fore.GREEN + Style.BRIGHT + 'SWAP EXECUTED'.center(terminal_width)}")
    except Exception as e:
        print(f"{Fore.RED + Style.BRIGHT + f'SWAP ERROR: {str(e)[:50]}...'.center(terminal_width)}")

def main():
    terminal_width = shutil.get_terminal_size().columns
    print(f"\n{Fore.MAGENTA + Style.BRIGHT + center_text(BANNER)}")
    print(Fore.MAGENTA + Style.BRIGHT + VERSION.center(terminal_width))
    print(Fore.YELLOW + Style.BRIGHT + CREDIT.center(terminal_width))
    print(f"{Fore.CYAN + f'Last Run: {get_last_run()}'.center(terminal_width)}")
    loading_animation("Initializing UOMI DEX Swap Terminal")
    save_last_run()

    while True:
        show_swap_menu()
        try:
            prompt = ">> Select Option: "
            choice_input = input(f"{Fore.CYAN + Style.BRIGHT + prompt.center(terminal_width)}")
            token_choice = int(choice_input)
        except ValueError:
            print(f"{Fore.RED + Style.BRIGHT + 'ERROR: Enter a valid number'.center(terminal_width)}")
            time.sleep(1.5)
            continue

        token_list = list(TOKENS.items())
        auto_all_option = len(TOKENS) + 1

        if token_choice == auto_all_option:
            try:
                prompt = ">> Number of Cycles: "
                num_cycles = int(input(f"{Fore.CYAN + Style.BRIGHT + prompt.center(terminal_width)}"))
                if num_cycles <= 0:
                    raise ValueError
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT + 'ERROR: Enter a positive number'.center(terminal_width)}")
                time.sleep(1.5)
                continue
            for cycle in range(num_cycles):
                print(f"\n{Fore.WHITE + Style.BRIGHT + f'Cycle {cycle + 1}/{num_cycles}'.center(terminal_width)}")
                for i, (token_name, token_addr) in enumerate(token_list):
                    is_token_to_uomi = token_name.endswith("_TO_UOMI")
                    pct = random.uniform(10, 15) / 100
                    print(f"{Fore.CYAN + f'[{i + 1}] {token_name}: {pct*100:.2f}%'.center(terminal_width)}")
                    do_swap(token_name, token_addr, is_token_to_uomi)
                    time.sleep(1.5)
                loading_animation("Cycle Completed")
            print(f"{Fore.GREEN + Style.BRIGHT + 'AUTO SWAP COMPLETED'.center(terminal_width)}")
        elif 1 <= token_choice <= len(token_list):
            token_name, token_addr = token_list[token_choice - 1]
            is_token_to_uomi = token_name.endswith("_TO_UOMI")
            try:
                prompt = ">> Number of Swaps: "
                num_swaps = int(input(f"{Fore.CYAN + Style.BRIGHT + prompt.center(terminal_width)}"))
                if num_swaps <= 0:
                    raise ValueError
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT + 'ERROR: Enter a positive number'.center(terminal_width)}")
                time.sleep(1.5)
                continue
            for i in range(num_swaps):
                pct = random.uniform(10, 15) / 100
                print(f"{Fore.CYAN + f'[{i + 1}/{num_swaps}] {token_name}: {pct*100:.2f}%'.center(terminal_width)}")
                do_swap(token_name, token_addr, is_token_to_uomi)
                time.sleep(1.5)
            print(f"{Fore.GREEN + Style.BRIGHT + 'SWAPS COMPLETED'.center(terminal_width)}")
        else:
            print(f"{Fore.RED + Style.BRIGHT + 'INVALID OPTION. EXITING.'.center(terminal_width)}")
            break
        print(f"{Fore.CYAN + 'Returning to Terminal'.center(terminal_width)}")
        loading_animation("Loading Terminal")

if __name__ == "__main__":
    main()
