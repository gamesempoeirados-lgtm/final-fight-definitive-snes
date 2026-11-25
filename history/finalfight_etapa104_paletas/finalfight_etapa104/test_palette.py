import unittest
from cps1_palette import cps1_rgb, rgb_to_bgr555, decode_words

class TestPalette(unittest.TestCase):
    def test_black(self): self.assertEqual(cps1_rgb(0xF000), (0,0,0))
    def test_white(self): self.assertEqual(cps1_rgb(0xFFFF), (255,255,255))
    def test_brightness(self): self.assertEqual(cps1_rgb(0x0FFF), (85,85,85))
    def test_primary(self): self.assertEqual(cps1_rgb(0xFF00), (255,0,0))
    def test_snes_red(self): self.assertEqual(rgb_to_bgr555((255,0,0)), 0x001f)
    def test_snes_blue(self): self.assertEqual(rgb_to_bgr555((0,0,255)), 0x7c00)
    def test_snes_white(self): self.assertEqual(rgb_to_bgr555((255,255,255)), 0x7fff)
    def test_endianness(self): self.assertEqual(decode_words(bytes.fromhex('ff00'))[0]['rgb888'], [255,0,0])
    def test_little_endian(self): self.assertEqual(decode_words(bytes.fromhex('00ff'), byteorder='little')[0]['rgb888'], [255,0,0])
    def test_odd_length(self):
        with self.assertRaises(ValueError): decode_words(b'\x00')
    def test_bad_word(self):
        with self.assertRaises(ValueError): cps1_rgb(-1)

if __name__ == '__main__': unittest.main()
