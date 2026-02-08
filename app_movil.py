import flet as ft
import requests
import time
import threading

# --- CONFIGURACIÓN NGROK (Tu dirección mundial) ---
DOMINIO_NGROK = 'https://app-ganar-dinero.onrender.com'
API_BASE = f'{DOMINIO_NGROK}/api'
URL_SUBIDA = f'{DOMINIO_NGROK}/subir/' 

def main(page: ft.Page):
    page.title = "App V17 - Referidos"
    page.bgcolor = "#f0f2f5"
    page.padding = 0 
    
    usuario_id = None
    nombre_usuario = "" # Este será tu código de referido
    saldo_actual = 0.0

    # --- UI Elements ---
    txt_saldo_header = ft.Text("$0.000", size=24, weight="bold", color="white")
    columna_tareas = ft.Column(spacing=15, scroll="auto", expand=True)
    contenedor_billetera = ft.Column(horizontal_alignment="center", spacing=20)
    input_paypal = ft.TextField(label="Tu Correo de PayPal", width=280, icon=ft.icons.EMAIL)

    def mostrar_alerta(mensaje, color="green"):
        page.snack_bar = ft.SnackBar(ft.Text(mensaje[:100]), bgcolor=color)
        page.snack_bar.open = True
        page.update()

    def obtener_estilo(nombre):
        n = nombre.lower()
        if 'youtube' in n: return ft.icons.SMART_DISPLAY, ft.colors.RED
        if 'facebook' in n: return ft.icons.FACEBOOK, ft.colors.BLUE
        if 'instagram' in n: return ft.icons.CAMERA_ALT, ft.colors.PINK
        if 'tiktok' in n: return ft.icons.MUSIC_NOTE, ft.colors.BLACK
        if 'like' in n: return ft.icons.THUMB_UP, ft.colors.BLUE_400
        if 'anuncio' in n: return ft.icons.FLASH_ON, ft.colors.AMBER
        return ft.icons.WORK, ft.colors.GREY_700

    # --- LOGICA REFERIDOS ---
    def mostrar_mi_codigo(e):
        # Muestra un diálogo con tu código para copiar
        dlg = ft.AlertDialog(
            title=ft.Text("¡Gana Dinero Invitando! 💸"),
            content=ft.Column([
                ft.Text("Comparte tu código con tus amigos."),
                ft.Text("Si se registran usándolo, tú ganas $0.10"),
                ft.Divider(),
                ft.Text(f"TU CÓDIGO: {nombre_usuario}", size=30, weight="bold", color="blue", text_align="center"),
                ft.Text("(Es tu mismo nombre de usuario)", size=12, color="grey")
            ], height=150, alignment="center"),
            actions=[ft.TextButton("Cerrar", on_click=lambda _: page.close_dialog())],
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    # --- BILLETERA ---
    def procesar_retiro(e):
        nonlocal saldo_actual
        if not input_paypal.value: mostrar_alerta("¡Escribe tu correo!", "red"); return
        if saldo_actual < 1.00: mostrar_alerta("Mínimo $1.00", "red"); return
        try:
            e.control.disabled = True; e.control.text = "Enviando..."; page.update()
            res = requests.post(f'{API_BASE}/solicitar_retiro/', json={'usuario_id': usuario_id, 'monto': saldo_actual, 'metodo': 'PayPal', 'cuenta': input_paypal.value})
            if res.status_code == 200:
                saldo_actual = float(res.json().get('nuevo_saldo', 0))
                actualizar_ui_billetera(); txt_saldo_header.value = f"${saldo_actual:.3f}"
                mostrar_alerta("¡Solicitud enviada!")
            else: mostrar_alerta("Error al retirar", "red")
            e.control.disabled = False; e.control.text = "SOLICITAR PAGO"; page.update()
        except: mostrar_alerta("Error de conexión", "red"); e.control.disabled = False; page.update()

    def actualizar_ui_billetera():
        contenedor_billetera.controls.clear()
        puede = saldo_actual >= 1.00
        
        # Botón de Referidos
        btn_invitar = ft.Container(
            content=ft.Row([ft.Icon(ft.icons.PEOPLE, color="white"), ft.Text("INVITAR AMIGOS (Gana $0.10)", color="white", weight="bold")], alignment="center"),
            bgcolor="#8b5cf6", padding=15, border_radius=10, on_click=mostrar_mi_codigo
        )

        tarjeta_retiro = ft.Container(
            content=ft.Column([
                ft.Icon(ft.icons.PAYMENT, size=50, color="#003087"),
                ft.Text(f"${saldo_actual:.3f}", size=40, weight="bold"),
                ft.Divider(),
                input_paypal,
                ft.ElevatedButton("RETIRAR A PAYPAL", bgcolor="#003087" if puede else "grey", color="white", width=280, disabled=not puede, on_click=procesar_retiro)
            ], horizontal_alignment="center"),
            bgcolor="white", padding=20, border_radius=20, shadow=ft.BoxShadow(blur_radius=10, color="grey")
        )
        contenedor_billetera.controls.extend([btn_invitar, ft.Container(height=20), tarjeta_retiro])
        page.update()

    # --- TAREAS ---
    def cargar_datos(e=None):
        nonlocal saldo_actual
        if e: e.control.text = "..."; page.update()
        try:
            res_p = requests.get(f'{API_BASE}/perfiles/'); res_h = requests.get(f'{API_BASE}/pruebas/'); res_t = requests.get(f'{API_BASE}/tareas/')
            if res_p.status_code == 200:
                for p in res_p.json():
                    if p['usuario'] == usuario_id: saldo_actual = float(p['saldo']); txt_saldo_header.value = f"${saldo_actual:.3f}"
            mis_pruebas = []
            if res_h.status_code == 200: mis_pruebas = [p['tarea'] for p in res_h.json() if p['trabajador'] == usuario_id]
            columna_tareas.controls.clear()
            columna_tareas.controls.append(ft.Container(content=ft.ElevatedButton("🔄 ACTUALIZAR", on_click=cargar_datos, bgcolor="#2196F3", color="white"), alignment=ft.alignment.center))
            
            if res_t.status_code == 200:
                for t in res_t.json():
                    icon, color = obtener_estilo(t['tipo'])
                    hecha = t['id'] in mis_pruebas
                    if hecha:
                        content = [ft.Row([ft.Icon(ft.icons.CHECK, color="green"), ft.Text("COMPLETADA", color="green", weight="bold")])]
                        bg = "#dcfce7"
                    else:
                        bg = "white"
                        if t.get('modo') == 'TIMER':
                            btn_cobrar = ft.ElevatedButton("Bloqueado", disabled=True, on_click=lambda e, tid=t['id']: cobrar_auto(e, tid))
                            btn_ver = ft.ElevatedButton("▶️ Ver", url=t['url_objetivo'], bgcolor="blue", color="white", on_click=lambda e, s=t.get('segundos_espera',10), b=btn_cobrar: iniciar_timer(e, s, b))
                            content = [ft.Text("⏳ AUTOMÁTICA", color="orange"), ft.Row([btn_ver, btn_cobrar])]
                        else:
                            url = f"{URL_SUBIDA}?usuario_id={usuario_id}&tarea_id={t['id']}"
                            content = [ft.Row([ft.ElevatedButton("Ir", url=t['url_objetivo'], bgcolor="blue", color="white"), ft.ElevatedButton("Subir", on_click=lambda _, u=url: page.launch_url(u), bgcolor="orange", color="white")])]
                    
                    card = ft.Container(content=ft.Column([
                        ft.Row([ft.Icon(icon, color=color), ft.Text(t['tipo'].upper(), weight="bold", expand=True), ft.Container(ft.Text(f"${t['pago_por_accion']}", color="white"), bgcolor="green", padding=5, border_radius=5)]),
                        ft.Divider(height=1), *content
                    ]), bgcolor=bg, padding=10, border_radius=10, border=ft.border.all(1, "green" if hecha else "transparent"))
                    columna_tareas.controls.append(card)
            actualizar_ui_billetera()
        except: pass
        if e: e.control.text = "🔄 ACTUALIZAR"; page.update()

    def iniciar_timer(e, s, btn):
        def run(): time.sleep(s); btn.disabled=False; btn.bgcolor="green"; btn.text="RECLAMAR"; page.update()
        threading.Thread(target=run).start()
    def cobrar_auto(e, tid):
        requests.post(f'{API_BASE}/reclamar_auto/', json={'usuario_id': usuario_id, 'tarea_id': tid}); cargar_datos()

    # --- PANTALLAS ---
    def cambiar_tab(e):
        idx = e.control.selected_index; page.clean()
        if idx == 0: page.add(pantalla_misiones); cargar_datos()
        else: page.add(pantalla_billetera); actualizar_ui_billetera()
        page.add(navegacion); page.update()

    navegacion = ft.NavigationBar(destinations=[ft.NavigationDestination(icon=ft.icons.HOME, label="Misiones"), ft.NavigationDestination(icon=ft.icons.WALLET, label="Billetera")], on_change=cambiar_tab)
    pantalla_misiones = ft.Column([ft.Container(content=ft.Row([ft.Text(f"Hola, {nombre_usuario}", color="white", size=20, weight="bold"), txt_saldo_header], alignment="spaceBetween"), bgcolor="#2563eb", padding=20), ft.Container(columna_tareas, padding=10, expand=True)], expand=True)
    pantalla_billetera = ft.Column([ft.Container(height=30), ft.Text("MI BILLETERA", size=24, weight="bold"), contenedor_billetera], horizontal_alignment="center", expand=True)

    # --- LOGIN / REGISTRO ---
    u_in = ft.TextField(label="Usuario"); p_in = ft.TextField(label="Clave", password=True)
    r_u = ft.TextField(label="Nuevo Usuario"); r_p = ft.TextField(label="Nueva Clave", password=True)
    r_c = ft.TextField(label="Código de Invitado (Opcional)", icon=ft.icons.QR_CODE, hint_text="Ej: marlon") # <--- CAMPO NUEVO

    def login(e):
        e.control.text = "Entrando..."
        e.control.disabled = True
        page.update()
        
        try:
            res = requests.post(f'{API_BASE}/login/', json={'username': u_in.value, 'password': p_in.value})
            
            if res.status_code == 200:
                data = res.json()
                nonlocal usuario_id, nombre_usuario
                usuario_id = data['id']
                nombre_usuario = data['nombre']
                page.clean()
                page.add(pantalla_misiones, navegacion)
                cargar_datos()
            else:
                # AQUI ESTA LA MEJORA: Leemos el error real del servidor
                try:
                    mensaje_error = res.json().get('error', 'Error desconocido')
                except:
                    mensaje_error = f"Error del Servidor ({res.status_code})"
                mostrar_alerta(f"FALLO: {mensaje_error}", "red")
                
        except Exception as ex:
            mostrar_alerta(f"Error de Conexión: {ex}", "red")
            
        e.control.text = "ENTRAR"
        e.control.disabled = False
        page.update()

    def registro(e):
        try:
            res = requests.post(f'{API_BASE}/registro/', json={'username': r_u.value, 'password': r_p.value, 'codigo_invitacion': r_c.value})
            if res.status_code == 200: mostrar_alerta("¡Creado! Entra ahora."); ir_login(None)
            else: mostrar_alerta(f"Error: {res.json().get('error')}", "red")
        except: mostrar_alerta("Error conexión", "red")

    def ir_reg(e): page.clean(); page.add(ft.Column([ft.Text("REGISTRO", size=30), r_u, r_p, r_c, ft.ElevatedButton("CREAR CUENTA", on_click=registro), ft.TextButton("Volver", on_click=ir_login)], alignment="center"))
    def ir_login(e): page.clean(); page.add(ft.Column([ft.Text("LOGIN", size=30), u_in, p_in, ft.ElevatedButton("ENTRAR", on_click=login), ft.TextButton("Crear Cuenta", on_click=ir_reg)], alignment="center"))
    ir_login(None)

ft.app(target=main, view=ft.WEB_BROWSER, port=9000, host="0.0.0.0")