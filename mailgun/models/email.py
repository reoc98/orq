from main.Database import base_class
from sqlalchemy import Column, Integer, String, DateTime, sql


class Email(base_class):
    __tablename__ = 'email'

    id = Column(Integer, primary_key=True, nullable=False)
    reference_id = Column(Integer, nullable=True)
    # type_id = Column('TYPE_ID', Integer, nullable=False)
    to = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    body = Column(String, nullable=False)
    status = Column(Integer, nullable=False,
                    server_default=sql.func.now())
    date_reg = Column(String, nullable=False,
                      server_default=sql.func.now())

    def __init__(self, reference_id, to, subject, body):
        self.reference_id = reference_id
        self.to = to
        self.subject = subject
        self.body = body
