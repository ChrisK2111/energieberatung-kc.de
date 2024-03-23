class Building:
    def __init__(self, year_of_constr, floor_area, floor_count, ug_floor_count, ext_walls_count):
        window_area_ratio = 0.3
        cubature = self.get_cubature(floor_area, window_area_ratio, floor_count, ug_floor_count, ext_walls_count)

        self.area_windows = cubature['window_area']
        self.volume = cubature['volume']
        self.g_windows_eff = 0.6
        self.a_solar_eff = 0.8
        self.qd_internal = 45 / 24  # 45 Wattstunden pro m2
        self.floor_area = floor_area
        self.theta_inner_set_heating = 20
        self.theta_inner_set_cooling = 25
        self.theta_inner_design_cooling = 26
        self.delta_dheta_desing_heating = 32
        self.air_change_rate = 0.5  # 1/h

        self.envelope_component = [
            EnvelopeComponent('windows', year_of_constr, cubature['window_area']),
            EnvelopeComponent('extWalls', year_of_constr, cubature['ext_wall_area']),
            EnvelopeComponent('roof', year_of_constr, cubature['roof_area']),
            EnvelopeComponent('basement', year_of_constr, cubature['basement_area'])
        ]

        self.heating_system = HeatingSystem('gas-70', year_of_constr, self.max_heating_load)

    @property
    def heat_trans_coeff(self):
        ht = 0
        for env_comp in self.envelope_component:
            ht += env_comp.u_value * env_comp.area
        return ht

    @property
    def max_heating_load(self):
        qd_heating_max = 1 / 1000 * (
            (self.heat_trans_coeff + 0.34 * self.volume * self.air_change_rate) *
            self.delta_dheta_desing_heating
        )
        return qd_heating_max

    @property
    def max_cooling_load(self):
        theta_amb_design = 25
        solar_rad_design = 700

        d_theta_cooling = self.theta_inner_set_cooling - theta_amb_design
        qd_trans = self.heat_trans_coeff * d_theta_cooling
        qd_vent = 0.34 * self.volume * self.air_change_rate * d_theta_cooling
        qd_sol = self.area_windows * self.a_solar_eff * self.g_windows_eff * solar_rad_design
        qd_int = self.qd_internal * self.floor_area

        qd_cooling_max = - 1 / 1000 * (qd_trans + qd_vent - qd_int - qd_sol)

        return qd_cooling_max

    def calc_energy_demand_yearly(self, weather_data):
        q = self.calc_energy_demand_monthly( weather_data);
        return {'heating_demand': sum(max(qh['heating_demand']/self.floor_area,0) for qh in q ),
                'cooling_demand': sum(max(qc['cooling_demand']/self.floor_area,0) for qc in q )}
        
    def calc_energy_demand_monthly(self, weather_data):
        # Rückgabe in kWh/Monat
        Q_f = []

        for month in range(len(weather_data)):
            d_theta_heating = self.theta_inner_set_heating - weather_data[month]["temperature"]
            d_theta_cooling = self.theta_inner_set_cooling - weather_data[month]["temperature"]
            
            Qd_trans_h = 1/1000 * self.heat_trans_coeff * d_theta_heating
            Qd_trans_c = 1/1000 * self.heat_trans_coeff * d_theta_cooling
            Qd_vent_h = 1/1000 * 0.34 * self.volume * self.air_change_rate * d_theta_heating
            Qd_vent_c = 1/1000 * 0.34 * self.volume * self.air_change_rate * d_theta_cooling
            Qd_sol = 1/1000 * self.area_windows * self.a_solar_eff * \
                    self.g_windows_eff * weather_data[month]["solar_radiation"]
            Qd_int = 1/1000 * self.qd_internal * self.floor_area

            Q_hf_mth = (Qd_trans_h + Qd_vent_h - Qd_int - Qd_sol) * 24 * 30
            Q_cf_mth = -(Qd_trans_c + Qd_vent_c - Qd_int - Qd_sol) * 24 * 30
            Q_hf_mth = max(Q_hf_mth, 0) / self.heating_system.efficiency
            Q_cf_mth = max(Q_cf_mth, 0)

            Q_f.append({"month": weather_data[month]["month"], "heating_demand": Q_hf_mth, "cooling_demand": Q_cf_mth})

        return Q_f

    def get_cubature(self, floor_area, window_area_ratio, floor_count, ug_floor_count, ext_walls_count):
        floor_height = 2.8
        aspect_ratio = 0.75
        roof_floor_ratio = 1.2

        basement_area = floor_area / floor_count

        length = (1 / aspect_ratio * basement_area) ** 0.5
        width = (aspect_ratio * basement_area) ** 0.5

        ext_perimeter = 0

        if ext_walls_count == 2:
            # Reihenmittelhaus
            ext_perimeter = 2 * width
        elif ext_walls_count == 3:
            # Reihenendhaus
            ext_perimeter = 1 * length + 2 * width
        else:
            # Freistehendes Haus
            ext_perimeter = 2 * length + 2 * width

        return {
            'ext_wall_area': floor_count * ext_perimeter * floor_height * (1 - window_area_ratio),
            'window_area': floor_count * ext_perimeter * floor_height * window_area_ratio,
            'basement_area': basement_area + (ug_floor_count * floor_height * ext_perimeter),
            'roof_area': roof_floor_ratio * basement_area,
            'volume': floor_area * floor_height
        }

    def retrofit_component(self, type, name, year):
        if type == 'envelope':
            return self.retrofit_envelope(name, year)
        elif type == 'heating':
            return self.retrofit_heating(name, year)

    def retrofit_envelope(self, name, year):
        retrofit_id = next((i for i, env_comp in enumerate(self.envelope_component) if env_comp.name == name), None)
        if retrofit_id is not None:
            retrofitted_component = EnvelopeComponent(name, year, self.envelope_component[retrofit_id].area)
            self.envelope_component[retrofit_id] = retrofitted_component
            return retrofitted_component

    def retrofit_heating(self, name, year):
        retrofitted_component = HeatingSystem(name, year, self.max_heating_load)
        self.heating_system = retrofitted_component
        return retrofitted_component


