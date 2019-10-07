class Level:
    def __init__(self, current_level=1, current_xp=0, level_up_base=100, level_up_factor=200, level_up_exponent=1):
        self.current_level = current_level
        self.current_xp = current_xp
        self.level_up_base = level_up_base
        self.level_up_factor = level_up_factor
        self.level_up_exponent = level_up_exponent

    @property
    def experience_to_next_level(self):
        return (self.level_up_base + self.current_level * self.level_up_factor) ** self.level_up_exponent

    def add_xp(self, xp):
        self.current_xp += xp

        if self.current_xp > self.experience_to_next_level:
            self.current_xp -= self.experience_to_next_level
            self.current_level += 1

            return True
        else:
            return False
