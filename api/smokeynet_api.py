import json
import yaml
import os
import numpy as np
import pandas as pd
import requests

class SmokeyNetAPI():

    SYNOPTIC_API_BASE_URL = "https://api.synopticdata.com/v2/"
    WEATHER_NETWORKS = "139,81,231" # SDGE, HPWREN, SC-EDISON
    
    def __init__(self, *args):
        if len(args) > 0: # config.yaml
            with open(args[0], "r") as yamlfile:
                config = yaml.safe_load(yamlfile)
            self.synoptic_api_token = config["synoptic_mesonet"]["token"]
        else:
            self.synoptic_api_token = os.environ['SYNOPTIC_TOKEN']
        
        self.camera_station_mapping_df = pd.read_csv("api/camera_station_mappings.csv")
        self.max_distance = self.camera_station_mapping_df["distance_mi"].max()

    def get_camera_weatherdata(self, camera_id: str):
        """
        Return weighted average weather data for mapped stations given a camera station id.
        Currently:
        - on no data, return empty dict
        - on missing data, add cols with null
        """
        # given: camera station id
        # return: weighted averaged of the weather station data available

        # 1. get mapping for nearest weather stations
        print(camera_id)
        mappings_df = self.camera_station_mapping_df[self.camera_station_mapping_df["camera_id"] == camera_id]
        # invalid camera id or no stations mapped
        if mappings_df.shape[0] == 0:
            return {}
        stid = ",".join(mappings_df["stid"].tolist())
        # print(mappings_df)
        # 2. get latest data foreach weather station
        endpoint = f"{self.SYNOPTIC_API_BASE_URL}stations/latest"
        params = {
            "token": self.synoptic_api_token,
            "within": 20, # latest within past 20 min
            "network": self.WEATHER_NETWORKS,
            "stid": stid,
            "obtimezone": "UTC",
            "output": "json",
        }
        r = requests.get(endpoint, params=params)
        if r.status_code not in range(200, 300):
            return {}
        r_json = r.json()
        num_objects = r_json["SUMMARY"]["NUMBER_OF_OBJECTS"]
        # no data - should return 204 none found?
        if num_objects == 0:
            return {}
        # parse data to df
        cols = [
            "stid",
            "name",
            "date_time",
            "air_temp_value_1",
            "relative_humidity_value_1",
            "wind_speed_value_1",
            "wind_gust_value_1",
            "wind_direction_value_1",
            "dew_point_temperature_value_1d",
        ]
        weather_df = pd.DataFrame(columns=cols)
        for i in range(num_objects):
            station = r_json["STATION"][i]
            row_list = [
                station["STID"],
                station["NAME"],
                station["OBSERVATIONS"]["air_temp_value_1"]["date_time"],
                station["OBSERVATIONS"]["air_temp_value_1"]["value"],
                station["OBSERVATIONS"]["relative_humidity_value_1"]["value"],
                station["OBSERVATIONS"]["wind_speed_value_1"]["value"],
                station["OBSERVATIONS"]["wind_gust_value_1"]["value"],
                station["OBSERVATIONS"]["wind_direction_value_1"]["value"],
                station["OBSERVATIONS"]["dew_point_temperature_value_1d"]["value"],
            ]
            weather_df.loc[len(weather_df)] = row_list
        # 3. calc uv componenets
        # Reference: http://colaweb.gmu.edu/dev/clim301/lectures/wind/wind-uv
        # convert direction to math direction
        weather_df["wind_direction_math"] = 270 - weather_df["wind_direction_value_1"]
        # if negative add 360
        weather_df.loc[weather_df["wind_direction_math"] < 0, ["wind_direction_math"]] += 360
        # convert degrees to radians
        weather_df["wind_direction_math_r"] = np.radians(weather_df["wind_direction_math"])
        # calculate uv components
        weather_df["u"] = weather_df["wind_speed_value_1"] * np.cos(weather_df["wind_direction_math_r"])
        weather_df["v"] = weather_df["wind_speed_value_1"] * np.sin(weather_df["wind_direction_math_r"])
        # drop unnecessary columns
        weather_df.drop(columns=["wind_direction_math", "wind_direction_math_r"], inplace=True)
        # join to get the distance values for weather station data available
        weather_df = weather_df.merge(mappings_df[["stid", "distance_mi"]], left_on="stid", right_on="stid", how="left")
        # 3. take weighted average of all values (will need max distance)
        # calc inverse distance
        weather_df["distance_mi_inverse"] = self.max_distance - weather_df["distance_mi"]
        # pivot
        pivoted_df = weather_df.melt(["stid", "name", "date_time", "distance_mi", "distance_mi_inverse"])
        # drop nas
        pivoted_df.dropna(subset=["value"], inplace=True)
        # calculate each variable total distance with nas dropped
        var_distance_df = pivoted_df[["variable", "distance_mi_inverse"]].groupby(["variable"]).sum().reset_index().copy().rename(columns={"distance_mi_inverse": "total_distance_mi_inverse"})
        # calc weighted avg
        pivoted_df = pivoted_df.merge(var_distance_df, left_on="variable", right_on="variable", how="left")
        pivoted_df["weighted_value"] = pivoted_df["value"] * (pivoted_df["distance_mi_inverse"] / pivoted_df["total_distance_mi_inverse"])
        weighted_avg_df = pivoted_df[["variable", "weighted_value"]].groupby(["variable"]).sum().reset_index()
        # 4. return data as json
        # unpivot
        # weighted_avg_df = weighted_avg_df.pivot_table(columns="variable", values="weighted_val")
        # insert nulls for any nonexistent values (all stations would need null for nonexistent)
        var = [
            "air_temp_value_1",
            "relative_humidity_value_1",
            "wind_speed_value_1",
            "wind_gust_value_1",
            "wind_direction_value_1",
            "dew_point_temperature_value_1d",
            "u",
            "v",
        ]
        val = [None] * 8
        null_d = {"variable": var, "value": val}
        null_df = pd.DataFrame(null_d)
        result_df = null_df.merge(
            weighted_avg_df, left_on="variable", right_on="variable", how="left"
        )
        result_df["value_return"] = result_df["weighted_value"].fillna(result_df["value"])
        result_df = result_df[["variable", "value_return"]].pivot_table(columns="variable", values="value_return")
        # return
        return result_df.iloc[0].to_dict()


# if __name__ == "__main__":
#     api = SmokeyNetAPI("")
#     print(api.get_camera_weatherdata("hpwren30_south"))