import flet as ft
import time
import socket
import bluetooth
import serial


def main(page):
    br=ft.Text("\n")
    page.window_width=390
    page.window_height=800
    page.bgcolor = "#EDEAE0"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.title = "RGB Led Strip App"
    address = None

    image = ft.Image(
        src="./assets/Logo.png",
        width=170,
        height=170,
        fit=ft.ImageFit.CONTAIN,
        rotate=ft.transform.Rotate(0, alignment=ft.alignment.center),
        animate_rotation=ft.animation.Animation(300, ft.AnimationCurve.BOUNCE_OUT),
    )
    welcome = ft.Text("Welcome!", 
                      size = 20, 
                      weight=ft.FontWeight.BOLD, 
                      font_family="Segoe UI",
                      color='#000000'
                      )
    connectingDevice = ft.Text("Let's start by connecting you to a device.\n\n", 
                               size=17, 
                               weight=ft.FontWeight.BOLD, 
                               font_family="Segoe UI",
                               color='#000000',
                               text_align='center'
                               )
    availableDevices = ft.Text("Available Devices:", 
                               size = 16,
                               color='#000000',
                               weight=ft.FontWeight.BOLD,
                               )
    devices = ft.Container(
        width=310, 
        height=244, 
        border_radius= 42, 
        bgcolor='#EDEAE0',
        margin=10,
        content=ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=True)
        )
    
    def connectToDevice(addr):
        page.clean()
        time.sleep(1)
        page.add(
            br,
            image, 
            ft.Text("\n\nAdjust the sliders to change the color:", color='#000000', weight=ft.FontWeight.BOLD,),
            ft.Row([ft.Text("R:", color='#000000', weight=ft.FontWeight.BOLD,), red_slider]),
            ft.Row([ft.Text("G:", color='#000000', weight=ft.FontWeight.BOLD,), green_slider]),
            ft.Row([ft.Text("B:", color='#000000', weight=ft.FontWeight.BOLD,), blue_slider]),
            color_display,
            color_code
        )
        nonlocal address
        address = addr


    def getnearbydevices(e):
        page.splash = ft.ProgressBar()
        devices.content.controls.clear()
        page.update()
        nearby_devices = bluetooth.discover_devices(lookup_names=True, duration=4)
        for bdaddr, name in nearby_devices:
            devices.content.controls.append(ft.ElevatedButton("  {} - {}".format(bdaddr, name), 
                                                              on_click=lambda e, 
                                                              addr=bdaddr: connectToDevice(addr),
                                                              color='#000000',
                                                              bgcolor='#0264A3'
                                                              ))
        page.splash = None
        page.update()
    
    buttonS = ft.Container(
        content=ft.Text("Search for devices",
                        size=18,
                        color='#000000',    
            weight=ft.FontWeight.BOLD,
            font_family="Segoe UI"),
        bgcolor='#0264A3',
        width=243, 
        height=58, 
        border_radius= 74,
        alignment=ft.alignment.center,
        on_click=getnearbydevices,
        ink=True
        )

    def slider_to_hex(value): # Format the value as a two-digit hex number
        return f"{int(value):02X}"

    def update_color(e): # Getting values from the sliders
        r_hex = slider_to_hex(red_slider.value)
        g_hex = slider_to_hex(green_slider.value)
        b_hex = slider_to_hex(blue_slider.value)
        
        hex_color = f"0x{r_hex}{g_hex}{b_hex}" # Combining the values to form a full hex color code
        print(hex_color)
        nonlocal address
        connection = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        try:
            connection.connect((address, 1))
            connection.send(hex_color.encode('utf-8'))

        except Exception as e:
            print(f"Error: {e}")

        
        # Updating the color display and the text field
        color_display.bgcolor = hex_color
        color_display.update()
        color_code.value = hex_color
        color_code.update()

    red_slider = ft.Slider(value=0, min=0, max=255, divisions=255, on_change=update_color, thumb_color="#FFFFFF", active_color="#FF0000", inactive_color="#FF0000", width=320)
    green_slider = ft.Slider(value=0, min=0, max=255, divisions=255, on_change=update_color, thumb_color="#FFFFFF", active_color="#00FF00", inactive_color="#00FF00", width=320)
    blue_slider = ft.Slider(value=0, min=0, max=255, divisions=255, on_change=update_color, thumb_color="#FFFFFF", active_color="#0000FF", inactive_color="#0000FF", width=320)
    
    color_code = ft.TextField(value="#000000", width=100, text_align=ft.TextAlign.CENTER, color='#000000') # Text field to display the resulting hex color
    color_display = ft.Container(height=100, width=100, bgcolor="#000000")  # Container to display the color

    page.add(br,image, welcome, connectingDevice, availableDevices, devices, buttonS)
    
    
ft.app(target=main)