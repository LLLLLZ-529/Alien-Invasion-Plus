import time

class Shield:
    """简单的护盾效果管理器：持续时间（秒）内减少或免疫伤害。"""
    def __init__(self, duration=5.0, invulnerable=False, damage_reduction=1.0):
        self.duration = duration
        self.invulnerable = invulnerable
        self.damage_reduction = damage_reduction
        self._start = None

    def activate(self):
        self._start = time.time()

    def is_active(self):
        if self._start is None:
            return False
        return (time.time() - self._start) < self.duration

    def apply_damage(self, damage):
        if not self.is_active():
            return damage
        if self.invulnerable:
            return 0
        return int(damage * self.damage_reduction)