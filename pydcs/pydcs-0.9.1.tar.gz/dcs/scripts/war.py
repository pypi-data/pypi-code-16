import sys
import dcs
import dcs.mission
import dcs.task
import dcs.mapping
import dcs.point
from dcs.mapping import Point, Polygon
import dcs.terrain
import dcs.unittype
import dcs.vehicles
import dcs.coalition
from dcs.countries import USA, Russia
import random
import datetime
import argparse
import os

red_control = Polygon([Point(-265942.85714286, 603885.71428571), Point(-233257.14285714, 632685.71428571),
                       Point(-175257.14285714, 642257.14285714), Point(-194257.14285714, 881257.14285715),
                       Point(-45114.285714285, 856971.42857143), Point(55457.142857144, 265257.14285715),
                       Point(-56542.857142856, 266114.28571429)])


def T72_brigade(mission, country, position, heading, name, skill=dcs.unit.Skill.Average):
    units = [dcs.vehicles.Armor.MBT_T_72B, dcs.vehicles.Armor.MBT_T_72B, dcs.vehicles.Armor.MBT_T_72B,
             dcs.vehicles.Armor.MBT_T_72B, dcs.vehicles.Armor.MBT_T_72B, dcs.vehicles.Armor.MBT_T_72B,
             dcs.vehicles.Armor.IFV_BMP_2, dcs.vehicles.Armor.IFV_BMP_2, dcs.vehicles.AirDefence.SPAAA_ZSU_23_4_Shilka,
             dcs.vehicles.AirDefence.SAM_SA_13_Strela_10M3_9A35M3, dcs.vehicles.Unarmed.Transport_Ural_4320_31_Armored]
    vg = mission.vehicle_group_platoon(
        country, name, units, position, heading)

    vg.formation_scattered(random.randint(0, 360))

    for u in vg.units:
        u.skill = skill

    return vg


def military_base(mission, country, position, name):
    base = []
    base.append(mission.static_group(country, name + " Command Center", dcs.statics.Fortification.Command_Center,
                                     position, 270))
    base.append(mission.static_group(country, name + " Ammo", dcs.statics.Fortification.FARP_Ammo_Storage,
                                     position.point_from_heading(0, 180)))
    base.append(mission.static_group(country, name + " Barracks 1", dcs.statics.Fortification.Barracks_2,
                position.point_from_heading(45, 50), 180))
    base.append(mission.static_group(country, name + " Barracks 2", dcs.statics.Fortification.Barracks_2,
                base[-1].position.point_from_heading(0, 20), 180))
    base.append(mission.static_group(country, name + " Barracks 3", dcs.statics.Fortification.Barracks_2,
                base[-1].position.point_from_heading(0, 20), 180))
    base.append(mission.static_group(country, name + " Barracks 4", dcs.statics.Fortification.Barracks_2,
                base[-1].position.point_from_heading(0, 20), 180))
    base.append(mission.static_group(country, name + " Barracks 5", dcs.statics.Fortification.Barracks_2,
                base[-1].position.point_from_heading(0, 20), 180))

    base.append(mission.static_group(country, name + " Bunker", dcs.statics.Fortification.Bunker,
                position.point_from_heading(315, 50), 270))
    base.append(mission.static_group(country, name + " Fuel depot", dcs.statics.Fortification.FARP_Fuel_Depot,
                base[-1].position.point_from_heading(0, 20), 270))
    base.append(mission.static_group(country, name + " Garage", dcs.statics.Fortification.Garage_A,
                base[-1].position.point_from_heading(0, 30)))
    base.append(mission.static_group(country, name + " Generator", dcs.statics.Fortification.GeneratorF,
                base[-1].position.point_from_heading(0, 20)))
    base.append(mission.static_group(country, name + " Cargo 1", dcs.statics.Cargo.ammo_cargo,
                base[-1].position.point_from_heading(0, 10)))
    base.append(mission.static_group(country, name + " Cargo 2", dcs.statics.Cargo.ammo_cargo,
                base[-1].position.point_from_heading(0, 10)))
    base.append(mission.static_group(country, name + " Cargo 3", dcs.statics.Cargo.iso_container,
                base[-1].position.point_from_heading(0, 10)))

    base.append(mission.static_group(country, name + " watch tower 1", dcs.statics.Fortification.TowerArmed,
                                     position.point_from_heading(90, 80)))
    base.append(mission.static_group(country, name + " watch tower 2", dcs.statics.Fortification.TowerArmed,
                                     base[-1].position.point_from_heading(0, 200)))
    base.append(mission.static_group(country, name + " watch tower 3", dcs.statics.Fortification.TowerArmed,
                                     position.point_from_heading(270, 80)))
    base.append(mission.static_group(country, name + " watch tower 4", dcs.statics.Fortification.TowerArmed,
                                     base[-1].position.point_from_heading(0, 200)))

    return base


