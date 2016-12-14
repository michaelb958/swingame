import swingame as sg

if __name__ == '__main__':
    sg.open_graphics_window('Hello World', 800, 600)
    sg.show_swin_game_splash_screen()
    while not sg.primary_window_close_requested():
        sg.process_events()
        sg.clear_screen_to(color_white())
        sg.draw_framerate_with_simple_font(0, 0)
        sg.refresh_screen_restrict_fps(60)
