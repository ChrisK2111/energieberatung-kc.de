from .energy_calculator import Building, weather_data

def calc_sfp(sfp_form):
    yr = int(sfp_form['floatingInput_ConstructionYear']);
    a_nra = int(sfp_form['floatingInput_NetRoomArea'])
    if sfp_form['selection-buildingType'] == '2':
        ext_wall_count = 3;
    elif sfp_form['selection-buildingType'] == '3':
        ext_wall_count = 2;
    else:
        ext_wall_count = 4;
    floor_count = int(sfp_form['floatingInput_NumOfStories'])

    if sfp_form['selection-basement'] == '2' or sfp_form['selection-basement'] == '3':
        ug_floor_count = 1;
    else:
        ug_floor_count = 0;
    
    building = Building(yr,a_nra,floor_count,ug_floor_count,ext_wall_count)
    initial_rf_measures = get_completed_retrofit_measures(sfp_form)

    for rf in initial_rf_measures:
        building.retrofit_component(rf['type'],rf['component'], rf['year'])
    
    q_net = building.calc_energy_demand_yearly(weather_data)

    return q_net

def get_completed_retrofit_measures(sfp_form):
    year_of_constr  = float(sfp_form['floatingInput_ConstructionYear'])
    rf_ext_walls    = float(sfp_form['selection-extWalls'])
    rf_windows      = float(sfp_form['selection-windows'])
    rf_heat_sys     = float(sfp_form['selection-heatingSystem'])
    rf_roof         = float(sfp_form['selection-roof'])
    rf_basement     = sfp_form.get('check-basementInsulation', False)

    rf = []

    if rf_ext_walls == 2:
        rf_year = max(year_of_constr + 10, 1996)
        rf.append({
            'year': rf_year,
            'type': 'envelope',
            'component': 'extWalls',
            'description': 'Dämmung der Außenwände'
        })

    if rf_ext_walls == 3:
        rf_year = max(year_of_constr + 20, 2010)
        rf.append({
            'year': rf_year,
            'type': 'envelope',
            'component': 'extWalls',
            'description': 'Dämmung der Außenwände'
        })

    if rf_windows == 2:
        rf_year = max(year_of_constr + 10, 1996)
        rf.append({
            'year': rf_year,
            'type': 'envelope',
            'component': 'windows',
            'description': 'Fenstertausch'
        })

    if rf_windows == 3:
        rf_year = max(year_of_constr + 20, 2010)
        rf.append({
            'year': rf_year,
            'type': 'envelope',
            'component': 'windows',
            'description': 'Fenstertausch'
        })

    if rf_roof == 2:
        rf_year = max(year_of_constr + 30, 2010)
        rf.append({
            'year': rf_year,
            'type': 'envelope',
            'component': 'roof',
            'description': 'Dachdämmung und Austausch der Dachflächenfenster'
        })

    if rf_heat_sys == 2:
        rf_year = max(year_of_constr + 20, 1996)
        rf.append({
            'year': rf_year,
            'type': 'heating',
            'component': 'gas-70',
            'description': 'Einbau eines effizienten Heizkessels'
        })

    if rf_heat_sys == 3:
        rf_year = max(year_of_constr + 30, 2010)
        rf.append({
            'year': rf_year,
            'type': 'heating',
            'component': 'gas-55',
            'description': 'Einbau eines effizienten Heizkessels'
        })

    if rf_basement:
        rf_year = max(year_of_constr + 30, 2010)
        rf.append({
            'year': rf_year,
            'type': 'envelope',
            'component': 'basement',
            'description': 'Dämmung der Kellerdecke'
        })

    return rf
