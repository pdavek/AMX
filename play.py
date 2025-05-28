import random
import datetime
import re
import os
import sys
import time
import select
from colorama import Fore, Style, init as colorama_init

# ====== GLOBAL VARIABLES ======
NAME: str = None
ROVER_POS: tuple = None
SAMPLE_POS: tuple = None
BASE_POS: tuple = None
SAMPLE_ONBOARD: bool = False
LEVEL: int = 1
GRID: list = []
CURRENT_BLOCK: str = "[X]"
CHAR_SIZE: int = 8
COST_PER_BYTE: float = 1.25
MEMORY: int = 0
EXECUTIONS: int = 1
BATTERY: int = 100
ENERGY_PER_MOVE: int = 2
LOGGING_ENABLED: bool = False
LOG_FILENAME: str = 'missions.log'
LIVE_SCRIPT_SIZE: int = 0
REMAINING_MEMORY: int = MEMORY
INPUT_DISABLED: bool = False  

colorama_init(autoreset=True)

# ====== UTILITY FUNCTIONS ======
def clear_input_buffer():
    """Clear any pending input in the buffer"""
    if os.name == 'nt':
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
    else:
        import termios
        termios.tcflush(sys.stdin, termios.TCIOFLUSH)

def disable_input():
    """Disable user input during critical operations"""
    global INPUT_DISABLED
    INPUT_DISABLED = True
    clear_input_buffer()

def enable_input():
    """Re-enable user input"""
    global INPUT_DISABLED
    INPUT_DISABLED = False

def safe_input(prompt):
    """Input wrapper that respects disabled input state"""
    while INPUT_DISABLED:
        time.sleep(0.1)
    clear_input_buffer()
    return input(prompt)

def strip_ansi(text):
    return re.sub(r'\x1B[@-_][0-?]*[ -/]*[@-~]', '', text)

# ====== MESSAGE CLASS ======
class Mess:
    """Enhanced system messages with Firewatch-inspired styling"""
    @staticmethod
    def success(message):
        return Fore.GREEN + Style.BRIGHT + message + Style.RESET_ALL

    @staticmethod
    def warning(message):
        return Fore.YELLOW + Style.BRIGHT + message + Style.RESET_ALL

    @staticmethod
    def error(message):
        return Fore.RED + Style.BRIGHT + message + Style.RESET_ALL

    @staticmethod
    def title(message):
        return Fore.WHITE + Style.BRIGHT + message + Style.RESET_ALL

    @staticmethod
    def text(message):
        return Fore.WHITE + message + Style.RESET_ALL

    @staticmethod
    def dim(message):
        return Fore.LIGHTBLACK_EX + message + Style.RESET_ALL

    @staticmethod
    def terminal(message):
        return Fore.CYAN + message + Style.RESET_ALL

    @staticmethod
    def suggestion(message):
        return Fore.BLUE + message + Style.RESET_ALL

    @staticmethod
    def hint(message):
        return Fore.WHITE + Style.DIM + message + Style.RESET_ALL

    @staticmethod
    def terminal_dim(message):
        return Fore.CYAN + Style.DIM + message + Style.RESET_ALL

    @staticmethod
    def operator(message):
        return Fore.MAGENTA + Style.BRIGHT + "Operator: " + Style.NORMAL + Fore.LIGHTWHITE_EX + message + Style.RESET_ALL

    @staticmethod
    def system(message):
        return Fore.LIGHTYELLOW_EX + Style.BRIGHT + "System: "  + Style.DIM + Fore.LIGHTYELLOW_EX + message + Style.RESET_ALL

    @staticmethod
    def mission(message):
        return Fore.LIGHTBLUE_EX + Style.BRIGHT + "Mission Control: " + Style.NORMAL + Fore.LIGHTCYAN_EX + message + Style.RESET_ALL

