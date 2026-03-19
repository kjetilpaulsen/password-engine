from __future__ import annotations
import secrets
import string



class PasswordGenerator:

    def __init__(self, uppercase: bool = False, lowercase: bool = False, numbers: bool = False, specials: bool = False, password_length: int = 12) -> None:
        self.uppercase = uppercase
        self.lowercase = lowercase
        self.numbers = numbers
        self.specials = specials
        self.password_length = password_length

    def generate(self) -> str:
        pools: list[str] = []

        if self.uppercase:
            pools.append(string.ascii_uppercase)
        if self.lowercase:
            pools.append(string.ascii_lowercase)
        if self.numbers:
            pools.append(string.digits)
        if self.specials:
            pools.append(string.punctuation)

        password_chars = [secrets.choice(pool) for pool in pools]

        combined = "".join(pools)
        remaining = self.password_length - len(password_chars)

        password_chars.extend(secrets.choice(combined) for _ in range(remaining))

        secrets.SystemRandom().shuffle(password_chars)

        return "".join(password_chars)

