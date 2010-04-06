#!/usr/bin/env python
from migrate.versioning.shell import main

main(url='sqlite:///../data/test-migration.sqlite',repository='../migraterepo')