# ====== LOADBAR CLASS ======
class Loadbar:
    @staticmethod
    def _bar(duration: float, color: str):
        bar = "[" + " " * 20 + "]"
        disable_input()
        for i in range(1, 21):
            bar = bar[:i] + "#" + bar[i+1:]
            sys.stdout.write(color + "\r" + bar)
            sys.stdout.flush()
            time.sleep(duration / 20)
        print()
        enable_input()

    @staticmethod
    def GREEN(duration: float):
        Loadbar._bar(duration, Fore.GREEN)

    @staticmethod
    def YELLOW(duration: float):
        Loadbar._bar(duration, Fore.YELLOW)

    @staticmethod
    def RED(duration: float):
        Loadbar._bar(duration, Fore.RED)

    @staticmethod
    def CYAN(duration: float):
        Loadbar._bar(duration, Fore.CYAN)

# ====== GAME COMMANDS ======
commands = [
    "mvn",
    "mve",
    "mvs",
    "mvw",
    "obs",
    "clt",
    "drp",
    "end"
]

# ====== GAME INITIALIZATION ======
def init_game():
    global NAME
    os.system('cls' if os.name == 'nt' else 'clear')

    print(Mess.system("Initializing Amethyx Mission Terminal..."))
    time.sleep(1.2)
    print(Mess.system("Establishing quantum link..."))
    Loadbar.CYAN(1.5)

    print()
    NAME = safe_input(Mess.title("Operator name: "))
    print()
    print(Mess.system("Authenticating operator credentials..."))
    Loadbar.YELLOW(1.2)

    print(Mess.operator(f"Identity confirmed: {NAME}"))
    time.sleep(1.0)
    print(Mess.operator("Running security clearance... You'd be surprised how many try to fake these."))
    Loadbar.YELLOW(1.5)
    
    print(Mess.system(f"Operator: {NAME}, Level 3 clearance verified"))
    time.sleep(1.0)
    print(Mess.operator("Welcome to the Amethyx Remote Surface Operations program."))
    time.sleep(1.5)
    print(Mess.operator("You'll be piloting Rover XM-86 across the surface of Kepler-186f."))
    time.sleep(1.5)
    print(Mess.operator("This isn't a simulation - that hardware costs more than a lunar colony."))
    time.sleep(1.5)
    print(Mess.operator("Make smart moves. There's no undo button out there."))
    time.sleep(1.5)

    print()
    tutorial = safe_input(Mess.operator("Do you need a control refresher? (y/n) ")).strip().lower()
    print()

    if tutorial == 'n':
        print(Mess.system("Skipping tutorial sequence..."))
        Loadbar.YELLOW(1)
        start_game()
    else:
        print(Mess.system("Loading orientation protocol..."))
        Loadbar.YELLOW(1)
        start_tutorial()

def start_tutorial():
    print(Mess.operator("Let's get you familiar with Rover operations..."))
    time.sleep(1.5)
    print()
    print(Mess.operator("Your primary objective: Retrieve mineral samples and return to base."))
    time.sleep(1.5)
    print()
    print(Mess.operator("Navigation commands: mvn (north), mve (east), mvs (south), mvw (west)"))
    time.sleep(1.5)
    print()
    print(Mess.operator("Special commands: obs (scan terrain), clt (collect sample), drp (deliver sample)"))
    time.sleep(2.0)
    print()
    print(Mess.operator("Watch your battery - move carefully. Charging stations [@] are your lifeline."))
    time.sleep(2.0)
    print()
    print(Mess.operator("Unexplored areas [?] can be risky but rewarding. Proceed with caution."))
    time.sleep(2.0)
    print()
    print(Mess.operator("Remember: it's space. Memory onboard is limited. Your code must be efficient or you won't be able to run it."))
    time.sleep(2.0)
    print()
    print(Mess.operator("Each character costs 8 bytes. Normally on your smart lightbulb at home this doesnt matter. "))
    time.sleep(2.0)
    print()
    print(Mess.operator("Here it can cost up to billions worth of equipent. If your code is large, it won't be run until you shorten it. "))
    time.sleep(2.0)
    print()
    print(Mess.operator("Just to remind you of our syntax and design rules:"))
    time.sleep(2.0)
    print()
    print(Mess.operator("Each instruction go in a new line. Just like this:"))
    time.sleep(1.0)
    print()
    print(Mess.hint("mvn # moving north"))
    time.sleep(1.0)
    print()
    print(Mess.hint("mve # moving east"))
    time.sleep(1.0)
    print()
    print(Mess.hint("clt # collect sample"))
    time.sleep(1.0)
    print()
    print(Mess.operator("You can do for loops. Syntax is simple: for 4 >> mve"))
    time.sleep(1.0)
    print()
    print(Mess.operator("This basically moves the rover east 4 times in a row. You can also with other movements like:"))
    time.sleep(1.0)
    print()
    print(Mess.hint("for 3 >> mve, mvw # it will move east, then west and repeat two more times"))
    time.sleep(1.0)
    print()
    print(Mess.operator("You can also do conditional statements like:"))
    time.sleep(1.0)
    print()
    print(Mess.hint("if mve == # then mvn else mve"))
    time.sleep(1.0)
    print()
    print(Mess.operator("This simulates the move to east and if it is an obsticle, it will go north. If safe, it'll go east as planned."))
    time.sleep(1.0)
    print()
    print(Mess.operator("Lots of information but I think you're ready. Good luck out there."))
    time.sleep(1.5)
    print()
    input(Mess.suggestion("Press any key to continue"))
    start_game()

