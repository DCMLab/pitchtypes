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
            return base_type.Pitch(val)
        elif sub_type == "Interval":
            return base_type.Interval(val)
        elif sub_type == "PitchClass":
            return base_type.PitchClass(val)
        elif sub_type == "IntervalClass":
            return base_type.IntervalClass(val)
        else:
            self.fail(f"Unknown type {sub_type}")

    def test_value_tables(self):
        # whether to ignore empty entries
        ignore_empty = True
        # regular expression for selecting what operation to perform on what type
        type_regex = re.compile("^(?P<type>Pitch|Interval|PitchClass|IntervalClass)$")
        operation_regex = re.compile("^(?P<type1>Pitch|Interval|PitchClass|IntervalClass)"
                                     "_(?P<operation>.+)_"
                                     "(?P<type2>Pitch|Interval|PitchClass|IntervalClass)$")
        # go through the folders in base_dir containing value tables
        base_dir = "tests/value_tables"
        valid_folders = False
        for folder in os.listdir(base_dir):
            # ignore files and folders starting with a dot
            if os.path.isfile(os.path.join(base_dir, folder)) or folder.startswith("."):
                continue
            valid_folders = True
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
            valid_tables = False
            for table in os.listdir(os.path.join(base_dir, folder)):
                # ignore files that don't end with ".txt" (like backup files etc)
                if not table.endswith(".txt"):
                    continue
                valid_tables = True
                # load the table as string array
                arr = np.loadtxt(os.path.join(base_dir, folder, table),
                                 ndmin=2,
                                 dtype=str,
                                 delimiter='\t',
                                 comments=None)
                # the file name without extension is used for determining the check to be performed
                check = table[:-4]
                type_match = type_regex.match(check)
                op_match = operation_regex.match(check)
                matches = np.array([type_match is not None, op_match is not None])
                self.assertFalse(matches.sum() == 0,
                                 f"Could not match {check} against any of the regular expressions ({matches}):\n"
                                 f"{type_regex.pattern}\n{operation_regex.pattern}")
                self.assertTrue(matches.sum() == 1,
                                f"Found more than one match for {check} against the regular expressions ({matches}):\n"
                                f"{type_regex.pattern}\n{operation_regex.pattern}")
                # type checks
                if type_match is not None:
                    # go through all values (if the first dimension is of length 1; its a row vector)
                    valid_values = False
                    for idx in range(arr.shape[0]):
                        val = arr[idx, 0]
                        if val == "" and ignore_empty:
                            continue
                        valid_values = True
                        # get the object
                        obj = self.make_obj(base_type=base_type, sub_type=type_match['type'], val=val)
                        # checks for intervals
                        if obj.is_interval:
                            print_val = arr[idx, 1]
                            print_inv = arr[idx, 2]
                            # for non-negative intervals make sure that adding a + makes no difference
                            if not val.startswith('-'):
                                _obj = self.make_obj(base_type=base_type, sub_type=type_match['type'], val='+' + val)
                                self.assertEqual(obj, _obj)
                            # check negative
                            # construct negative string description and initialise object from it
                            if val.startswith('-'):
                                neg_val = val[1:]
                            else:
                                neg_val = '-' + val
                            neg_obj_ = self.make_obj(base_type=base_type, sub_type=type_match['type'], val=neg_val)
                            # construct from string in value table
                            neg_obj = self.make_obj(base_type=base_type, sub_type=type_match['type'], val=print_inv)
                            try:
                                # make sure they are the same
                                self.assertEqual(neg_obj_, neg_obj)
                                # and both print as in the table
                                self.assertEqual(print_inv, str(neg_obj_))
                                self.assertEqual(print_inv, str(neg_obj))
                                # make sure that unary negative operator produces the same object
                                self.assertEqual(neg_obj, -obj)
                                # and that double negation cancels out
                                self.assertEqual(obj, -(-obj))
                            except:
                                print(self.make_obj(base_type=base_type, sub_type=type_match['type'], val=neg_val))
                                print(val, print_val, print_inv,
                                      obj, obj.value,
                                      -obj, (-obj).value,
                                      neg_obj, neg_obj.value,
                                      neg_obj_, neg_obj_.value)
                                raise
                        else:
                            print_val = val
                        # check class
                        if not obj.is_class:
                            if obj.is_pitch:
                                class_str = arr[idx, 1]
                                class_obj = obj.PitchClass(class_str)
                            else:
                                class_str = arr[idx, 3]
                                class_obj = obj.IntervalClass(class_str)
                            # make sure to_class produces the same object as initialising interval class directly
                            self.assertEqual(obj.to_class(), class_obj)
                            # make sure to_class prints the same
                            self.assertEqual(class_str, str(obj.to_class()))
                        # make sure it prints correctly
                        try:
                            self.assertEqual(print_val, str(obj))
                        except:
                            print(val, print_val, obj, obj.value)
                            raise
                    if not valid_values:
                        self.fail(f"No values in file '{table}'")
                    # mark type as checked
                    type_checks[type_match['type']] = True
                elif op_match is not None:
                    # otherwise it's an operation check
                    # iterate through rows (skip first)
                    valid_values = False
                    for idx_1 in range(1, arr.shape[0]):
                        val_1 = arr[idx_1, 0]
                        if val_1 == "" and ignore_empty:
                            continue
                        valid_values = True
                        # initialise first object from first column
                        obj_1 = self.make_obj(base_type=base_type,
                                              sub_type=op_match['type1'],
                                              val=val_1)
                        # iterate through columns (skip first)
                        for idx_2 in range(1, arr.shape[1]):
                            val_2 = arr[0, idx_2]
                            val_res = arr[idx_1, idx_2]
                            if (val_2 == "" or val_res == "") and ignore_empty:
                                continue
                            # initialise second object from first row
                            obj_2 = self.make_obj(base_type=base_type,
                                                  sub_type=op_match['type2'],
                                                  val=val_2)
                            # determine the operation to check
                            operation = op_match['operation']
                            # remember result for error reporting
                            res = None
                            # catch errors (and later re-raise) for better reporting
                            try:
                                # check that result from operations prints as indicated in the table
                                if operation == "minus":
                                    res = obj_1 - obj_2
                                    try:
                                        self.assertEqual(val_res, str(res))
                                    except:
                                        print(f"{obj_1} - {obj_2} = {res} "
                                              f"[{obj_1.value} - {obj_2.value} = {res.value}] "
                                              f"({val_1} - {val_2} = {val_res})")
                                        raise
                                elif operation == "plus":
                                    res = obj_1 + obj_2
                                    try:
                                        self.assertEqual(val_res, str(res))
                                    except:
                                        print(f"{obj_1} + {obj_2} = {res} "
                                              f"[{obj_1.value} + {obj_2.value} = {res.value}] "
                                              f"({val_1} + {val_2} = {val_res})")
                                        raise
                                else:
                                    self.fail(f"Unknown operation '{operation}'")
                            except:
                                # in case of error: report objects and operation for better debugging
                                print(f"{obj_1} {type(obj_1)} {operation} {obj_2} {type(obj_2)} == {res} {type(res)} "
                                      f"(should be {val_res})")
                                # re-raise original error
                                raise
                    if not valid_values:
                        self.fail(f"No values in file '{table}'")
                    # mark operation as checked
                    operation_checks[check] = True
                else:
                    self.fail()
            # make sure all sub-types were checked
            if not np.all(list(type_checks.values())):
                unchecked_types = ''.join(f"\n    {key}" for key, val in type_checks.items() if not val)
                self.fail(f"For base type {folder} some types were not checked:{unchecked_types}")
            # make sure all operations were checked
            if not np.all(list(operation_checks.values())):
                unchecked_ops = ''.join(f"\n    {key}" for key, val in operation_checks.items() if not val)
                self.fail(f"For base type {folder} some operations were not checked:{unchecked_ops}")
            if not valid_tables:
                self.fail(f"no valid files in folder '{folder}'")
        if not valid_folders:
            self.fail("no valid folders found")
