import flet as ft
from datetime import datetime
import json
import os
from typing import Dict, List, Optional
import pandas as pd

class GasLoadingSystem:
    def __init__(self):
        self.data_file = "gas_loading_data.json"
        self.load_data()
        
    def load_data(self):
        """โหลดข้อมูลจากไฟล์"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        else:
            self.data = {
                "bays": {
                    "1": {},
                    "2": {},
                    "3": {},
                    "4": {}
                },
                "completed": []
            }
    
    def save_data(self):
        """บันทึกข้อมูลลงไฟล์"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def get_bay_data(self, bay_number: str) -> dict:
        """ดึงข้อมูลของ bay ที่เลือก"""
        return self.data["bays"].get(bay_number, {})
    
    def save_bay_data(self, bay_number: str, data: dict):
        """บันทึกข้อมูลของ bay"""
        if bay_number not in self.data["bays"]:
            self.data["bays"][bay_number] = {}
        self.data["bays"][bay_number].update(data)
        self.save_data()
    
    def complete_loading(self, bay_number: str):
        """ย้ายข้อมูลไปยัง completed เมื่อโหลดเสร็จ"""
        if bay_number in self.data["bays"] and self.data["bays"][bay_number]:
            completed_data = self.data["bays"][bay_number].copy()
            completed_data["bay_number"] = bay_number
            completed_data["completed_time"] = datetime.now().isoformat()
            self.data["completed"].append(completed_data)
            self.data["bays"][bay_number] = {}
            self.save_data()