# ====== GAME CORE FUNCTIONS ======
def start_game():
    print(Mess.operator("Transmitting mission parameters..."))
    time.sleep(1.0)
    print(Mess.system("Objective: Retrieve mineral sample from designated site"))
    print(Mess.system("Secondary: Return to base with minimal energy expenditure"))
    time.sleep(1.5)
    
    print(Mess.operator("Establishing satellite uplink..."))
    Loadbar.CYAN(2.0)
    
    print(Mess.success("Rover telemetry: ONLINE"))
    time.sleep(0.7)
    print(Mess.system("Coordinates locked: Sector Gamma-" + str(random.randint(10, 99))))
    time.sleep(1.0)
    print(Mess.system("Rendering topographic map..."))
    time.sleep(1.5)

    get_map()

    print(Mess.operator(f"Alright {NAME}, you have control. Make it count."))
    write_script()

def get_map():
    global LEVEL, GRID, EXECUTIONS, BATTERY, MEMORY, ROVER_POS, SAMPLE_POS, BASE_POS, REMAINING_MEMORY
    from maps import maps

    EXECUTIONS = maps[LEVEL]['executions']
    MEMORY = maps[LEVEL]['memory']
    REMAINING_MEMORY = MEMORY
    BATTERY = maps[LEVEL]['battery']
    GRID = []  # Reset grid
    
    raw_map = maps[LEVEL]['map']

    for i, row in enumerate(raw_map):
        grid_row = []
        for j, cell in enumerate(row):
            if cell == "[R]":
                ROVER_POS = (i, j)
            elif cell == "[S]":
                SAMPLE_POS = (i, j)
            elif cell == "[B]":
                BASE_POS = (i, j)
            grid_row.append(cell)
        GRID.append(grid_row)
    
    print_map()

def print_map():
    global BATTERY
    os.system('cls' if os.name == 'nt' else 'clear')
    
    for row in GRID:
        line = ''
        for cell in row:
            if cell == '[B]':
                line += Fore.CYAN + cell + Style.RESET_ALL + ' '
            elif cell == '[S]':
                line += Fore.GREEN + cell + Style.RESET_ALL + ' '
            elif cell == '[R]':
                line += Fore.YELLOW + Style.BRIGHT + cell + Style.RESET_ALL + ' '
            elif cell == '[#]':
                line += Fore.RED + Style.BRIGHT + cell + Style.RESET_ALL + ' '
            elif cell == '[?]':
                line += Fore.BLUE + Style.BRIGHT + cell + Style.RESET_ALL + ' '
            elif cell == '[@]':
                line += Fore.LIGHTBLACK_EX + Style.DIM + cell + Style.RESET_ALL + ' '
            elif cell == '[*]':
                line += Fore.CYAN + Style.BRIGHT + cell + Style.RESET_ALL + ' '
            elif cell == '[X]':
                line += Fore.LIGHTWHITE_EX + Style.DIM + cell + Style.RESET_ALL + ' '
            else:
                line += cell + ' '
        
        print(line.rstrip())

    # Battery status with color coding
    battery_color = Fore.GREEN
    if BATTERY < 30:
        battery_color = Fore.RED
    elif BATTERY < 60:
        battery_color = Fore.YELLOW
        
    print(Mess.system(f"Battery: {battery_color}{BATTERY}%{Style.RESET_ALL}"))
    print(Mess.system(f"Available memory: {REMAINING_MEMORY} bytes"))
    print(Mess.system(f"Used memory: {MEMORY - REMAINING_MEMORY} bytes"))
    print(Mess.system(f"Code executions left: {EXECUTIONS}"))

    if SAMPLE_ONBOARD:
        print(Mess.success("Sample secured in cargo bay"))
    else:
        print(Mess.warning("Sample not collected"))

