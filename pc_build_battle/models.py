from dataclasses import dataclass, field, asdict

CATEGORIES = ['CPU', 'CPU Cooler', 'Motherboard', 'GPU', 'RAM', 'Storage', 'PSU', 'Case']


@dataclass
class Component:
    id: str
    category: str
    name: str
    brand: str
    price: int
    performance: int = 0
    watts: int = 0
    specs: dict = field(default_factory=dict)


@dataclass
class Challenge:
    name: str
    mode: str
    budget: int
    description: str
    requirements: dict = field(default_factory=dict)
    bonuses: dict = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)


@dataclass
class Build:
    challenge: Challenge
    parts: dict = field(default_factory=dict)
    discounts: dict = field(default_factory=dict)
    event_used: bool = False

    @property
    def cost(self):
        return sum(max(0, p.price - self.discounts.get(p.id, 0)) for p in self.parts.values())

    @property
    def watts(self):
        return sum(p.watts for p in self.parts.values()) + 25
