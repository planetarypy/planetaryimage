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
            assert data_products.mission_data[file_name]['label'] \
                == image.label.items()[0][1]
        except (pvl.decoder.ParseError, KeyError, UnicodeDecodeError,
                ValueError):
            try:
                assert data_products.mission_data[file_name]['opens'] \
                    == "False"
            except:
                print (file_name, "is marked as True and should be false")
        except AssertionError:
            print (file_name, "is marked as False and should be True")