def write_script():
    global LIVE_SCRIPT_SIZE, REMAINING_MEMORY, MEMORY
    script = []
    i = 1
    while not 'end' in script:
        ins = safe_input(f"{i}: ")
        inssize = int(sum(len(s) for s in ins) * CHAR_SIZE)
        LIVE_SCRIPT_SIZE = inssize
        script.append(ins)
        i += 1

    execute_script(script)

def parse_commands(ins):
    global ROVER_POS, CURRENT_BLOCK, GRID, SAMPLE_ONBOARD, LEVEL, EXECUTIONS, BATTERY, MEMORY, REMAINING_MEMORY
    
    if_match = re.match(r"^\s*(if)\s+(\S+)\s*(==|!=|>|<|>=|<=)\s*(\S+|\'[^']+\'|\"[^\"]+\")\s+(then)\s+(\S+)\s+(else)\s+(\S+)", ins)
    for_match = re.match(r"^\s*(for)\s+(\d+)\s*(>>)\s*(.+)", ins)

    if if_match:
        condition = list(if_match.groups())
        handle_if(condition)
        return
    elif for_match:
        condition = list(for_match.groups()[:3]) + [x.strip() for x in for_match.group(4).split(',')]
        handle_for(condition)
        return
    
    if ins in commands:
        BATTERY -= ENERGY_PER_MOVE  # Deduct energy for every command
        
        match ins:
            case "mvn":
                new_pos = (ROVER_POS[0] - 1, ROVER_POS[1])
                if 0 <= new_pos[0] < len(GRID) and 0 <= new_pos[1] < len(GRID[0]):
                    # Convert previous [?] to [X]
                    if strip_ansi(GRID[ROVER_POS[0]][ROVER_POS[1]]) == "[?]":
                        GRID[ROVER_POS[0]][ROVER_POS[1]] = "[X]"
                    
                    # Clear the old rover position
                    GRID[ROVER_POS[0]][ROVER_POS[1]] = CURRENT_BLOCK
                    
                    # Save new current block
                    CURRENT_BLOCK = GRID[new_pos[0]][new_pos[1]]
                    
                    # Move rover
                    ROVER_POS = new_pos
                    GRID[ROVER_POS[0]][ROVER_POS[1]] = "[R]"
                else:
                    out_of_bounds()

            case "mve":
                new_pos = (ROVER_POS[0], ROVER_POS[1] + 1)
                if 0 <= new_pos[0] < len(GRID) and 0 <= new_pos[1] < len(GRID[0]):
                    # Convert previous [?] to [X]
                    if strip_ansi(GRID[ROVER_POS[0]][ROVER_POS[1]]) == "[?]":
                        GRID[ROVER_POS[0]][ROVER_POS[1]] = "[X]"
                    
                    GRID[ROVER_POS[0]][ROVER_POS[1]] = CURRENT_BLOCK
                    CURRENT_BLOCK = GRID[new_pos[0]][new_pos[1]]
                    ROVER_POS = new_pos
                    GRID[ROVER_POS[0]][ROVER_POS[1]] = "[R]"
                else:
                    out_of_bounds()

            case "mvs":
                new_pos = (ROVER_POS[0] + 1, ROVER_POS[1])
                if 0 <= new_pos[0] < len(GRID) and 0 <= new_pos[1] < len(GRID[0]):
                    # Convert previous [?] to [X]
                    if strip_ansi(GRID[ROVER_POS[0]][ROVER_POS[1]]) == "[?]":
                        GRID[ROVER_POS[0]][ROVER_POS[1]] = "[X]"
                    
                    GRID[ROVER_POS[0]][ROVER_POS[1]] = CURRENT_BLOCK
                    CURRENT_BLOCK = GRID[new_pos[0]][new_pos[1]]
                    ROVER_POS = new_pos
                    GRID[ROVER_POS[0]][ROVER_POS[1]] = "[R]"
                else:
                    out_of_bounds()

            case "mvw":
                new_pos = (ROVER_POS[0], ROVER_POS[1] - 1)
                if 0 <= new_pos[0] < len(GRID) and 0 <= new_pos[1] < len(GRID[0]):
                    # Convert previous [?] to [X]
                    if strip_ansi(GRID[ROVER_POS[0]][ROVER_POS[1]]) == "[?]":
                        GRID[ROVER_POS[0]][ROVER_POS[1]] = "[X]"
                    
                    GRID[ROVER_POS[0]][ROVER_POS[1]] = CURRENT_BLOCK
                    CURRENT_BLOCK = GRID[new_pos[0]][new_pos[1]]
                    ROVER_POS = new_pos
                    GRID[ROVER_POS[0]][ROVER_POS[1]] = "[R]"
                else:
                    out_of_bounds()

            case "obs":
                terrain_descriptions = [
                    "Dusty gravel field",
                    "Rocky outcrop showing iron deposits",
                    "Fine sand dunes shifting in the wind",
                    "Cracked clay surface with mineral veins",
                    "Basalt formations from ancient lava flows",
                    "Impact crater debris field",
                    "Crystalline formations glittering in starlight"
                ]

                print(Mess.system("Scanning terrain composition.."))
                Loadbar.YELLOW(1.5)
                block = strip_ansi(CURRENT_BLOCK)
                match block:
                    case "[X]":
                        td = random.choice(terrain_descriptions)
                        print(Mess.system(td))
                    case "[B]":
                        print(Mess.system("Base station - return point for samples"))
                    case "[S]":
                        print(Mess.system("Sample site: High mineral concentration detected"))
                    case "[@]":
                        print(Mess.system("Charging station: Solar-powered energy replenishment node"))
                    case "[?]":
                        print(Mess.system("Uncharted territory: Sensor readings inconclusive"))
                        print(Mess.operator("These zones are unpredictable - could be gold or could be trouble."))
                time.sleep(1.5)

            case "clt":
                if strip_ansi(CURRENT_BLOCK) == "[S]":
                    print(Mess.system("Extending drill apparatus.."))
                    Loadbar.CYAN(2.5)
                    if 0 <= ROVER_POS[0] < len(GRID) and 0 <= ROVER_POS[1] < len(GRID[0]):
                        GRID[ROVER_POS[0]][ROVER_POS[1]] = "[X]"  # Convert to path
                    print(Mess.success("Core sample secured in storage"))
                    SAMPLE_ONBOARD = True
                    time.sleep(1.0)
                    print(Mess.operator(f"Excellent work {NAME}. That sample is worth more than our annual budget. Get it back safely."))
                    time.sleep(2.5)
                else:
                    print(Mess.error("No sample detected at this location"))
                    time.sleep(1.5)

            case "drp":
                if strip_ansi(CURRENT_BLOCK) == "[B]" and SAMPLE_ONBOARD:
                    print(Mess.system("Initiating sample transfer.."))
                    Loadbar.CYAN(3.0)
                    print(Mess.success("Sample container secured!"))
                    print(Mess.operator(f"Mission accomplished {NAME}! Lab team is ecstatic."))
                    time.sleep(2.0)
                    
                    if LEVEL == 1:
                        print(Mess.operator("""
Outstanding work for a first mission. That sample shows promising exobiological signatures. 
We're advancing you to more challenging terrain - expect more complex mineral formations 
and unpredictable weather patterns. Remember: 

    Efficiency = Credits
    Carelessness = Unemployment

Your bonus for this run: €{:,.2f}. Spend it wisely.
""".format((MEMORY - LIVE_SCRIPT_SIZE) * COST_PER_BYTE)))
                        time.sleep(5.0)
                    
                    next_level = safe_input(Mess.operator("Proceed to next sector? (y/n): ")).lower()
                    if next_level == 'y':
                        LEVEL += 1
                        REMAINING_MEMORY = MEMORY
                        start_game()
                    else:
                        end_game()

                elif SAMPLE_ONBOARD:
                    print(Mess.warning("You can only deliver samples at base stations"))
                    time.sleep(1.5)
                else:
                    print(Mess.error("No sample in cargo bay"))
                    time.sleep(1.5)

    # Handle special block actions AFTER updating position
    handle_action(strip_ansi(CURRENT_BLOCK))
    print_map()

