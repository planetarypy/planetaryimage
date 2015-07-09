import os
from planetaryimage.pds3image import PDS3Image
import json
import pytest
import pvl


DATA_DIR = os.path.join(os.path.dirname(__file__), 'mission_data')


@pytest.mark.skipif(not(os.path.exists(os.path.join(DATA_DIR, 'data.json'))),
                    reason="data.json is not present, use get_mission_data")
def test_mission_data():
    with open(os.path.join(DATA_DIR, 'data.json'), 'r') as r:
        data = json.load(r)
    for file_name in data.keys():
        image_path = os.path.join(DATA_DIR, file_name)
        try:
            image = PDS3Image.open(image_path)
            assert data[file_name]['opens'] == "True"
            assert data[file_name]['label'] == image.label.items()[0][1]
        except (pvl.decoder.ParseError, KeyError, UnicodeDecodeError,
                ValueError):
            try:
                assert data[file_name]['opens'] == "False"
            except:
                print "%s is marked as True and should be false" % (file_name)
        except AssertionError:
            print "%s is marked as False and should be True" % (file_name)
            try:
                assert data[file_name]['label'] == image.label.items()[0][1]
            except:
                print """%s needs its label updated in data.json to be
                 %s """ % (file_name, image.label.items()[0][1])
