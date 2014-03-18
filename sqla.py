#!/usr/bin/env python
#coding=utf-8

"""
    mydb.py
    ~~~~~~~~~~~~~

    Database connect class, from flask-sqlalchemy

    :license: BSD, see LICENSE for more details.
"""
import re
from functools import partial
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy.orm.mapper import Mapper
from sqlalchemy.orm.session import Session
from sqlalchemy.orm.interfaces import MapperExtension, SessionExtension, \
     EXT_CONTINUE
from sqlalchemy.orm.exc import UnmappedClassError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.util import to_list

_camelcase_re = re.compile(r'([A-Z]+)(?=[a-z0-9])')

def _create_scoped_session(db, options):
    if options is None:
        options = {}
    return orm.scoped_session(partial(_SignallingSession, db, **options))


def _make_table(db):
    def _make_table(*args, **kwargs):
        if len(args) > 1 and isinstance(args[1], db.Column):
            args = (args[0], db.metadata) + args[1:]
        return sqlalchemy.Table(*args, **kwargs)
    return _make_table


def _include_sqlalchemy(obj):
    for module in sqlalchemy, sqlalchemy.orm:
        for key in module.__all__:
            if not hasattr(obj, key):
                setattr(obj, key, getattr(module, key))
    obj.Table = _make_table(obj)


class _SignallingSession(Session):

    def __init__(self, db, autocommit=False, autoflush=False, **options):
        Session.__init__(self, autocommit=autocommit, autoflush=autoflush,
                         bind=db.engine, **options)


class _QueryProperty(object):

    def __init__(self, sa):
        self.sa = sa

    def __get__(self, obj, type):
        try:
            mapper = orm.class_mapper(type)
            if mapper:
                return type.query_class(mapper, session=self.sa.session())
        except UnmappedClassError:
            return None


class _SignalTrackingMapper(Mapper):
    def __init__(self, *args, **kwargs):
        extensions = to_list(kwargs.pop('extension', None), [])
        kwargs['extension'] = extensions
        Mapper.__init__(self, *args, **kwargs)


class _ModelTableNameDescriptor(object):

    def __get__(self, obj, type):
        tablename = type.__dict__.get('__tablename__')
        if not tablename:
            def _join(match):
                word = match.group()
                if len(word) > 1:
                    return ('_%s_%s' % (word[:-1], word[-1])).lower()
                return '_' + word.lower()
            tablename = _camelcase_re.sub(_join, type.__name__).lstrip('_')
            setattr(type, '__tablename__', tablename)
        return tablename


class Model(object):
    """Baseclass for custom user models."""

    #: an instance of :attr:`query_class`.  Can be used to query the
    #: database for instances of this model.
    query = None

    #: arguments for the mapper
    __mapper_cls__ = _SignalTrackingMapper

    __tablename__ = _ModelTableNameDescriptor()


class SQLAlchemy(object):
    """
        sqlalchemy
    """
    def __init__(self, engine_url, echo=False,
                 session_extensions=None, session_options=None):
        """Init""" 
        self.session = _create_scoped_session(self, session_options)
        self.Model = declarative_base(cls=Model, name='Model')
        self.Model.query = _QueryProperty(self)
        self.engine = sqlalchemy.create_engine(engine_url, echo=echo)
        _include_sqlalchemy(self)

    def create_all(self):
        """Creates all tables."""
        self.Model.metadata.create_all(bind=self.engine)

    def drop_all(self):
        """Drops all tables."""
        self.Model.metadata.drop_all(bind=self.engine)

