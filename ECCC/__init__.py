import os, sys, math

APP_DIR = "/system/apps/ECCC"

sys.path.insert(0, APP_DIR)
os.chdir(APP_DIR)

from badgeware import set_case_led

big_font = pixel_font.load("/system/assets/fonts/ignore.ppf")
pattern_font = rom_font.ignore
pattern = image(128, 128)
pattern.font = pattern_font
pattern_text = "2026"
bg_pattern = brush.pattern(color.rgb(90, 90, 90, 80), color.rgb(0, 0, 0, 0), 11)
spotlight_img = image.load("eccc2.png")
spotlight_img.alpha = int(255 * 0.3)

leds_enabled = True
spotlight_enabled = True
cycle_words = True


def update():
  global leds_enabled, spotlight_enabled, cycle_words

  if io.BUTTON_A in io.pressed:
    leds_enabled = not leds_enabled
  if io.BUTTON_B in io.pressed:
    spotlight_enabled = not spotlight_enabled
  if io.BUTTON_C in io.pressed:
    cycle_words = not cycle_words

  screen.pen = color.rgb(0, 20, 0)
  screen.clear()
  screen.pen = bg_pattern
  screen.rectangle(0, 0, screen.width, screen.height)

  # Year texture (rotated)
  pattern.antialias = image.X2
  pattern.pen = color.rgb(0, 0, 0, 0)
  pattern.clear()
  pattern.pen = color.rgb(128, 128, 128)

  text_w, text_h = pattern.measure_text(pattern_text)
  min_pad = 4
  min_step_x = int(text_w) + min_pad
  min_step_y = int(text_h) + min_pad
  cols = max(1, int(pattern.width / min_step_x))
  rows = max(1, int(pattern.height / min_step_y))
  step_x = max(min_step_x, int(pattern.width / cols))
  step_y = max(min_step_y, int(pattern.height / rows))
  for y in range(-step_y, pattern.height + step_y, step_y):
    for x in range(-step_x, pattern.width + step_x, step_x):
      pattern.text(pattern_text, x, y)

  screen.pen = brush.image(pattern, mat3().scale(1.2).rotate(-20))

  if spotlight_enabled:
    t_move = io.ticks / 600
    cx = screen.width / 2
    cy = screen.height / 2
    amp_x = screen.width * 0.35
    amp_y = screen.height * 0.35
    spot_x = cx + math.sin(t_move) * amp_x
    spot_y = cy + math.sin(t_move * 2) * amp_y
    spot_w = spotlight_img.width * 2
    spot_h = spotlight_img.height * 2
    screen.blit(
      spotlight_img,
      rect(int(spot_x - spot_w / 2), int(spot_y - spot_h / 2), int(spot_w), int(spot_h)),
    )

  # Main text (first letters always visible, one word active)
  screen.font = big_font
  lines = ["EMERALD", "CITY", "COMIC", "CONVENTION"]
  _, line_h = screen.measure_text(lines[0])
  line_gap = 2
  total_h = line_h * len(lines) + line_gap * (len(lines) - 1)
  start_y = int((screen.height - total_h) / 2)

  target_w = int(screen.width * 0.88)
  phase = io.ticks / 200
  r = int((math.sin(phase) + 1) * 127.5)
  g = int((math.sin(phase + 2.094) + 1) * 127.5)
  b = int((math.sin(phase + 4.188) + 1) * 127.5)

  def draw_line(text, y, x, cell_w, spacing, show_full):
    char_widths = [screen.measure_text(ch)[0] for ch in text]

    cursor_x = x
    for i, (ch, ch_w) in enumerate(zip(text, char_widths)):
      if not show_full and i > 0:
        cursor_x += cell_w + spacing
        continue
      ch_x = int(cursor_x + (cell_w - ch_w) / 2)
      screen.pen = color.rgb(0, 0, 0, 220)
      screen.text(ch, ch_x + 3, y + 3)
      if i == 0:
        screen.pen = color.rgb(r, g, b)
      else:
        screen.pen = color.rgb(240, 240, 240)
      screen.text(ch, ch_x, y)
      cursor_x += cell_w + spacing

  max_cell_w = 0
  max_len = 0
  for line in lines:
    if len(line) > max_len:
      max_len = len(line)
    if line:
      w = max(screen.measure_text(ch)[0] for ch in line)
      if w > max_cell_w:
        max_cell_w = w

  spacing = int(max(2, (target_w - max_cell_w * max_len)) / max(1, (max_len - 1)))
  total_w = (max_cell_w * max_len + spacing * (max_len - 1)) if max_len else 0
  left_x = int((screen.width - total_w) / 2)
  active_index = int(io.ticks / 500) % 4
  for i, line in enumerate(lines):
    show_full = True if not cycle_words else i == active_index
    draw_line(line, start_y + i * (line_h + line_gap), left_x, max_cell_w, spacing, show_full)

  # Reverse LED chase
  if leds_enabled:
    led_index = (3 - (int(io.ticks / 500) % 4) + 2) % 4
    for led in range(4):
      set_case_led(led, 1 if led == led_index else 0)
  else:
    for led in range(4):
      set_case_led(led, 0)


def on_exit():
  pass


if __name__ == "__main__":
  run(update)