def handle_if(condition):
    """Handle conditional logic with variable comparisons"""
    global BATTERY, MEMORY, EXECUTIONS

    _, left, op, right, _, then_cmd, _, else_cmd = condition
    right = right.strip("'\"")  # Strip quotes

    def get_value(token):
        token_upper = token.upper()
        if token_upper == "BATTERY":
            return BATTERY
        elif token_upper == "MEMORY":
            return MEMORY
        elif token_upper == "EXECUTIONS":
            return EXECUTIONS
        elif token_upper == "LEVEL":
            return LEVEL
        elif token_upper == "CURRENT_BLOCK":
            block = strip_ansi(CURRENT_BLOCK)
            return block[1] if len(block) == 3 and block.startswith('[') and block.endswith(']') else block
        elif token in {"mvn", "mve", "mvs", "mvw"}:
            return simulate_block(token)
        try:
            return int(token)
        except ValueError:
            return token.strip("\"'")

    def simulate_block(move):
        dr = {"mvn": -1, "mve": 0, "mvs": 1, "mvw": 0}
        dc = {"mvn": 0, "mve": 1, "mvs": 0, "mvw": -1}
        r, c = ROVER_POS[0] + dr[move], ROVER_POS[1] + dc[move]
        if 0 <= r < len(GRID) and 0 <= c < len(GRID[0]):
            block = strip_ansi(GRID[r][c])
            return block[1] if len(block) == 3 and block.startswith('[') and block.endswith(']') else block
        return None

    def execute(cmd):
        if cmd.startswith("for"):
            match = re.match(r"for\s+(\d+)\s*>>\s*(.+)", cmd)
            if match:
                count, cmds = int(match.group(1)), [x.strip() for x in match.group(2).split(",")]
                for _ in range(count):
                    for c in cmds:
                        parse_commands(c)
        else:
            parse_commands(cmd)

    left_val = get_value(left)
    right_val = get_value(right)

    ops = {
        "==": lambda a, b: a == b,
        "!=": lambda a, b: a != b,
        ">":  lambda a, b: a > b,
        "<":  lambda a, b: a < b,
        ">=": lambda a, b: a >= b,
        "<=": lambda a, b: a <= b
    }

    if op in ops:
        condition_met = ops[op](left_val, right_val)
        execute(then_cmd if condition_met else else_cmd)
        time.sleep(0.5)

