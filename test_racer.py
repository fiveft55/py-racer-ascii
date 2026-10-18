import unittest
from racer import Race, Vehicle


class RaceTests(unittest.TestCase):
    def test_course_is_reproducible_and_varies(self):
        self.assertEqual(Race(12).road(500), Race(12).road(500))
        self.assertNotEqual(Race(12).road(500), Race(13).road(500))
        self.assertNotEqual(Race().biome(0), Race().biome(900))

    def test_acceleration_braking_and_generation(self):
        race = Race()
        for _ in range(40):
            race.update(.1, throttle=True)
        self.assertGreater(race.distance, 0)
        self.assertEqual(race.speed, 70)
        self.assertTrue(race.vehicles)
        race.update(.1, brake=True)
        self.assertLess(race.speed, 70)

    def test_collision_and_offroad_damage(self):
        race = Race()
        race.vehicles = [Vehicle(0, 0, 0)]
        race.update(.1)
        self.assertEqual(race.health, 77)
        race.lane = 1.2
        race.update(.1)
        self.assertLess(race.health, 77)

    def test_directional_combat(self):
        race = Race()
        race.vehicles = [Vehicle(8, .4, 0, True)]
        race.update(.1, punch=-1)
        self.assertEqual(race.hits, 0)
        race.update(.1, punch=1)
        self.assertEqual(race.hits, 1)
        self.assertTrue(all(v.distance > 14 for v in race.vehicles))

    def test_finish_and_wreck_stop_simulation(self):
        for health, distance in ((0, 0), (100, Race.finish)):
            race = Race()
            race.health, race.distance = health, distance
            race.update(.1, throttle=True)
            self.assertTrue(race.done)
            self.assertEqual(race.distance, distance)


if __name__ == '__main__':
    unittest.main()
