from energy_calculator import building, weather_data

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
    q_net = building.calc_energy_demand_yearly(weather_data)
    return q_net