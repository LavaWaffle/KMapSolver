def enumerate(iterable, start=0):
    # Initialize the counter
    count = start
    # Loop through the iterable
    for item in iterable:
        yield count, item  # Yield the index and the item
        count += 1  # Increment the counter

def merge_minterms(minterm1: str, minterm2: str) -> str:
    """
    Merges two minterms by comparing each bit position.
    If bits are the same, keeps the bit.
    If bits differ, replaces with a dash ('-').
    
    Args:
        minterm1: First minterm string (e.g., '1001')
        minterm2: Second minterm string (e.g., '1011')
    Returns:
        Merged minterm string (e.g., '10-1')
    """
    merged_minterm = ""
    for i in range(len(minterm1)):
        if minterm1[i] == minterm2[i]:
            merged_minterm += minterm1[i]
        else:
            merged_minterm += '-'
    return merged_minterm

def check_dashes_align(minterm1: str, minterm2: str) -> bool:
    """
    Checks if dashes in two minterms are in the same positions.
    Minterms can only be merged if their dashes align.
    
    Args:
        minterm1: First minterm string (e.g., '10-1')
        minterm2: Second minterm string (e.g., '1-11')
    Returns:
        True if dashes align, False otherwise (e.g., False for '10-1' and '1-11')
    """
    for i in range(len(minterm1)):
        if minterm1[i] != '-' and minterm2[i] == '-':
            return False
        elif minterm1[i] == '-' and minterm2[i] != '-':
            return False
    return True

def check_minterm_differences(minterm1: str, minterm2: str) -> bool:
    """
    Checks if two minterms differ in exactly one position (excluding dashes).
    Converts minterms to integers and uses bitwise operations to check.
    
    Args:
        minterm1: First minterm string (e.g., '1001')
        minterm2: Second minterm string (e.g., '1011')
    Returns:
        True if minterms differ in exactly one position, False otherwise (e.g., True for '1001' and '1011')
    """

    # Convert '-' -> '0'
    m1 = int(''.join('0' if c == '-' else c for c in minterm1), 2)
    m2 = int(''.join('0' if c == '-' else c for c in minterm2), 2)

    # Ensure minterms differ in exactly one position
    res = m1 ^ m2
    return res != 0 and (res & (res - 1)) == 0

def get_prime_implicants(minterms: list[str]) -> list[str]:
    """
    Finds all prime implicants by repeatedly merging compatible minterms.
    A prime implicant is a minterm that cannot be merged further.
    
    Args:
        minterms: List of minterm strings
    Returns:
        List of prime implicant strings
    """

    # Initialize vars
    prime_implicants = []
    merges = [False for _ in minterms]
    number_of_merges = 0
    merged_minterm = ""
    minterm1 = ""
    minterm2 = ""

    # For each minterm, check if it can be merged with another
    for i in range(len(minterms)):
        for c in range(i+1, len(minterms)):
            minterm1 = minterms[i]
            minterm2 = minterms[c]
            
            if check_dashes_align(minterm1, minterm2) and check_minterm_differences(minterm1, minterm2):
                # Dashes align and minterms differ in exactly one position!
                merged_minterm = merge_minterms(minterm1, minterm2)

                # Add to list of prime implicants if it's not already there
                if merged_minterm not in prime_implicants:
                    prime_implicants.append(merged_minterm)
                number_of_merges+=1
                merges[i] = True
                merges[c] = True
    
    # Add any unmerged minterms to the list of prime implicants
    for j in range(len(minterms)):
        if not merges[j] and minterms[j] not in prime_implicants:
            prime_implicants.append(minterms[j])
    
    # If we can furhter merge minterms, recurse
    if number_of_merges > 0:
        return get_prime_implicants(prime_implicants)
    else:
        return prime_implicants

def create_prime_implicant_chart(prime_implicants: list[str], minterms: list[str]) -> dict[str, list[str]]:
    """
    Creates a chart showing which minterms are covered by each prime implicant.
    For each prime implicant, checks if it covers each minterm and creates a boolean array.
    
    Args:
        prime_implicants: List of prime implicant strings
        minterms: List of minterm strings
    Returns:
        Dictionary mapping each prime implicant to its coverage array
    """

    prime_implicant_chart = {}
    
    # Initialize chart
    for i in range(len(prime_implicants)):
        prime_implicant_chart[prime_implicants[i]] = []
    
    # For each prime implicant, check if it covers each midterm
    for i in range(len(list(prime_implicant_chart.keys()))):
        prime_implicant = list(prime_implicant_chart.keys())[i]

        for j in range(len(minterms)):
            # Does this prime implicant match this midterm?
            failed = False
            for k in range(len(minterms[j])):
                if prime_implicant[k] == '-':
                    continue
                minterm = minterms[j][k]
                if (minterm != prime_implicant[k]):
                    failed = True
                    break
            
            # If it does, mark the column as covered
            if not failed:
                prime_implicant_chart[prime_implicant].append(True)
            else:
                prime_implicant_chart[prime_implicant].append(False)

    return prime_implicant_chart