class Campaign:

    def __init__(self):
        self.startdate = datetime.datetime(2017, 5, 24, 9, 12, 0)
        self.time = 0
        self.d = {}
        self.baric_system = dcs.weather.Weather.BaricSystem.AntiCyclone

    def scan_mission(self, m: dcs.mission.Mission):
        self.d = {"red": {"planes": []}, "blue": {"planes": []}}

        for col in m.coalition:
            for cn in m.coalition[col].countries:
                c = m.country(cn)
                to_remove = []
                for pg in c.plane_group:
                    d = {
                        "name": str(pg.name),
                        "airport": pg.airport_id(),
                        "country": c.id,
                        "processed": False,
                        "units": []
                    }

                    for u in pg.units:
                        ud = {
                            "name": str(u.name),
                            "x": u.position.x,
                            "y": u.position.y,
                            "alt": u.alt,
                            "type": u.type,
                            "skill": u.skill.value
                        }
                        if d["airport"]:
                            ud["parking"] = u.parking
                        d["units"].append(ud)
                    self.d[col]["planes"].append(d)
                    to_remove.append(pg)

                for pg in to_remove:
                    m.remove_plane_group(pg)

    @staticmethod
    def is_awacs(type_id):
        return dcs.planes.plane_map[type_id].category == "AWACS"

    def setup_awacs(self, m: dcs.mission.Mission):

        for coln in self.d:
            col = self.d[coln]
            awacs = None
            for pg in col["planes"]:
                if Campaign.is_awacs(pg["units"][0]["type"]):
                    airport = m.terrain.airport_by_id(pg["airport"])
                    counter_airport = m.terrain.nearest_airport(airport.position, "blue" if coln == 'red' else "red")
                    heading = airport.position.heading_between_point(counter_airport.position)
                    awacs = m.awacs_flight(
                        m.country_by_id(pg["country"]),
                        pg["name"],
                        dcs.planes.plane_map[pg["units"][0]["type"]],
                        airport,
                        airport.position.point_from_heading(heading + 180, 30 * 1000),
                        80 * 1000,
                        270)
                    awacs.units[0].name = m.string(pg["units"][0]["name"])
                    pg["processed"] = True
                    break

            if awacs:
                for pg in col["planes"]:
                    if pg["name"].lower().startswith("escort"):
                        airport = m.terrain.airport_by_id(pg["airport"])
                        m.escort_flight(
                            m.country_by_id(pg["country"]),
                            pg["name"],
                            dcs.planes.plane_map[pg["units"][0]["type"]],
                            airport,
                            awacs,
                            group_size=len(pg["units"]))
                        pg["processed"] = True
                        break

    def setup_flights(self, m: dcs.mission.Mission):

        self.setup_awacs(m)
        russia = m.country("Russia")

        # cas flights
        cas = []
        for coln in self.d:
            col = self.d[coln]
            for pg in col["planes"]:
                _type = dcs.planes.plane_map[pg["units"][0]["type"]]
                if _type.task_default == dcs.task.CAS:
                    print(pg)
                    airport = m.terrain.airport_by_id(pg["airport"])
                    cas.append(m.strike_flight(
                        m.country_by_id(pg["country"]),
                        pg["name"],
                        _type,
                        random.choice(russia.vehicle_group_within(airport.position, 100 * 1000)),
                        airport))
                    for i in range(0, len(pg["units"])):
                        cas[-1].units[i].parking = pg["units"][i]["parking"]
                        cas[-1].units[i].parking_id = "30"
                        cas[-1].units[i].skill = dcs.unit.Skill(pg["units"][i]["skill"])
                        print(cas[-1].units[i])
                    pg["processed"] = True


        # place remaining flights
        for col in self.d:
            col = self.d[col]
            for pg in [x for x in col["planes"] if not x["processed"]]:
                print("REM", pg)
                if pg["airport"]:
                    airport = m.terrain.airport_by_id(pg["airport"])
                    f = m.flight_group_from_airport(
                        m.country_by_id(pg["country"]),
                        pg["name"],
                        dcs.planes.plane_map[pg["units"][0]["type"]],
                        airport, group_size=len(pg["units"]))
                    f.uncontrolled = True
                    for i in range(0, len(pg["units"])):
                        f.units[i].parking = pg["units"][i]["parking"]
                        f.units[i].name = m.string(pg["units"][i]["name"])

                    pg["processed"] = True

    def setup_mission(self, m: dcs.mission.Mission):
        m.start_time = self.startdate + datetime.timedelta(seconds=self.time)
        m.weather.dynamic_weather(self.baric_system, 2)
        self.setup_flights(m)


