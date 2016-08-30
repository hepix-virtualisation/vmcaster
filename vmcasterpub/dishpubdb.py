from sqlalchemy import Column, Integer, String, ForeignKey, DateTime

try:
    from sqlalchemy.orm import relationship
except:
    from sqlalchemy.orm import relation as relationship


from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.schema import UniqueConstraint


##########################################
# makes key value tables to increase flexibility.

Base = declarative_base()


class Endorser(Base):
    __tablename__ = 'endorser'
    id = Column(Integer, primary_key=True)
    subject = Column(String(100),nullable = False,unique=True)
    def __init__(self,subject):
        self.subject = subject
    def __repr__(self):
        return "<Endorser('%s')>" % (self.subject)

class EndorserMetadata(Base):
    __tablename__ = 'endorserMetadata'
    id = Column(Integer, primary_key=True)
    fkEndorser = Column(Integer, ForeignKey(Endorser.id, onupdate="CASCADE", ondelete="CASCADE"))
    key = Column(String(200),nullable = False)
    value = Column(String(200),nullable = False)
    # explicit/composite unique constraint.  'name' is optional.
    UniqueConstraint('fkEndorser', 'key')
    def __init__(self,imagelist,key,value):
        self.fkEndorser = imagelist
        self.key = key
        self.value = value
    def __repr__(self):
        return "<EndorserMetadata('%s','%s', '%s')>" % (self.fkEndorser, self.key, self.value)



class Imagelist(Base):
    __tablename__ = 'imagelist'
    id = Column(Integer, primary_key=True)
    identifier = Column(String(50),nullable = False,unique=True)
    # Line woudl be but for inconsitancy #imagelist_latest =Column(Integer, ForeignKey('imagelist.id'))
    orm_metadata = relationship("ImagelistMetadata", backref="Imagelist",cascade='all, delete')
    # The data of the last update to the subscription.
    #     This is different from the creation time of the image list.
    #     It is provided only for instrumentation purposes.
    updated = Column(DateTime)
    def __init__(self,identifier):
        self.identifier = identifier
    def __repr__(self):
        return "<Imagelist('%s')>" % (self.identifier)


class ImagelistMetadata(Base):
    __tablename__ = 'ImagelistMetadata'
    id = Column(Integer, primary_key=True)
    fkImageList = Column(Integer, ForeignKey(Imagelist.id, onupdate="CASCADE", ondelete="CASCADE"))
    key = Column(String(200),nullable = False)
    value = Column(String(200),nullable = False)
    UniqueConstraint('fkImageList', 'key')
    def __init__(self,imagelist,key,value):
        self.fkImageList = imagelist
        self.key = key
        self.value = value
    def __repr__(self):
        return "<ImagelistMetadata('%s','%s', '%s')>" % (self.fkImageList, self.key, self.value)


class Image(Base):
    __tablename__ = 'Image'
    id = Column(Integer, primary_key=True)
    identifier = Column(String(50),nullable = False,unique=True)
    def __init__(self,identifier):
        self.identifier = identifier
    def __repr__(self):
        return "<Image('%s','%s', '%s')>" % (self.fkImageList, self.key, self.value)


class ImageMetadata(Base):
    __tablename__ = 'ImageMetadata'
    id = Column(Integer, primary_key=True)
    fkImage = Column(Integer, ForeignKey(Image.id, onupdate="CASCADE", ondelete="CASCADE"))
    key = Column(String(200),nullable = False)
    value = Column(String(200),nullable = False)
    def __init__(self,image,key,value):
        self.fkImage = image
        self.key = key
        self.value = value
    def __repr__(self):
        return "<ImageMetadata('%s','%s', '%s')>" % (self.fkImage, self.key, self.value)


class Endorsement(Base):
    __tablename__ = 'Endorsement'
    id = Column(Integer, primary_key=True)
    fkImageList = Column(Integer, ForeignKey(Imagelist.id, onupdate="CASCADE", ondelete="CASCADE"))
    fkEndorser = Column(Integer, ForeignKey(Endorser.id, onupdate="CASCADE", ondelete="CASCADE"))
    def __init__(self,imagelist,endorser):
        self.fkImageList = imagelist
        self.fkEndorser = endorser

class ImageListImage(Base):
    __tablename__ = 'ImageListImage'
    id = Column(Integer, primary_key=True)
    fkImageList = Column(Integer, ForeignKey(Imagelist.id, onupdate="CASCADE", ondelete="CASCADE"))
    fkImage = Column(Integer, ForeignKey(Image.id, onupdate="CASCADE", ondelete="CASCADE"))
    def __init__(self,imagelist,image):
        self.fkImageList = imagelist
        self.fkImage = image


def init(engine):
    Base.metadata.create_all(engine)
