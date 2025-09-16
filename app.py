import flet as ft
from datetime import datetime
import json
import os
import pandas as pd
from typing import Dict, List, Optional

# -------------------- Data Management Class --------------------
class GasLoadingSystem:
    """Class to manage all data related to the gas loading process."""
    def __init__(self):
        # On a deployed server, files might not be persistent.
        # So we'll keep data in memory for the session.
        self.data = {
            "bays": {"1": {}, "2": {}, "3": {}, "4": {}},
            "completed": []
        }
        # In a real-world scenario, this would be a database.

    def get_bay_data(self, bay_number: str) -> dict:
        """Retrieves data for a specific bay."""
        return self.data["bays"].get(bay_number, {})

    def save_bay_data(self, bay_number: str, data: dict):
        """Saves or updates data for a specific bay."""
        if bay_number not in self.data["bays"]:
            self.data["bays"][bay_number] = {}
        self.data["bays"][bay_number].update(data)
    
    def complete_loading(self, bay_number: str):
        """Moves data from an active bay to the completed list."""
        if bay_number in self.data["bays"] and self.data["bays"][bay_number]:
            completed_data = self.data["bays"][bay_number].copy()
            completed_data["bay_number"] = bay_number
            completed_data["completed_time"] = datetime.now().isoformat()
            self.data["completed"].append(completed_data)
            self.data["bays"][bay_number] = {}  # Clear the bay