class EnvelopeComponent:
    def __init__(self, name, year_of_constr, area):
        self.name = name
        self.u_value = self.look_up_heat_trans_coeff(name, year_of_constr)
        self.area = area
    
    def look_up_heat_trans_coeff(self, name, year_of_constr):
        # Rückgabe von uValue in W/m2K
        u_value = None
        
        # Definition der U-Werte für verschiedene Bauteile und Jahre
        # (...1978 1995 2009)
        u_values = {
            'windows': [3.5, 2.4, 1.8, 1.3, 0.7],
            'extWalls': [1.7, 1.3, 0.5, 0.24, 0.18],
            'roof': [2.2, 0.45, 0.3, 0.25, 0.2],
            'basement': [1.8, 0.9, 0.5, 0.35, 0.3]}
        
        # Index basierend auf dem Baujahr bestimmen
        if year_of_constr <= 1978:
            index = 0
        elif 1978 < year_of_constr <= 1995:
            index = 1
        elif 1995 < year_of_constr <= 2009:
            index = 2
        elif 2009 < year_of_constr <= 2022:
            index = 3
        else:
            index = 4
        
        u_value = u_values.get(name, [])[index]

        return u_value
    
    def get_installation_cost_euro(self):
        # Quellen: co2online.de
        # https://www.co2online.de/modernisieren-und-bauen/

        cost_table = [  # € und € pro m2
            {"type": "windows", "fixCost": 1000, "specificCost": 450},
            {"type": "extWalls", "fixCost": 5000, "specificCost": 140},
            {"type": "roof", "fixCost": 2000, "specificCost": 250},
            {"type": "basement", "fixCost": 1000, "specificCost": 40}
        ]

        cost = 0
        for item in cost_table:
            if self.name == item["type"]:
                cost = item["fixCost"] + self.area * item["specificCost"]

        return cost

