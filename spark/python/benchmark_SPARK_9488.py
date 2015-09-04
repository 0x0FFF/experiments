import random
import time
from hashlib import md5


def _create_row(fields, values):
    row = Row(*values)
    row.__fields__ = fields
    return row


class Row(tuple):

    """
    A row in L{DataFrame}. The fields in it can be accessed like attributes.

    Row can be used to create a row object by using named arguments,
    the fields will be sorted by names.

    >>> row = Row(name="Alice", age=11)
    >>> row
    Row(age=11, name='Alice')
    >>> row.name, row.age
    ('Alice', 11)

    Row also can be used to create another Row like class, then it
    could be used to create Row objects, such as

    >>> Person = Row("name", "age")
    >>> Person
    <Row(name, age)>
    >>> Person("Alice", 11)
    Row(name='Alice', age=11)
    """

    def __new__(self, *args, **kwargs):
        if args and kwargs:
            raise ValueError("Can not use both args "
                             "and kwargs to create Row")
        if args:
            # create row class or objects
            return tuple.__new__(self, args)

        elif kwargs:
            # create row objects
            names = sorted(kwargs.keys())
            row = tuple.__new__(self, [kwargs[n] for n in names])
            row.__fields__ = names
            return row

        else:
            raise ValueError("No args or kwargs")

    def asDict(self, recursive=False):
        """
        Return as an dict

        :param recursive: turns the nested Row as dict (default: False).

        >>> Row(name="Alice", age=11).asDict() == {'name': 'Alice', 'age': 11}
        True
        >>> row = Row(key=1, value=Row(name='a', age=2))
        >>> row.asDict() == {'key': 1, 'value': Row(age=2, name='a')}
        True
        >>> row.asDict(True) == {'key': 1, 'value': {'name': 'a', 'age': 2}}
        True
        """
        if not hasattr(self, "__fields__"):
            raise TypeError("Cannot convert a Row class into dict")

        if recursive:
            def conv(obj):
                if isinstance(obj, Row):
                    return obj.asDict(True)
                elif isinstance(obj, list):
                    return [conv(o) for o in obj]
                elif isinstance(obj, dict):
                    return dict((k, conv(v)) for k, v in obj.items())
                else:
                    return obj
            return dict(zip(self.__fields__, (conv(o) for o in self)))
        else:
            return dict(zip(self.__fields__, self))

    # let object acts like class
    def __call__(self, *args):
        """create new Row object"""
        return _create_row(self, args)

    def __getattr__(self, item):
        if item.startswith("__"):
            raise AttributeError(item)
        try:
            # it will be slow when it has many fields,
            # but this will not be used in normal cases
            idx = self.__fields__.index(item)
            return self[idx]
        except IndexError:
            raise AttributeError(item)
        except ValueError:
            raise AttributeError(item)

    def __setattr__(self, key, value):
        if key != '__fields__':
            raise Exception("Row is read-only")
        self.__dict__[key] = value

    def __reduce__(self):
        """Returns a tuple so Python knows how to pickle Row."""
        if hasattr(self, "__fields__"):
            return (_create_row, (self.__fields__, tuple(self)))
        else:
            return tuple.__reduce__(self)

    def __repr__(self):
        """Printable representation of Row used in Python REPL."""
        if hasattr(self, "__fields__"):
            return "Row(%s)" % ", ".join("%s=%r" % (k, v)
                                         for k, v in zip(self.__fields__, tuple(self)))
        else:
            return "<Row(%s)>" % ", ".join(self)


def _create_indexed_row(fields, values):
    row = Row(*values)
    row.__fields__ = fields
    row.__fieldindex__ = dict(zip(fields, range(len(fields))))
    return row