def find_valid_combinations(coverage_dict):
    """
    Finds all valid combinations of prime implicants that cover all minterms.
    Tests combinations of all possible lengths to find those that provide complete coverage.
   
    Args:
        coverage_dict: Dictionary mapping prime implicants to their coverage arrays
    Returns:
        List of valid combinations (each combination is a list of prime implicants)
    """
    def combinations(iterable, r):
        # Get the length of the iterable
        n = len(iterable)
        # Create a list to hold the combinations
        result = []
        
        # Helper function to generate combinations
        def combo(start, path):
            if len(path) == r:
                result.append(path)
                return
            for i in range(start, n):
                combo(i + 1, path + [iterable[i]])
        
        combo(0, [])
        return result
    
    # Get all possible implicants
    implicants = list(coverage_dict.keys())
    num_columns = len(list(coverage_dict.values())[0])
    valid_solutions = []
    
    # Try combinations of different lengths, from 1 up to total number of implicants
    for length in range(1, len(implicants) + 1):
        # Get all possible combinations of current length
        for combo in combinations(implicants, length):
            # Check if this combination covers all columns
            is_valid = True
            for col in range(num_columns):
                # Check if any implicant in the combination covers this column
                column_covered = False
                for imp in combo:
                    if coverage_dict[imp][col]:
                        column_covered = True
                        break
                
                # If no implicant covers this column, combination is invalid
                if not column_covered:
                    is_valid = False
                    break
            
            # If we found a valid combination, add it to solutions
            if is_valid:
                valid_solutions.append(list(combo))
        
        # If we found valid solutions at this length, we can stop
        # (as longer combinations would be redundant)
        if valid_solutions:
            break
    
    return valid_solutions

minterms = [
    {
        'binary': "0100",
        'required': True,
    },
    {
        'binary': "1000",
        'required': True,
    },
    {
        'binary': "1001",
        'required': False,
    },
    {
        'binary': "1010",
        'required': True,
    },
    {
        'binary': "1100",
        'required': True,
    },
    {
        'binary': "1011",
        'required': True,
    },
    {
        'binary': "1110",
        'required': False,
    },
    {
        'binary': "1111",
        'required': True
    }
]

def request_kmap_size() -> int:
    return int(input("Please enter kmap size \n1=2x2\n2=2x4\n3=4x4\n"))

def request_analysis_type() -> int:
    return int(input("Please enter analysis type \n1=SOP\n2=POS\n"))

