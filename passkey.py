#!/usr/bin/env python3
"""
PassKey - Advanced Password Profiler
A modern password wordlist generator for penetration testing
Version: 2.0.0

DISCLAIMER: This tool is for authorized penetration testing only.
Unauthorized access to computer systems is illegal.

Author: Security Research Team
License: GPL-3.0
"""

import argparse
import configparser
import json
import csv
import hashlib
import os
import sys
import re
import gzip
import urllib.request
import urllib.error
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass, asdict, field
from datetime import datetime
import itertools
from collections import Counter
import time

__version__ = "2.0.0"
__author__ = "PassKey Security Team"
__license__ = "GPL-3.0"

# Global configuration
CONFIG = {}

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def read_config(filename: str = "passkey.cfg") -> bool:
    """Read configuration file and update global CONFIG"""
    
    # Default configuration
    default_config = {
        "global": {
            "years": list(range(1950, 2026)),
            "chars": ['!', '@', '#', '$', '%', '&', '*', '_', '-', '+', '='],
            "numfrom": 0,
            "numto": 99,
            "wcfrom": 6,
            "wcto": 20,
            "threshold": 1000,
            "modern_terms": [
                "ai", "crypto", "bitcoin", "nft", "meta", "chatgpt", "web3",
                "defi", "blockchain", "covid", "vaccine", "zoom", "tiktok",
                "2025", "2024", "2023", "gaming", "streaming", "cloud"
            ]
        },
        "LEET": {
            'a': '4', 'e': '3', 'i': '1', 'o': '0', 
            's': '5', 't': '7', 'g': '9', 'b': '8'
        }
    }
    
    if os.path.isfile(filename):
        try:
            config = configparser.ConfigParser()
            config.read(filename)
            
            CONFIG["global"] = {
                "years": [str(y) for y in range(1950, 2026)],
                "chars": config.get("specialchars", "chars", fallback="!@#$%&*_-+=").split(","),
                "numfrom": config.getint("nums", "from", fallback=0),
                "numto": config.getint("nums", "to", fallback=99),
                "wcfrom": config.getint("nums", "wcfrom", fallback=6),
                "wcto": config.getint("nums", "wcto", fallback=20),
                "threshold": config.getint("nums", "threshold", fallback=1000),
                "modern_terms": default_config["global"]["modern_terms"]
            }
            
            # Leet speak configs
            leet = {}
            for letter in ['a', 'i', 'e', 't', 'o', 's', 'g', 'b']:
                leet[letter] = config.get("leet", letter, fallback=default_config["LEET"].get(letter, letter))
            
            CONFIG["LEET"] = leet
            
            print(f"{Colors.GREEN}[✓] Configuration loaded from {filename}{Colors.ENDC}")
            return True
            
        except Exception as e:
            print(f"{Colors.YELLOW}[!] Error reading config: {e}{Colors.ENDC}")
            print(f"{Colors.YELLOW}[!] Using default configuration{Colors.ENDC}")
            CONFIG.update(default_config)
            return False
    else:
        # Use default config
        CONFIG.update(default_config)
        # Create default config file
        create_default_config(filename)
        return True

def create_default_config(filename: str = "passkey.cfg"):
    """Create default configuration file"""
    config_content = """[years]
years = 2020,2021,2022,2023,2024,2025

[specialchars]
chars = !,@,#,$,%,&,*,_,-,+,=

[nums]
from = 0
to = 99
wcfrom = 6
wcto = 20
threshold = 1000

[leet]
a = 4
i = 1
e = 3
t = 7
o = 0
s = 5
g = 9
b = 8
"""
    try:
        with open(filename, 'w') as f:
            f.write(config_content)
        print(f"{Colors.GREEN}[✓] Default config created: {filename}{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.YELLOW}[!] Could not create config file: {e}{Colors.ENDC}")