def main():
    m = dcs.mission.Mission()

    m.load_file("C:\\Users\\peint\\Saved Games\\DCS\\Missions\\dcscs_setup\\warehouse.miz")

    city_graph = m.terrain.city_graph
    russia = m.coalition["red"].country("Russia")
    usa = m.coalition["blue"].country("USA")

    c = Campaign()
    c.scan_mission(m)
    redspawns = [z for z in m.triggers.zones() if z.name.startswith("red spawn")]
    print(redspawns)

    for spawn in redspawns:
        vg = T72_brigade(m, russia, spawn.position, 0, spawn.name)
        near_node = city_graph.nearest_node(spawn.position)
        vg.add_waypoint(near_node.position, dcs.point.PointAction.OnRoad)
        city_graph.travel(vg, near_node, city_graph.node("Zugidi"))
        #vg.add_waypoint(city_graph.node("Zugidi").position, dcs.point.PointAction.OnRoad)

    m.triggers.clear()

    remove = []
    for s in russia.static_group:
        if s.units[0].type == dcs.statics.Fortification.Mark_Flag_Red.id:
            military_base(m, russia, s.position, str(s.name))
            remove.append(s)

    for s in remove:
        russia.remove_static_group(s)

    for n in city_graph.rated_nodes_within(red_control, 60):
        r = random.random()
        if r > 0.9:
            dcs.templates.VehicleTemplate.sa11_site(m, russia, n.position, random.randint(0, 360), n.name)
        elif r > 0.8:
            dcs.templates.VehicleTemplate.sa15_site(m, russia, n.position, random.randint(0, 360), n.name)
        else:
            m.vehicle_group(
                russia,
                n.name + " def",
                dcs.vehicles.AirDefence.AAA_ZU_23_on_Ural_375,
                n.position.random_point_within(40, 20),
                random.randint(0, 360),
                2)

    print(city_graph.node("Sochi Airport"))
    print(m.terrain.sukhumi().name)

    zone = m.triggers.add_triggerzone(dcs.mapping.Point(-247248, 618130), 5000, False, "intercept trigger")

    ig = m.intercept_flight(russia, "fuck of", dcs.planes.Su_30, m.terrain.gudauta(), zone)

    sead = m.sead_flight(m.country("USA"), "aa down", dcs.planes.F_16C_bl_52d, zone.position, m.terrain.kutaisi(),
                         dcs.mission.StartType.Runway, group_size=2)

    hs = m.strike_flight(m.country("USA"), "heli strike", dcs.helicopters.AH_64A,
                         random.choice(russia.vehicle_group_within(m.terrain.senaki().position, 100 * 1000)),
                         m.terrain.senaki())
    hs.delay_start(m, 60)

    c.setup_mission(m)
    # awacs = m.awacs_flight(
    #     usa,
    #     "AWACS",
    #     plane_type=dcs.planes.E_3A,
    #     airport=m.terrain.vaziani(),
    #     position=m.terrain.vaziani().position.point_from_heading(200, 30 * 1000),
    #     race_distance=80 * 1000, heading=270,
    #     altitude=random.randrange(4000, 5500, 100), frequency=140)
    #
    # ef = m.escort_flight(usa, "AWACS Escort", dcs.countries.USA.Plane.M_2000C, m.terrain.vaziani(), awacs, group_size=2)
    # ef.delay_start(m, 180)


    m.save("C:\\Users\\peint\\Saved Games\\DCS\\Missions\\fun.miz")
    return 0


if __name__ == '__main__':
    sys.exit(main())