def request_kmap_input(kmap_size: int) -> list[dict]:
    minterms = []

    # Define dimensions based on kmap_size
    if kmap_size == 1:  # 2x2
        rows, cols = 2, 2
        bits = 2
    elif kmap_size == 2:  # 2x4
        rows, cols = 2, 4
        bits = 3
    elif kmap_size == 3:  # 4x4
        rows, cols = 4, 4
        bits = 4
    else:
        raise ValueError("Invalid kmap size. Must be 1 (2x2), 2 (2x4), or 3 (4x4)")
    
    # Generate all binary combinations in Gray code order
    def gray_code_order(n):
        if n == 0:
            return ['']
        
        smaller = gray_code_order(n-1)
        result = []
        # Reflect and prefix
        for i in range(len(smaller)):
            result.append('0' + smaller[i])
        for i in range(len(smaller)-1, -1, -1):
            result.append('1' + smaller[i])
        return result
    
    # Generate row and column gray codes
    row_codes = gray_code_order(bits//2)
    col_codes = gray_code_order((bits+1)//2)
    
    print("Enter values for " + str(rows) + "x" + str(cols) + " K-map\n1=True\n0=False\nX=don't care")
    
    # Collect input for each cell
    for row in row_codes:
        for col in col_codes:
            binary = row + col
            while True:
                value = input(str(binary) + "= ").upper()
                if value in ['0', '1', '2', 'X']:
                    break
                print("Invalid input. Please enter 0, 1, or X")
            
            if value in ['1', '2', 'X']:
                minterms.append({
                    'binary': binary,
                    'required': True if value == '1' else False
                })
    
    return minterms

def print_kmap(minterms: list[dict]) -> None:
    # Determine kmap size based on binary length
    binary_length = len(minterms[0]['binary'])
    
    if binary_length == 2:
        rows, cols = 2, 2
        kmap = [[' ' for _ in range(2)] for _ in range(2)]
        col_header = ['0', '1']
        row_header = ['0', '1']
    elif binary_length == 3:
        rows, cols = 2, 4
        kmap = [[' ' for _ in range(4)] for _ in range(2)]
        col_header = ['00', '01', '11', '10']
        row_header = ['0', '1']
    elif binary_length == 4:
        rows, cols = 4, 4
        kmap = [[' ' for _ in range(4)] for _ in range(4)]
        col_header = ['00', '01', '11', '10']
        row_header = ['00', '01', '11', '10']
    else:
        raise ValueError("Invalid minterm binary length")
    
    # Fill the K-map
    for term in minterms:
        binary = term['binary']
        if binary_length == 2:
            row = int(binary[0])
            col = int(binary[1])
        elif binary_length == 3:
            row = int(binary[0])
            col_bits = binary[1:]
            col = col_header.index(col_bits)
        else:  # binary_length == 4
            row_bits = binary[0:2]
            col_bits = binary[2:]
            row = row_header.index(row_bits)
            col = col_header.index(col_bits)
        
        # Set the value based on required field
        if term['required'] == False:
            kmap[row][col] = 'X'
        elif term['required']:
            kmap[row][col] = '1'
        else:
            kmap[row][col] = '0'
    
    # Fill remaining empty spaces with '0'
    for i in range(rows):
        for j in range(cols):
            if kmap[i][j] == ' ':
                kmap[i][j] = '0'
    
    # Print the K-map
    # Print column headers
    print('   ', end='')
    for header in col_header:
        print('  ' + header, end='')
    print()
    
    # Print rows with headers
    for i in range(rows):
        print(' ' + row_header[i] + ' ', end='')
        for j in range(cols):
            print('  ' + kmap[i][j] + ' ', end='')
        print()

def format(value, fmt_spec):
    if fmt_spec.startswith('0') and 'b' in fmt_spec:
        zero_padding = int(fmt_spec[1:fmt_spec.index('b')])
        # Manual binary conversion with zero padding
        binary_str = bin(value)[2:]  # Convert to binary and remove '0b'
        return '0' * (zero_padding - len(binary_str)) + binary_str
    return str(value)

def transform_minterms(minterms: list[dict]) -> list[dict]:
    # First, get the length of binary strings to determine total possible combinations
    binary_length = len(minterms[0]['binary'])
    
    # Create a set of all possible binary combinations
    all_binary = {format(i, '0' + str(binary_length) + 'b') for i in range(2 ** binary_length)}
    
    # Create sets for existing binaries
    existing_binaries = {term['binary'] for term in minterms}
    # false_binaries = {term['binary'] for term in minterms if term['required'] is False}
    
    # Find missing binaries (ones not in the original input)
    missing_binaries = all_binary - existing_binaries
    
    # Create new minterms list starting with the False required terms
    new_minterms = [term for term in minterms if term['required'] is False]
    
    # Add missing binaries as True required terms
    for binary in missing_binaries:
        new_minterms.append({
            'binary': binary,
            'required': True
        })
    
    # Sort by binary value to maintain order
    new_minterms.sort(key=lambda x: x['binary'])
    
    return new_minterms

def flip_binary_strings(arr: list[str]) -> list[str]:
    flipped = []
    for s in arr:
        # Create new string by replacing each character
        new_s = ''.join('1' if c == '0' else '0' if c == '1' else c for c in s)
        flipped.append(new_s)
    return flipped

def binary_groups_to_POS_expression(groups: list[str]) -> str:
    def term_to_expression(term: str) -> str:
        expression_parts = []
        variables = ['A', 'B', 'C', 'D']
        
        for i, bit in enumerate(term):
            if bit == '1':
                expression_parts.append(variables[i])
            elif bit == '0':
                expression_parts.append(str(variables[i]) + "'")
            # Skip '-' bits
        
        return '+'.join(expression_parts)
    
    # Convert each group to expression and wrap in parentheses
    group_expressions = ["(" + str(term_to_expression(group)) + ")" for group in groups]
    return ''.join(group_expressions)

def binary_groups_to_SOP_simplified_expression(groups: list[str]) -> str:
    def term_to_expression(term: str) -> str:
        expression_parts = []
        variables = ['A', 'B', 'C', 'D']
        
        for i, bit in enumerate(term):
            if bit == '1':
                expression_parts.append(variables[i])
            elif bit == '0':
                expression_parts.append(str(variables[i]) + "'")
            # Skip '-' bits
        
        # Join without '+' to make product terms
        return ''.join(expression_parts)

    # Convert each group to expression
    group_expressions = [term_to_expression(group) for group in groups]
    
    # Join with '+' to create sum of products
    return '+'.join(group_expressions)

kmap_size = request_kmap_size()
analysis_type = request_analysis_type()
minterms = request_kmap_input(kmap_size)
# print(minterms)
print("Inputted KMAP!")
print_kmap(minterms)
input()

if analysis_type == 2:
    # add missing minterms for non existing binaries atm. Delete old ones where required is true
    minterms = transform_minterms(minterms)
    # print(minterms)
    print("Flipped KMAP!")
    print_kmap(minterms)
    input()
    # pass

all_implicants = [q['binary'] for q in minterms]
pm_implicants = [q['binary'] for q in minterms if q['required']]

# print(pm_implicants)

prime_implicants = get_prime_implicants(all_implicants)
# print(prime_implicants)
pi_chart = create_prime_implicant_chart(prime_implicants, pm_implicants)
# print(pi_chart)
results = find_valid_combinations(pi_chart)

# print("RES")
for result in results:
    if analysis_type == 2:
        result = flip_binary_strings(result)
        result = binary_groups_to_POS_expression(result)
        # print(result)
    else:
        result = binary_groups_to_SOP_simplified_expression(result)
        # print(result)

    print(result)