# 🔐 PassKey - Advanced Password Profiler

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-GPL--3.0-green.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/JassHacz/PassKey.svg)](https://github.com/JassHacz/PassKey/stargazers)

Advanced password wordlist generator for **authorized penetration testing**. Creates targeted wordlists based on personal information with modern 2025 patterns.

## ⚠️ Disclaimer

**THIS TOOL IS FOR AUTHORIZED PENETRATION TESTING AND EDUCATIONAL PURPOSES ONLY.**

Unauthorized access to computer systems is **illegal**. The developers assume no liability and are not responsible for any misuse or damage caused by this tool. Use responsibly and only with proper authorization.

---

## ✨ Features

### 🎯 Core Capabilities
- **Profile-Based Generation** - Create wordlists from personal information
- **Modern 2025 Patterns** - AI, crypto, blockchain, COVID-19, Web3 terms
- **Smart Combinations** - Names + dates, years, special characters
- **Leet Speak** - Automatic 1337 sp34k transformations
- **Multiple Separators** - Underscore, hyphen, dot, @ symbol

### 📊 Advanced Analysis
- **Password Strength Calculator** - Weak/Medium/Strong classification
- **Statistical Reports** - Length distribution, character analysis
- **Comprehensive Metrics** - Total generated, averages, percentages

### 📁 Export Formats
- **TXT** - Standard wordlist format
- **JSON** - With metadata and full statistics
- **CSV** - With strength analysis per password

### 🔧 Additional Tools
- **Wordlist Improvement** - Enhance existing wordlists
- **Merge Wordlists** - Combine multiple lists
- **Download Common Passwords** - From SecLists repository
- **Configuration File** - Customize generation parameters

---

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Quick Setup
```bash
# Clone the repository
git clone https://github.com/JassHacz/PassKey.git
cd PassKey

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies (if any)
pip install -r requirements.txt
```

---

## 💻 Usage

### Interactive Mode (Recommended)
```bash
python passkey.py -i
```

You'll be prompted for:
- Target's personal information (name, birthdate, etc.)
- Partner & family details
- Pets, company, keywords
- Email and phone patterns

### Command-Line Options
```bash
# Basic interactive mode
python passkey.py -i

# Custom password length
python passkey.py -i --min-len 8 --max-len 16

# Disable leet speak
python passkey.py -i --no-leet

# Disable special characters
python passkey.py -i --no-special

# Disable modern terms
python passkey.py -i --no-modern

# Improve existing wordlist
python passkey.py -w existing_list.txt -o improved.txt

# Merge multiple wordlists
python passkey.py -m list1.txt list2.txt list3.txt -o merged.txt

# Download common passwords
python passkey.py -d

# Quiet mode (no banner)
python passkey.py -i --quiet

# Show version
python passkey.py --version

# Show help
python passkey.py --help
```

---

## 📖 Usage Examples

### Example 1: Basic Profile
```bash
$ python passkey.py -i

→ First Name: john
→ Surname: smith
→ Birthdate (DDMMYYYY): 15031990
→ Email: john.smith@gmail.com

[✓] Generated 8,543 unique passwords
```

**Sample Output:**
```
john1990
smith1990
johnsmith
John@1990
j0hn1990
smith_15031990
johnsmith@gmail.com
j0hnsm1th
```

### Example 2: Enhanced Generation
```bash
$ python passkey.py -i --min-len 10 --max-len 15

# Generates only 10-15 character passwords
# More secure for modern systems
```

### Example 3: Wordlist Improvement
```bash
$ python passkey.py -w old_wordlist.txt -o enhanced.txt

[*] Loading wordlist...
[✓] Loaded 1,000 words
[*] Enhancing wordlist...
[✓] Enhanced: 1,000 → 12,547 passwords
[✓] Saved to enhanced.txt
```

---

## ⚙️ Configuration

Edit `passkey.cfg` to customize:
```ini
[years]
years = 2020,2021,2022,2023,2024,2025

[specialchars]
chars = !,@,#,$,%,&,*,_,-,+,=

[nums]
from = 0
to = 99
wcfrom = 6    # Minimum length
wcto = 20     # Maximum length
threshold = 1000

[leet]
a = 4
i = 1
e = 3
o = 0
s = 5
```

---

## 📊 Output Statistics

PassKey provides detailed statistics:
```
═══ Generation Statistics ═══

📊 Total Passwords: 16,356
📏 Average Length: 13.46
📐 Length Range: 6 - 20

🔒 Strength Distribution:
  ● Weak:   1.88% (307 passwords)
  ● Medium: 36.71% (6,003 passwords)
  ● Strong: 61.41% (10,046 passwords)

📝 Character Type Distribution:
  • Uppercase: 8,234
  • Lowercase: 16,356
  • Digits: 14,892
  • Special: 5,432
```

---

## 🎯 Use Cases

### Authorized Penetration Testing
- Password auditing for clients
- Security assessments
- Compliance testing

### Security Research
- Password pattern analysis
- Human behavior studies
- Dictionary attack research

### Education
- Cybersecurity courses
- Security awareness training
- Demonstration purposes

---

## 🔒 Best Practices

1. **Always Get Authorization** - Written permission before testing
2. **Document Everything** - Keep logs of your testing
3. **Use Responsibly** - Follow ethical hacking guidelines
4. **Secure Your Wordlists** - Encrypt sensitive generated lists
5. **Report Findings** - Properly disclose vulnerabilities

---

## 🛠️ Advanced Features

### Password Strength Analysis

PassKey analyzes each password:
- Length scoring
- Character variety (upper, lower, digit, special)
- Complexity calculation
- Uniqueness ratio

### Modern 2025 Patterns

Includes trending terms:
- `ai`, `crypto`, `bitcoin`, `nft`
- `chatgpt`, `web3`, `defi`, `blockchain`
- `covid`, `vaccine`, `zoom`
- `tiktok`, `gaming`, `streaming`, `cloud`

### Email Pattern Generation

Automatically creates variations:
```
john.smith@gmail.com
johnsmith@yahoo.com
jsmith@hotmail.com
john_smith@outlook.com
```

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📜 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Inspired by [CUPP](https://github.com/Mebus/cupp) by Mebus
- Built for the security community
- Thanks to all contributors

---

## 📞 Contact

**Author:** JassHacz  
**GitHub:** [@JassHacz](https://github.com/JassHacz)  
**Repository:** [PassKey](https://github.com/JassHacz/PassKey)

---

## ⭐ Star History

If you find this tool useful, please consider giving it a star! ⭐

---

## 📸 Screenshots

### Interactive Mode
```
    ██████╗  ██████╗ ███████╗███████╗██╗  ██╗███████╗██╗   ██╗
    ██╔══██╗██╔═══██╗██╔════╝██╔════╝██║ ██╔╝██╔════╝╚██╗ ██╔╝
    ██████╔╝███████║███████╗███████╗█████╔╝ █████╗   ╚████╔╝ 
    ██╔═══╝ ██╔══██║╚════██║╚════██║██╔═██╗ ██╔══╝    ╚██╔╝  
    ██║     ██║  ██║███████║███████║██║  ██╗███████╗   ██║   
```

---

**⚠️ Remember: With great power comes great responsibility. Use ethically!**
