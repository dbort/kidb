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
"""Tests for storage.py."""

import storage
import unittest


class StorageTestCase(unittest.TestCase):
  def testSmoke(self):
    s = storage.Storage()

    # Key does't exist, then does exist.
    self.assertRaises(KeyError, s.Retrieve, 'key1')
    s.Create('key1', 'value1')
    self.assertEqual(s.Retrieve('key1'), 'value1')

    # Can't create the same key again.
    self.assertRaises(KeyError, s.Create, 'key1', 'value1.1')

    # Add another key, and both have different values.
    s.Create('key2', 'value2')
    self.assertEqual(s.Retrieve('key1'), 'value1')
    self.assertEqual(s.Retrieve('key2'), 'value2')

    # Modify a value.
    s.Update('key1', 'value1.2')
    self.assertEqual(s.Retrieve('key1'), 'value1.2')

    # Can't modify a missing key.
    self.assertRaises(KeyError, s.Update, 'keyNone', 'valueNone')

    # Remove a key and see that it's gone.
    s.Delete('key2')
    self.assertRaises(KeyError, s.Retrieve, 'key2')

    # Can't remove a missing key.
    self.assertRaises(KeyError, s.Delete, 'keyNone')

  def testRetrieveMultiple(self):
    entries = {
      'root[1].sub[1].leaf': 'rl1.1',
      'root[1].sub[2].leaf': 'rl1.2',
      'root[2].sub[1].leaf': 'rl2.1',
      'root[2].int[1].end': 're2.1',
      'other[1].sub[1].leaf': 'ol1.1',
      'other[1].int[1].end': 'oe1.1',
    }
    s = storage.Storage(entries=entries)

    actual = s.RetrieveMultiple(['root[%'])
    expected = [
        ('root[1].sub[1].leaf', 'rl1.1'),
        ('root[1].sub[2].leaf', 'rl1.2'),
        ('root[2].int[1].end', 're2.1'),
        ('root[2].sub[1].leaf', 'rl2.1'),
        ]
    self.assertItemsEqual(actual, expected)

    actual = s.RetrieveMultiple(['root[%.leaf'])
    expected = [
        ('root[1].sub[1].leaf', 'rl1.1'),
        ('root[1].sub[2].leaf', 'rl1.2'),
        ('root[2].sub[1].leaf', 'rl2.1'),
        ]
    self.assertItemsEqual(actual, expected)

    actual = s.RetrieveMultiple(['root[%.sub[1].leaf'])
    expected = [
        ('root[1].sub[1].leaf', 'rl1.1'),
        ('root[2].sub[1].leaf', 'rl2.1'),
        ]
    self.assertItemsEqual(actual, expected)

    actual = s.RetrieveMultiple(['%.end'])
    expected = [
        ('other[1].int[1].end', 'oe1.1'),
        ('root[2].int[1].end', 're2.1'),
        ]
    self.assertItemsEqual(actual, expected)

    actual = s.RetrieveMultiple([
        'root[1]%',
        'root[2].sub[1].leaf',  # Mix in a non-wildcard element
        ])
    expected = [
        ('root[1].sub[1].leaf', 'rl1.1'),
        ('root[1].sub[2].leaf', 'rl1.2'),
        ('root[2].sub[1].leaf', 'rl2.1'),
        ]
    self.assertItemsEqual(actual, expected)

    # Can't contain multiple wildcard characters.
    self.assertRaises(storage.WildcardError, s.RetrieveMultiple, ['a%b%c'])

    # It's ok if a pattern doesn't match anything.
    actual = s.RetrieveMultiple(['none%none'])
    self.assertItemsEqual(actual, [])

    # It's not ok if a non-wildcard key pattern doesn't match anything.
    self.assertRaises(KeyError, s.RetrieveMultiple, ['missing'])


if __name__ == '__main__':
  unittest.main()
