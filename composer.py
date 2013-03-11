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
"""Maps between python dict hierarchies and key/value pairs.

Does no validation that a given set of keys makes sense;
that's the job of a higher level.
"""

import re

# Matches strings that end with "[.*]", capturing the string before
# the brackets and the contents of the brackets. Starts with the first
# appearance of '[', which means that the bracketed group could itself
# contain brackets.
_SUBSCRIPT_PATTERN = re.compile(r'^([^[]*)\[(.*)\]$')


# The name of extra fields added to composed dicts, whose value is
# the full dotted key associated with a given dict.
_DEFAULT_KEY_FIELD_NAME = '_key'


def _GetParent(key, keys_to_dicts, key_field_name):
  """Returns the parent dict of a leaf key.

  If necessary, creates all nodes between the root and the parent dict.

  Args:
    key: The key to find the parent of.
    keys_to_dicts: Maps keys to their associated dicts.  The root dict
        must already be mapped, with the empty string as its key.
    key_field_name: If non-empty, add to each dict an extra field with this
        name whose value is the full dotted key.
  Returns:
    The parent dict of the key.
  """
  # Drop the last dotted element to get the parent.
  parts = key.split('.')[:-1]
  parent_key = '.'.join(parts)

  # Look in the cache.
  parent_dict = keys_to_dicts.get(parent_key)
  if parent_dict is not None:
    return parent_dict

  # We should have found the root.
  if parent_key == '':
    raise ValueError('Root was not registered in keys_to_dicts')

  # Build the chain to the root.
  grandparent_dict = _GetParent(
      parent_key, keys_to_dicts, key_field_name=key_field_name)

  # The name of the element we're adding.
  field_name = parts[-1]

  # The dict we're adding.
  if key_field_name:
    new_dict = {key_field_name: parent_key}
  else:
    new_dict = {}

  # If it's a [] node, there's a list in the middle.
  match = _SUBSCRIPT_PATTERN.match(field_name)
  if match:
    # The portion of the part before the first left bracket.
    list_name = match.group(1)

    # Create the containing list if it doesn't already exist.
    containing_list = grandparent_dict.setdefault(list_name, [])

    # Add the new dict to the list.
    containing_list.append(new_dict)
  else:
    # The new dict goes directly in the grandparent.
    grandparent_dict[field_name] = new_dict

  keys_to_dicts[parent_key] = new_dict
  return new_dict


def Compose(entries, key_field_name=_DEFAULT_KEY_FIELD_NAME):
  """Composes the entry tuples into a list of python dicts.
  
  Args:
    entries: A list of (key, value) tuples, where key is a string and
        value is an object.
    key_field_name: If non-empty, add to each dict an extra field with this
        name whose value is the full dotted key.
  Returns:
    A list of python dicts representing the input entries.
  """
  root = {}
  keys_to_dicts = {'': root}
  for key, value in entries:
    parent_dict = _GetParent(key, keys_to_dicts, key_field_name)
    leaf_name = key.split('.')[-1]
    parent_dict[leaf_name] = value
  return root


# TODO(dbort): Write Decompose(root, key_field_name=_DEFAULT_KEY_FIELD_NAME).
