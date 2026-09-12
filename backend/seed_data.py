"""
Mock data seed script for Fleet Management System.
Run inside the backend container:
    docker-compose exec backend python seed_data.py
"""
import os, django, random
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fleet.settings.production")
django.setup()

from decimal import Decimal
from datetime import date, datetime, timedelta, timezone
from apps.vehicles.models import Vehicle
from apps.drivers.models import Driver, VehicleAssignment
from apps.fueling.models import FuelingRecord
from apps.maintenance.models import MaintenanceRecord

print("🚀 Seeding mock data...")

# ──────────────────────────────────────────────
# 1. VEHICLES
# ──────────────────────────────────────────────
vehicles_data = [
    dict(license_plate="АА1234ВВ", vin="1HGBH41JXMN109186", make="Toyota",    model="Corolla",    year=2019, fuel_type="petrol", norm_consumption_summer="7.80", norm_consumption_winter="9.20",  odometer="142350.50", status="active"),
    dict(license_plate="КА5678НН", vin="WBAYB6C51DD167145", make="Volkswagen", model="Crafter",    year=2020, fuel_type="diesel", norm_consumption_summer="9.50", norm_consumption_winter="11.80", odometer="98765.00",  status="active"),
    dict(license_plate="ВА0001СС", vin="JN1CV6AP0CM931154", make="Mercedes",   model="Sprinter",   year=2021, fuel_type="diesel", norm_consumption_summer="10.20",norm_consumption_winter="12.50", odometer="67432.75",  status="active"),
    dict(license_plate="ОА3399КК", vin="1N4AL3AP1EC147143", make="Ford",       model="Transit",    year=2018, fuel_type="diesel", norm_consumption_summer="11.00",norm_consumption_winter="13.50", odometer="215890.00", status="maintenance"),
    dict(license_plate="ХА7722РР", vin="5YJSA1CN5DFP14794", make="Renault",    model="Master",     year=2022, fuel_type="diesel", norm_consumption_summer="8.90", norm_consumption_winter="10.80", odometer="31200.00",  status="active"),
    dict(license_plate="МА4411ТТ", vin="WAUAFAFL9GN014399", make="Iveco",      model="Daily",      year=2017, fuel_type="diesel", norm_consumption_summer="12.50",norm_consumption_winter="15.00", odometer="298100.00", status="active"),
    dict(license_plate="ДА8800УУ", vin="3VWFX7AT5FM041861", make="DAF",        model="XF 480",     year=2020, fuel_type="diesel", norm_consumption_summer="28.00",norm_consumption_winter="33.00", odometer="445000.00", status="active"),
    dict(license_plate="ЗА2233ФФ", vin="1FTFW1ET9DFC51946", make="MAN",        model="TGX 18.440", year=2019, fuel_type="diesel", norm_consumption_summer="30.00",norm_consumption_winter="36.00", odometer="512300.00", status="active"),
    dict(license_plate="ЛА6655ХХ", vin="SAJWA0ES5EM242091", make="Volvo",      model="FH 500",     year=2016, fuel_type="diesel", norm_consumption_summer="31.00",norm_consumption_winter="37.00", odometer="789000.00", status="decommissioned"),
    dict(license_plate="НА9912ЦЦ", vin="2T1BURHE0JC077458", make="Toyota",     model="Land Cruiser",year=2023,fuel_type="diesel", norm_consumption_summer="13.50",norm_consumption_winter="16.00", odometer="15200.00",  status="active"),
]

created_vehicles = []
for v in vehicles_data:
    obj, created = Vehicle.objects.get_or_create(
        vin=v["vin"],
        defaults={**v, "registered_at": date.today() - timedelta(days=random.randint(30, 1000))}
    )
    created_vehicles.append(obj)
    print(f"  {'✅' if created else '⏭'} Vehicle: {obj.license_plate} {obj.make} {obj.model}")

