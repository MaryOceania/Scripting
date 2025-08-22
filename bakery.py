# BAKERY INVENTORY SYSTEM
# ==========================
# This program allows you to manage an inventory of ingredients with unit conversion.
# Features: add ingredients, consume quantities, view inventory, and search for items.
# Supports mass (mg, g, kg, oz, lb) and volume (ml, l, tsp, tbsp) unit conversions.

import sys
from typing import Dict, Optional, Tuple, List

# UNIFIED CONVERSION FACTORS
CONVERSION_FACTORS = {
    'mass': {
        'mg': 0.001,
        'g': 1,
        'kg': 1000,
        'oz': 28.3495,
        'lb': 453.592
    },
    'volume': {
        'ml': 1,
        'l': 1000,
        'tsp': 4.92892,
        'tbsp': 14.7868
    }
}

# Inventory dictionary
inventory: Dict[str, Dict[str, float]] = {}



# Helper Functions
#Ask user to confirm (yes/no)
def confirm(prompt: str) -> bool:
    return input(f"{prompt} (y/n): ").strip().lower() in ["y", "yes"]

# Return all available units
def get_all_units(as_string: bool = False) -> List[str] or str:
    units = [unit for cat in CONVERSION_FACTORS.values() for unit in cat]
    return ", ".join(units) if as_string else units
    
# Determine the unit type (mass or volume)
def get_unit_type(unit: str) -> Optional[str]:
    for category, units in CONVERSION_FACTORS.items():
        if unit in units:
            return category
    return None

# Convert between compatible units
def convert_unit(value: float, from_unit: str, to_unit: str) -> Optional[float]:
    from_type = get_unit_type(from_unit)
    to_type = get_unit_type(to_unit)

    if from_type != to_type or from_type is None:
        return None
    base_value = value * CONVERSION_FACTORS[from_type][from_unit]
    return base_value / CONVERSION_FACTORS[to_type][to_unit]
    
# Convert to bigger unit if possible
def auto_convert(quantity: float, unit: str) -> Tuple[float, str]:
    unit_type = get_unit_type(unit)
    if not unit_type:
        return quantity, unit

    # Sort units by conversion factor in ascending order
    sorted_units = sorted(CONVERSION_FACTORS[unit_type].items(), key=lambda x: x[1])
    # Check if we can convert to a larger unit
    for bigger_unit, factor in reversed(sorted_units):
        if quantity >= factor:
            return round(quantity / factor, 2), bigger_unit
    return quantity, unit

# Ensure user inputs a positive float
def get_validated_positive_float(prompt: str) -> float:
    while True:
        try:
            value = float(input(prompt))
            if value > 0: 
                return value
            print("Value must be greater than zero.")
        except ValueError:
            print("Invalid number. Please enter a valid numeric value.")
                        
# Inventory Operations
# Add a new ingredient or update an existing one
def add_ingredient():
    name = input("Enter ingredient name: ").strip().lower()
    if not name:
        print("Ingredient name cannot be empty.")
        return

    unit = input(f"Enter unit ({get_all_units(True)}): ").strip().lower()
    if unit not in get_all_units():
        print("Unknown unit. Please choose from:", get_all_units(True))
        return

    quantity = get_validated_positive_float(f"Quantity in {unit}: ")

    if name in inventory:
        current_unit = inventory[name]['unit']
        current_quantity = inventory[name]['quantity']

        # If current quantity is zero, we can change the unit
        if current_quantity == 0:
            inventory[name] = {'unit': unit, 'quantity': quantity}
            print(f"'{name}' updated to {quantity} {unit}.")
        else:
            converted_quantity = convert_unit(quantity, unit, current_unit)
            if converted_quantity is None:
                print(f"Cannot add. Unit '{unit}' is incompatible with existing unit '{current_unit}'.")
                return
            inventory[name]['quantity'] += converted_quantity
            print(f"Added {quantity} {unit} to existing {name}. New quantity: {inventory[name]['quantity']:.2f} {current_unit}")
    else:
        # If ingredient doesn't exist, create it
        inventory[name] = {'quantity': quantity, 'unit': unit}
        print(f"{quantity} {unit} of {name} have been added to the inventory.") 

# Display the current inventory
def view_inventory():
    print("\n--- INVENTORY ---")
    # Consider inventory empty if no items or all quantities are zero
    if not inventory or all(data['quantity'] == 0 for data in inventory.values()):
        print("The inventory is empty.")
        return

    for name, data in inventory.items():     # there are ingredients (some have zero)
        qty, unit = data['quantity'], data['unit']
        print(f"{name.capitalize():<15} : {qty:>8.2f} {unit}")
        converted_qty, bigger_unit = auto_convert(qty, unit)
        if bigger_unit != unit:
            print(f"   ≈ {converted_qty:.2f} {bigger_unit}")
                            
# Consume a quantity from inventory
def consume_ingredient():
    name = input("Enter ingredient to consume: ").strip().lower()
    if name not in inventory:
        print("Ingredient not found.")
        return
    consumption_unit = input(f"Enter unit of consumption ({get_all_units(True)}): ").strip().lower()
    if consumption_unit not in get_all_units():
        print("Unknown unit.")
        return
    consumption_quantity = get_validated_positive_float(f"Enter quantity in {consumption_unit}: ")
    current_data = inventory[name]
    converted_quantity = convert_unit(consumption_quantity, consumption_unit, current_data['unit'])
    
    if converted_quantity is None:
        print("Incompatible units.")
        return

    if converted_quantity > current_data['quantity']:
        print(f"Error: Not enough {name} in stock. Available: {current_data['quantity']} {current_data['unit']}")
        return
    
    inventory[name]['quantity'] -= converted_quantity
    print(f"{consumption_quantity} {consumption_unit} of {name} has been consumed, remaining: {inventory[name]['quantity']:.2f} {current_data['unit']}")
   
# Search for an ingredient
def search_ingredient():
    while True:
        name = input("Enter ingredient to search: ").strip().lower()
        if name in inventory:
            data = inventory[name]
            qty, unit = data['quantity'], data['unit']
            print(f"{name.capitalize()} - {qty:.2f} {unit}")
            converted_qty, bigger_unit = auto_convert(qty, unit)
            if bigger_unit != unit:
                print(f"   ≈ {converted_qty:.2f} {bigger_unit}")
            break
        else:
            print("Ingredient not found. Try again.")
            if not confirm("Do you want to try another search?"):
                break

# Main menu interface
def main_menu():
    while True:
        print("\n--- MAIN MENU ---")
        print("1. Add Ingredient")
        print("2. View Inventory")
        print("3. Consume Ingredient")
        print("4. Search Ingredient")
        print("5. Exit")
        
        choice = input("Choose an option (1-5): ").strip()
        if choice == '1':
            add_ingredient()
        elif choice == '2':
            view_inventory()
        elif choice == '3':
            consume_ingredient()
        elif choice == '4':
            search_ingredient()
        elif choice == '5':
            if confirm("Are you sure you want to exit?"):
               print("Exiting…") 
               sys.exit()
            else:
               print("Returning to main menu...")
        else:
            print("Invalid option. Please try again.")

# Run the application
if __name__ == "__main__":
    main_menu()
