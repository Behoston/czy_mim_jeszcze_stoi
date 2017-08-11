import collections

Status = collections.namedtuple(
    'Status',
    ['timestamp', 'mail', 'lab', 'usos', 'ssh'],
)
