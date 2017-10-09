from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import Base, Category, Item

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# clear tables
# menu items are first so as not to violate key constraints
items = session.query(Item).all()
for item in items:
        session.delete(item)
session.commit()
items = session.query(Category).all()
for item in items:
        session.delete(item)
session.commit()

# Committing the information for each category seperately so that unique
# constraints are not violated
# Category 1
cat = Category(name="Sports")
session.add(cat)
session.add(Item(name="Baseball Bat",
            description="Used for hitting baseballs \
in the game of baseball",
            category=cat))
session.add(Item(name="Baseball",
                 description="Some are even signed by Babe Ruth",
                 category=cat))
session.add(Item(name="Surf Board",
                 description="Used for riding waves--\
especially big ones",
                 category=cat))
# Category 2
cat = Category(name="Cooking")
session.add(cat)
session.add(Item(name="Frying Pan",
                 description="It's not, itself, frying; \
it's used for frying",
                 category=cat))
session.add(Item(name="Oven Mits",
                 description="Used for touching hot things \
that go in and out of the oven.",
                 category=cat))
session.add(Item(name="Eggs",
                 description="If you put one in a frying pan \
on a hot stove, you'll find out what happens to your \
brain if you get hooked on heroin.",
                 category=cat))
# Category 2
cat = Category(name="School")
session.add(cat)
session.add(Item(name="#2 Pencil",
                 description="The best kind.",
                 category=cat))
session.add(Item(name="Pencil Case",
                 description="Make sure to fill it with #2 pencils.",
                 category=cat))
session.add(Item(name="Pencil Sharpener",
                 description="Perfect for sharpening those #2s",
                 category=cat))
session.add(Item(name="Back Pack",
                 description="Also useful for camping trips--\
especially SCHOOL camping trips",
                 category=cat))
session.add(Item(name="Notebook",
                 description="A book for taking notes",
                 category=cat))
session.commit()

print "Populating done..."