@dataclass
class Profile:
    """User profile data structure with validation"""
    name: str = ""
    surname: str = ""
    nickname: str = ""
    birthdate: str = ""
    partner_name: str = ""
    partner_nickname: str = ""
    partner_birthdate: str = ""
    child_name: str = ""
    child_nickname: str = ""
    child_birthdate: str = ""
    pet_name: str = ""
    company: str = ""
    keywords: List[str] = field(default_factory=list)
    email: str = ""
    phone: str = ""
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Validate profile data"""
        errors = []
        
        if not self.name:
            errors.append("Name is required")
        
        # Validate dates
        for date_field, field_name in [
            (self.birthdate, "Birthdate"),
            (self.partner_birthdate, "Partner's birthdate"),
            (self.child_birthdate, "Child's birthdate")
        ]:
            if date_field and (len(date_field) != 8 or not date_field.isdigit()):
                errors.append(f"{field_name} must be in DDMMYYYY format")
        
        # Validate email
        if self.email and '@' not in self.email:
            errors.append("Invalid email format")
        
        return len(errors) == 0, errors
    
    def to_dict(self) -> Dict:
        """Convert profile to dictionary"""
        return asdict(self)

class PasswordConfig:
    """Configuration for password generation"""
    
    def __init__(self):
        self.min_length = CONFIG["global"]["wcfrom"]
        self.max_length = CONFIG["global"]["wcto"]
        self.use_leet = True
        self.use_special_chars = True
        self.use_numbers = True
        self.use_modern_terms = True
        self.year_range = [str(y) for y in range(1950, 2026)]
        self.special_chars = CONFIG["global"]["chars"]
        self.modern_terms = CONFIG["global"]["modern_terms"]
        self.num_from = CONFIG["global"]["numfrom"]
        self.num_to = CONFIG["global"]["numto"]

class ProgressBar:
    """Simple progress bar for terminal"""
    
    def __init__(self, total: int, description: str = "Processing"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = time.time()
    
    def update(self, amount: int = 1):
        """Update progress bar"""
        self.current += amount
        self.display()
    
    def display(self):
        """Display progress bar"""
        if self.total == 0:
            return
        
        percent = (self.current / self.total) * 100
        filled = int(50 * self.current / self.total)
        bar = '█' * filled + '-' * (50 - filled)
        
        elapsed = time.time() - self.start_time
        
        sys.stdout.write(f'\r{Colors.CYAN}[{bar}] {percent:.1f}% {Colors.ENDC}{self.description} ({self.current}/{self.total})')
        sys.stdout.flush()
        
        if self.current >= self.total:
            print()

class PassKey:
    """Main PassKey password generator class"""
    
    def __init__(self, config: PasswordConfig = None):
        self.config = config or PasswordConfig()
        self.wordlist: Set[str] = set()
        self.stats = {
            'total_generated': 0,
            'unique_passwords': 0,
            'avg_length': 0,
            'strength_distribution': Counter()
        }
    
    def print_banner(self):
        """Display tool banner"""
        banner = f"""
{Colors.CYAN}
    ██████╗  ██████╗ ███████╗███████╗██╗  ██╗███████╗██╗   ██╗
    ██╔══██╗██╔═══██╗██╔════╝██╔════╝██║ ██╔╝██╔════╝╚██╗ ██╔╝
    ██████╔╝███████║███████╗███████╗█████╔╝ █████╗   ╚████╔╝ 
    ██╔═══╝ ██╔══██║╚════██║╚════██║██╔═██╗ ██╔══╝    ╚██╔╝  
    ██║     ██║  ██║███████║███████║██║  ██╗███████╗   ██║   
    ╚═╝     ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝╚══════╝   ╚═╝   
{Colors.ENDC}
{Colors.GREEN}╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║          {Colors.BOLD}{Colors.YELLOW}Advanced Password Profiler & Wordlist Generator{Colors.ENDC}{Colors.GREEN}         ║
║                          {Colors.CYAN}Version 2.0.0{Colors.GREEN}                             ║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  {Colors.YELLOW}Features:{Colors.GREEN}                                                        ║
║    {Colors.CYAN}→{Colors.GREEN} Modern 2025 Password Patterns (AI, Crypto, Web3)         ║
║    {Colors.CYAN}→{Colors.GREEN} Smart Combinations & Leet Speak                          ║
║    {Colors.CYAN}→{Colors.GREEN} Password Strength Analysis                               ║
║    {Colors.CYAN}→{Colors.GREEN} Multiple Export Formats (TXT, JSON, CSV)                 ║
║    {Colors.CYAN}→{Colors.GREEN} Email & Phone Pattern Generation                         ║
║    {Colors.CYAN}→{Colors.GREEN} Wordlist Improvement & Merging                           ║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  {Colors.RED}{Colors.BOLD}⚠  WARNING: For Authorized Penetration Testing ONLY!  ⚠{Colors.ENDC}{Colors.GREEN}      ║
║     {Colors.YELLOW}Unauthorized access to computer systems is illegal.{Colors.GREEN}          ║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  {Colors.CYAN}Author:{Colors.GREEN} Security Research Team                                  ║
║  {Colors.CYAN}GitHub:{Colors.GREEN} github.com/yourusername/passkey                       ║
║  {Colors.CYAN}License:{Colors.GREEN} GPL-3.0                                              ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝{Colors.ENDC}
"""
        print(banner)
    
    def interactive_profile(self) -> Profile:
        """Collect user information interactively with validation"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}═══ Profile Information ═══{Colors.ENDC}\n")
        print(f"{Colors.YELLOW}Tip: Press Enter to skip any field{Colors.ENDC}\n")
        
        profile = Profile()
        
        # Personal info with validation
        while True:
            profile.name = input(f"{Colors.GREEN}→{Colors.ENDC} First Name: ").strip().lower()
            if profile.name:
                break
            print(f"{Colors.RED}✗ Name is required!{Colors.ENDC}")
        
        profile.surname = input(f"{Colors.GREEN}→{Colors.ENDC} Surname: ").strip().lower()
        profile.nickname = input(f"{Colors.GREEN}→{Colors.ENDC} Nickname: ").strip().lower()
        profile.birthdate = self._get_date_input("Birthdate")
        
        # Contact info
        profile.email = self._get_email_input()
        profile.phone = input(f"{Colors.GREEN}→{Colors.ENDC} Phone Number: ").strip()
        
        # Partner info
        print(f"\n{Colors.CYAN}Partner Information:{Colors.ENDC}")
        profile.partner_name = input(f"{Colors.GREEN}→{Colors.ENDC} Partner's Name: ").strip().lower()
        profile.partner_nickname = input(f"{Colors.GREEN}→{Colors.ENDC} Partner's Nickname: ").strip().lower()
        profile.partner_birthdate = self._get_date_input("Partner's Birthdate")
        
        # Child info
        print(f"\n{Colors.CYAN}Child Information:{Colors.ENDC}")
        profile.child_name = input(f"{Colors.GREEN}→{Colors.ENDC} Child's Name: ").strip().lower()
        profile.child_nickname = input(f"{Colors.GREEN}→{Colors.ENDC} Child's Nickname: ").strip().lower()
        profile.child_birthdate = self._get_date_input("Child's Birthdate")
        
        # Other info
        print(f"\n{Colors.CYAN}Other Information:{Colors.ENDC}")
        profile.pet_name = input(f"{Colors.GREEN}→{Colors.ENDC} Pet's Name: ").strip().lower()
        profile.company = input(f"{Colors.GREEN}→{Colors.ENDC} Company Name: ").strip().lower()
        
        keywords_input = input(f"{Colors.GREEN}→{Colors.ENDC} Keywords (comma-separated): ").strip()
        if keywords_input:
            profile.keywords = [k.strip().lower() for k in keywords_input.split(',')]
        
        # Validate profile
        is_valid, errors = profile.validate()
        if not is_valid:
            print(f"\n{Colors.YELLOW}[!] Validation warnings:{Colors.ENDC}")
            for error in errors:
                print(f"  {Colors.YELLOW}• {error}{Colors.ENDC}")
            confirm = input(f"\n{Colors.YELLOW}Continue anyway? (Y/n): {Colors.ENDC}").lower()
            if confirm == 'n':
                return self.interactive_profile()
        
        return profile
    
    def _get_date_input(self, prompt: str) -> str:
        """Get and validate date input"""
        while True:
            date = input(f"{Colors.GREEN}→{Colors.ENDC} {prompt} (DDMMYYYY): ").strip()
            if not date:
                return ""
            if len(date) == 8 and date.isdigit():
                return date
            print(f"{Colors.RED}✗ Invalid format! Use DDMMYYYY (e.g., 15031990){Colors.ENDC}")
    
    def _get_email_input(self) -> str:
        """Get and validate email input"""
        while True:
            email = input(f"{Colors.GREEN}→{Colors.ENDC} Email: ").strip().lower()
            if not email:
                return ""
            if '@' in email and '.' in email.split('@')[1]:
                return email
            print(f"{Colors.RED}✗ Invalid email format! Use format: user@example.com{Colors.ENDC}")
    
    def make_leet(self, word: str) -> str:
        """Convert string to leet speak"""
        leet_word = word.lower()
        for letter, leet_char in CONFIG["LEET"].items():
            leet_word = leet_word.replace(letter, leet_char)
        return leet_word
    
    def generate_base_words(self, profile: Profile) -> List[str]:
        """Generate base words from profile"""
        words = []
        
        # Names and variations
        if profile.name:
            words.extend([profile.name, profile.name.capitalize(), profile.name.upper()])
        if profile.surname:
            words.extend([profile.surname, profile.surname.capitalize(), profile.surname.upper()])
        if profile.nickname:
            words.extend([profile.nickname, profile.nickname.capitalize()])
        
        # Combinations
        if profile.name and profile.surname:
            words.extend([
                profile.name + profile.surname,
                profile.surname + profile.name,
                profile.name.capitalize() + profile.surname.capitalize(),
                profile.name[0] + profile.surname
            ])
        
        # Partner
        if profile.partner_name:
            words.extend([profile.partner_name, profile.partner_name.capitalize()])
            if profile.partner_nickname:
                words.extend([profile.partner_nickname, profile.partner_nickname.capitalize()])
        
        # Child
        if profile.child_name:
            words.extend([profile.child_name, profile.child_name.capitalize()])
            if profile.child_nickname:
                words.extend([profile.child_nickname, profile.child_nickname.capitalize()])
        
        # Pet and company
        if profile.pet_name:
            words.extend([profile.pet_name, profile.pet_name.capitalize()])
        if profile.company:
            words.extend([profile.company, profile.company.capitalize(), profile.company.replace(' ', '')])
        
        # Keywords
        if profile.keywords:
            for kw in profile.keywords:
                words.extend([kw, kw.capitalize(), kw.upper()])
        
        # Email username
        if profile.email and '@' in profile.email:
            username = profile.email.split('@')[0]
            words.extend([username, username.capitalize()])
            # Email variations
            words.extend([username.replace('.', ''), username.replace('_', '')])
        
        # Reverse words
        for word in words[:]:
            if len(word) > 3:
                words.append(word[::-1])
        
        return list(set(words))
    
    def generate_date_variations(self, date: str) -> List[str]:
        """Generate date variations from DDMMYYYY format"""
        if not date or len(date) != 8:
            return []
        
        variations = []
        dd, mm, yyyy = date[:2], date[2:4], date[4:]
        yy = yyyy[2:]
        yyy = yyyy[1:]
        
        variations.extend([
            dd, mm, yyyy, yy, yyy,
            dd + mm, mm + dd,
            dd + mm + yyyy, mm + dd + yyyy,
            dd + mm + yy, mm + dd + yy,
            yyyy + mm + dd, yyyy + dd + mm,
            yy + mm + dd, yy + dd + mm,
            dd[1], mm[1]  # Single digit
        ])
        
        return list(set(variations))
    
    def generate_combinations(self, profile: Profile) -> Set[str]:
        """Generate all password combinations with progress tracking"""
        passwords = set()
        
        print(f"\n{Colors.CYAN}[*] Generating base words...{Colors.ENDC}")
        base_words = self.generate_base_words(profile)
        print(f"{Colors.GREEN}[✓] Generated {len(base_words)} base words{Colors.ENDC}")
        
        print(f"{Colors.CYAN}[*] Generating date variations...{Colors.ENDC}")
        dates = []
        for date_field in [profile.birthdate, profile.partner_birthdate, profile.child_birthdate]:
            dates.extend(self.generate_date_variations(date_field))
        dates = list(set(dates))
        print(f"{Colors.GREEN}[✓] Generated {len(dates)} date variations{Colors.ENDC}")
        
        # Years
        current_year = datetime.now().year
        years = self.config.year_range[-10:]  # Last 10 years
        
        print(f"\n{Colors.CYAN}[*] Creating combinations...{Colors.ENDC}")
        
        # Calculate total operations for progress
        total_ops = len(base_words) + len(base_words) * len(dates) + len(base_words) * len(years)
        progress = ProgressBar(total_ops, "Generating passwords")
        
        # Base words alone
        passwords.update(base_words)
        progress.update(len(base_words))
        
        # Words + dates with separators
        separators = ['', '_', '-', '.', '@', '!']
        for word in base_words:
            for date in dates:
                for sep in separators[:3]:  # Limit separators
                    passwords.add(f"{word}{sep}{date}")
                    passwords.add(f"{date}{sep}{word}")
            progress.update(1)
        
        # Words + years
        for word in base_words:
            for year in years:
                for sep in separators[:3]:
                    passwords.add(f"{word}{sep}{year}")
                    passwords.add(f"{year}{sep}{word}")
            progress.update(1)
        
        # Words + numbers
        if self.config.use_numbers:
            print(f"\n{Colors.CYAN}[*] Adding number combinations...{Colors.ENDC}")
            for word in base_words[:50]:  # Limit to prevent explosion
                for num in [str(n) for n in range(self.config.num_from, min(self.config.num_to, 100), 11)]:
                    passwords.add(f"{word}{num}")
                    passwords.add(f"{num}{word}")
        
        # Special characters
        if self.config.use_special_chars:
            print(f"{Colors.CYAN}[*] Adding special characters...{Colors.ENDC}")
            for word in base_words[:50]:
                for char in self.config.special_chars[:5]:
                    passwords.add(f"{word}{char}")
                    passwords.add(f"{char}{word}")
                    for year in years[-3:]:
                        passwords.add(f"{word}{char}{year}")
        
        # Modern terms
        if self.config.use_modern_terms:
            print(f"{Colors.CYAN}[*] Adding modern terms (2025 trends)...{Colors.ENDC}")
            for word in base_words[:20]:
                for term in self.config.modern_terms[:15]:
                    passwords.add(f"{word}{term}")
                    passwords.add(f"{term}{word}")
                    passwords.add(f"{word}{term.capitalize()}")
        
        # Email patterns
        if profile.email and '@' in profile.email:
            username = profile.email.split('@')[0]
            domain = profile.email.split('@')[1]
            providers = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
            for provider in providers:
                passwords.add(f"{username}@{provider}")
        
        # Phone patterns
        if profile.phone:
            clean_phone = re.sub(r'\D', '', profile.phone)
            if len(clean_phone) >= 4:
                passwords.add(clean_phone[-4:])
                passwords.add(clean_phone[-6:])
                passwords.add(clean_phone[-8:])
        
        # Leet speak
        if self.config.use_leet:
            print(f"\n{Colors.CYAN}[*] Applying leet speak transformations...{Colors.ENDC}")
            leet_passwords = set()
            sample_size = min(len(passwords), 5000)
            for pwd in list(passwords)[:sample_size]:
                leet_passwords.add(self.make_leet(pwd))
            passwords.update(leet_passwords)
        
        # Filter by length
        print(f"{Colors.CYAN}[*] Filtering by length ({self.config.min_length}-{self.config.max_length})...{Colors.ENDC}")
        passwords = {p for p in passwords if self.config.min_length <= len(p) <= self.config.max_length}
        
        return passwords
    
    def calculate_password_strength(self, password: str) -> str:
        """Calculate password strength score"""
        score = 0
        
        # Length
        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1
        if len(password) >= 16:
            score += 1
        
        # Character variety
        if any(c.isupper() for c in password):
            score += 1
        if any(c.islower() for c in password):
            score += 1
        if any(c.isdigit() for c in password):
            score += 1
        if any(c in self.config.special_chars for c in password):
            score += 2
        
        # Complexity
        if len(set(password)) > len(password) * 0.7:  # High uniqueness
            score += 1
        
        if score <= 3:
            return "weak"
        elif score <= 6:
            return "medium"
        else:
            return "strong"
    
    def generate_statistics(self, passwords: Set[str]) -> Dict:
        """Generate comprehensive statistics"""
        if not passwords:
            return {}
        
        total = len(passwords)
        lengths = [len(p) for p in passwords]
        avg_length = sum(lengths) / total
        
        strength_dist = Counter()
        for pwd in passwords:
            strength = self.calculate_password_strength(pwd)
            strength_dist[strength] += 1
        
        # Character distribution
        char_types = {'upper': 0, 'lower': 0, 'digit': 0, 'special': 0}
        for pwd in passwords:
            if any(c.isupper() for c in pwd):
                char_types['upper'] += 1
            if any(c.islower() for c in pwd):
                char_types['lower'] += 1
            if any(c.isdigit() for c in pwd):
                char_types['digit'] += 1
            if any(c in self.config.special_chars for c in pwd):
                char_types['special'] += 1
        
        return {
            'total_passwords': total,
            'average_length': round(avg_length, 2),
            'min_length': min(lengths),
            'max_length': max(lengths),
            'strength_distribution': dict(strength_dist),
            'weak_percentage': round(strength_dist.get('weak', 0) / total * 100, 2),
            'medium_percentage': round(strength_dist.get('medium', 0) / total * 100, 2),
            'strong_percentage': round(strength_dist.get('strong', 0) / total * 100, 2),
            'char_type_distribution': char_types,
            'generation_timestamp': datetime.now().isoformat()
        }
    
    def export_txt(self, passwords: Set[str], filename: str):
        """Export passwords to text file"""
        sorted_passwords = sorted(passwords)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sorted_passwords))
        print(f"{Colors.GREEN}[✓] Saved to {filename} ({len(passwords)} passwords){Colors.ENDC}")
    
    def export_json(self, passwords: Set[str], stats: Dict, filename: str, profile: Profile):
        """Export passwords and stats to JSON"""
        data = {
            'metadata': {
                'tool': f'PassKey v{__version__}',
                'generated_at': datetime.now().isoformat(),
                'target_name': profile.name,
                'profile': profile.to_dict()
            },
            'statistics': stats,
            'passwords': sorted(passwords)
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"{Colors.GREEN}[✓] Saved to {filename}{Colors.ENDC}")
    
    def export_csv(self, passwords: Set[str], filename: str):
        """Export passwords to CSV with strength analysis"""
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Password', 'Length', 'Strength', 'Has_Upper', 'Has_Lower', 'Has_Digit', 'Has_Special'])
            
            for pwd in sorted(passwords):
                strength = self.calculate_password_strength(pwd)
                has_upper = any(c.isupper() for c in pwd)
                has_lower = any(c.islower() for c in pwd)
                has_digit = any(c.isdigit() for c in pwd)
                has_special = any(c in self.config.special_chars for c in pwd)
                
                writer.writerow([pwd, len(pwd), strength, has_upper, has_lower, has_digit, has_special])
        
        print(f"{Colors.GREEN}[✓] Saved to {filename}{Colors.ENDC}")
    
    def display_statistics(self, stats: Dict):
        """Display statistics in a formatted table"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}╔══════════════════════════════════════════════════════════╗")
        print(f"║              GENERATION STATISTICS                       ║")
        print(f"╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")
        
        print(f"{Colors.GREEN}📊 Total Passwords:{Colors.ENDC} {Colors.BOLD}{stats['total_passwords']}{Colors.ENDC}")
        print(f"{Colors.GREEN}📏 Average Length:{Colors.ENDC} {stats['average_length']}")
        print(f"{Colors.GREEN}📐 Length Range:{Colors.ENDC} {stats['min_length']} - {stats['max_length']}")
        
        print(f"\n{Colors.BOLD}🔒 Strength Distribution:{Colors.ENDC}")
        print(f"  {Colors.RED}● Weak:{Colors.ENDC}   {stats['weak_percentage']}% ({stats['strength_distribution'].get('weak', 0)} passwords)")
        print(f"  {Colors.YELLOW}● Medium:{Colors.ENDC} {stats['medium_percentage']}% ({stats['strength_distribution'].get('medium', 0)} passwords)")
        print(f"  {Colors.GREEN}● Strong:{Colors.ENDC} {stats['strong_percentage']}% ({stats['strength_distribution'].get('strong', 0)} passwords)")
        
        print(f"\n{Colors.BOLD}📝 Character Type Distribution:{Colors.ENDC}")
        char_dist = stats['char_type_distribution']
        print(f"  {Colors.CYAN}• Uppercase:{Colors.ENDC} {char_dist['upper']}")
        print(f"  {Colors.CYAN}• Lowercase:{Colors.ENDC} {char_dist['lower']}")
        print(f"  {Colors.CYAN}• Digits:{Colors.ENDC} {char_dist['digit']}")
        print(f"  {Colors.CYAN}• Special:{Colors.ENDC} {char_dist['special']}")
    
    def improve_wordlist(self, input_file: str, output_file: str = None) -> Set[str]:
        """Improve existing wordlist with additional combinations"""
        
        if not os.path.isfile(input_file):
            print(f"{Colors.RED}[✗] Error: File {input_file} not found{Colors.ENDC}")
            return set()
        
        print(f"\n{Colors.CYAN}[*] Loading wordlist from {input_file}...{Colors.ENDC}")
        
        try:
            with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
                words = [line.strip() for line in f if line.strip()]
        except Exception as e:
            print(f"{Colors.RED}[✗] Error reading file: {e}{Colors.ENDC}")
            return set()
        
        print(f"{Colors.GREEN}[✓] Loaded {len(words)} words{Colors.ENDC}")
        
        if len(words) > CONFIG["global"]["threshold"]:
            print(f"{Colors.YELLOW}[!] Warning: Large wordlist detected ({len(words)} words){Colors.ENDC}")
            print(f"{Colors.YELLOW}[!] This may take a while and generate many combinations{Colors.ENDC}")
            confirm = input(f"{Colors.YELLOW}Continue? (y/N): {Colors.ENDC}").lower()
            if confirm != 'y':
                return set()
        
        enhanced = set(words)
        
        print(f"\n{Colors.CYAN}[*] Enhancing wordlist...{Colors.ENDC}")
        
        # Add variations
        print(f"{Colors.CYAN}  → Adding case variations...{Colors.ENDC}")
        for word in words[:1000]:  # Limit to prevent explosion
            enhanced.add(word.capitalize())
            enhanced.add(word.upper())
            enhanced.add(word.lower())
        
        # Add leet speak
        if self.config.use_leet:
            print(f"{Colors.CYAN}  → Adding leet speak...{Colors.ENDC}")
            for word in words[:500]:
                enhanced.add(self.make_leet(word))
        
        # Add years
        print(f"{Colors.CYAN}  → Adding year combinations...{Colors.ENDC}")
        years = [str(y) for y in range(2020, 2026)]
        for word in words[:500]:
            for year in years:
                enhanced.add(f"{word}{year}")
                enhanced.add(f"{year}{word}")
        
        # Add special chars
        if self.config.use_special_chars:
            print(f"{Colors.CYAN}  → Adding special characters...{Colors.ENDC}")
            for word in words[:300]:
                for char in self.config.special_chars[:3]:
                    enhanced.add(f"{word}{char}")
        
        # Add numbers
        print(f"{Colors.CYAN}  → Adding number combinations...{Colors.ENDC}")
        for word in words[:300]:
            for num in ['123', '1', '12', '01', '007']:
                enhanced.add(f"{word}{num}")
        
        # Filter by length
        enhanced = {w for w in enhanced if self.config.min_length <= len(w) <= self.config.max_length}
        
        print(f"\n{Colors.GREEN}[✓] Enhanced: {len(words)} → {len(enhanced)} passwords{Colors.ENDC}")
        
        # Save if output file specified
        if output_file:
            self.export_txt(enhanced, output_file)
        
        return enhanced
    
    def merge_wordlists(self, files: List[str], output_file: str):
        """Merge multiple wordlists and remove duplicates"""
        
        print(f"\n{Colors.CYAN}[*] Merging {len(files)} wordlists...{Colors.ENDC}")
        
        merged = set()
        
        for file in files:
            if not os.path.isfile(file):
                print(f"{Colors.YELLOW}[!] Warning: {file} not found, skipping{Colors.ENDC}")
                continue
            
            try:
                with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                    words = [line.strip() for line in f if line.strip()]
                    merged.update(words)
                    print(f"{Colors.GREEN}[✓] Loaded {len(words)} from {file}{Colors.ENDC}")
            except Exception as e:
                print(f"{Colors.RED}[✗] Error reading {file}: {e}{Colors.ENDC}")
        
        # Filter by length
        merged = {w for w in merged if self.config.min_length <= len(w) <= self.config.max_length}
        
        print(f"\n{Colors.GREEN}[✓] Merged total: {len(merged)} unique passwords{Colors.ENDC}")
        
        self.export_txt(merged, output_file)
    
    def run_interactive(self):
        """Run interactive mode"""
        self.print_banner()
        
        profile = self.interactive_profile()
        
        print(f"\n{Colors.BOLD}{Colors.BLUE}╔══════════════════════════════════════════════════════════╗")
        print(f"║              GENERATING WORDLIST                         ║")
        print(f"╚══════════════════════════════════════════════════════════╝{Colors.ENDC}")
        
        start_time = time.time()
        passwords = self.generate_combinations(profile)
        generation_time = time.time() - start_time
        
        print(f"\n{Colors.GREEN}[✓] Generated {len(passwords)} unique passwords in {generation_time:.2f} seconds{Colors.ENDC}")
        
        stats = self.generate_statistics(passwords)
        self.display_statistics(stats)
        
        # Export options
        print(f"\n{Colors.BOLD}{Colors.BLUE}╔══════════════════════════════════════════════════════════╗")
        print(f"║              EXPORT OPTIONS                              ║")
        print(f"╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")
        
        base_filename = f"{profile.name}_passwords"
        
        # Always export TXT
        self.export_txt(passwords, f"{base_filename}.txt")
        
        # Ask for additional formats
        if input(f"\n{Colors.YELLOW}Export JSON with full statistics? (y/N): {Colors.ENDC}").lower() == 'y':
            self.export_json(passwords, stats, f"{base_filename}.json", profile)
        
        if input(f"{Colors.YELLOW}Export CSV with analysis? (y/N): {Colors.ENDC}").lower() == 'y':
            self.export_csv(passwords, f"{base_filename}.csv")
        
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ Complete! Good luck with your authorized testing!{Colors.ENDC}\n")
        print(f"{Colors.CYAN}💡 Tip: Load {base_filename}.txt into your favorite password cracking tool{Colors.ENDC}\n")

def download_common_passwords(output_file: str = "common_passwords.txt"):
    """Download common passwords list"""
    
    url = "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10-million-password-list-top-1000.txt"
    
    print(f"{Colors.CYAN}[*] Downloading common passwords list...{Colors.ENDC}")
    
    try:
        response = urllib.request.urlopen(url, timeout=30)
        data = response.read().decode('utf-8')
        
        with open(output_file, 'w') as f:
            f.write(data)
        
        print(f"{Colors.GREEN}[✓] Downloaded to {output_file}{Colors.ENDC}")
        return True
    except Exception as e:
        print(f"{Colors.RED}[✗] Download failed: {e}{Colors.ENDC}")
        return False

def main():
    """Main entry point"""
    
    # Read configuration
    read_config()
    
    parser = argparse.ArgumentParser(
        description='PassKey - Advanced Password Profiler for Penetration Testing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f'''
Examples:
  {sys.argv[0]} -i                           Interactive mode
  {sys.argv[0]} -i --min-len 8 --max-len 16  Set password length
  {sys.argv[0]} -i --no-leet                 Disable leet speak
  {sys.argv[0]} -w wordlist.txt              Improve existing wordlist
  {sys.argv[0]} -m file1.txt file2.txt -o merged.txt  Merge wordlists
  {sys.argv[0]} -d                           Download common passwords
  
⚠️  WARNING: This tool is for authorized penetration testing only.
   Unauthorized access to computer systems is illegal.

📚 Learn more: https://github.com/yourusername/passkey
        ''')
    
    group = parser.add_mutually_exclusive_group()
    
    group.add_argument('-i', '--interactive', action='store_true',
                       help='Interactive mode for profile-based generation')
    
    group.add_argument('-w', '--improve', metavar='FILE',
                       help='Improve existing wordlist with combinations')
    
    group.add_argument('-m', '--merge', nargs='+', metavar='FILES',
                       help='Merge multiple wordlists')
    
    group.add_argument('-d', '--download', action='store_true',
                       help='Download common passwords list')
    
    parser.add_argument('-o', '--output', metavar='FILE',
                        help='Output filename (for -w and -m options)')
    
    parser.add_argument('--min-len', type=int, metavar='N',
                        help=f'Minimum password length (default: {CONFIG.get("global", {}).get("wcfrom", 6)})')
    
    parser.add_argument('--max-len', type=int, metavar='N',
                        help=f'Maximum password length (default: {CONFIG.get("global", {}).get("wcto", 20)})')
    
    parser.add_argument('--no-leet', action='store_true',
                        help='Disable leet speak transformations')
    
    parser.add_argument('--no-special', action='store_true',
                        help='Disable special characters')
    
    parser.add_argument('--no-modern', action='store_true',
                        help='Disable modern terms (2025 trends)')
    
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='Quiet mode (no banner)')
    
    parser.add_argument('-v', '--version', action='version',
                        version=f'PassKey v{__version__}')
    
    args = parser.parse_args()
    
    # Configure
    config = PasswordConfig()
    
    if args.min_len:
        config.min_length = args.min_len
    if args.max_len:
        config.max_length = args.max_len
    
    config.use_leet = not args.no_leet
    config.use_special_chars = not args.no_special
    config.use_modern_terms = not args.no_modern
    
    passkey = PassKey(config)
    
    try:
        if args.interactive:
            # Interactive mode
            passkey.run_interactive()
        
        elif args.improve:
            # Improve wordlist mode
            if not args.quiet:
                passkey.print_banner()
            
            output = args.output or f"{args.improve}.enhanced.txt"
            passkey.improve_wordlist(args.improve, output)
        
        elif args.merge:
            # Merge wordlists mode
            if not args.quiet:
                passkey.print_banner()
            
            if not args.output:
                print(f"{Colors.RED}[✗] Error: --output required for merge operation{Colors.ENDC}")
                sys.exit(1)
            
            passkey.merge_wordlists(args.merge, args.output)
        
        elif args.download:
            # Download mode
            if not args.quiet:
                passkey.print_banner()
            
            output = args.output or "common_passwords.txt"
            download_common_passwords(output)
        
        else:
            # No arguments, show help
            if not args.quiet:
                passkey.print_banner()
            parser.print_help()
    
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}[!] Interrupted by user{Colors.ENDC}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}[✗] Error: {e}{Colors.ENDC}")
        if '--debug' in sys.argv:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()