def main(page: ft.Page):
    page.title = "ระบบจัดการลานโหลดก๊าซธรรมชาติ"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.window.width = 1200
    page.window.height = 800
    
    # Initialize data system
    gas_system = GasLoadingSystem()
    current_bay = "1"  # Default bay
    
    def show_snackbar(message: str, color: str = "green"):
        snackbar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=color,
            duration=2000
        )
        page.overlay.append(snackbar)
        snackbar.open = True
        page.update()
    
    def get_timestamp():
        """Get current timestamp"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def save_current_data(field: str, value):
        """Save data for current bay"""
        bay_data = gas_system.get_bay_data(current_bay)
        bay_data[field] = value
        gas_system.save_bay_data(current_bay, bay_data)
        show_snackbar(f"บันทึกข้อมูล {field} สำเร็จ", "green")
    
    def load_bay_data_to_form():
        """Load saved data for current bay into form fields"""
        bay_data = gas_system.get_bay_data(current_bay)
        
        # Admin check order fields
        if hasattr(page, 'admin_fields'):
            fields = page.admin_fields
            fields['carrier_name'].value = bay_data.get('carrier_name', '')
            fields['license_front'].value = bay_data.get('license_front', '')
            fields['license_rear'].value = bay_data.get('license_rear', '')
            fields['truck_type'].value = bay_data.get('truck_type', 'Semi-Trailer')
            fields['shift'].value = bay_data.get('shift', 'A')
            fields['order_no'].value = bay_data.get('order_no', '')
            fields['customer_name'].value = bay_data.get('customer_name', '')
            fields['load_qty'].value = bay_data.get('load_qty', '')
            fields['checker_name'].value = bay_data.get('checker_name', '')
            
        # Loading fields
        if hasattr(page, 'loading_fields'):
            fields = page.loading_fields
            for key, field in fields.items():
                if key in bay_data:
                    if isinstance(field, ft.TextField):
                        field.value = bay_data[key]
                    elif isinstance(field, ft.Dropdown):
                        field.value = bay_data[key]
                    elif isinstance(field, ft.Text):
                        field.value = bay_data[key]
        
        page.update()
    
    # Bay selector
    def on_bay_changed(e):
        nonlocal current_bay
        current_bay = e.control.value
        load_bay_data_to_form()
        bay_status.value = f"กำลังทำงานที่ Bay {current_bay}"
        page.update()
    
    bay_selector = ft.Dropdown(
        label="เลือก Bay",
        width=150,
        value="1",
        options=[
            ft.dropdown.Option("1", "Bay 1"),
            ft.dropdown.Option("2", "Bay 2"),
            ft.dropdown.Option("3", "Bay 3"),
            ft.dropdown.Option("4", "Bay 4"),
        ],
        on_change=on_bay_changed
    )
    
    bay_status = ft.Text(f"กำลังทำงานที่ Bay {current_bay}", size=16, weight=ft.FontWeight.BOLD)
    
    # Admin check order tab
    def create_admin_tab():
        carrier_name = ft.TextField(label="Carrier Name", width=300)
        license_front = ft.TextField(label="License (Front)", width=200, keyboard_type=ft.KeyboardType.NUMBER)
        license_rear = ft.TextField(label="License (Rear)", width=200, keyboard_type=ft.KeyboardType.NUMBER)
        
        truck_type = ft.Dropdown(
            label="Types of truck",
            width=300,
            options=[
                ft.dropdown.Option("Semi-Trailer"),
                ft.dropdown.Option("10 wheel truck"),
                ft.dropdown.Option("ISO Tank"),
            ],
            value="Semi-Trailer"
        )
        
        shift = ft.Dropdown(
            label="Shift",
            width=150,
            options=[
                ft.dropdown.Option("A"),
                ft.dropdown.Option("B"),
                ft.dropdown.Option("C"),
                ft.dropdown.Option("D"),
            ],
            value="A"
        )
        
        order_no = ft.TextField(label="Order No.", width=200, keyboard_type=ft.KeyboardType.NUMBER)
        customer_name = ft.TextField(label="Customer name", width=300)
        load_qty = ft.TextField(label="Calculated/Load Q'ty (kg)", width=200, keyboard_type=ft.KeyboardType.NUMBER)
        checker_name = ft.TextField(label="ชื่อผู้ตรวจสอบ", width=300)
        
        # Store fields for later access
        page.admin_fields = {
            'carrier_name': carrier_name,
            'license_front': license_front,
            'license_rear': license_rear,
            'truck_type': truck_type,
            'shift': shift,
            'order_no': order_no,
            'customer_name': customer_name,
            'load_qty': load_qty,
            'checker_name': checker_name
        }
        
        def save_admin_data(e):
            data = {
                'carrier_name': carrier_name.value,
                'license_front': license_front.value,
                'license_rear': license_rear.value,
                'truck_type': truck_type.value,
                'shift': shift.value,
                'order_no': order_no.value,
                'customer_name': customer_name.value,
                'load_qty': load_qty.value,
                'checker_name': checker_name.value,
                'admin_saved_time': get_timestamp()
            }
            gas_system.save_bay_data(current_bay, data)
            show_snackbar("บันทึกข้อมูล Admin check order สำเร็จ")
        
        save_btn = ft.ElevatedButton(
            "บันทึกข้อมูล Admin",
            on_click=save_admin_data,
            bgcolor=ft.colors.BLUE,
            color=ft.colors.WHITE
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text("Admin Check Order", size=20, weight=ft.FontWeight.BOLD),
                ft.Row([carrier_name]),
                ft.Row([license_front, license_rear]),
                ft.Row([truck_type, shift]),
                ft.Row([order_no, customer_name]),
                ft.Row([load_qty]),
                ft.Row([checker_name]),
                ft.Row([save_btn])
            ], scroll=ft.ScrollMode.AUTO),
            padding=20
        )
    
    # Loading tab
    def create_loading_tab():
        loading_steps = []
        page.loading_fields = {}
        
        def create_timestamp_button(label: str, field_name: str):
            timestamp_text = ft.Text("", size=12)
            page.loading_fields[f"{field_name}_timestamp"] = timestamp_text
            
            def on_click(e):
                timestamp = get_timestamp()
                timestamp_text.value = timestamp
                save_current_data(f"{field_name}_timestamp", timestamp)
                page.update()
            
            btn = ft.ElevatedButton("OK", on_click=on_click, width=80)
            return ft.Column([
                ft.Text(label, size=14),
                ft.Row([btn, timestamp_text])
            ])
        
        def create_input_field(label: str, field_name: str, unit: str = "", keyboard_type=ft.KeyboardType.NUMBER):
            field = ft.TextField(
                label=f"{label} ({unit})" if unit else label,
                width=200,
                keyboard_type=keyboard_type,
                on_change=lambda e: save_current_data(field_name, e.control.value)
            )
            page.loading_fields[field_name] = field
            return field
        
        def create_dropdown_field(label: str, field_name: str, options: List[str]):
            dropdown = ft.Dropdown(
                label=label,
                width=200,
                options=[ft.dropdown.Option(opt) for opt in options],
                on_change=lambda e: save_current_data(field_name, e.control.value)
            )
            page.loading_fields[field_name] = dropdown
            return dropdown
        
        # Create all loading steps
        loading_steps = [
            create_timestamp_button("Check weight scale / Truck on bay time", "truck_on_bay"),
            create_timestamp_button("Parking and stop engine", "parking_stop"),
            create_timestamp_button("Put wheel chock, traffic cone, pole sign & connect ground", "safety_setup"),
            create_input_field("Create and check instruction sheet", "instruction_sheet", "Ton"),
            create_timestamp_button("Check ground before tare weight (F1)", "check_ground"),
            create_input_field("Connect liquid & vapor arms", "connect_arms", "Kg"),
            create_timestamp_button("Open manual valve vent safe location", "open_vent"),
            create_timestamp_button("Supply N2 & open valve vapor arm (3-5 Barg)", "supply_n2"),
            create_timestamp_button("Open valve liquid arm and purging O2 < 1%", "purging"),
            create_timestamp_button("Close N2 supply and bypass valve", "close_n2"),
            create_timestamp_button("Close manual valve vent safe location", "close_vent"),
            create_input_field("Open SDV vapor for releasing pressure", "release_pressure", "barg"),
            create_timestamp_button("Open vapor and liquid valve of truck", "open_truck_valves"),
            ft.Row([
                create_input_field("Open SDV liquid start cooldown", "cooldown_flow", "m3/hr"),
                create_dropdown_field("Cooldown status", "cooldown_status", ["cool down", "Not cool down"])
            ]),
            create_input_field("Ramp up flow rate", "ramp_up_flow", "m3/hr"),
            create_input_field("ช่างเข้า", "technician_name", "", ft.KeyboardType.TEXT),
            create_timestamp_button("Ramp down and confirm gross weight", "ramp_down"),
            create_timestamp_button("Close liquid & vapor valve", "close_valves"),
            create_timestamp_button("Supply N2 for drain & purging", "n2_drain"),
            create_timestamp_button("Close N2 supply and drain valve", "close_n2_drain"),
            create_timestamp_button("Close manual liquid and vapor arm", "close_arms"),
            create_timestamp_button("Open manual valve vent release pressure", "release_final"),
            create_timestamp_button("Disconnect liquid & vapor arm", "disconnect_arms"),
            create_timestamp_button("Check all people out and gross weigh", "gross_weigh"),
            create_input_field("Check tank normal and start engine", "tank_check", "kg"),
            create_input_field("Disconnect ground at parking", "disconnect_ground", "kg"),
            create_input_field("Remove wheel chock and signs", "remove_safety", "kg"),
            create_timestamp_button("Confirm bay normal and drive out", "drive_out"),
            create_timestamp_button("Create and sign Bill of Loading", "bill_loading"),
            create_input_field("ผู้ตรวจสอบน้ำหนัก", "weight_checker", "", ft.KeyboardType.TEXT),
            create_input_field("Remark", "remark", "", ft.KeyboardType.TEXT),
        ]
        
        def complete_loading(e):
            gas_system.complete_loading(current_bay)
            show_snackbar(f"บันทึกข้อมูล Bay {current_bay} เสร็จสมบูรณ์", "blue")
            load_bay_data_to_form()
        
        complete_btn = ft.ElevatedButton(
            "เสร็จสิ้นการโหลด",
            on_click=complete_loading,
            bgcolor=ft.colors.GREEN,
            color=ft.colors.WHITE
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
    
    # Data review tab
    def create_review_tab():
        data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Bay")),
                ft.DataColumn(ft.Text("Carrier")),
                ft.DataColumn(ft.Text("License")),
                ft.DataColumn(ft.Text("Order No.")),
                ft.DataColumn(ft.Text("Customer")),
                ft.DataColumn(ft.Text("Load Q'ty (kg)")),
                ft.DataColumn(ft.Text("Status")),
                ft.DataColumn(ft.Text("Time")),
            ],
            rows=[]
        )
        
        def refresh_data(e=None):
            rows = []
            
            # Active bays
            for bay_num, bay_data in gas_system.data["bays"].items():
                if bay_data:
                    rows.append(ft.DataRow(cells=[
                        ft.DataCell(ft.Text(f"Bay {bay_num}")),
                        ft.DataCell(ft.Text(bay_data.get('carrier_name', '-'))),
                        ft.DataCell(ft.Text(f"{bay_data.get('license_front', '-')}/{bay_data.get('license_rear', '-')}")),
                        ft.DataCell(ft.Text(bay_data.get('order_no', '-'))),
                        ft.DataCell(ft.Text(bay_data.get('customer_name', '-'))),
                        ft.DataCell(ft.Text(bay_data.get('load_qty', '-'))),
                        ft.DataCell(ft.Text("กำลังดำเนินการ", color=ft.colors.ORANGE)),
                        ft.DataCell(ft.Text(bay_data.get('admin_saved_time', '-')[:10] if 'admin_saved_time' in bay_data else '-')),
                    ]))
            
            # Completed loads
            for completed in gas_system.data["completed"][-10:]:  # Show last 10 completed
                rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(f"Bay {completed.get('bay_number', '-')}")),
                    ft.DataCell(ft.Text(completed.get('carrier_name', '-'))),
                    ft.DataCell(ft.Text(f"{completed.get('license_front', '-')}/{completed.get('license_rear', '-')}")),
                    ft.DataCell(ft.Text(completed.get('order_no', '-'))),
                    ft.DataCell(ft.Text(completed.get('customer_name', '-'))),
                    ft.DataCell(ft.Text(completed.get('load_qty', '-'))),
                    ft.DataCell(ft.Text("เสร็จสิ้น", color=ft.colors.GREEN)),
                    ft.DataCell(ft.Text(completed.get('completed_time', '-')[:10] if 'completed_time' in completed else '-')),
                ]))
            
            data_table.rows = rows
            page.update()
        
        def export_to_excel(e):
            try:
                # Prepare data for export
                all_data = []
                
                # Add active bays
                for bay_num, bay_data in gas_system.data["bays"].items():
                    if bay_data:
                        record = bay_data.copy()
                        record['bay_number'] = bay_num
                        record['status'] = 'กำลังดำเนินการ'
                        all_data.append(record)
                
                # Add completed
                for completed in gas_system.data["completed"]:
                    record = completed.copy()
                    record['status'] = 'เสร็จสิ้น'
                    all_data.append(record)
                
                if all_data:
                    df = pd.DataFrame(all_data)
                    filename = f"gas_loading_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    df.to_excel(filename, index=False)
                    show_snackbar(f"ส่งออกข้อมูลเป็น {filename} สำเร็จ", "green")
                else:
                    show_snackbar("ไม่มีข้อมูลให้ส่งออก", "red")
            except Exception as ex:
                show_snackbar(f"เกิดข้อผิดพลาด: {str(ex)}", "red")
        
        refresh_btn = ft.IconButton(
            icon=ft.icons.REFRESH,
            on_click=refresh_data,
            tooltip="รีเฟรชข้อมูล"
        )
        
        export_btn = ft.ElevatedButton(
            "ส่งออก Excel",
            on_click=export_to_excel,
            icon=ft.icons.FILE_DOWNLOAD
        )
        
        # Summary cards for all 4 bays
        def create_bay_summary_card(bay_num: str):
            bay_data = gas_system.get_bay_data(bay_num)
            is_active = bool(bay_data)
            
            return ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text(f"Bay {bay_num}", size=16, weight=ft.FontWeight.BOLD),
                        ft.Text(f"Status: {'กำลังดำเนินการ' if is_active else 'ว่าง'}", 
                               color=ft.colors.ORANGE if is_active else ft.colors.GREEN),
                        ft.Text(f"Carrier: {bay_data.get('carrier_name', '-')}" if is_active else "Carrier: -"),
                        ft.Text(f"Order: {bay_data.get('order_no', '-')}" if is_active else "Order: -"),
                    ]),
                    padding=10
                ),
                width=250,
                height=150
            )
        
        bay_summaries = ft.Row([
            create_bay_summary_card("1"),
            create_bay_summary_card("2"),
            create_bay_summary_card("3"),
            create_bay_summary_card("4"),
        ], wrap=True)
        
        # Initial data load
        refresh_data()
        
        return ft.Container(
            content=ft.Column([
                ft.Text("ตรวจสอบข้อมูล", size=20, weight=ft.FontWeight.BOLD),
                ft.Row([refresh_btn, export_btn]),
                ft.Text("สรุปสถานะ 4 Bay", size=16, weight=ft.FontWeight.BOLD),
                bay_summaries,
                ft.Divider(),
                ft.Text("ข้อมูลทั้งหมด", size=16, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=data_table,
                    border=ft.border.all(1, ft.colors.GREY_400),
                    border_radius=10,
                    padding=10
                )
            ], scroll=ft.ScrollMode.AUTO),
            padding=20
        )
    
    # Create tabs
    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(
                text="Admin check order",
                icon=ft.icons.ADMIN_PANEL_SETTINGS,
                content=create_admin_tab()
            ),
            ft.Tab(
                text="Loading",
                icon=ft.icons.LOCAL_SHIPPING,
                content=create_loading_tab()
            ),
            ft.Tab(
                text="ตรวจสอบข้อมูล",
                icon=ft.icons.TABLE_CHART,
                content=create_review_tab()
            ),
        ],
        expand=1
    )
    
    # Main layout
    page.add(
        ft.Column([
            ft.Row([
                ft.Icon(ft.icons.LOCAL_GAS_STATION, size=40, color=ft.colors.BLUE),
                ft.Text("ระบบจัดการลานโหลดก๊าซธรรมชาติ", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                bay_selector,
                bay_status
            ]),
            ft.Divider(),
            tabs
        ], expand=True)
    )
    
    # Load initial data
    load_bay_data_to_form()

# Run the app
if __name__ == "__main__":
    ft.app(target=main)