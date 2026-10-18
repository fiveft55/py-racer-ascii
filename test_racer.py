import unittest
from unittest.mock import Mock, patch
from racer import Race, Vehicle, render


class RaceTests(unittest.TestCase):
    def test_renderer_draws_game_and_small_terminal_notice(self):
        screen = Mock()
        screen.getmaxyx.return_value = (24, 80)
        screen.color_pair = lambda index: 0
        screen.bold = 0
        with patch('racer.time.monotonic', return_value=0):
            render(screen, Race(), False)
        drawn = ' '.join(call.args[2] for call in screen.addnstr.call_args_list)
        self.assertIn('D U S T L I N E', drawn)
        self.assertIn('W/UP gas', drawn)
        screen.refresh.assert_called_once()
        screen.reset_mock()
        screen.getmaxyx.return_value = (20, 60)
        render(screen, Race(), False)
        self.assertIn('Resize terminal', screen.addnstr.call_args.args[2])

    def test_windows_renderer_without_curses(self):
        import io
        from racer_windows import WindowsScreen
        screen = WindowsScreen()
        with patch('racer.curses', None), patch('sys.stdout', new_callable=io.StringIO) as output:
            render(screen, Race(), False)
            self.assertIn('D U S T L I N E', output.getvalue())
            self.assertIn('\x1b[', output.getvalue())

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
