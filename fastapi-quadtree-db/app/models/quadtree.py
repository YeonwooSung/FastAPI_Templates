from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
import json

# custom import
from app.models.base import Base


class Rectangle(Base):
    __tablename__ = "rectangle"

    id = Column(Integer, primary_key=True)
    x = Column(Float)
    y = Column(Float)
    w = Column(Float)
    h = Column(Float)

    def contains(self, location):
        return location.longitude >= self.x and location.longitude < self.x + self.w and location.latitude >= self.y and location.latitude < self.y + self.h

    def intersects(self, rect):
        return abs(self.x - rect.x) < (self.w + rect.w) or abs(self.y - rect.y) < (self.y + rect.y)


class QuadTree(Base):
    __tablename__ = "quadtree"

    id = Column(Integer, primary_key=True)
    boundary_id = Column(Integer, ForeignKey('rectangle.id'))
    boundary = relationship('Rectangle')
    capacity = Column(Integer, default=4)
    location_ids = Column(String(1000), default='[]')
    divided = Column(Boolean, default=False)
    child_nw_id = Column(Integer, ForeignKey('quadtree.id'))
    child_nw = relationship('QuadTree', remote_side=[id])
    child_ne_id = Column(Integer, ForeignKey('quadtree.id'))
    child_ne = relationship('QuadTree', remote_side=[id])
    child_sw_id = Column(Integer, ForeignKey('quadtree.id'))
    child_sw = relationship('QuadTree', remote_side=[id])
    child_se_id = Column(Integer, ForeignKey('quadtree.id'))
    child_se = relationship('QuadTree', remote_side=[id])

    # UTILITY FUNCTIONS #

    def subdivide(self):
        # get bounds
        x = self.boundary.x
        y = self.boundary.y
        w = self.boundary.w
        h = self.boundary.h

        # create sub division bound (4 quaters)
        nw = Rectangle(x=x, y=y + h / 2, w=w / 2, h=h / 2)
        ne = Rectangle(x=x + w / 2, y=y + h / 2, w=w / 2, h=h / 2)
        sw = Rectangle(x=x, y=y, w=w / 2, h=h / 2)
        se = Rectangle(x=x + w / 2, y=y, w=w / 2, h=h / 2)

        # save those quaters
        # create self out of 4 quaters
        child_nw = QuadTree(boundary=nw)
        child_ne = QuadTree(boundary=ne)
        child_sw = QuadTree(boundary=sw)
        child_se = QuadTree(boundary=se)

        self.child_nw = child_nw
        self.child_ne = child_ne
        self.child_sw = child_sw
        self.child_se = child_se

        # since its divided
        self.divided = True


    def insert(self, location):
        # if location doesn't fit boundary just not right place to insert
        if not self.boundary.contains(location):
            return False

        # get all users id present in current self
        location_ids = json.loads(self.location_ids)

        # ensure no duplicate location get added
        if location.id in location_ids:
            print('location already exist in quadtree', self.id)
            return False

        # if users id count is less than capacity just fill it and return True
        if len(location_ids) < self.capacity:
            location_ids.append(location.id)
            self.location_ids = json.dumps(location_ids)
            print('location added in quadtree', self.id)
            return True

        # we reached here because capacity was full so we need to subdivide if is not divided
        if not self.divided:
            self.subdivide()

        # check right self to insert
        return self.child_nw.insert(location) or \
               self.child_ne.insert(location) or \
               self.child_sw.insert(location) or \
               self.child_se.insert(location)

    def query(self, locations, query_boundary, found_locations):
        if not self.boundary.intersects(query_boundary):
            return

        location_ids = json.loads(self.location_ids)
        for location_id in location_ids:
            location = locations.get(id=location_id)
            if query_boundary.contains(location):
                found_locations.append(location)

        if self.divided:
            self.child_nw.query(locations, query_boundary, found_locations)
            self.child_ne.query(locations, query_boundary, found_locations)
            self.child_sw.query(locations, query_boundary, found_locations)
            self.child_se.query(locations, query_boundary, found_locations)
