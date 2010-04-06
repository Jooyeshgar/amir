from sqlalchemy import *
from migrate import *

meta = MetaData(migrate_engine)
subject = Table("subject", meta,
                Column('id', Integer, primary_key=True),
                Column('code', String(20)),
                Column('name', String(60)),
                Column('parent_id', Integer, ColumnDefault(0), ForeignKey('subject.id'), nullable=False)
                )
def upgrade():
    subject.create()
def downgrade():
    subject.drop()
    