class HeatingSystem:
    def __init__(self, name, year, power):
        self.name = name
        self.year = year
        self.thermal_power_kw = power

    @property
    def effort_number(self):
        return 1 / self.efficiency

    @property
    def prop_table(self):
        return [  # € pro kW
            {"type": "hp-35", "fixCost": 3000, "specificCost": 3000, "energyCost": 0.27, "eta": [3.4, 3.7, 3.9, 4.0, 4.3]},
            {"type": "hp-45", "fixCost": 3000, "specificCost": 3000, "energyCost": 0.27, "eta": [3.1, 3.3, 3.5, 3.6, 3.7]},
            {"type": "hp-55", "fixCost": 3000, "specificCost": 3000, "energyCost": 0.27, "eta": [2.7, 3.0, 3.1, 3.3, 3.4]},
            {"type": "gas-90", "fixCost": 3000, "specificCost": 100, "energyCost": 0.09, "eta": [0.72, 0.75, 0.8, 0.8, 0.8]},
            {"type": "gas-70", "fixCost": 3000, "specificCost": 100, "energyCost": 0.09, "eta": [0.82, 0.85, 0.9, 0.9, 0.9]},
            {"type": "gas-55", "fixCost": 3000, "specificCost": 100, "energyCost": 0.09, "eta": [0.88, 0.9, 0.92, 0.92, 0.92]},
            {"type": "oil", "fixCost": 3000, "specificCost": 3000, "energyCost": 0.1, "eta": [0.72, 0.75, 0.75, 0.77, 0.8]},
            {"type": "coal", "fixCost": 3000, "specificCost": 3000, "energyCost": 0.1, "eta": [0.66, 0.7, 0.72, 0.72, 0.72]}
        ]

    @property
    def installation_cost_euro(self):
        cost_table = self.prop_table
        cost = 0
        for item in cost_table:
            if self.name == item["type"]:
                cost = item["fixCost"] + self.thermal_power_kw * item["specificCost"]
                break
        return cost

    @property
    def energy_cost(self):
        cost_table = self.prop_table
        cost = 0
        for item in cost_table:
            if item["type"] == self.name:
                cost = item["energyCost"]
                break
        return cost

    @property
    def efficiency(self):
        efficiency_table = self.prop_table
        eta = 1
        for item in efficiency_table:
            if item["type"] == self.name:
                eta = item["eta"]
                break

        if self.year <= 1978:
            eta = eta[0]
        elif 1978 < self.year <= 1995:
            eta = eta[1]
        elif 1995 < self.year <= 2009:
            eta = eta[2]
        elif 2009 < self.year <= 2022:
            eta = eta[3]
        elif self.year > 2023:
            eta = eta[4]

        return eta

class CoolingSystem:
    def __init__(self, name, year):
        self.name = name
        self.year = year

    @property
    def effort_number(self):
        e = 0
        if self.name is not None:
            e = 0.28
        return e


weather_data = [
    {"month": "Jan", "temperature": 1.0, "solar_radiation": 29},
    {"month": "Feb", "temperature": 1.9, "solar_radiation": 44},
    {"month": "Mär", "temperature": 4.7, "solar_radiation": 97},
    {"month": "Apr", "temperature": 9.2, "solar_radiation": 189},
    {"month": "Mai", "temperature": 14.1, "solar_radiation": 221},
    {"month": "Jun", "temperature": 16.7, "solar_radiation": 241},
    {"month": "Jul", "temperature": 19.0, "solar_radiation": 210},
    {"month": "Aug", "temperature": 18.6, "solar_radiation": 180},
    {"month": "Sep", "temperature": 14.3, "solar_radiation": 127},
    {"month": "Okt", "temperature": 9.5, "solar_radiation": 77},
    {"month": "Nov", "temperature": 4.1, "solar_radiation": 31},
    {"month": "Dez", "temperature": 0.9, "solar_radiation": 17}
]

description_initial_condition = [
    {"qp": 30, "text": ["Ihr Gebäude erfüllt die fortschrittlichsten energetischen Standards. Glückwunsch!"]},
    {"qp": 60, "text": ["Ihr Gebäude erfüllt die aktuell geltenden Anforderungen an Neubauten. Glückwunsch!"]},
    {"qp": 90, "text": ["Ihr Gebäude erfüllt die Anforderungen an Neubauten aus dem Jahr 2002."]},
    {"qp": 130, "text": ["Die energetische Eigenschaften ihres Gebäudes sind überdurchschnittlich gut, bieten aber dennoch ein großes Einsparpotential."]},
    {"qp": 180, "text": ["Der Energieverbrauch Ihres Gebäudes ist überdurchschnittlich groß.",
                         "Eine energetische Sanierung lohnt sich in Ihrem Fall besonders, da Sie Ihre Energiekosten erheblich senken können."]},
    {"qp": 230, "text": ["Der Energieverbrauch Ihres Gebäudes ist überdurchschnittlich groß.",
                         "Eine energetische Sanierung lohnt sich in Ihrem Fall besonders, da Sie Ihre Energiekosten erheblich senken können."]},
    {"qp": 999, "text": ["Der Energieverbrauch Ihres Gebäudes ist außerordentlich groß.",
                         "Eine energetische Sanierung lohnt sich in Ihrem Fall besonders, da Sie Ihre Energiekosten erheblich senken können."]}
]


if __name__ == "__main__":
    building = Building(1990,120,2,0,3)
    res = building.calc_energy_demand(weather_data)
    for m in res:
        print(m)