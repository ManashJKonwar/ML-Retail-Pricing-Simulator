__author__ = "konwar.m"
__copyright__ = "Copyright 2022, AI R&D"
__credits__ = ["konwar.m"]
__license__ = "Individual Ownership"
__version__ = "1.0.1"
__maintainer__ = "konwar.m"
__email__ = "rickykonwar@gmail.com"
__status__ = "Development"

import os
import json
import base64
import pickle
import pandas as pd

from zipfile import ZipFile, ZIP_DEFLATED
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

#region Task Class
class Task(UserMixin, db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=True)
    username = db.Column(db.String(15), nullable=False)
    dbtaskid = db.Column(db.String(50), nullable=False)
    taskid = db.Column(db.String(50))
    taskdata = db.Column(db.LargeBinary)
    taskstatus = db.Column(db.String(15))
    scenarioname = db.Column(db.String(15), nullable=False)
    submissiondate = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return '<Task {}>'.format(self.id)

# Function to create a specific task
def create_tasks_table(engine):
    Task.metadata.create_all(engine)
#endregion

#region Task Upload Model
class TaskUploadModel:
    def __init__(self, **kwargs):
        self._kwargs = kwargs
        self._var_object = {} # Includes floats and integers
        self._df_object = {} # Includes dataframes
        self._list_object = {} # Includes lists
        self._dict_object = {} # Includes dicts
        self._extract_items()

    def _extract_items(self):
        for k in self._kwargs.keys():
            if isinstance(self._kwargs[k], int) or isinstance(self._kwargs[k], float) or isinstance(self._kwargs[k], str):
                self._var_object[k] = self._kwargs[k]
            elif isinstance(self._kwargs[k], pd.DataFrame):
                self._df_object[k] = self._kwargs[k]
            elif isinstance(self._kwargs[k], dict):
                self._dict_object[k] = self._kwargs[k]
            elif isinstance(self._kwargs[k], list):
                self._list_object[k] = self._kwargs[k]

    def upload_files(self, upload_path=None):
        try:
            # Creating task related folder
            if not os.path.exists(upload_path):
                os.makedirs(upload_path)

            # Storing Dataframes
            for df_key in self._df_object.keys():
                self._df_object[df_key].to_csv(os.path.join(upload_path, df_key+'.csv'), index=False)

            # Storing Dictionaries
            for dict_key in self._dict_object.keys():
                with open(os.path.join(upload_path, dict_key+'.pickle'), 'wb') as f:
                    pickle.dump(self._dict_object[dict_key], f)
            
            # Storing Lists
            for list_key in self._list_object.keys():
                with open(os.path.join(upload_path, list_key+'.pickle'), 'wb') as f:
                    pickle.dump(self._list_object[list_key], f)

            # Storing Variables (int, float and str)
            with open(os.path.join(upload_path, 'var.json'), 'w') as outfile:
                json.dump({var_key: self._var_object[var_key] for var_key in self._var_object.keys()}, outfile, indent=4)
            
            return True
        except Exception as ex:
            print(ex)
            return False

    def convert_to_blob(self, upload_path=None):
        try:
            if os.path.exists(upload_path):
                zipped_file_path = os.path.basename(upload_path)+'.zip'
                zip_directory(upload_path, os.path.join(os.path.dirname(upload_path), zipped_file_path))

                with open(os.path.join(os.path.dirname(upload_path), zipped_file_path), 'rb') as f:
                    return base64.b64encode(f.read())
        except Exception as ex:
            raise ex
    
    def generate_json(self, db_task_id=None, user_name=None):
        message_object = {}
        try:
            message_object['user_name'] = user_name if user_name is not None else ''
            message_object['db_task_id'] = db_task_id if db_task_id is not None else ''
            message_object['dataframe_objects'] = list(self._df_object.keys())
            message_object['dictionary_objects'] = list(self._dict_object.keys())
            message_object['list_objects'] = list(self._list_object.keys())
            message_object['var_objects'] = list(self._var_object.keys())
            return message_object
        except Exception as ex:
            raise ex

def zip_directory(folder_path, zip_path):
    with ZipFile(zip_path, mode='w', compression=ZIP_DEFLATED, compresslevel=9) as zipf:
        len_dir_path = len(folder_path)
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, file_path[len_dir_path:])

def convert_64str_2_64bytes(base64str):
    return base64.b64decode(base64str)

def write_64str_2_file(byte_data, filepath):
    if os.path.exists(filepath):
        os.path.remove(filepath)
    with open(filepath, 'wb') as f:
        f.write(byte_data)
#endregion