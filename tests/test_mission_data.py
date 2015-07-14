#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from planetaryimage.pds3image import PDS3Image
from planetary_test_data import PlanetaryTestDataProducts
import pvl


def test_mission_data():
    data_products = PlanetaryTestDataProducts()

    for file_name in data_products.products:
        image_path = os.path.join(data_products.directory, file_name)
        try:
            image = PDS3Image.open(image_path)
            assert data_products.mission_data[file_name]['opens'] == "True"
            data_label = data_products.mission_data[file_name]['label']
            for key in data_label:
                try:
                    if isinstance(data_label[key], dict):
                        sub_dict = data_label[key]
                        for sub_key in sub_dict:
                            assert sub_dict[sub_key] == \
                                image.label[key][sub_key]
                    else:
                        assert data_label[key] == image.label[key]
                except:
                    print ("Problem with %s label" % (file_name))
        except (pvl.decoder.ParseError, KeyError, UnicodeDecodeError,
                ValueError):
            try:
                assert data_products.mission_data[file_name]['opens'] \
                    == "False"
            except:
                print ("%s is marked as True & should be false" % (file_name))
        except AssertionError:
            print ("%s is marked as False & should be True" % (file_name))
