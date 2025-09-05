import random
from django.contrib.auth.models import User
from core.models import ServiceProvider, Review, Connection  # apne app ka naam lagao "core" ki jagah

# ---- Seed Users ----
usernames = [
    "navya", "aarav", "mehul", "riya", "tanvi", "arjun", "sanya", "rahul", "neha", "ananya",
    "kabir", "isha", "aditya", "priya", "rohan", "diya", "krish", "pari", "manav", "avani"
]

users = []
for uname in usernames:
    user, created = User.objects.get_or_create(username=uname, defaults={"password": "pass1234"})
    users.append(user)

print("✅ Users added:", len(users))

# ---- Seed Service Providers ----
services = [
    ("Plumber", "Leakage fixing, pipe installation"),
    ("Electrician", "Wiring, fan, and light repair"),
    ("Carpenter", "Furniture and wood work"),
    ("Painter", "Wall painting, polishing"),
    ("Cleaner", "House cleaning"),
    ("Mechanic", "Bike and car repair"),
    ("Gardener", "Lawn and plant care"),
    ("Barber", "Haircut and grooming"),
    ("Tutor", "Math and Science tuition"),
    ("Technician", "AC/Fridge repair")
]

providers = []
for i, (name, desc) in enumerate(services, start=1):
    provider, created = ServiceProvider.objects.get_or_create(
        name=name,
        description=desc,
        defaults={"rating": random.randint(3, 5)}
    )
    providers.append(provider)

print("✅ Providers added:", len(providers))

# ---- Seed Connections (friends/social layer) ----
for i in range(30):  # 30 random connections
    u1, u2 = random.sample(users, 2)
    Connection.objects.get_or_create(user=u1, friend=u2)

print("✅ Connections added")

# ---- Seed Reviews ----
for i in range(50):  # 50 reviews
    reviewer = random.choice(users)
    provider = random.choice(providers)
    Review.objects.create(
        user=reviewer,
        provider=provider,
        rating=random.randint(1, 5),
        comment=random.choice([
            "Very good service!",
            "Average experience.",
            "Highly recommended.",
            "Not satisfied.",
            "Will call again."
        ])
    )

print("✅ Reviews added")
