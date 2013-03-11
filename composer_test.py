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
"""Tests for composer.py."""

import composer
import unittest


class ComposerTestCase(unittest.TestCase):
  def setUp(self):
    self.entries = [
      ('contacts[c:1].id', 'c:1'),
      ('contacts[c:1].fullname', 'Kim Lee'),
      ('contacts[c:1].fields[uid:1].email', 'user@example.com'),
      ('contacts[c:1].fields[uid:2].phone', '+1 650 555-1234'),
      ('contacts[c:1].fields[uid:3].email', 'user@gmail.com'),
      ('contacts[c:2].id', 'c:2'),
      ('contacts[c:2].fields[uid:4].email', 'otheruser@example.com'),
      # Non-string value.
      ('contacts[c:2].fields[uid:5].address', {
        'street': '123 Every St.',
        'city': 'Everyville',
        'state': 'CA',
        'zip': 94949,
      }),
      # A leaf node whose parent is a non-[] node.
      ('contacts[c:2].name.first', 'Alice'),
      ('contacts[c:2].name.last', 'Smith'),
    ]
    self.maxDiff = None

  def testCompose_SmokeWithKeyFields(self):
    actual = composer.Compose(self.entries)
    expected = {
      'contacts': [
        {
          '_key': 'contacts[c:1]',
          'id': 'c:1',
          'fullname': 'Kim Lee',
          'fields': [
            {
              '_key': 'contacts[c:1].fields[uid:1]',
              'email': 'user@example.com',
            },
            {
              '_key': 'contacts[c:1].fields[uid:2]',
              'phone': '+1 650 555-1234',
            },
            {
              '_key': 'contacts[c:1].fields[uid:3]',
              'email': 'user@gmail.com'
            },
          ]
        },
        {
          '_key': 'contacts[c:2]',
          'id': 'c:2',
          'name': {
            '_key': 'contacts[c:2].name',
            'first': 'Alice',
            'last': 'Smith',
          },
          'fields': [
            {
              '_key': 'contacts[c:2].fields[uid:4]',
              'email': 'otheruser@example.com',
            },
            {
              '_key': 'contacts[c:2].fields[uid:5]',
              'address': {
                'street': '123 Every St.',
                'city': 'Everyville',
                'state': 'CA',
                'zip': 94949,
              },
            },
          ]
        },
      ]
    }
    print 'got ' + repr(actual)
    self.assertEqual(actual, expected)

  def testCompose_SmokeWithoutKeyFields(self):
    actual = composer.Compose(self.entries, key_field_name=None)
    expected = {
      'contacts': [
        {
          'id': 'c:1',
          'fullname': 'Kim Lee',
          'fields': [
            {
              'email': 'user@example.com',
            },
            {
              'phone': '+1 650 555-1234',
            },
            {
              'email': 'user@gmail.com'
            },
          ]
        },
        {
          'id': 'c:2',
          'name': {
            'first': 'Alice',
            'last': 'Smith',
          },
          'fields': [
            {
              'email': 'otheruser@example.com',
            },
            {
              'address': {
                'street': '123 Every St.',
                'city': 'Everyville',
                'state': 'CA',
                'zip': 94949,
              },
            },
          ]
        },
      ]
    }
    self.assertEqual(actual, expected)


if __name__ == '__main__':
  unittest.main()
