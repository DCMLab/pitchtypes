from unittest import TestCase
import os
from importlib import import_module
import re

import numpy as np


class TestValueTables(TestCase):

    def make_obj(self, base_type, sub_type, val):
        """
        Initialise an object of base_type.sub_type with val
        :param base_type: the base type
        :param sub_type: the sub-type
        :param val: the value
        :return: the object
        """
        if sub_type == "Pitch":
            self.fail()
        elif sub_type == "Interval":
            self.fail()
        elif sub_type == "PitchClass":
            return base_type.PitchClass(val)
        elif sub_type == "IntervalClass":
            return base_type.IntervalClass(val)
        else:
            self.fail(f"Unknown type {sub_type}")

    def test_value_tables(self):
        # regular expression for selecting what operation to perform on what type
        check_regex = re.compile("^(?P<type1>Pitch|Interval|PitchClass|IntervalClass)"
                                 "_(?P<operation>.+)_"
                                 "(?P<type2>Pitch|Interval|PitchClass|IntervalClass)$")
        # go through the folders in base_dir containing value tables
        base_dir = "value_tables"
        for folder in os.listdir(base_dir):
            # remember what type checks have been done
            type_checks = {"Pitch": False,
                           "Interval": False,
                           "PitchClass": False,
                           "IntervalClass": False}
            # remember what operation checks have been done
            operation_checks = {"Pitch_plus_Interval": False,
                                "Interval_plus_Interval": False,
                                "Pitch_minus_Pitch": False,
                                "Pitch_minus_Interval": False,
                                "Interval_minus_Interval": False,
                                "PitchClass_plus_IntervalClass": False,
                                "IntervalClass_plus_IntervalClass": False,
                                "PitchClass_minus_PitchClass": False,
                                "PitchClass_minus_IntervalClass": False,
                                "IntervalClass_minus_IntervalClass": False}
            # the folders are assumed to be named according to the base types, which are imported
            base_type = getattr(import_module('pitchtypes'), folder)
            # go through all the value tables
            for table in os.listdir(os.path.join(base_dir, folder)):
                # ignore files that don't end with ".txt" (like backup files etc)
                if not table.endswith(".txt"):
                    continue
                # load the table as string array
                arr = np.loadtxt(os.path.join(base_dir, folder, table),
                                 ndmin=2,
                                 dtype=str,
                                 delimiter='\t',
                                 comments=None)
                # the file name without extension is used for determining the check to be performed
                check = table[:-4]
                # check shape
                if arr.shape[0] == 1:
                    # if the first dimension is 1 (row vector) this is a type check
                    # go through all values
                    for val in arr[0, :]:
                        # get the object
                        obj = self.make_obj(base_type=base_type, sub_type=check, val=val)
                        # make sure it prints as the string it was initialised from
                        self.assertEqual(str(obj), val)
                    # mark type as checked
                    type_checks[check] = True
                else:
                    # otherwise it's an operation check
                    # match against regex
                    match = check_regex.match(check)
                    # make sure the match was successful
                    self.assertIsNotNone(match, f"Could not match {check} to regex {check_regex.pattern}")
                    # iterate through rows (skip first)
                    for idx_1 in range(1, arr.shape[0]):
                        # initialise first object from first column
                        obj_1 = self.make_obj(base_type=base_type,
                                              sub_type=match['type1'],
                                              val=arr[idx_1, 0])
                        # iterate through columns (skip first)
                        for idx_2 in range(1, arr.shape[1]):
                            # initialise second object from first row
                            obj_2 = self.make_obj(base_type=base_type,
                                                  sub_type=match['type2'],
                                                  val=arr[0, idx_2])
                            # determine the operation to check
                            operation = match['operation']
                            # remember result for error reporting
                            res = None
                            # catch errors (an later re-raise) for better reporting
                            try:
                                # check that result from operations prints as indicated in the table
                                if operation == "minus":
                                    res = obj_1 - obj_2
                                    self.assertEqual(str(res), arr[idx_1, idx_2])
                                elif operation == "plus":
                                    res = obj_1 + obj_2
                                    self.assertEqual(str(res), arr[idx_1, idx_2])
                                else:
                                    self.fail(f"Unknown operation '{operation}'")
                            except:
                                # in case of error: report objects and operation for better debugging
                                print(f"{obj_1} {type(obj_1)} {operation} {obj_2} {type(obj_2)} == {res} {type(res)} "
                                      f"(should be {arr[idx_1, idx_2]})")
                                # re-raise original error
                                raise
                    # mark operation as checked
                    operation_checks[check] = True
            # make sure all sub-types were checked
            if not np.all(list(type_checks.values())):
                unchecked_types = ''.join(f"\n    {key}" for key, val in type_checks.items() if not val)
                self.fail(f"For base type {folder} some types were not checked:{unchecked_types}")
            # make sure all operations were checked
            if not np.all(list(operation_checks.values())):
                unchecked_ops = ''.join(f"\n    {key}" for key, val in operation_checks.items() if not val)
                self.fail(f"For base type {folder} some operations were not checked:{unchecked_ops}")
