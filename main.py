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
    for i in range(len(prime_implicant_chart.keys())):
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
    Tests combinations of three implicants to find those that provide complete coverage.
    
    Args:
        coverage_dict: Dictionary mapping prime implicants to their coverage arrays
    Returns:
        List of valid combinations (each combination is a list of prime implicants)
    """
    # Get all possible implicant combinations
    implicants = list(coverage_dict.keys())
    num_columns = len(list(coverage_dict.values())[0])
    valid_solutions = []
    
    # Try every possible combination of 3 implicants
    # (we know we need at least 3 for full coverage in this case)
    for i in range(len(implicants)):
        for j in range(i + 1, len(implicants)):
            for k in range(j + 1, len(implicants)):
                # Get the three implicants to test
                imp1 = implicants[i]
                imp2 = implicants[j]
                imp3 = implicants[k]
                
                # Check if this combination covers all columns
                is_valid = True
                for col in range(num_columns):
                    # If any column isn't covered, this combination is invalid
                    if not (coverage_dict[imp1][col] or 
                           coverage_dict[imp2][col] or 
                           coverage_dict[imp3][col]):
                        is_valid = False
                        break
                
                # If we found a valid combination, add it to solutions
                if is_valid:
                    valid_solutions.append([imp1, imp2, imp3])
    
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

all_implicants = [q['binary'] for q in minterms]
pm_implicants = [q['binary'] for q in minterms if q['required']]

prime_implicants = get_prime_implicants(all_implicants)
pi_chart = create_prime_implicant_chart(prime_implicants, pm_implicants)
result = find_valid_combinations(pi_chart)

print(result)

# merge_minterms([1, 2, 3], [4, 5, 6])