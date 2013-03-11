#!/usr/bin/python -B
# Copyright 2013 Dave Bort
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Defines a CRUD interface with minor extra querying capabilities."""

import copy
import re


class Error(Exception):
  """Base class for exceptions defined by this module."""


class WildcardError(Error):
  """Raised when encountering a misused wildcard."""


class Storage(object):

  def __init__(self, entries=None):
    """Initializes a Storage object.

    Args:
      entries: The key:value map to use to initialize the datastore.
    """
    if entries:
      self._entries = copy.deepcopy(entries)
    else:
      self._entries = {}

  def Create(self, key, value):
    """Adds the key/value pair to the datastore.

    Args:
      key: The key string to add.
      value: The value string to add.
    Raises:
      KeyError: The key is already present in the datastore.
    """
    if key in self._entries:
      raise KeyError('Key "{}" already exists'.format(key))
    self._entries[key] = value

  def Retrieve(self, key):
    """Returns the value associated with a key.

    Args:
      key: The key string of the entry to retrieve.
    Raises:
      KeyError: The key is already present in the datastore.
    """
    if key not in self._entries:
      raise KeyError('Key "{}" does not exist'.format(key))
    return self._entries[key]

  def RetrieveMultiple(self, keys):
    """Returns a list of key/value pairs associated with the requested keys.

    Args:
      keys: A list of key patterns to look up.  A key pattern may contain
          a single '%' wildcard character, in which case all entries with
          keys matching the pattern are added to the returned results.
    Returns:
      A list of (key, value) tuple entries.  Entries are not de-duplicated,
      and no specific stable order is implied.
    Raises:
      KeyError: A non-wildcard key is not present in the datastore.
    """
    results = []  # TODO(dbort): Consider yielding
    for key in keys:
      parts = key.split('%')
      if len(parts) == 1:
        # No wildcard.
        results.append((key, self.Retrieve(key)))
      else:
        if len(parts) != 2:
          raise WildcardError(
              'Key "{}" contains multiple wildcards'.format(key))
        else:
          pattern = r'.*'.join(re.escape(part) for part in parts) + r'$'
          prog = re.compile(pattern)
          for ekey, evalue in self._entries.iteritems():
            if prog.match(ekey):
              results.append((ekey, evalue))
    return results

  # TODO(dbort): To reduce round trips, we'll probably want a way to
  # chain queries, letting the result of one join against the next.
  #
  # select * from valuestore where
  #   key like "contact[%"
  #   and reverse_key like "email.field[%"
  #   and value = "user@example.com";
  # select * from valuestore where
  #   key like "site[%"
  #   and reverse_key like "id.contact[%"
  #   and value = (contact id scraped from first select);
  # select * from collections where
  #   site_id = (site id scraped from second select)
  #
  # select * from valuestore where key like (
  #   select concat(trim(trailing ".timestamp" key), "%") from valuestore where
  #     reverse_key like "timestamp.note[%"
  #     and value >= "2013-03-01"
  # );

  def Update(self, key, value):
    """Modifies the value associated with a key, which must already exist.

    Args:
      key: The key string of the entry to modify.
      value: The new value string for the entry.
    Raises:
      KeyError: The key is not present in the datastore.
    """
    if key not in self._entries:
      raise KeyError('Key "{}" does not exist'.format(key))
    self._entries[key] = value

  def Delete(self, key):
    """Removes the entry for the given key, which must already exist.

    Args:
      key: The key string of the entry to delete.
    Raises:
      KeyError: The key is not present in the datastore.
    """
    if key not in self._entries:
      raise KeyError('Key "{}" does not exist'.format(key))
    del self._entries[key]