class IndexedRow(tuple):

    """
    A row in L{DataFrame}. The fields in it can be accessed like attributes.

    Row can be used to create a row object by using named arguments,
    the fields will be sorted by names.

    >>> row = Row(name="Alice", age=11)
    >>> row
    Row(age=11, name='Alice')
    >>> row.name, row.age
    ('Alice', 11)

    Row also can be used to create another Row like class, then it
    could be used to create Row objects, such as

    >>> Person = Row("name", "age")
    >>> Person
    <Row(name, age)>
    >>> Person("Alice", 11)
    Row(name='Alice', age=11)
    """

    def __new__(self, *args, **kwargs):
        if args and kwargs:
            raise ValueError("Can not use both args "
                             "and kwargs to create Row")
        if args:
            # create row class or objects
            return tuple.__new__(self, args)

        elif kwargs:
            # create row objects
            names = sorted(kwargs.keys())
            row = tuple.__new__(self, [kwargs[n] for n in names])
            row.__fields__ = names
            row.__fieldindex__ = dict(zip(names, range(len(names))))
            return row

        else:
            raise ValueError("No args or kwargs")

    def asDict(self, recursive=False):
        """
        Return as an dict

        :param recursive: turns the nested Row as dict (default: False).

        >>> Row(name="Alice", age=11).asDict() == {'name': 'Alice', 'age': 11}
        True
        >>> row = Row(key=1, value=Row(name='a', age=2))
        >>> row.asDict() == {'key': 1, 'value': Row(age=2, name='a')}
        True
        >>> row.asDict(True) == {'key': 1, 'value': {'name': 'a', 'age': 2}}
        True
        """
        if not hasattr(self, "__fields__"):
            raise TypeError("Cannot convert a Row class into dict")

        if recursive:
            def conv(obj):
                if isinstance(obj, Row):
                    return obj.asDict(True)
                elif isinstance(obj, list):
                    return [conv(o) for o in obj]
                elif isinstance(obj, dict):
                    return dict((k, conv(v)) for k, v in obj.items())
                else:
                    return obj
            return dict(zip(self.__fields__, (conv(o) for o in self)))
        else:
            return dict(zip(self.__fields__, self))

    # let object acts like class
    def __call__(self, *args):
        """create new Row object"""
        return _create_indexed_row(self, args)

    def __getattr__(self, item):
        if item.startswith("__"):
            raise AttributeError(item)
        try:
            # it will be slow when it has many fields,
            # but this will not be used in normal cases
            idx = self.__fieldindex__[item]
            return self[idx]
        except IndexError:
            raise AttributeError(item)
        except ValueError:
            raise AttributeError(item)
        except KeyError:
            raise AttributeError(item)

    def __setattr__(self, key, value):
        if key not in ('__fields__', '__fieldindex__'):
            raise Exception("Row is read-only")
        self.__dict__[key] = value

    def __reduce__(self):
        """Returns a tuple so Python knows how to pickle Row."""
        if hasattr(self, "__fields__"):
            return (_create_indexed_row, (self.__fields__, tuple(self)))
        else:
            return tuple.__reduce__(self)

    def __repr__(self):
        """Printable representation of Row used in Python REPL."""
        if hasattr(self, "__fields__"):
            return "Row(%s)" % ", ".join("%s=%r" % (k, v)
                                         for k, v in zip(self.__fields__, tuple(self)))
        else:
            return "<Row(%s)>" % ", ".join(self)


def generate_field_list(num, seed=None):
    length = 0
    fields = []
    random.seed(seed)
    while length != num:
        fields = ['f' + md5('field' + str(random.randint(0, 10000000))).hexdigest() for _ in range(num)]
        length = len(set(fields))
    return fields


def generate_data(fields, seed=None):
    res = {}
    random.seed(seed)
    for f in fields:
        res[f] = random.randint(1, 1000000000) if random.random() < 0.5 \
            else md5('field' + str(random.randint(0, 10000000))).hexdigest()
    return res


def test(row, fields, num):
    data = generate_data(fields)
    num_fields = len(fields)
    start = time.time()
    ds = [row(**data) for _ in range(num)]
    print 'Created %10d %s objects with %3d fields in %6.2f sec' % (num, row.__name__, num_fields, time.time()-start)
    start = time.time()
    for field in fields:
        tds = [r.__getattr__(field) for r in ds]
    print 'Queried %10d %s objects with %3d fields in %6.2f sec' % (num, row.__name__, num_fields, time.time()-start)


def main():
    for obj in [Row, IndexedRow]:
        for num_fields in range(1, 101):
            test(obj, generate_field_list(num_fields), 1000000)


if __name__ == "__main__":
    main()

