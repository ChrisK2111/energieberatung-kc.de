from .energy_calculator import Building, weather_data
from . import retrofit_order, color_codes, description_initial_condition


def calc_sfp(sfp_form):
    yr = int(sfp_form['floatingInput_ConstructionYear']);
    a_nra = int(sfp_form['floatingInput_NetRoomArea'])
    if sfp_form['selection_buildingType'] == '2':
        ext_wall_count = 3;
    elif sfp_form['selection_buildingType'] == '3':
        ext_wall_count = 2;
    else:
        ext_wall_count = 4;
    floor_count = int(sfp_form['floatingInput_NumOfStories'])

    if sfp_form['selection_basement'] == '2' or sfp_form['selection_basement'] == '3':
        ug_floor_count = 1;
    else:
        ug_floor_count = 0;
    
    building = Building(yr,a_nra,floor_count,ug_floor_count,ext_wall_count)
    initial_rf_measures = get_completed_retrofit_measures(sfp_form)

    for rf in initial_rf_measures:
        building.retrofit_component(rf['type'],rf['component'], rf['year'])
    
    q_net = building.calc_energy_demand_yearly(weather_data)

    rf_data = calc_renovation(building,weather_data)
    return rf_data

def get_completed_retrofit_measures(sfp_form):

    year_of_constr  = float(sfp_form['floatingInput_ConstructionYear'])
    rf_ext_walls    = float(sfp_form['selection_extWalls'])
    rf_windows      = float(sfp_form['selection_windows'])
    rf_heat_sys     = float(sfp_form['selection_heatingSystem'])
    rf_roof         = float(sfp_form['selection_roof'])
    rf_basement     = sfp_form.get('check_basementInsulation', False)

    rf = []

    if rf_ext_walls == 2:
        rf_year = max(year_of_constr + 10, 1996)
        rf.append({
            'year': rf_year,
            '"type"': 'envelope',
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

def calc_renovation(building: Building, weather_data):

    rf_data = []

    for year in range(2024, 2046):
        rf_performed = False
        rf_cost = 0
        rf_description = ""

        for ro in retrofit_order:
            if ro['year'] == year:
                retrofitted_component = building.retrofit_component(ro['type'], ro['component'], year)
                rf_performed = True
                rf_cost += retrofitted_component.installation_cost_euro
                if len(rf_description) == 0:
                    rf_description += ro['description']
                else:
                    rf_description += (" und " + ro['description'])


        q_data = building.calc_energy_demand_yearly(weather_data)


        qh = building.calc_energy_demand_yearly(weather_data)['heating_demand']
        qc = building.calc_energy_demand_yearly(weather_data)['cooling_demand']
        energy_cost_yearly = qh * building.floor_area * building.heating_system.energy_cost

        rf_data.append({
            'primary_energy_demand': qh,
            'cooling_demand': qc,
            'heating_demand': qh,
            'energy_cost': energy_cost_yearly,
            'retrofit_cost': rf_cost,
            'retrofit_description': rf_description})

    return rf_data

def initial_cond_card(rf_data):
    demand_0 = rf_data[0]['primary_energy_demand']
    demand_0 = round(demand_0)
    energy_class = get_energy_class(rf_data[0]['primary_energy_demand'])

    for item in description_initial_condition:
            if demand_0 <= item['qp']:
                description = ' '.join(item['text'])
                break
    text= [  
        description,
        "Der rechnerische Endenergiebedarf Ihres Gebäudes beträgt " + '<span style="white-space: nowrap">' + str(demand_0) + ' kWh/(m\u00B2a). </span>',
        "Damit erfüllt Ihr saniertes Gebäude die Anforderungen der Energieeffizienzklasse <strong>" + energy_class + "</strong>.",
        ]

    return text

def final_cond_card(rf_data):
    demand_end = rf_data[-1]['primary_energy_demand']
    demand_end = round(demand_end)
    savings = round((rf_data[0]['energy_cost'] - rf_data[-1]['energy_cost'])/10)*10
    energy_class = get_energy_class(rf_data[-1]['primary_energy_demand'])

    

    text_list = [  
        "Durch eine energetische Sanierung können Sie den rechnerischen Endenergiebedarf Ihres Gebäudes auf " +
        '<span style="white-space: nowrap">' + str(demand_end) + ' kWh/(m\u00B2a) </span>' + "senken.",
        
        "Damit erfüllt Ihr saniertes Gebäude die Anforderungen der Energieeffizienzklasse <strong>" + energy_class + "</strong>.",
    
        "Gleichzeitig senken Sie Ihre Energiekosten und Sie können bis zu <strong>" +
        format_number_with_thousand_dots(savings) + " € </strong> pro Jahr einsparen."
        ]
    

    return text_list

def sfp_cards(rf_data):
    cards_data = []
    card_data = {}
    id_rf = 0;

    for rf in rf_data:
        if rf['retrofit_cost'] > 0:
            id_rf = id_rf + 1
            rgb = get_rgb_of_demand(rf['primary_energy_demand'])

            card_data = {}
            card_data['heading']      = 'Maßnahme ' + str(id_rf)
            card_data['color']        = 'rgba(' + ', '.join(map(str,rgb)) + ',0.7)'
            card_data['energy_class'] = get_energy_class(rf['primary_energy_demand'])
            card_data['text']         = rf['retrofit_description']
            card_data['energy_cost']  = format_number_with_thousand_dots(round(rf['energy_cost'] / 10) * 10) + "€/a"
            card_data['savings']      = format_number_with_thousand_dots(round((rf['energy_cost'] - prev_rf['energy_cost']) / 10) * 10) + "€/a"
            card_data['invest']       = format_number_with_thousand_dots(round(rf['retrofit_cost'] / 100) * 100) + "€"
            card_data['support']      = format_number_with_thousand_dots(round(rf['retrofit_cost'] * 0.3/100)*100) + "€"
            
            cards_data.append(card_data)
        prev_rf = rf
    
    return cards_data


def get_rgb_of_demand(demand):
    rgb_values = [200, 200, 200]
    
    # Neue RGB-Werte definieren (z.B. 255, 0, 0 für Rot)
    # lineare Interpolation zwischen zwei Werten
    for j_code in range(len(color_codes)):
        if demand <= color_codes[j_code]['qp']:
            ratio = 1
            rgb1 = color_codes[j_code]['rgb']
            rgb2 = color_codes[j_code]['rgb']
            
            if j_code != 0:
                rgb2 = color_codes[j_code - 1]['rgb']
                ratio = (demand - color_codes[j_code]['qp']) / (color_codes[j_code - 1]['qp'] - color_codes[j_code]['qp'])
            
            rgb_values = [rgb1[i] + (rgb2[i] - rgb1[i]) * ratio for i in range(3)]
            break
    
    return rgb_values

def get_energy_class(demand):
    e_class = ""
    for item in color_codes:
        if demand <= item["qp"]:
            e_class = item["class"]
            break
    return e_class


def format_number_with_thousand_dots(number):
    # Zuerst die Zahl in einen String umwandeln
    num_str = str(number)

    # Den String mit Tausenderpunkten versehen
    formatted_number = '{0:,}'.format(number).replace(',', '.')

    return formatted_number