def handle_for(condition):
    """Expand loop commands into individual instructions"""
    count = int(condition[1])
    cmds = condition[3:]
    expanded = cmds * count
    for cmd in expanded:
        parse_commands(cmd)
        time.sleep(0.5)

def handle_action(block):
    global BATTERY
    match block:
        case "[?]":
            # Always convert [?] to [X] after exploration
            if 0 <= ROVER_POS[0] < len(GRID) and 0 <= ROVER_POS[1] < len(GRID[0]):
                GRID[ROVER_POS[0]][ROVER_POS[1]] = "[X]"
            GRID[ROVER_POS[0]][ROVER_POS[1]] = "[R]"
            
            outcome = random.choice(["positive", "negative"])
            if outcome == "positive":
                charge = min(15, 100 - BATTERY)
                BATTERY += charge
                print(Mess.system("Unexpected solar flare! Battery +{}%".format(charge)))
                print(Mess.operator("Good stuff! Uncharted territory can be pleasant surprise."))
                Loadbar.GREEN(2.5)
            else:
                drain = random.randint(5, 20)
                BATTERY = max(0, BATTERY - drain)
                print(Mess.warning("Magnetic interference! Battery -{}%".format(drain)))
                print(Mess.operator("Yep, sometimes the unknown can kick us in the butts."))
                Loadbar.RED(2.5)
                
                if BATTERY <= 0:
                    print(Mess.error("CRITICAL POWER FAILURE"))
                    time.sleep(1.5)
                    end_game()

        case "[@]":
            # Always charge at charging stations
            charge_amount = min(25, 100 - BATTERY)
            BATTERY += charge_amount
            
            print(Mess.system("Charging station activated +{}%".format(charge_amount)))
            if BATTERY < 30:
                print(Mess.operator("That was too close for comfort. Don't push your luck next time."))
            elif BATTERY > 90:
                print(Mess.operator("Efficient power management. Headquarters will be pleased."))
            Loadbar.GREEN(2.0)

        case "[#]":
            print(Mess.error("Disconnected!"))
            time.sleep(1)
            print(Mess.operator(f"Hey {NAME}, did something happen? I lost connection to the rover."))
            print(Mess.system("Connecting.."))
            Loadbar.YELLOW(5)
            print(Mess.error("Connection failed"))
            time.sleep(1)
            print(Mess.operator(f"{NAME}? You crashed didn't you?"))
            time.sleep(1)
            print(Mess.operator(f"S&%t.."))
            time.sleep(1)
            end_game()


        case _:
            pass  # No special action for other blocks