# -------------------- Main Application UI --------------------
def main(page: ft.Page):
    page.title = "ระบบจัดการลานโหลดก๊าซธรรมชาติ"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.window.width = 1200
    page.window.height = 800
    page.auto_scroll = True
    
    # Initialize the data system
    gas_system = GasLoadingSystem()
    current_bay = "1"  # Default bay
    
    # -------------------- UI elements (created once) --------------------
    # Admin check order fields
    carrier_name = ft.TextField(label="Carrier Name", width=300)
    license_front = ft.TextField(label="License (Front)", width=200, keyboard_type=ft.KeyboardType.NUMBER)
    license_rear = ft.TextField(label="License (Rear)", width=200, keyboard_type=ft.KeyboardType.NUMBER)
    truck_type = ft.Dropdown(label="Types of truck", width=300, options=[ft.dropdown.Option("Semi-Trailer"), ft.dropdown.Option("10 wheel truck"), ft.dropdown.Option("ISO Tank")])
    shift = ft.Dropdown(label="Shift", width=150, options=[ft.dropdown.Option("A"), ft.dropdown.Option("B"), ft.dropdown.Option("C"), ft.dropdown.Option("D")])
    order_no = ft.TextField(label="Order No.", width=200, keyboard_type=ft.KeyboardType.NUMBER)
    customer_name = ft.TextField(label="Customer name", width=300)
    load_qty = ft.TextField(label="Calculated/Load Q'ty (kg)", width=200, keyboard_type=ft.KeyboardType.NUMBER)
    checker_name = ft.TextField(label="ชื่อผู้ตรวจสอบ", width=300)
    
    # Store admin fields for easier access
    admin_fields = {
        'carrier_name': carrier_name, 'license_front': license_front, 'license_rear': license_rear,
        'truck_type': truck_type, 'shift': shift, 'order_no': order_no,
        'customer_name': customer_name, 'load_qty': load_qty, 'checker_name': checker_name
    }
    
    # -------------------- Helper Functions --------------------
    def show_snackbar(message: str, color: str = ft.Colors.GREEN):
        """Displays a temporary message at the bottom of the screen."""
        snackbar = ft.SnackBar(content=ft.Text(message), bgcolor=color, duration=2000)
        page.overlay.append(snackbar)
        snackbar.open = True
        page.update()
    
    def get_timestamp():
        """Returns the current timestamp in a readable format."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def save_all_fields():
        """Saves data from all fields for the current bay."""
        bay_data = {}
        # Save Admin fields
        for key, field in admin_fields.items():
            bay_data[key] = field.value
        # Save Loading fields
        for key, field in loading_fields.items():
            if isinstance(field, (ft.TextField, ft.Dropdown)):
                bay_data[key] = field.value
            elif isinstance(field, ft.Text):
                # We need to get the value from the UI element
                bay_data[key] = field.value

        gas_system.save_bay_data(current_bay, bay_data)
        page.update()

    def load_bay_data_to_form():
        """Loads saved data for the current bay into the form fields."""
        bay_data = gas_system.get_bay_data(current_bay)
        
        # Load Admin fields
        for key, field in admin_fields.items():
            field.value = bay_data.get(key, '')
        
        # Load Loading fields
        for key, field in loading_fields.items():
            if isinstance(field, (ft.TextField, ft.Dropdown)):
                field.value = bay_data.get(key, '')
            elif isinstance(field, ft.Text):
                field.value = bay_data.get(key, '')
                
        page.update()
    
    # -------------------- Bay Selector UI --------------------
    def on_bay_changed(e):
        """Handles a change in the selected bay."""
        nonlocal current_bay
        # Save data of the OLD bay before switching
        save_all_fields()
        
        current_bay = e.control.value
        bay_status.value = f"กำลังทำงานที่ Bay {current_bay}"
        # Load data of the NEW bay
        load_bay_data_to_form()
        page.update()
    
    bay_selector = ft.Dropdown(
        label="เลือก Bay",
        width=150,
        value="1",
        options=[ft.dropdown.Option("1", "Bay 1"), ft.dropdown.Option("2", "Bay 2"), ft.dropdown.Option("3", "Bay 3"), ft.dropdown.Option("4", "Bay 4")],
        on_change=on_bay_changed
    )
    
    bay_status = ft.Text(f"กำลังทำงานที่ Bay {current_bay}", size=16, weight=ft.FontWeight.BOLD)
    
    # -------------------- Tab 1: Admin Check Order --------------------
    def create_admin_tab():
        # Set on_change handlers for Admin fields
        for field in admin_fields.values():
            field.on_change = lambda e: save_all_fields()

        return ft.Container(
            content=ft.Column([
                ft.Text("Admin Check Order", size=20, weight=ft.FontWeight.BOLD),
                ft.Row([carrier_name]),
                ft.Row([license_front, license_rear]),
                ft.Row([truck_type, shift]),
                ft.Row([order_no, customer_name]),
                ft.Row([load_qty]),
                ft.Row([checker_name]),
            ], scroll=ft.ScrollMode.AUTO),
            padding=20
        )
    
    # -------------------- Tab 2: Loading Process --------------------
    loading_fields = {} # A dictionary to hold all loading UI elements

    def create_loading_tab():
        loading_steps = []
        
        def create_timestamp_button(label: str, field_name: str):
            """Creates a button to save a timestamp and displays it."""
            timestamp_text = ft.Text("", size=12)
            loading_fields[f"{field_name}_timestamp"] = timestamp_text
            
            def on_click(e):
                timestamp = get_timestamp()
                timestamp_text.value = timestamp
                save_all_fields()
                page.update()
            
            return ft.Row([
                ft.Text(label, size=14, expand=True),
                ft.ElevatedButton("OK", on_click=on_click, width=80),
                timestamp_text
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER)
            
        def create_input_field(label: str, field_name: str, unit: str = "", keyboard_type=ft.KeyboardType.NUMBER):
            """Creates a text field with a label and unit."""
            field = ft.TextField(
                label=f"{label} ({unit})" if unit else label,
                width=300,
                keyboard_type=keyboard_type
            )
            field.on_change = lambda e: save_all_fields()
            loading_fields[field_name] = field
            return field
            
        def create_dropdown_field(label: str, field_name: str, options: List[str], initial_value: str = None):
            """Creates a dropdown field."""
            dropdown = ft.Dropdown(
                label=label,
                width=300,
                options=[ft.dropdown.Option(opt) for opt in options],
                value=initial_value
            )
            dropdown.on_change = lambda e: save_all_fields()
            loading_fields[field_name] = dropdown
            return dropdown
        
        # Create all loading steps based on the provided list
        loading_steps.extend([
            create_timestamp_button("Check weight scale / Truck on bay time", "truck_on_bay"),
            create_timestamp_button("Parking and stop engine", "parking_stop"),
            create_timestamp_button("Put wheel chock, traffic cone, pole sign & connect ground (Geen Lamp)", "safety_setup"),
            create_input_field("Create and check instruction sheet", "instruction_sheet_ton", "Ton"),
            create_timestamp_button("Check ground before tare weight (F1) & confirm Q'ty and status with DCS", "check_ground_tare"),
            create_input_field("Connect liquid & vapor arms / Flexible hose Open bypass valve of truck", "connect_arms_kg", "Kg"),
            create_timestamp_button("Open manual valve vent safe location at liquid line", "open_vent"),
            create_timestamp_button("Supply N2 & open valve vapor arm for leak test (3-5 Barg)", "supply_n2"),
            create_timestamp_button("Open valve liquid arm/Flexible hose and purging and check O2 (< 1% by Vol.) -Close N2 supply valve and Close bypass valve of truck", "purging_o2"),
            create_timestamp_button("Close manual valve vent safe location at liquid line of bay", "close_vent"),
            create_input_field("Open SDV vapor of Bay for releasing tank pressure", "release_pressure_barg", "barg"),
            create_timestamp_button("Open vapor valve and liquid valve (Top/Bottom fill) of truck", "open_truck_valves"),
            ft.Row([
                create_input_field("Open SDV liquid and start cooldown (F3)", "cooldown_flow_m3", "m3/hr"),
                create_dropdown_field("Cooldown status", "cooldown_status", ["cool down", "Not cool down"], "cool down")
            ]),
            ft.Column([
                create_input_field("Ramp up by FV open to full rate", "ramp_up_flow_m3", "m3/hr"),
                ft.Row([ft.Text("ผู้ตรวจสอบ (ช่างเข้า)"), ft.VerticalDivider(width=10), create_input_field("", "technician_name", "", ft.KeyboardType.TEXT)])
            ]),
            create_timestamp_button("Ramp down by FV close and confirm Gross weight order", "ramp_down"),
            create_timestamp_button("Close liquid & vapor valve of truck & open bypass valve of truck for draining", "close_truck_valves"),
            create_timestamp_button("Supply N2 for drain & continue purging and check %LEL(CH4) ( < 3%byVol or 60%LEL)", "n2_drain_purging"),
            create_timestamp_button("Close valve N2 supply and close valve line drain", "close_n2_drain"),
            create_timestamp_button("Closed manual liquid and vapor arm/flexible hose", "close_arms_manual"),
            create_timestamp_button("Open manual valve vent (safe to location) release pressure at liquid line&close", "release_final_pressure"),
            create_timestamp_button("Disconnect liquid & vapor arm /Flexible hose ( Install seal )", "disconnect_arms"),
            create_timestamp_button("Check all people out of bay and gross weigh truck (F1)", "gross_weigh_truck"),
            create_input_field("Check all condition tank normal and start truck's engine", "tank_normal_kg", "kg."),
            create_input_field("Disconnect ground and check ground camp at parking point", "disconnect_ground_kg", "kg."),
            create_input_field("Remove wheel chock, Traffic cone and pole sign at parking area", "remove_safety_kg", "kg."),
            create_timestamp_button("Confirm operating bay is normal and inform drive out of bay", "drive_out"),
            ft.Column([
                create_timestamp_button("Create and sign for confirm loading Q'ty on Bill of Loading / Excise", "bill_loading_sign"),
                ft.Row([ft.Text("ผู้ตรวจสอบน้ำหนัก"), ft.VerticalDivider(width=10), create_input_field("", "weight_checker", "", ft.KeyboardType.TEXT)])
            ]),
            create_input_field("Remark", "remark", "", ft.KeyboardType.TEXT)
        ])
        
        def complete_loading(e):
            """Completes the loading process for the current bay."""
            gas_system.complete_loading(current_bay)
            show_snackbar(f"บันทึกข้อมูล Bay {current_bay} เสร็จสมบูรณ์", ft.Colors.BLUE)
            load_bay_data_to_form()
            
        complete_btn = ft.ElevatedButton(
            "เสร็จสิ้นการโหลด",
            on_click=complete_loading,
            bgcolor=ft.Colors.GREEN,
            color=ft.Colors.WHITE
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text("Loading Process", size=20, weight=ft.FontWeight.BOLD),
                *loading_steps,
                ft.Divider(),
                complete_btn
            ], scroll=ft.ScrollMode.AUTO),
            padding=20
        )
    
    # -------------------- Tab 3: Data Review --------------------
    def create_review_tab():
        data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Bay")),
                ft.DataColumn(ft.Text("Carrier")),
                ft.DataColumn(ft.Text("License")),
                ft.DataColumn(ft.Text("Order No.")),
                ft.DataColumn(ft.Text("Load Q'ty (kg)")),
                ft.DataColumn(ft.Text("Status")),
                ft.DataColumn(ft.Text("Time")),
            ],
            rows=[]
        )
        
        def refresh_data(e=None):
            """Refreshes the data table with the latest information."""
            rows = []
            
            # Active bays
            for bay_num, bay_data in gas_system.data["bays"].items():
                if bay_data:
                    rows.append(ft.DataRow(cells=[
                        ft.DataCell(ft.Text(f"Bay {bay_num}")),
                        ft.DataCell(ft.Text(bay_data.get('carrier_name', '-'))),
                        ft.DataCell(ft.Text(f"{bay_data.get('license_front', '-')}/{bay_data.get('license_rear', '-')}")),
                        ft.DataCell(ft.Text(bay_data.get('order_no', '-'))),
                        ft.DataCell(ft.Text(bay_data.get('load_qty', '-'))),
                        ft.DataCell(ft.Text("กำลังดำเนินการ", color=ft.Colors.ORANGE)),
                        ft.DataCell(ft.Text(bay_data.get('admin_saved_time', '-'))),
                    ]))
            
            # Completed loads
            for completed in gas_system.data["completed"][-10:]:  # Show last 10 completed
                rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(f"Bay {completed.get('bay_number', '-')}")),
                    ft.DataCell(ft.Text(completed.get('carrier_name', '-'))),
                    ft.DataCell(ft.Text(f"{completed.get('license_front', '-')}/{completed.get('license_rear', '-')}")),
                    ft.DataCell(ft.Text(completed.get('order_no', '-'))),
                    ft.DataCell(ft.Text(completed.get('load_qty', '-'))),
                    ft.DataCell(ft.Text("เสร็จสิ้น", color=ft.Colors.GREEN)),
                    ft.DataCell(ft.Text(completed.get('completed_time', '-'))),
                ]))
            
            data_table.rows = rows
            page.update()
        
        def export_to_excel(e):
            """Exports all data to an Excel file."""
            try:
                all_data = []
                
                for bay_num, bay_data in gas_system.data["bays"].items():
                    if bay_data:
                        record = bay_data.copy()
                        record['bay_number'] = bay_num
                        record['status'] = 'กำลังดำเนินการ'
                        all_data.append(record)
                
                for completed in gas_system.data["completed"]:
                    record = completed.copy()
                    record['status'] = 'เสร็จสิ้น'
                    all_data.append(record)
                
                if all_data:
                    # In a deployed environment, you can't save to a local file.
                    # Instead, you would use a web-based approach.
                    show_snackbar("ฟังก์ชันส่งออก Excel ไม่สามารถใช้งานได้บนเว็บไซต์", ft.Colors.RED)
                else:
                    show_snackbar("ไม่มีข้อมูลให้ส่งออก", ft.Colors.RED)
            except Exception as ex:
                show_snackbar(f"เกิดข้อผิดพลาด: {str(ex)}", ft.Colors.RED)
        
        refresh_btn = ft.IconButton(icon=ft.Icons.REFRESH, on_click=refresh_data, tooltip="รีเฟรชข้อมูล")
        export_btn = ft.ElevatedButton("ส่งออก Excel", on_click=export_to_excel, icon=ft.Icons.FILE_DOWNLOAD)
        
        # Summary cards for all 4 bays
        def create_bay_summary_card(bay_num: str):
            bay_data = gas_system.get_bay_data(bay_num)
            is_active = bool(bay_data)
            
            return ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text(f"Bay {bay_num}", size=16, weight=ft.FontWeight.BOLD),
                        ft.Text(f"Status: {'กำลังดำเนินการ' if is_active else 'ว่าง'}", color=ft.Colors.ORANGE if is_active else ft.Colors.GREEN),
                        ft.Text(f"Carrier: {bay_data.get('carrier_name', '-')}" if is_active else "Carrier: -"),
                        ft.Text(f"Order: {bay_data.get('order_no', '-')}" if is_active else "Order: -"),
                    ]),
                    padding=10
                ),
                width=250,
                height=150
            )
        
        bay_summaries = ft.Row([
            create_bay_summary_card("1"), create_bay_summary_card("2"),
            create_bay_summary_card("3"), create_bay_summary_card("4"),
        ], wrap=True)
        
        refresh_data()
        
        return ft.Container(
            content=ft.Column([
                ft.Text("ตรวจสอบข้อมูล", size=20, weight=ft.FontWeight.BOLD),
                ft.Row([refresh_btn, export_btn]),
                ft.Text("สรุปสถานะ 4 Bay", size=16, weight=ft.FontWeight.BOLD),
                bay_summaries,
                ft.Divider(),
                ft.Text("ข้อมูลทั้งหมด", size=16, weight=ft.FontWeight.BOLD),
                ft.Container(content=data_table, border=ft.border.all(1, ft.Colors.GREY_400), border_radius=10, padding=10)
            ], scroll=ft.ScrollMode.AUTO),
            padding=20
        )
    
    # -------------------- Main UI Layout --------------------
    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(text="Admin check order", icon=ft.Icons.ADMIN_PANEL_SETTINGS, content=create_admin_tab()),
            ft.Tab(text="Loading", icon=ft.Icons.LOCAL_SHIPPING, content=create_loading_tab()),
            ft.Tab(text="ตรวจสอบข้อมูล", icon=ft.Icons.TABLE_CHART, content=create_review_tab()),
        ],
        expand=1
    )
    
    page.add(
        ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.LOCAL_GAS_STATION, size=40, color=ft.Colors.BLUE),
                ft.Text("ระบบจัดการลานโหลดก๊าซธรรมชาติ", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                bay_selector,
                bay_status
            ]),
            ft.Divider(),
            tabs
        ], expand=True)
    )
    
    load_bay_data_to_form()

# -------------------- Run the application --------------------
if __name__ == "__main__":
    ft.app(target=main, view=ft.WEB_BROWSER)