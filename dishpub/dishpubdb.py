from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import mapper

from sqlalchemy import ForeignKey

from sqlalchemy.orm import backref
try:
    from sqlalchemy.orm import relationship
except:
    from sqlalchemy.orm import relation as relationship


from sqlalchemy import Sequence
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import datetime
Base = declarative_base()


class Imagelist(Base):
    __tablename__ = 'subscription'
    id = Column(Integer, primary_key=True)
    identifier = Column(String(50),nullable = False,unique=True)
    # Line woudl be but for inconsitancy #imagelist_latest =Column(Integer, ForeignKey('imagelist.id'))
    imagelist_latest =Column(Integer)
    orm_metadata = relationship("ImagelistMetadata", backref="Imagelist",cascade='all, delete')
    # The data of the last update to the subscription.
    #     This is different from the creation time of the image list.
    #     It is provided only for instrumentation purposes.
    updated = Column(DateTime)
    def __init__(self,details, authorised = False):
        self.identifier = details[u'dc:identifier']
    def __repr__(self):
        return "<Imagelist('%s')>" % (self.identifier)


class ImagelistMetadata(Base):
    __tablename__ = 'ImagelistMetadata'
    id = Column(Integer, primary_key=True)
    fkImageList = Column(Integer, ForeignKey(Imagelist.id, onupdate="CASCADE", ondelete="CASCADE"))
    key = Column(String(200),nullable = False,unique=True)
    value = Column(String(200),nullable = False)
    def __init__(self,imagelist,key,value):
        self.fkImageList = imagelist
        self.key = key
        self.value = value
    def __repr__(self):
        return "<ImagelistMetadata('%s','%s', '%s')>" % (self.fkImageList, self.key, self.value)



def init(engine):
    Base.metadata.create_all(engine)
