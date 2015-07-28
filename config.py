"""
Specify the names of the profiles (defined in the image service config.py)
which define the typ on analysis to perform. Can be a function of variable
and model.

"""

profiles = {
    "UKV2EGRR_cloud_frac": ["UKV_HR", "UKV_LR"]
    "UKV2EGRR_potential_temperature": ["UKV_HR", "UKV_LR"]
}

def getProfiles(model, variable):
    return profiles[model + "_" + variable]