# ──────────────────────────────────────────────
# 2. DRIVERS
# ──────────────────────────────────────────────
drivers_data = [
    dict(full_name="Іванов Іван Іванович",              personnel_number="DRV-001", date_of_birth=date(1985,3,15),  phone="+380671234001", license_category="C",  license_number="АВС123001", license_issued_at=date(2015,1,10), license_expires_at=date(2027,1,10), status="active"),
    dict(full_name="Петренко Олексій Сергійович",        personnel_number="DRV-002", date_of_birth=date(1990,7,22),  phone="+380671234002", license_category="CE", license_number="АВС123002", license_issued_at=date(2018,5,20), license_expires_at=date(2028,5,20), status="active"),
    dict(full_name="Коваленко Микола Павлович",          personnel_number="DRV-003", date_of_birth=date(1978,11,5),  phone="+380671234003", license_category="D",  license_number="АВС123003", license_issued_at=date(2012,3,15), license_expires_at=date(2026,3,15), status="active"),
    dict(full_name="Сидоренко Василь Миколайович",       personnel_number="DRV-004", date_of_birth=date(1982,4,18),  phone="+380671234004", license_category="B",  license_number="АВС123004", license_issued_at=date(2016,8,5),  license_expires_at=date(2028,8,5),  status="active"),
    dict(full_name="Мельник Андрій Васильович",          personnel_number="DRV-005", date_of_birth=date(1995,9,30),  phone="+380671234005", license_category="CE", license_number="АВС123005", license_issued_at=date(2020,2,10), license_expires_at=date(2030,2,10), status="active"),
    dict(full_name="Ткаченко Роман Олегович",            personnel_number="DRV-006", date_of_birth=date(1988,1,12),  phone="+380671234006", license_category="C",  license_number="АВС123006", license_issued_at=date(2017,9,25), license_expires_at=date(2027,9,25), status="active"),
    dict(full_name="Бондаренко Юрій Петрович",           personnel_number="DRV-007", date_of_birth=date(1975,6,8),   phone="+380671234007", license_category="CE", license_number="АВС123007", license_issued_at=date(2010,4,1),  license_expires_at=date(2026,4,1),  status="dismissed"),
    dict(full_name="Кравченко Дмитро Анатолійович",      personnel_number="DRV-008", date_of_birth=date(1993,12,25), phone="+380671234008", license_category="B",  license_number="АВС123008", license_issued_at=date(2019,7,14), license_expires_at=date(2029,7,14), status="active"),
]

created_drivers = []
for d in drivers_data:
    obj, created = Driver.objects.get_or_create(
        personnel_number=d["personnel_number"], defaults=d
    )
    created_drivers.append(obj)
    print(f"  {'✅' if created else '⏭'} Driver: {obj.full_name}")

# ──────────────────────────────────────────────
# 3. VEHICLE ASSIGNMENTS
# ──────────────────────────────────────────────
for drv_idx, veh_idx in [(0,0),(1,1),(2,2),(4,3),(5,4),(6,5),(7,6)]:
    drv = created_drivers[drv_idx]
    veh = created_vehicles[veh_idx]
    if not VehicleAssignment.objects.filter(driver=drv, vehicle=veh, released_at__isnull=True).exists():
        VehicleAssignment.objects.create(
            driver=drv, vehicle=veh,
            assigned_at=datetime.now(timezone.utc) - timedelta(days=random.randint(10, 180)),
        )
        print(f"  ✅ Assignment: {drv.full_name} → {veh.license_plate}")

# ──────────────────────────────────────────────
# 4. FUELING RECORDS
# ──────────────────────────────────────────────
stations = ["WOG", "OKKO", "SOCAR", "ANP", "KLO", "БРСМ"]

def make_fueling(vehicle, driver, days_ago, liters, price, station):
    fueled_at = datetime.now(timezone.utc) - timedelta(days=days_ago, hours=random.randint(0, 12))
    norm = float(vehicle.norm_consumption_summer)
    actual_cons = round(norm + random.uniform(-1.5, 2.5), 2)
    deviation = round((actual_cons - norm) / norm * 100, 2)
    is_anomalous = abs(deviation) > 10
    odo = Decimal(str(vehicle.odometer)) - Decimal(str(days_ago * random.uniform(50, 200)))
    if odo < 0: odo = Decimal("100.00")

    if FuelingRecord.objects.filter(vehicle=vehicle, fueled_at__date=fueled_at.date()).exists():
        return False
    FuelingRecord.objects.create(
        vehicle=vehicle,
        driver=driver,
        fueled_at=fueled_at,
        fuel_liters=Decimal(str(liters)),
        price_per_liter=Decimal(str(price)),
        station_name=station,
        odometer_at_fueling=odo,
        actual_consumption=Decimal(str(actual_cons)),
        deviation_pct=Decimal(str(deviation)),
        is_anomalous=is_anomalous,
    )
    return True

fueling_scenarios = [
    (0,0,5,   45.5, 56.9,"WOG"),  (0,0,35, 48.2,55.5,"OKKO"), (0,0,65, 44.0,54.0,"SOCAR"),
    (0,0,95,  49.8, 53.8,"WOG"),  (0,0,130,47.1,52.5,"ANP"),  (0,0,180,65.0,52.0,"KLO"),
    (1,1,8,   80.0, 57.2,"OKKO"), (1,1,38, 85.5,55.8,"WOG"),  (1,1,68, 78.0,54.5,"KLO"),
    (1,1,100, 90.0, 53.0,"БРСМ"),
    (2,2,12,  75.0, 57.0,"WOG"),  (2,2,42, 70.5,55.5,"SOCAR"),(2,2,72, 80.0,54.0,"OKKO"),
    (4,3,3,   55.0, 57.5,"ANP"),  (4,3,33, 52.5,56.0,"WOG"),  (4,3,63, 58.0,55.0,"KLO"),
    (5,4,7,   150.0,57.3,"OKKO"), (5,4,37,160.0,56.0,"WOG"),  (5,4,67,145.0,55.0,"SOCAR"),
    (6,5,10,  400.0,56.8,"KLO"),  (6,5,40,420.0,55.5,"WOG"),
    (7,6,15,  450.0,57.0,"БРСМ"), (7,6,45,430.0,55.8,"OKKO"),
    (9,7,20,  100.0,57.5,"WOG"),  (9,7,50,110.0,56.2,"SOCAR"),
]
fuel_count = sum(
    1 for veh_idx,drv_idx,days,liters,price,station in fueling_scenarios
    if make_fueling(created_vehicles[veh_idx], created_drivers[drv_idx], days, liters, price, station)
)
print(f"  ✅ Created {fuel_count} fueling records")