def out_of_bounds():
    global GRID, ROVER_POS
    print(Mess.system("Signal weakening..."))
    Loadbar.RED(1.5)
    print(Mess.system("Connection unstable..."))
    Loadbar.RED(1.5)
    print(Mess.error("LINK TERMINATED"))
    time.sleep(1.0)
    print(Mess.operator(f"{NAME}, we've lost telemetry! The rover's gone dark beyond the perimeter."))
    time.sleep(3.0)
    end_game()

def execute_script(script):
    global MEMORY, CHAR_SIZE, REMAINING_MEMORY, EXECUTIONS, LIVE_SCRIPT_SIZE
    print(Mess.system("Compiling instructions..."))
    Loadbar.YELLOW(1.0)

    script_size = int(sum(len(s) for s in script) * CHAR_SIZE)
    LIVE_SCRIPT_SIZE = script_size
    EXECUTIONS -= 1

    if script_size > REMAINING_MEMORY:
        print(Mess.error("Memory overflow! Script too large."))
        print(Mess.system(f"Required: {script_size} bytes | Available: {REMAINING_MEMORY} bytes"))
        time.sleep(3.0)
        write_script()
    else:
        REMAINING_MEMORY -= script_size
        print(Mess.success(f"Script loaded ({script_size} bytes)"))
        time.sleep(1.0)
        
        for ins in script:
            parse_commands(ins)
            time.sleep(0.3)
            
            # Check for critical conditions
            if BATTERY <= 0:
                print(Mess.error("POWER DEPLETED"))
                time.sleep(1.5)
                end_game()
            elif EXECUTIONS <= 0:
                print(Mess.error("EXECUTION LIMIT REACHED"))
                time.sleep(1.5)
                end_game()

        if EXECUTIONS > 0:
            write_script()

def end_game():
    print(Mess.system("Terminating mission protocol..."))
    Loadbar.RED(2.0)
    # print(Mess.operator(f"Session ended. Good work out there, {NAME}."))
    time.sleep(2.0)
    sys.exit(0)

# ====== MAIN EXECUTION ======
if __name__ == '__main__':
    init_game()