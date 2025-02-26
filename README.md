Here's a polished and well-structured README for your GitHub repository based on the information you provided, written in Markdown format:
markdown
# Multi Currency Rich Address Finder v2.0
Developed by Mustafa AKBAL 
                                             ██████╗██╗  ██╗ █████╗ ██╗    ██╗██████╗ ███████╗███████╗██╗  ██╗
                                            ██╔════╝██║  ██║██╔══██╗██║    ██║██╔══██╗██╔════╝██╔════╝██║  ██║
                                            ██║     ███████║███████║██║ █╗ ██║██████╔╝█████╗  ███████╗███████║
                                            ██║     ██╔══██║██╔══██║██║███╗██║██╔══██╗██╔══╝  ╚════██║██╔══██║
                                            ╚██████╗██║  ██║██║  ██║╚███╔███╔╝██║  ██║███████╗███████║██║  ██║
                                             ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚══╝╚══╝ ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝
                                            AUTHOR : Mustafa AKBAL e-mail: mstf.akbal@gmail.com 
                                            Telegram: @chawresho   Instagram: mstf.akbal
---

## Overview

Multi Currency Rich Address Finder v2.0 is a powerful and user-friendly tool designed to generate and check cryptocurrency addresses across multiple blockchains, including BTC, ETH, TRX, DOGE, BCH, DASH, ZEC, and LTC. Built with efficiency and flexibility in mind, it supports various address types and offers a multi-threaded checking system with an intuitive GUI powered by PyQt5.

This tool is ideal for blockchain enthusiasts, researchers, and developers looking to explore or test cryptocurrency address generation and matching against a database.

---

## Features

- **Multi-Coin Support:** Generate addresses for BTC (P2PKH, P2WPKH, P2SH, etc.), ETH, TRX, DOGE, BCH, DASH, ZEC, and LTC.
- **Fast & Multithreaded:** Leverage multiple workers for high-speed address checking with dynamic batch sizing.
- **Database Management:** Easily create, optimize, backup, and restore SQLite databases of public keys.
- **Customizable Settings:** Adjust batch size, worker count, and cryptocurrency selection.
- **File Import:** Add addresses from text/CSV files with configurable delimiters and columns.
- **Multilingual GUI:** Supports Turkish and English interfaces.
- **Logging & Export:** Real-time logs and exportable results of found addresses.

Launch the GUI:
Start the program with the command above. The interface includes five tabs: Control, Logs, Found Addresses, Settings, and About.
Configure Settings:
Select cryptocurrencies to check in the "Control" tab.
Specify database and output file paths in the "Settings" tab.
Adjust performance settings (batch size, worker count).
Start Checking:
Click "Start" in the "Control" tab to begin generating and checking addresses.
Monitor progress in real-time via the stats display and logs.
Manage Results:
View matched addresses in the "Found Addresses" tab.
Export findings to a text file.
Database Management:
Create a new database or import addresses from a file in the "Settings" tab.
Optimize, backup, or restore your database as needed.
Supported Cryptocurrencies & Address Types
Coin
Symbol
Address Types Supported
Bitcoin
BTC
P2PKH, P2WPKH, P2WPKH-in-P2SH, P2WSH-in-P2SH, P2SH, P2WSH
Ethereum
ETH
P2PKH (EVM-compatible)
Tron
TRX
P2PKH
Dogecoin
DOGE
P2PKH
Bitcoin Cash
BCH
P2PKH, P2SH
Dash
DASH
P2PKH, P2SH
Zcash
ZEC
P2PKH, P2SH
Litecoin
LTC
P2PKH, P2SH, P2WSH, P2WPKH
Donate
Support the development of this tool with a donation! Your contributions help fuel updates and improvements.
Coin
Address
BTC (P2PKH)
191QB72rS77vP8NC1EC11wWqKtkfbm5SM8
BTC (P2WPKH)
bc1q2l29nc6puvuk0rn449wf6l8rm62wuxst7uvjeu
BTC (P2WPKH-in-P2SH)
3AkjfoQn494K5FBdqMrnQRr4UsWji7Az62
BTC (P2WSH-in-P2SH)
3Cf3J2jw4xx8DVuwHDiQuVrsRoroUgzd7M
BTC (P2SH)
3LPo8JHFdXZxvyZDQiWxiWCvPYU4oUhyHz
BTC (P2WSH)
bc1q47rduwq76v4fteqvxm8p9axq39nq25kurgwlyaefmyqz3nhyc8rscuhwwq
ETH/BSC/AVAX/Polygon
0x279f020A74BfE5Ba6a539B0f523D491A4122d18D
TRX
TDahqcDTkM2qnfoCPfed1YhcB5Eocc2Cwe
DOGE
DD9ViMyVjX2Cv8YnjpBZZhgSD2Uy1NQVbk
DASH
XihF1MgkPpLWY4xms7WDsUCdAELMiBXCFZ
ZEC
t1Rt1BSSzQRuWymR5wf189kckaYwkSSQAb1
LTC (P2PKH)
LTEMSKLgWmMydw4MBNBJHxabY77wp1zyZ6
LTC (P2SH)
MSbwSBhDaeRPjUq7WbWJY9TKiF4WpZbBd8
LTC (P2WSH)
ltc1q47rduwq76v4fteqvxm8p9axq39nq25kurgwlyaefmyqz3nhyc8rsmce759
LTC (P2WPKH)
ltc1q2l29nc6puvuk0rn449wf6l8rm62wuxst6qkkpv
For additional donation addresses, feel free to contact me via email. Thank you for your support!
License
This project is licensed under the MIT License. You are free to use, modify, and distribute it, provided you retain the copyright notice and do not share it without permission. See the LICENSE file for details.
Legal Disclaimer
Unlawful use of this software is strictly prohibited. The author and copyright holders are not responsible for any illegal activities conducted using this tool. Users must ensure compliance with all applicable local, national, and international laws. This software is intended for ethical and legal purposes only, such as research and testing. Any misuse is at the user's own risk and may result in legal consequences.
Disclaimer of Liability
This software is provided "AS IS" without any warranties, express or implied. The author and copyright holders are not liable for any damages, losses, or responsibilities arising from its use. Users assume all risks, including potential damage to systems or data. Ensure you take appropriate precautions, such as backing up data, before use.
Contributing
Ideas, bug reports, or contributions are welcome! Feel free to:
Open an issue for suggestions or problems.
Submit a pull request with improvements.
Contact me directly via email or Telegram.
Acknowledgments
Built with passion for the blockchain community. Special thanks to all supporters and users who help make this project better!
Happy address hunting!


This README should effectively showcase your project on GitHub while providing all necessary information for users and contributors. Let me know if you'd like any adjustments!