# ──────────────────────────────────────────────
# 5. MAINTENANCE RECORDS
# ──────────────────────────────────────────────
maintenance_data = [
    dict(
        vehicle=created_vehicles[3],  # Ford Transit — open record
        record_type="current_repair",
        opened_at=datetime.now(timezone.utc) - timedelta(days=25),
        closed_at=None, is_open=True,
        fault_description="Не запускається двигун, несправність паливної системи.",
        work_performed="",
        contractor_name="СТО Авторемонт",
        parts_cost=Decimal("0"), labor_cost=Decimal("0"),
    ),
    dict(
        vehicle=created_vehicles[0],  # Toyota Corolla — closed
        record_type="planned_to",
        opened_at=datetime.now(timezone.utc) - timedelta(days=90),
        closed_at=datetime.now(timezone.utc) - timedelta(days=85),
        is_open=False,
        fault_description="Планове ТО-2.",
        work_performed="Замінено масло, фільтри, свічки запалювання.",
        contractor_name="Офіційний дилер Toyota",
        parts_cost=Decimal("3200.00"), labor_cost=Decimal("1800.00"),
        odometer_at_closing=Decimal("138000.00"),
    ),
    dict(
        vehicle=created_vehicles[1],  # VW Crafter — closed
        record_type="current_repair",
        opened_at=datetime.now(timezone.utc) - timedelta(days=60),
        closed_at=datetime.now(timezone.utc) - timedelta(days=55),
        is_open=False,
        fault_description="Несправність гальмівної системи.",
        work_performed="Замінено гальмівні колодки та диски.",
        contractor_name="ТОВ Автосервіс Плюс",
        parts_cost=Decimal("8500.00"), labor_cost=Decimal("3200.00"),
        odometer_at_closing=Decimal("95000.00"),
    ),
    dict(
        vehicle=created_vehicles[6],  # DAF XF — major closed
        record_type="major_repair",
        opened_at=datetime.now(timezone.utc) - timedelta(days=180),
        closed_at=datetime.now(timezone.utc) - timedelta(days=160),
        is_open=False,
        fault_description="Капітальний ремонт двигуна.",
        work_performed="Замінено поршневі кільця, шатунні вкладиші, прокладку ГБЦ.",
        contractor_name="DAF Trucks Ukraine",
        parts_cost=Decimal("85000.00"), labor_cost=Decimal("35000.00"),
        odometer_at_closing=Decimal("420000.00"),
    ),
    dict(
        vehicle=created_vehicles[2],  # Sprinter — closed TO
        record_type="planned_to",
        opened_at=datetime.now(timezone.utc) - timedelta(days=30),
        closed_at=datetime.now(timezone.utc) - timedelta(days=27),
        is_open=False,
        fault_description="Планове ТО-1.",
        work_performed="Замінено моторне масло, фільтр.",
        contractor_name="Mercedes-Benz Service",
        parts_cost=Decimal("2100.00"), labor_cost=Decimal("900.00"),
        odometer_at_closing=Decimal("65000.00"),
    ),
]

maint_count = 0
for m in maintenance_data:
    veh = m.pop("vehicle")
    if not MaintenanceRecord.objects.filter(vehicle=veh, opened_at__date=m["opened_at"].date()).exists():
        MaintenanceRecord.objects.create(vehicle=veh, **m)
        maint_count += 1

print(f"  ✅ Created {maint_count} maintenance records")

# Update Ford Transit status → maintenance
transit = created_vehicles[3]
if transit.status != "maintenance":
    transit.status = "maintenance"
    transit.save(update_fields=["status"])

print("\n✅ Seed complete!")
print(f"   Vehicles:    {Vehicle.objects.count()}")
print(f"   Drivers:     {Driver.objects.count()}")
print(f"   Assignments: {VehicleAssignment.objects.count()}")
print(f"   Fuelings:    {FuelingRecord.objects.count()}")
print(f"   Maintenance: {MaintenanceRecord.objects.count()}")
