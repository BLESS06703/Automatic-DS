# diagnostic_engine.py - Complete diagnostic logic for all systems
from config import Config

class DiagnosticEngine:
    
    @staticmethod
    def diagnose_engine(symptoms):
        """Complete engine diagnostic"""
        diagnosis = {
            'symptoms': [],
            'results': '',
            'tools': [],
            'action_plan': [],
            'severity': 'low',
            'estimated_parts': []
        }
        
        # Cooling system check
        if symptoms.get('overheating') in ['yes', 'y', 'true']:
            diagnosis['symptoms'].append("Engine overheating")
            diagnosis['tools'].extend(['Coolant pressure tester', 'Infrared thermometer', 'Coolant hydrometer'])
            diagnosis['action_plan'].extend([
                "1. Perform cooling system pressure test (should hold 15-20 PSI)",
                "2. Check coolant level and condition with hydrometer",
                "3. Verify thermostat operation (should open at 180-195°F)",
                "4. Test water pump flow and check for leaks",
                "5. Inspect radiator for blockages or damage",
                "6. Check cooling fan operation (electric or clutch)"
            ])
            diagnosis['results'] += "⚠️ COOLING SYSTEM ISSUE: Possible low coolant, radiator blockage, thermostat failure, or water pump problem.\n"
            diagnosis['severity'] = 'high'
            diagnosis['estimated_parts'].append({'part': 'Thermostat', 'price': 25.99})
            diagnosis['estimated_parts'].append({'part': 'Water Pump', 'price': 89.99})
        
        # Smoke/exhaust check
        if symptoms.get('smoke') in ['yes', 'y', 'true']:
            smoke_color = symptoms.get('smoke_color', 'white')
            diagnosis['symptoms'].append(f"Exhaust smoke ({smoke_color})")
            diagnosis['tools'].extend(['Compression tester', 'Leak-down tester', 'Borescope', 'Cylinder leak detector'])
            
            if smoke_color == 'blue':
                diagnosis['results'] += "💨 BLUE SMOKE: Oil burning issue - Worn piston rings or valve seals.\n"
                diagnosis['estimated_parts'].append({'part': 'Piston Rings Set', 'price': 150.00})
                diagnosis['estimated_parts'].append({'part': 'Valve Seal Set', 'price': 45.99})
            elif smoke_color == 'white':
                diagnosis['results'] += "☁️ WHITE SMOKE: Coolant burning - Blown head gasket or cracked cylinder head.\n"
                diagnosis['estimated_parts'].append({'part': 'Head Gasket Set', 'price': 89.99})
                diagnosis['severity'] = 'critical'
            elif smoke_color == 'black':
                diagnosis['results'] += "⬛ BLACK SMOKE: Rich fuel mixture - Faulty injectors or sensors.\n"
                diagnosis['estimated_parts'].append({'part': 'Fuel Injector', 'price': 120.00})
                diagnosis['estimated_parts'].append({'part': 'O2 Sensor', 'price': 65.99})
            
            diagnosis['action_plan'].extend([
                "1. Run compression test on all cylinders (min 120 PSI, variance <15%)",
                "2. Perform leak-down test to identify source",
                "3. Inspect spark plugs for oil/coolant fouling",
                "4. Check PCV system operation",
                "5. Perform cylinder leakage test"
            ])
            diagnosis['severity'] = max(diagnosis['severity'], 'high')
        
        # Unusual noise check
        if symptoms.get('noise') in ['yes', 'y', 'true']:
            noise_type = symptoms.get('noise_type', 'unknown')
            diagnosis['symptoms'].append(f"Unusual noise ({noise_type})")
            diagnosis['tools'].extend(['Mechanic stethoscope', 'Belt tension gauge', 'Sound analyzer'])
            
            if noise_type == 'knocking':
                diagnosis['results'] += "🔊 KNOCKING NOISE: Possible rod knock or main bearing failure - Serious internal damage.\n"
                diagnosis['severity'] = 'critical'
            elif noise_type == 'squealing':
                diagnosis['results'] += "🔊 SQUEALING NOISE: Belt or pulley issue - Worn serpentine belt or tensioner.\n"
                diagnosis['estimated_parts'].append({'part': 'Serpentine Belt', 'price': 35.99})
            elif noise_type == 'ticking':
                diagnosis['results'] += "🔊 TICKING NOISE: Lifter or valve train issue - Low oil pressure or worn components.\n"
            
            diagnosis['action_plan'].extend([
                "1. Locate noise source with mechanic stethoscope",
                "2. Inspect belts, pulleys, and tensioners",
                "3. Check oil pressure and level",
                "4. Remove drive belt to isolate accessory noise",
                "5. Inspect timing components"
            ])
        
        # Check engine light
        if symptoms.get('check_light') in ['yes', 'y', 'true']:
            diagnosis['symptoms'].append("Check engine light active")
            diagnosis['tools'].extend(['OBD2 Scanner', 'Multimeter', 'Diagnostic software'])
            diagnosis['action_plan'].extend([
                "1. Connect OBD2 scanner and read trouble codes",
                "2. Document all Diagnostic Trouble Codes (DTCs)",
                "3. Check freeze frame data for conditions when code set",
                "4. Perform manufacturer-specified diagnostic tests",
                "5. Verify repair with code clearing and retest"
            ])
            diagnosis['results'] += "⚠️ ELECTRONIC FAULT: OBD2 scanning required for specific codes.\n"
            diagnosis['severity'] = max(diagnosis['severity'], 'medium')
        
        # No issues found
        if not diagnosis['symptoms']:
            diagnosis['results'] = "✅ No immediate issues found during initial inspection."
            diagnosis['action_plan'] = [
                "1. Perform routine maintenance check",
                "2. Test drive to verify normal operation",
                "3. Check service records for scheduled maintenance",
                "4. Recommend oil change if due"
            ]
        
        return diagnosis
    
    @staticmethod
    def diagnose_battery(symptoms):
        """Complete battery and charging system diagnostic"""
        diagnosis = {
            'symptoms': [],
            'results': '',
            'tools': [],
            'action_plan': [],
            'severity': 'low',
            'estimated_parts': []
        }
        
        # Starting issues
        if symptoms.get('start') in ['yes', 'y', 'true']:
            if symptoms.get('lights') in ['yes', 'y', 'true']:
                diagnosis['symptoms'].append("Engine won't crank + dim lights")
                diagnosis['tools'].extend(['Multimeter', 'Battery load tester', 'Jump starter', 'Battery charger'])
                diagnosis['action_plan'].extend([
                    "1. Measure battery voltage (12.6V+ = good, 12.4V = low, <12V = dead)",
                    "2. Perform battery load test (should maintain 9.6V+ during crank)",
                    "3. Jump start vehicle to test",
                    "4. If jump works, test alternator output (13.7-14.7V when running)",
                    "5. Check for parasitic draw (should be <50mA when off)"
                ])
                diagnosis['results'] += "🔋 DEAD OR WEAK BATTERY: Battery cannot provide sufficient power.\n"
                diagnosis['severity'] = 'high'
                diagnosis['estimated_parts'].append({'part': 'Battery', 'price': 189.99})
            else:
                diagnosis['symptoms'].append("Intermittent starting")
                diagnosis['tools'].extend(['Wire brush', 'Wrench set', 'Dielectric grease', 'Battery terminal cleaner'])
                diagnosis['action_plan'].extend([
                    "1. Disconnect negative battery cable first",
                    "2. Clean battery terminals and cable ends with wire brush",
                    "3. Check for corrosion on cable ends (white/green powder)",
                    "4. Tighten connections to manufacturer spec (usually 8-10 Nm)",
                    "5. Apply dielectric grease to prevent future corrosion",
                    "6. Test all ground connections"
                ])
                diagnosis['results'] += "🔌 POOR CONNECTION: Corroded or loose battery terminals.\n"
                diagnosis['severity'] = 'medium'
        
        # Clicking sound
        if symptoms.get('clicks') in ['yes', 'y', 'true']:
            diagnosis['symptoms'].append("Rapid clicking when starting")
            diagnosis['tools'].extend(['Multimeter', 'Battery analyzer', 'Carbon pile tester'])
            diagnosis['action_plan'].extend([
                "1. Check battery voltage during cranking attempt",
                "2. Measure battery Cold Cranking Amps (CCA)",
                "3. Compare CCA to manufacturer specification",
                "4. If CCA below 70% of rated, replace battery"
            ])
            diagnosis['results'] += "⚡ INSUFFICIENT POWER: Battery charge too low for starter engagement.\n"
            diagnosis['severity'] = 'high'
        
        # Battery age
        if symptoms.get('age') in ['yes', 'y', 'true']:
            diagnosis['symptoms'].append("Battery age > 3 years")
            diagnosis['tools'].extend(['Battery analyzer', 'Hydrometer', 'Load tester'])
            diagnosis['action_plan'].extend([
                "1. Check battery date code (letter+number on case)",
                "2. Perform capacity test",
                "3. Test specific gravity of each cell (if serviceable)",
                "4. Load test at 50% of CCA rating",
                "5. Recommend replacement if failing or >5 years old"
            ])
            diagnosis['results'] += "📅 AGE-RELATED DEGRADATION: Battery nearing end of service life (3-5 years typical).\n"
            diagnosis['estimated_parts'].append({'part': 'Battery', 'price': 189.99})
        
        # No issues
        if not diagnosis['symptoms']:
            diagnosis['results'] = "✅ Battery and charging system appear healthy."
            diagnosis['action_plan'] = [
                "1. Verify alternator output (13.7-14.7V at 2000 RPM)",
                "2. Test for parasitic draw (should be <50mA)",
                "3. Inspect drive belt condition and tension",
                "4. Check battery terminals for any corrosion",
                "5. Perform battery load test as preventative maintenance"
            ]
        
        return diagnosis
    
    @staticmethod
    def diagnose_starter(symptoms):
        """Complete starter system diagnostic"""
        diagnosis = {
            'symptoms': [],
            'results': '',
            'tools': [],
            'action_plan': [],
            'severity': 'low',
            'estimated_parts': []
        }
        
        # Click but no crank
        if symptoms.get('click') in ['yes', 'y', 'true'] and symptoms.get('crank') in ['no', 'n', 'false']:
            diagnosis['symptoms'].append("Single click or rapid click, no crank")
            diagnosis['tools'].extend(['Multimeter', 'Remote starter switch', 'Test light', 'Ammeter clamp'])
            diagnosis['action_plan'].extend([
                "1. Perform voltage drop test on battery cables (should be <0.5V)",
                "2. Test starter relay with test light",
                "3. Bypass starter relay to test starter directly",
                "4. Measure starter current draw (should be 150-200A)",
                "5. Remove and bench test starter if necessary",
                "6. Check starter mounting bolts (ground path)"
            ])
            
            if symptoms.get('lights') in ['no', 'n', 'false']:
                diagnosis['results'] += "🔋 WEAK BATTERY: Headlights dim, battery likely discharged.\n"
                diagnosis['severity'] = 'high'
            else:
                diagnosis['results'] += "⚡ STARTER MOTOR FAILURE: Electrical power present but starter not engaging.\n"
                diagnosis['estimated_parts'].append({'part': 'Starter Motor', 'price': 159.99})
                diagnosis['severity'] = 'high'
        
        # No click, no crank
        elif symptoms.get('click') in ['no', 'n', 'false'] and symptoms.get('crank') in ['no', 'n', 'false']:
            diagnosis['symptoms'].append("No sound, no crank")
            diagnosis['tools'].extend(['Test light', 'Wiring diagram', 'Fuse puller', 'Relay tester'])
            diagnosis['action_plan'].extend([
                "1. Check starter fuse in fuse box",
                "2. Test starter relay operation (should click when key turned)",
                "3. Check ignition switch signal wire (should have 12V in START)",
                "4. Verify neutral safety switch (automatic transmission)",
                "5. Check clutch safety switch (manual transmission)",
                "6. Test for 12V at starter solenoid when key turned"
            ])
            
            if symptoms.get('lights') in ['yes', 'y', 'true']:
                diagnosis['results'] += "🔌 CONTROL CIRCUIT FAILURE: Battery good but starter not receiving signal.\n"
                diagnosis['estimated_parts'].append({'part': 'Starter Relay', 'price': 15.99})
                diagnosis['estimated_parts'].append({'part': 'Ignition Switch', 'price': 45.99})
            else:
                diagnosis['results'] += "⚠️ COMPLETE POWER LOSS: No power to starter circuit.\n"
            
            diagnosis['severity'] = 'high'
        
        # Cranks but no start
        elif symptoms.get('crank') in ['yes', 'y', 'true']:
            diagnosis['symptoms'].append("Engine cranks normally but won't start")
            diagnosis['tools'].extend(['Fuel pressure gauge', 'Spark tester', 'Noid light', 'Compression tester'])
            diagnosis['action_plan'].extend([
                "1. Check for spark at spark plugs (should have strong blue spark)",
                "2. Test fuel pressure at rail (should be 40-60 PSI depending on vehicle)",
                "3. Check injector pulse with noid light",
                "4. Scan for engine codes (crank/cam sensor issues)",
                "5. Check crankshaft position sensor signal",
                "6. Verify timing belt/chain hasn't broken"
            ])
            diagnosis['results'] += "✅ STARTER OPERATIONAL: Problem is in fuel or ignition system.\n"
            diagnosis['severity'] = 'medium'
        
        # Burning smell
        if symptoms.get('smell') in ['yes', 'y', 'true']:
            diagnosis['symptoms'].append("Burning smell from starter area")
            diagnosis['tools'].extend(['Infrared thermometer', 'Amperage clamp meter', 'Thermal camera'])
            diagnosis['action_plan'].extend([
                "🚨 STOP! Do not attempt to start again immediately!",
                "1. Allow starter to cool for minimum 15 minutes",
                "2. Check for engine seizure (try turning crankshaft manually)",
                "3. Measure starter amperage draw during crank attempt",
                "4. Check for excessive resistance in engine",
                "5. Inspect flywheel/flexplate for damaged teeth",
                "6. Replace starter if amperage exceeds 250A or if smoking"
            ])
            diagnosis['results'] += "🔥⚠️ STARTER OVERHEATING: Internal short or engine mechanical seizure!\n"
            diagnosis['severity'] = 'critical'
            diagnosis['estimated_parts'].append({'part': 'Starter Motor', 'price': 159.99})
        
        return diagnosis
    
    @staticmethod
    def calculate_cost(diagnosis, labor_hours, parts_cost):
        """Calculate total cost estimate"""
        subtotal = (labor_hours * Config.HOURLY_RATE) + parts_cost
        tax = subtotal * Config.TAX_RATE
        total = subtotal + tax
        
        return {
            'labor_hours': labor_hours,
            'labor_cost': labor_hours * Config.HOURLY_RATE,
            'parts_cost': parts_cost,
            'subtotal': subtotal,
            'tax': tax,
            'total': total
        }
